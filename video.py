import requests
import aria2p
from datetime import datetime
from status import format_progress_bar
import asyncio
import os, time
import logging

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

async def download_video(url, reply_msg, user_mention, user_id):
async def download_video(url, reply_msg, user_mention, user_id):
    # Fetch API data
    response = requests.get(f"https://terabox.udayscriptsx.workers.dev/?url={url}")
    response.raise_for_status()
    data = response.json()

    if not data:
        raise Exception("API response is empty or invalid.")

    video_file_name = data.get("file_name")
    fast_download_link = data.get("direct_link")
    thumbnail_url = data.get("thumb")
    video_size = data.get("size", "Unknown")
    video_size_bytes = data.get("sizebytes", 0)

    if not fast_download_link:
        raise Exception("Fast download link is missing in the API response.")

    # Add download to aria2
    download = aria2.add_uris([fast_download_link])
    start_time = datetime.now()

    # Monitor download progress
    while not download.is_complete:
        download.update()
        percentage = download.progress
        done = download.completed_length
        total_size = download.total_length
        speed = download.download_speed
        eta = download.eta
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
        progress_text = format_progress_bar(
            filename=f"{video_file_name} ({video_size})",
            percentage=percentage,
            done=done,
            total_size=total_size,
            status="Downloading",
            eta=eta,
            speed=speed,
            elapsed=elapsed_time_seconds,
            user_mention=user_mention,
            user_id=user_id,
            aria2p_gid=download.gid
        )
        await reply_msg.edit_text(progress_text)
        await asyncio.sleep(2)

    # Handle download completion
    if download.is_complete:
        file_path = download.files[0].path

        # Download thumbnail
        thumbnail_path = "thumbnail.jpg"
        thumbnail_response = requests.get(thumbnail_url)
        with open(thumbnail_path, "wb") as thumb_file:
            thumb_file.write(thumbnail_response.content)

        await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ...")

        return file_path, thumbnail_path, video_file_name, video_size
    else:
        raise Exception("Download failed")
async def upload_video(client, file_path, thumbnail_path, video_title, video_size, reply_msg, collection_channel_id, user_mention, user_id, message):
    file_size = os.path.getsize(file_path)
    uploaded = 0
    start_time = datetime.now()
    last_update_time = time.time()

    async def progress(current, total):
        nonlocal uploaded, last_update_time
        uploaded = current
        percentage = (current / total) * 100
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
        
        if time.time() - last_update_time > 2:
            progress_text = format_progress_bar(
                filename=f"{video_title} ({video_size})",
                percentage=percentage,
                done=current,
                total_size=total,
                status="Uploading",
                eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                speed=current / elapsed_time_seconds if current > 0 else 0,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=""
            )
            try:
                await reply_msg.edit_text(progress_text)
                last_update_time = time.time()
            except Exception as e:
                logging.warning(f"Error updating progress message: {e}")

    with open(file_path, 'rb') as file:
        collection_message = await client.send_video(
            chat_id=collection_channel_id,
            video=file,
            caption=(
                f"✨ {video_title}\n"
                f"📦 Size: {video_size}\n"
                f"👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ: {user_mention}\n"
                f"📥 ᴜsᴇʀ ʟɪɴᴋ: tg://user?id={user_id}"
            ),
            thumb=thumbnail_path,
            progress=progress
        )
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=collection_channel_id,
            message_id=collection_message.id
        )
        await asyncio.sleep(1)
        await message.delete()
        await message.reply_sticker("CAACAgIAAxkBAAEZdwRmJhCNfFRnXwR_lVKU1L9F3qzbtAAC4gUAAj-VzApzZV-v3phk4DQE")

    await reply_msg.delete()

    # Clean up temporary files
    os.remove(file_path)
    os.remove(thumbnail_path)
    return collection_message.id
