from io import BytesIO

from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv()
api_token = os.getenv("API_TOKEN")
upload_url = os.getenv("VANCE_API_UPLOAD_URL")
transform_url = os.getenv("VANCE_API_TRANSFORM_URL")
download_url = os.getenv("VANCE_API_DOWNLOAD_URL")
progress_url = os.getenv("VANCE_API_PROGRESS_URL")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")


app = Client("Mieux", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


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


def dispatch_media_download(trans_uid) -> BytesIO:
    remote_file_url = (
        download_url + "?trans_id=" + trans_uid + "&api_token=" + api_token
    )
    response = requests.get(remote_file_url)
    return BytesIO(response.content)


@app.on_message(filters.command("start") & filters.private)
def start(client: Client, message: Message):
    app.send_message(message.chat.id, "Hello! How can I help you?")


@app.on_message(filters.command("enhance") & filters.private)
def photo_handler(client: Client, message: Message):
    app.send_message(
        message.chat.id, "Send me a photo to enhance its quality with AI"
    )


@app.on_message(filters.photo)
def enhance_photo(client: Client, message: Message):
    if message.photo:
        message.reply_text("I'm enhancing your photo...")
        process_media(message)
    else:
        message.reply_text("The message does not contain any photo.")


def process_media(message: Message):
    try:
        file_data = app.download_media(message, "", True)
        upload_uid = dispatch_media_upload(file_data)
        trans_uid = dispatch_media_transform(upload_uid)
        media = dispatch_media_download(trans_uid)
        message.reply_photo(media)
        message.reply_text("Done, I hope you like it!")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        message.reply_text("Something went wrong while processing your photo.")


app.run()
