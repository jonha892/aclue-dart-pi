from io import BytesIO
from time import sleep

from picamera import PiCamera
from fastapi import FastAPI, Response


camera = PiCamera()
camera.start_preview()
sleep(2)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/new-image")
async def new_image():
    img_byte_stream = BytesIO()
    camera.capture(img_byte_stream, "png")
    
    headers = { 'Access-Control-Allow-Origin': '*' }
    return Response(content=img_byte_stream.getvalue(), media_type="image/png", headers=headers)
