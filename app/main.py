"""Brief: FAST-API based microservice for the Kattila happenings."""
import os, secrets, time

from fastapi import FastAPI, Security, UploadFile, HTTPException, status, WebSocket, Depends
from fastapi.responses import Response, FileResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from app.seuranta import SeurantaUsers
import aiofiles
import asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
seuranta_users: SeurantaUsers = SeurantaUsers()

INTERESTED_MAX = 10
INTERESTED_TIMEOUT = 15 * 60
interested: list[float] = []


def init_dir(name: str, default: str, parent=None):
    """Initializing a directory.

    Brief:
        Create a directory dictated by the environment variable called `name`
        or default is such a variable is not found. Insert parent path at the
        beginning if given.

    Returns:
        A string containing the path to the created directory.
    """
    dirc = os.getenv(name)
    if dirc is None:
        dirc = default
    if parent is not None:
        dirc = os.path.join(parent, dirc)
    if not os.path.exists(dirc):
        os.makedirs(dirc)
    return dirc


def init_api_key(name, default):
    """Initializing an api-key.

    Returns:
        A tuple containing the api-key-header and api-key respectively.
    """
    header = APIKeyHeader(name="X-API-Key")
    if not (path := os.getenv(name)):
        path = default
    with open(path, "r") as key_file:
        # File leaves a trailing newline
        key = key_file.read().strip()
    return header, key


# Initialize paths and api-key.
DATA_DIR = init_dir("DATA_DIR", "/tmp/data")
COFFEE_DIR = init_dir("COFFEE_DIR", "coffee", parent=DATA_DIR)
API_KEY_HEADER, API_KEY = init_api_key("API_KEY_FILE", "/run/secrets/apikey")


@app.get("/")
async def lifesign():
    return Response(status_code=status.HTTP_200_OK)


async def refresh_interested():
    t = time.time()
    while len(interested) != 0 \
        and t - interested[0] > INTERESTED_TIMEOUT:
        interested.pop(0)


@app.post("/interested", status_code=status.HTTP_200_OK)
async def post_interested():
    refresh_interested()
    if len(interested) > INTERESTED_MAX:
        return
    interested.append(time.time())


@app.get("/interested/amount", status_code=status.HTTP_200_OK)
async def get_interested_amount():
    await refresh_interested()
    return len(interested)


@app.get("/interested/max", status_code=status.HTTP_200_OK)
async def get_interested_max():
    return INTERESTED_MAX


@app.get("/seuranta/users", status_code=status.HTTP_200_OK)
async def get_seuranta_users():
    return seuranta_users


@app.put("/seuranta/users", status_code=status.HTTP_200_OK)
async def put_seuranta_users(users: SeurantaUsers, key: str = Security(API_KEY_HEADER)):
    authorized = secrets.compare_digest(key, API_KEY)
    if not authorized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    seuranta_users.users = users.users
    return seuranta_users


@app.put("/coffee/image")
async def update_coffee_image(file: UploadFile, key: str = Security(API_KEY_HEADER)):
    authorized = secrets.compare_digest(key, API_KEY)
    if not authorized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    ACCEPTED_FILE_TYPES = ["image/jpeg", "image/webp", "image/png"]
    if not file.content_type in ACCEPTED_FILE_TYPES:
        return Response(
            content=f"Bad content type. Accepted types are: {ACCEPTED_FILE_TYPES}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )
    extension = file.content_type.split("/")[-1]

    for dir_entry in os.scandir(path=COFFEE_DIR):
        os.remove(dir_entry)

    image_path = os.path.join(COFFEE_DIR, f"image.{extension}")
    async with aiofiles.open(image_path, "wb") as image_file:
        await image_file.write(await file.read())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/coffee/image", status_code=status.HTTP_200_OK)
async def get_coffee_image():
    COFFEE_PLACEHOLDER_PATH = "app/coffee-placeholder.png"

    image_path = None
    for file in os.scandir(path=COFFEE_DIR):
        image_path = file
    if not image_path:
        image_path = COFFEE_PLACEHOLDER_PATH

    return FileResponse(path=image_path)


class PubSub:
    """
    Simple observer pattern implementation in asyncio.
    """

    def __init__(self):
        self.subscribers = set()

    def subscribe(self):
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue):
        self.subscribers.discard(queue)

    async def publish(self, message):
        for queue in self.subscribers:
            await queue.put(message)


pubsub = PubSub()


@app.get("/announcer/new")
async def new_message(msg: str):
    await pubsub.publish(msg)


@app.websocket("/announcer/listen")
async def listen_messages(websocket: WebSocket):
    await websocket.accept()
    queue = pubsub.subscribe()

    try:
        while True:
            message = await queue.get()
            await websocket.send_text(message)
    finally:
        pubsub.unsubscribe(queue)
