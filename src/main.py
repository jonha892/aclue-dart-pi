from io import BytesIO
from time import sleep
import platform
from pprint import pprint
import base64
import os

from fastapi import FastAPI, Response
from pydantic import BaseModel

DATA_PATH = "../data"

app = FastAPI()

camera = None
if platform.machine() == "armv7l":
    print("RaspberryPi detected, setting up PI specific paths")

    from picamera import PiCamera
    camera = PiCamera()
    camera.resolution = (1024,720)
    camera.start_preview()
    sleep(2)

    @app.get("/image")
    async def take_image():
        img_byte_stream = BytesIO()
        camera.capture(img_byte_stream, "png")
        
        headers = { 'Access-Control-Allow-Origin': '*' }
        return Response(content=img_byte_stream.getvalue(), media_type="image/png", headers=headers)

    @app.put("led-green")
    async def led_green():
        pass

    @app.put("led-red")
    async def led_green():
        pass

class ThrowRequest(BaseModel):
    series_id: str
    throw_id: str
    img_str: str
    dart: str

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/throw")
async def throw(throw: ThrowRequest):
    save_path = os.path.join(DATA_PATH, throw.series_id, f"{throw.throw_id}.png")
    with open(save_path, 'wb') as f:
        f.write(base64.urlsafe_b64decode(throw.img_str))

    

    return {"message": "success"}

@app.get("/label/{throw_id}")
async def get_label():
    pass

@app.post("/label/{throw_id}")
async def update_label():
    pass