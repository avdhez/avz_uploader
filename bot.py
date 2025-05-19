import os
from pyrogram import Client, filters
from pyrogram.types import Message
from downloader import download_and_process_links
from uploader import clean_download_dir

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ALLOWED_USERS = {123456789}  # Replace with your own Telegram user ID
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.reply("Unauthorized user.")
    await message.reply(
        "**Welcome!**\n\nSend me direct or yt-dlp-supported links (e.g., .zip, .m3u8).\n"
        "- Download files\n"
        "- Extract zip files\n"
        "- Upload with progress\n"
        "- Clean all messages after task"
    )

@app.on_message(filters.private & filters.text)
async def handle_links(client, message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        return await message.reply("Unauthorized user.")

    links = message.text.split()
    status = await message.reply("Processing your links...")

    try:
        await download_and_process_links(links, message.chat.id, status, app)
    finally:
        await status.delete()
        clean_download_dir(DOWNLOAD_DIR)

app.run()
