import os, secrets
import aiofiles

from fastapi import FastAPI, Security, UploadFile, HTTPException, status, WebSocket
from fastapi.responses import Response, FileResponse
from fastapi.security import APIKeyHeader
from watchfiles import awatch
from app.seuranta import SeurantaUser, SeurantaUsers

app = FastAPI()

seuranta_users: SeurantaUsers = SeurantaUsers()

data_dir = os.getenv("DATA_DIR")
if not data_dir:
    data_dir = "/tmp/data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

COFFEE_SUBDIR = "coffee"
coffee_dir = os.path.join(data_dir, COFFEE_SUBDIR)
if not os.path.exists(coffee_dir):
    os.mkdir(coffee_dir)

ANNOUNCER_FILE = "announcer"
announcer_path = os.path.join(data_dir, ANNOUNCER_FILE)

api_key_header = APIKeyHeader(name="X-API-Key")
if not (api_key_path := os.getenv("API_KEY_FILE")):
    api_key_path = "/run/secrets/apikey"
with open(api_key_path, "r") as key_file:
    # File leaves a trailing newline
    api_key = key_file.read().strip()


@app.get("/")
async def lifesign():
    return Response(status_code=status.HTTP_200_OK)


@app.get("/seuranta/users", status_code=status.HTTP_200_OK)
async def get_seuranta_users():
    return seuranta_users


@app.put("/seuranta/users", status_code=status.HTTP_200_OK)
async def put_seuranta_users(users: SeurantaUsers, key: str = Security(api_key_header)):
    authorized = secrets.compare_digest(key, api_key)
    if not authorized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    seuranta_users.users = users.users
    return seuranta_users


@app.put("/coffee/image")
async def update_coffee_image(file: UploadFile, key: str = Security(api_key_header)):
    authorized = secrets.compare_digest(key, api_key)
    if not authorized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    ACCEPTED_FILE_TYPES = ["image/jpeg", "image/webp", "image/png"]
    if not file.content_type in ACCEPTED_FILE_TYPES:
        return Response(
            content=f"Bad content type. Accepted types are: {ACCEPTED_FILE_TYPES}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )
    extension = file.content_type.split("/")[-1]

    for dir_entry in os.scandir(path=coffee_dir):
        os.remove(dir_entry)

    image_path = os.path.join(coffee_dir, f"image.{extension}")
    async with aiofiles.open(image_path, "wb") as image_file:
        await image_file.write(await file.read())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/coffee/image", status_code=status.HTTP_200_OK)
async def get_coffee_image():
    COFFEE_PLACEHOLDER_PATH = "app/coffee-placeholder.png"

    image_path = None
    for file in os.scandir(path=coffee_dir):
        image_path = file
    if not image_path:
        image_path = COFFEE_PLACEHOLDER_PATH

    return FileResponse(path=image_path)


@app.get("/announcer/new")
async def new_message(msg: str):
    async with aiofiles.open(announcer_path, "w") as file:
        await file.write(msg)


@app.websocket("/announcer/listen")
async def listen_messages(websocket: WebSocket):
    await websocket.accept()
    async for _ in awatch(announcer_path):
        async with aiofiles.open(announcer_path, "r") as file:
            message = await file.read()
            await websocket.send_text(message)
