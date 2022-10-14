from io import BytesIO
from time import sleep
import platform
from pprint import pprint
import base64
import os
from turtle import width

from fastapi import FastAPI, Response

app = FastAPI()

camera = None
width = 1024
height = 720

headers = {"Access-Control-Allow-Origin": "*"}

if platform.machine() == "armv7l":
    print("RaspberryPi detected, setting up PI specific paths")

    from picamera import PiCamera

    camera = PiCamera()
    camera.resolution = (width, height)
    camera.start_preview()
    sleep(2)

    @app.get("/image")
    async def take_image():
        img_byte_stream = BytesIO()
        camera.capture(img_byte_stream, "png")

        return Response(
            content=img_byte_stream.getvalue(), media_type="image/png", headers=headers
        )

    @app.get("/resolution")
    async def resolution():
        content = {
            "width": width,
            "height": height,
        }

        return Response(content=content, headers=headers)

    @app.put("led-green")
    async def led_green():
        pass

    @app.put("led-red")
    async def led_green():
        pass

else:
    print("WARN: PI not detected. API is limited!")


@app.get("/")
async def root():
    return {"message": "Hello World"}
