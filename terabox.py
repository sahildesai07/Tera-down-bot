from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from datetime import datetime
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
import os
import time
import random
import string
import json
from shortzy import Shortzy
from uuid import uuid4
from helper_func import (
    get_shortlink,
    get_verify_status,
    update_verify_status,
    get_exp_time,
)
from config import *
from database.database import present_user, add_user, db_verify_status, db_update_verify_status
from video import download_video, upload_video

load_dotenv('config.env', override=True)

logging.basicConfig(level=logging.INFO)

api_id = os.environ.get('TELEGRAM_API', '22505271')
if not api_id:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

api_hash = os.environ.get('TELEGRAM_HASH', 'c89a94fcfda4bc06524d0903977fc81e')
if not api_hash:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)

bot_token = os.environ.get('BOT_TOKEN', '7156255687:AAEXQtlTzE8Jbwt9VD6NLfcZX08Czu7w7gQ')
if not bot_token:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

dump_id = os.environ.get('DUMP_CHAT_ID', '-1002062925443')
if not dump_id:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    dump_id = int(dump_id)

fsub_id = os.environ.get('FSUB_ID', '-1002108419450')
if not fsub_id:
    logging.error("FSUB_ID variable is missing! Exiting now")
    exit(1)
else:
    fsub_id = int(fsub_id)

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("check"))
async def check(client, message):
    user_id = message.from_user.id

    verify_status = await db_verify_status(user_id)
    print(f"Verify status for user {user_id}: {verify_status}")

    if verify_status['is_verified']:
        expiry_time = get_exp_time(VERIFY_EXPIRE - (time.time() - verify_status['verified_time']))
        await message.reply(f"Your token is verified and valid for {expiry_time}.")
    else:
        await message.reply("Your token is not verified or has expired.")

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        user_details = json.dumps(
            {"username": message.from_user.username, "first_name": message.from_user.first_name, "last_name": message.from_user.last_name}
        )
        await add_user(user_id, user_details)

    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEYonplzwrczhVu3I6HqPBzro3L2JU6YAACvAUAAj-VzAoTSKpoG9FPRjQE")
    await asyncio.sleep(2)
    await sticker_message.delete()

    user_mention = message.from_user.mention
    reply_message = f"ᴡᴇʟᴄᴏᴍᴇ, {user_mention}.\n\n🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ᴡɪᴛʜɪɴ ғᴇᴡ sᴇᴄᴏɴᴅs ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ ✨."
    join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/ultroid_official")
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://t.me/ultroidxTeam")
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])
    await message.reply_text(reply_message, reply_markup=reply_markup)

async def is_user_member(client, user_id):
    try:
        member = await client.get_chat_member(fsub_id, user_id)
        logging.info(f"User {user_id} membership status: {member.status}")
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking membership status for user {user_id}: {e}")
        return False

@app.on_message(filters.text)
async def handle_message(client, message: Message):
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    is_member = await is_user_member(client, user_id)

    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/ultroid_official")
        reply_markup = InlineKeyboardMarkup([[join_button]])
        await message.reply_text("ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ.", reply_markup=reply_markup)
        return

    print(f"Received message from user: {user_id}")

    if user_id in ADMINS:
        await message.reply("You are the owner! Additional actions can be added here.")
    else:
        if not await present_user(user_id):
            try:
                await add_user(user_id)
            except Exception as e:
                print(f"Error adding user: {e}")

        verify_status = await db_verify_status(user_id)
        print(f"Verify status for user {user_id}: {verify_status}")

        if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
            await db_update_verify_status(user_id, {**verify_status, 'is_verified': False})

        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            print(f"Extracted token: {token}")
            if verify_status['verify_token'] != token:
                await message.reply("Your token is invalid or Expired. Try again by clicking /start")
                return
            await db_update_verify_status(user_id, {**verify_status, 'is_verified': True, 'verified_time': time.time()})
            await message.reply("Your token successfully verified and valid for: 24 Hour")
        elif len(message.text) > 7 and verify_status['is_verified']:
            # Handle valid verified user message
            await handle_message(client, message)
        else:
            if IS_VERIFY and not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                print(f"Generated token: {token}")
                link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.me/Terabox_sis_bot?start=verify_{token}')
                await db_update_verify_status(user_id, {**verify_status, 'verify_token': token, 'link': link})
                await message.reply(f"Your Ads token is expired, refresh your token and try again.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE)}\n\nWhat is the token?\n\nThis is an ads token. If you pass 1 ad, you can use the bot for 24 Hour after passing the ad.\n\n[Click here to verify your token]({link})")

    terabox_link = message.text.strip()
    if "terabox" not in terabox_link:
        await message.reply_text("ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ.")
        return

    reply_msg = await message.reply_text("sᴇɴᴅɪɴɢ ʏᴏᴜ ᴛʜᴇ ᴍᴇᴅɪᴀ...🤤")

    try:
        file_path, thumbnail_path, video_title = await download_video(terabox_link, reply_msg, user_mention, user_id)
        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, dump_id, user_mention, user_id, message)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await reply_msg.edit_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ.\nɪғ ʏᴏᴜʀ ғɪʟᴇ sɪᴢᴇ ɪs ᴍᴏʀᴇ ᴛʜᴀɴ 120ᴍʙ ɪᴛ ᴍɪɢʜᴛ ғᴀɪʟ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ.")

if __name__ == "__main__":
    app.run()
