from io import BytesIO
import io
from time import sleep
import platform
import json
import logging, logging.config
import time

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

@app.get("/api/imagev2")
async def take_image_v2():
    cap = cv.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    cap.set(5, 30)

    if not cap.isOpened():
        print("Cannot open camera")
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

    # Save the flattened array as a PNG byte buffer
    with io.BytesIO() as output:
        writer = png.Writer(width=width, height=height, bitdepth=8, planes=channels, greyscale=False)
        writer.write(output, flat_arr)
        png_bytes = output.getvalue()

    logger.info("image converted to bytes")

    return Response(
            content=png_bytes, media_type="image/png", headers=headers
        )

@app.get("/")
async def root():
    return {"message": "Hello World"}
