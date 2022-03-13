from io import BytesIO
from time import sleep

from picamera import PiCamera
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/new-image")
async def new_image():
    img_byte_stream = BytesIO()
    with PiCamera() as camera:
        camera.resolution = (1920,1080)
        camera.start_preview()
        sleep(1)
        camera.capture(img_byte_stream, "png")
        camera.close()
        
    
    headers = { 'Access-Control-Allow-Origin': '*' }
    return Response(content=img_byte_stream.getvalue(), media_type="image/png", headers=headers)
