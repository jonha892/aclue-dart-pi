from fastapi import FastAPI, Response
from io import BytesIO
from time import sleep
from picamera import PiCamera

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/new-image")
async def new_image():
    img_byte_stream = BytesIO()
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    camera.capture(img_byte_stream, "png")
    camera.close()
    return Response(content=img_byte_stream.getvalue(), media_type="image/png")
