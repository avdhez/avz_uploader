import os
import aiohttp
import asyncio
import zipfile
import yt_dlp
from uploader import upload_file_with_progress, update_status_bar

DOWNLOAD_DIR = "downloads"

async def download_regular_file(session, url, file_path, status, file_name):
    async with session.get(url) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        with open(file_path, "wb") as f:
            downloaded = 0
            last_update = 0
            async for chunk in resp.content.iter_chunked(1024 * 512):
                f.write(chunk)
                downloaded += len(chunk)
                if asyncio.get_event_loop().time() - last_update >= 5:
                    await update_status_bar(status, "Downloading", file_name, downloaded, total)
                    last_update = asyncio.get_event_loop().time()
    await update_status_bar(status, "Downloaded", file_name, downloaded, total)

async def download_ytdlp_file(url, status, chat_id, app):
    await status.edit_text("Fetching info with yt-dlp...")
    output = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {"outtmpl": output, "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
    await upload_file_with_progress(file_path, status, chat_id, app)

async def extract_zip_and_upload(zip_path, status, chat_id, app):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DOWNLOAD_DIR)
        for file in zip_ref.namelist():
            file_path = os.path.join(DOWNLOAD_DIR, file)
            if os.path.isfile(file_path):
                await upload_file_with_progress(file_path, status, chat_id, app)
                os.remove(file_path)

async def download_and_process_links(links, chat_id, status, app):
    async with aiohttp.ClientSession() as session:
        for url in links:
            file_name = url.split("/")[-1].split("?")[0]
            file_path = os.path.join(DOWNLOAD_DIR, file_name)

            if any(x in url for x in ("m3u8", "youtube.com", "youtu.be")):
                await download_ytdlp_file(url, status, chat_id, app)
            else:
                await download_regular_file(session, url, file_path, status, file_name)
                if file_path.endswith(".zip"):
                    await status.edit_text(f"Extracting {file_name}...")
                    await extract_zip_and_upload(file_path, status, chat_id, app)
                else:
                    await upload_file_with_progress(file_path, status, chat_id, app)
                os.remove(file_path)
