import os

from fastapi import FastAPI
from fastapi.responses import FileResponse


app = FastAPI()


image_path = os.getenv("IMAGE_PATH")


@app.get("/coffee/image")
async def get_coffee_image():
    return FileResponse(path=image_path, media_type="image/png")
