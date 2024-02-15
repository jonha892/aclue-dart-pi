from io import BytesIO
import io
from time import sleep
import platform
import json
import logging, logging.config

import cv2 as cv
import numpy as np
import png

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"default": {"format": "%(asctime)s [%(process)s] %(levelname)s: %(message)s"}},
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "INFO",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "gunicorn": {"propagate": True},
        "gunicorn.access": {"propagate": True},
        "gunicorn.error": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "uvicorn.error": {"propagate": True},
    },
}

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



camera = None
#width = 1280
#height = 720
width = 1920
height = 1080
channels = 3
cap = cv.VideoCapture(0)

headers = {"Access-Control-Allow-Origin": "*"}

with_pi_camera = False
if platform.machine() == "armv7l" and with_pi_camera:
    logger.info("RaspberryPi detected, setting up PI specific paths")

    from picamera import PiCamera

    camera = PiCamera()
    camera.resolution = (width, height)
    camera.start_preview()
    sleep(2)

    @app.get("/api/image")
    async def take_image():
        img_byte_stream = BytesIO()
        camera.capture(img_byte_stream, "png")

        return Response(
            content=img_byte_stream.getvalue(), media_type="image/png", headers=headers
        )

    @app.put("led-green")
    async def led_green():
        pass

    @app.put("led-red")
    async def led_green():
        pass
else:
    logger.warn("PI not detected. API is limited!")

@app.get("/api/resolution")
async def resolution():
    content = {
        "width": width,
        "height": height,
    }

    return Response(content= json.dumps(content), headers=headers)

def take_image():
    cap.set(3, width)
    cap.set(4, height)
    cap.set(5, 30)

    if not cap.isOpened():
        logger.info("Cannot open camera")
        exit()

    logger.info("take_image_v2")
    _ret, frame = cap.read()
    logger.info(f"got image with shape: {frame.shape}")

    arr = np.zeros(frame.shape, dtype=frame.dtype)
    arr[:,:,0] = frame[:,:, 2]
    arr[:,:,1] = frame[:,:, 1]
    arr[:,:,2] = frame[:,:, 0]
    logger.info(f"reordered image with shape {arr.shape}")
    logger.info(f"width: {width}, height: {height}, channels: {channels}")


    # Reshape the (height, width, channels) array into 2D array with shape that png.Writer expects
    # (height, width * channels)
    flat_arr = arr.reshape(height, -1)
    logger.info(f'flat_arr shape: {flat_arr.shape}, flat_arr type: {flat_arr.dtype}')

    return flat_arr

@app.get("/api/imagev2")
async def take_image_v2():
    flat_arr = take_image()

    # Save the flattened array as a PNG byte buffer
    with io.BytesIO() as output:
        writer = png.Writer(width=width, height=height, bitdepth=8, planes=channels, greyscale=False)
        writer.write(output, flat_arr)
        png_bytes = output.getvalue()

    logger.info("image converted to bytes")

    return Response(
            content=png_bytes, media_type="image/png", headers=headers
        )

import load
import infer
import torch
from ultralytics import YOLO
from torchvision.transforms import v2

transforms = v2.Compose([
    v2.Resize((640, 640)),
    v2.PILToTensor()
])
model = YOLO("../data/best.pt")

pi_img_width, pi_img_height = 1920, 1080
yolo_img_width, yolo_img_height = 640, 640
yolo_size = yolo_img_width, yolo_img_height

crop_window = 450, 350, 1440, 1080
orig_size = crop_window[2] - crop_window[0], crop_window[3] - crop_window[1]

@app.get("/api/prediction")
async def prediction():

    #img_tensor = take_image()
    # random tensor in the shape of the cropped image
    img_tensor = torch.rand((3, crop_window[2] - crop_window[0], crop_window[3] - crop_window[1]), dtype=torch.float32)
    
    logger.info(f'img_tensor shape: {img_tensor.shape}')
    img_tensor = transforms(img_tensor)
    logger.info(f'after transform img_tensor shape: {img_tensor.shape}')
    img_tensor = img_tensor / 255.0
    img_tensor = img_tensor.unsqueeze(0)

    result = model(img_tensor)
    logger.info(f'result len {len(result)}')
    predictions = { 'boxes': result[0].boxes.numpy().data.tolist() }

    resized_predictions = load.translate_yolo_to_crop(predictions, orig_size=orig_size, yolo_size=yolo_size)

    anchor_candidates = infer.filter(resized_predictions, class_id=infer.CLASS_ANCHOR)
    anchor_candidates = infer.to_coordinates(anchor_candidates)
    homography_matrix = infer.build_homography_matrix_2(anchor_candidates)

    anchors = []
    for candidate in anchor_candidates:
        anchor = infer.translate_position(candidate, homography_matrix)
        logger.info('anchor', anchor)
        anchors.append(anchor)

    darts = infer.filter(resized_predictions, class_id=infer.CLASS_DART)
    darts = infer.to_coordinates(darts)
    result = []

    for dart in darts:
        x, y = dart

        dart_pos = infer.translate_position((x, y), homography_matrix)
        score = infer.build_score_prediction(dart_pos)
        result.append((score, dart_pos))

    return Response(
            content=json.dumps(result), media_type="application/json", headers=headers
        )

@app.get("/")
async def root():
    return {"message": "Hello World"}
