from io import BytesIO

from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_token = os.getenv("VANCE_API_TOKEN")
upload_url = os.getenv("VANCE_API_UPLOAD_URL")
transform_url = os.getenv("VANCE_API_TRANSFORM_URL")
download_url = os.getenv("VANCE_API_DOWNLOAD_URL")


app = Client(
    "Mieux",
    api_id=os.getenv("TELEGRAM_API_ID"),
    api_hash=os.getenv("TELEGRAM_API_HASH"),
    bot_token= os.getenv("TELEGRAM_BOT_TOKEN")
    )


def dispatch_media_upload(file: BytesIO = None):
    file.seek(0)
    response = requests.post(
        upload_url,
        files={"file": (file.name, file)},
        data={"api_token": api_token},
    )
    r = response.json()
    if r["code"] == 200:
        uid: object = r["data"]["uid"]
        return uid


def dispatch_media_transform(uid: str = None):
    json_path = "configs/enlarge.json"
    jparam = {}
    with open(json_path, "rb") as f:
        jparam = json.load(f)

    data = {
        "api_token": api_token,
        "uid": uid,
        "jconfig": json.dumps(jparam),
    }
    response = requests.post(transform_url, data)
    r = response.json()
    if r["code"] == 200:
        trans_uid: object = r["data"]["trans_id"]
        return trans_uid


def dispatch_media_download(trans_uid):
    remote_file_url = (
        download_url + "?trans_id=" + trans_uid + "&api_token=" + api_token
    )
    response = requests.get(remote_file_url, stream=True)

    dst_path = "path/to/file.jpg"

    response = requests.get(remote_file_url, stream=True)

    f = open(dst_path, "wb")
    for chunk in response.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
    f.close()


@app.on_message(filters.command("start") & filters.private)
def start(client: Client, message: Message):
    app.send_message(message.chat.id, "Hello! How can I help you?")


@app.on_message(filters.command("enhance") & filters.private)
def photo_handler(client: Client, message: Message):
    app.send_message(message.chat.id, "Send me a photo to enhance it with AI")


@app.on_message(filters.photo)
def enhance_photo(client: Client, message: Message):
    message.reply_text("I'm enhancing your photo...")
    process_media(message)
    message.reply_photo(open("/Users/yasna/Downloads/demo.jpg", "rb"))


def process_media(message):
    try:
        if message.media:
            file_data = app.download_media(message, "", True)
            upload_uid = dispatch_media_upload(file_data)
            trans_uid = dispatch_media_transform(upload_uid)
            dispatch_media_download(trans_uid)
        else:
            print("The message does not contain any media.")

    except Exception as e:
        print(f"Error: {e}")


app.run()
