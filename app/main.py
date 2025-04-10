import os
import aiofiles

from fastapi import FastAPI, UploadFile, status
from fastapi.responses import Response, FileResponse


app = FastAPI()


image_path = os.getenv("IMAGE_PATH")


@app.put("/coffee/image")
async def update_coffee_image(file: UploadFile):
    async with aiofiles.open(image_path, "wb") as image_file:
        await image_file.write(await file.read())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/coffee/image")
async def get_coffee_image():
    return FileResponse(path=image_path, media_type="image/png")
