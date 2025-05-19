import os
import asyncio
from pyrogram.types import Message

def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

async def update_status_bar(msg: Message, phase: str, filename: str, current: int, total: int):
    percent = int(current * 100 / total) if total else 0
    bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
    text = (f"{phase} {filename}\n"
            f"[{bar}] {percent}% ({format_bytes(current)}/{format_bytes(total)})")
    if msg.text != text:
        await msg.edit_text(text)

async def upload_file_with_progress(file_path, msg, chat_id, app):
    file_size = os.path.getsize(file_path)
    sent = 0
    last_update = 0

    async def progress(current, total):
        nonlocal sent, last_update
        sent = current
        now = asyncio.get_event_loop().time()
        if now - last_update >= 5:
            await update_status_bar(msg, "Uploading", os.path.basename(file_path), sent, total)
            last_update = now

    await app.send_document(chat_id, file_path, caption=os.path.basename(file_path), progress=progress)
    await msg.edit_text(f"Uploaded {os.path.basename(file_path)}")

def clean_download_dir(path):
    for f in os.listdir(path):
        fp = os.path.join(path, f)
        try:
            os.remove(fp)
        except:
            pass
