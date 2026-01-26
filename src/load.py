###
### Load image from PI
###
import json
from io import BytesIO

from PIL import Image
import requests

# faked
def load_image_from_pi_fake(path):
    with open(path, 'rb') as f:
        img = Image.open(f)
        img = img.convert('RGB')
        return img
    
def load_image_from_pi():
    url = 'http://raspberrypi:8000/api/imagev2'
    res = requests.get(url)
    img = Image.open(BytesIO(res.content))
    img = img.convert('RGB')
    return img

def preprocess_image(img, crop_window):
    img = img.crop(crop_window)
    return img

###
### get predictions from sagemaker endpoint
###

def get_predictions(img, client):
    # Create a BytesIO object to store the JPEG image bytes
    img_bytesio = BytesIO()

    # Save the JPEG image to the BytesIO object
    img.save(img_bytesio, format='JPEG')

    # Get the byte representation of the JPEG image
    img_bytes = img_bytesio.getvalue()
    response = client.invoke_endpoint(
        EndpointName='dartnet-test-yolov8-endpoint',
        Body=img_bytes,
        ContentType='image/png'
    )
    print(response)

    body = response['Body'].read()
    return json.loads(body.decode('utf-8'))

def rescale(xmin, ymin, xmax, ymax, orig_size=(990, 730), new_size=(640, 640)):
    orig_w, orig_h = orig_size
    new_w, new_h = new_size
    
    xmin = (xmin/new_w) * orig_w
    xmax = (xmax/new_w) * orig_w
    ymin = (ymin/new_h) * orig_h
    ymax = (ymax/new_h) * orig_h
    return xmin, ymin, xmax, ymax


def shift_box(box, shift=35):
    """
    Because of bug duing yolo formatting
    """
    xmin, ymin, xmax, ymax = box
    xmin += shift
    ymin += shift
    xmax += shift
    ymax += shift
    return xmin, ymin, xmax, ymax

###
### rescale predictions
### Probably not needed?
###
def translate_yolo_to_crop(predictions, orig_size=(990, 730), yolo_size=(640, 640)):
    res = []
    for i, box in enumerate(predictions['boxes']):
            xmin, ymin, xmax, ymax, p, x = box
            #print(xmin, ymin, xmax, ymax, p, x)
            xmin, ymin, xmax, ymax = rescale(xmin, ymin, xmax, ymax, orig_size, yolo_size)
            # tmp
            #xmin, ymin, xmax, ymax = shift_box((xmin, ymin, xmax, ymax))
            res.append([xmin, ymin, xmax, ymax, p, x])
    return res