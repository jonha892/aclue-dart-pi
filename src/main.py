from io import BytesIO
import io
from time import sleep
import platform
from pprint import pprint
import base64
import os
import json

import cv2 as cv
import numpy as np
from PIL import Image
from fastapi import FastAPI, Response

app = FastAPI()

camera = None
# width = 1024
# height = 720
width = 1920
height = 1024

cap = cv.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

headers = {"Access-Control-Allow-Origin": "*"}

with_pi_camera = False
if platform.machine() == "armv7l" and with_pi_camera:
    print("RaspberryPi detected, setting up PI specific paths")

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

    @app.get("/api/resolution")
    async def resolution():
        content = {
            "width": width,
            "height": height,
        }

        return Response(content= json.dumps(content), headers=headers)

    @app.put("led-green")
    async def led_green():
        pass

    @app.put("led-red")
    async def led_green():
        pass
else:
    print("WARN: PI not detected. API is limited!")

@app.get("/api/imagev2")
async def take_image_v2():
    _ret, frame = cap.read()
    #print(_ret, frame)
    print(_ret, "frame shape: ", frame.shape)
    # height, width, channels = frame.shape
    
    #img_encoded = cv.imencode(".png", frame)[1]
    shifted = np.zeros(frame.shape, dtype=frame.dtype)
    shifted[:,:,0] = frame[:,:, 2]
    shifted[:,:,1] = frame[:,:, 1]
    shifted[:,:,2] = frame[:,:, 0]

    im = Image.fromarray(shifted)
    
    # save image to an in-memory bytes buffer
    with io.BytesIO() as buf:
        im.save(buf, format='PNG')
        im_bytes = buf.getvalue()

    return Response(
            content=im_bytes, media_type="image/png", headers=headers
        )
@app.get("/")
async def root():
    return {"message": "Hello World"}
