import os, secrets
import aiofiles

from fastapi import FastAPI, Security, UploadFile, HTTPException, status
from fastapi.responses import Response, FileResponse
from fastapi.security import APIKeyHeader


app = FastAPI()


data_dir = os.getenv("DATA_DIR")
if not data_dir:
    data_dir = "/tmp/data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

api_key_header = APIKeyHeader(name="X-API-Key")
api_key_path = os.getenv("API_KEY_FILE")
if not api_key_path:
    api_key_path = "/run/secrets/apikey"
with open(api_key_path, "r") as key_file:
    # File leaves a trailing newline
    api_key = key_file.read().strip()


@app.get("/")
async def lifesign():
    return Response(status_code=status.HTTP_200_OK)


@app.put("/coffee/image")
async def update_coffee_image(file: UploadFile, key: str = Security(api_key_header)):
    authorized = secrets.compare_digest(key, api_key)
    if not authorized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    async with aiofiles.open(image_path, "wb") as image_file:
        await image_file.write(await file.read())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/coffee/image", status_code=status.HTTP_200_OK)
async def get_coffee_image():
    COFFEE_PLACEHOLDER_PATH = "app/coffee-placeholder.png"
    
    image_path = COFFEE_PLACEHOLDER_PATH
    return FileResponse(path=image_path)
