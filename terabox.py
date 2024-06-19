from datetime import datetime
import logging
import asyncio
import random
import string
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from os import environ
import time
from status import format_progress_bar  # Assuming this is a custom module
from video import download_video, upload_video  # Assuming these are custom modules
from database.database import present_user, add_user, full_userbase, del_user, db_verify_status, db_update_verify_status  # Assuming these are custom modules
from shortzy import Shortzy  # Assuming this is a custom module
from pymongo.errors import DuplicateKeyError
from web import keep_alive

load_dotenv('config.env', override=True)

logging.basicConfig(level=logging.INFO)

ADMINS = os.environ.get('ADMINS', '5878078253')
if len(ADMINS) == 0:
    logging.error("ADMINS variable is missing! Exiting now")
    exit(1)
    
api_id = os.environ.get('TELEGRAM_API', '24089352')
if len(api_id) == 0:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

api_hash = os.environ.get('TELEGRAM_HASH', 'd8712980f37bab2ba8a1db9a69b2d95a')
if len(api_hash) == 0:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)
    
bot_token = os.environ.get('BOT_TOKEN', '7493926455:AAGRBGNiZF2k3mn3lWoKOxq1Q1XcRTfYgU8')
if len(bot_token) == 0:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)
dump_id = os.environ.get('DUMP_CHAT_ID', '-1001862834499')
if len(dump_id) == 0:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    dump_id = int(dump_id)

fsub_id = os.environ.get('FSUB_ID', '-1001904747613')
if len(fsub_id) == 0:
    logging.error("FSUB_ID variable is missing! Exiting now")
    exit(1)
else:
    fsub_id = int(fsub_id)


mongo_url = os.environ.get('MONGO_URL', 'mongodb+srv://ultroidxTeam:ultroidxTeam@cluster0.gabxs6m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(mongo_url)
db = client['aphdlust']
users_collection = db['users']

SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "modijiurl.com")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "1b69cabcad8a473ca707823d783a0f9ccf7c3583")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 43200))  # 24 hours in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True") == "True"
TUT_VID = os.environ.get("TUT_VID", "https://t.me/Ultroid_Official/18")

def save_user(user_id, username):
    try:
        existing_user = users_collection.find_one({'user_id': user_id})
        if existing_user is None:
            users_collection.insert_one({'user_id': user_id, 'username': username})
            logging.info(f"Saved new user {username} with ID {user_id} to the database.")
        else:
            users_collection.update_one({'user_id': user_id}, {'$set': {'username': username}})
            logging.info(f"Updated user {username} with ID {user_id} in the database.")
    except DuplicateKeyError as e:
        logging.error(f"DuplicateKeyError: {e}")

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name} '
    return result

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

async def get_verify_status(user_id):
    verify = await db_verify_status(user_id)
    return verify

async def update_verify_status(user_id, verify_token="", is_verified=False, verified_time=0, link=""):
    current = await db_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['verified_time'] = verified_time
    current['link'] = link
    await db_update_verify_status(user_id, current)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except Exception as e:
            logging.error(f"Failed to add user {user_id} to the database: {e}")

    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAJfrGZy2E8hshoE1ZOqdtjqyZ4t9VpKAAKFAAOmysgMiq1L6Q_-yXw1BA")
    await asyncio.sleep(2)
    await sticker_message.delete()
    user_mention = message.from_user.mention

    verify_status = await db_verify_status(user_id)
    logging.info(f"Verify status for user {user_id}: {verify_status}")

    if verify_status["is_verified"] and VERIFY_EXPIRE < (time.time() - verify_status["verified_time"]):
        await db_update_verify_status(user_id, {**verify_status, 'is_verified': False})

    text = message.text
    if "verify_" in text:
        _, token = text.split("_", 1)
        logging.info(f"Extracted token: {token}")
        if verify_status["verify_token"] != token:
            return await message.reply("Your token is invalid or expired. Try again by clicking /start.")
        await db_update_verify_status(user_id, {**verify_status, 'is_verified': True, 'verified_time': time.time()})
        await message.reply("Your token has been successfully verified and is valid for 12 hours.")
    elif len(text) > 7 and verify_status["is_verified"]:
        reply_message = f"Welcome, {user_mention}.\n\n🌟 I am a terabox downloader bot. Send me any terabox link and I will download it within a few seconds and send it to you ✨."
        join_button = InlineKeyboardButton("Join ❤️🚀", url="https://t.me/megafilesofficial")
        developer_button = InlineKeyboardButton("Developer ⚡️", url="https://t.me/ambani_hu")
        reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])
        await message.reply_text(reply_message, reply_markup=reply_markup)
    else:
        if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            logging.info(f"Generated token: {token}")
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/Teralinkdownloaderbot?start=verify_{token}')
            await db_update_verify_status(user_id, {**verify_status, 'verify_token': token, 'link': link})
            message_text = (
                "Your ads token has expired. Please refresh your token and try again.\n\n"
                f"Token Timeout: {get_exp_time(VERIFY_EXPIRE)}\n\n"
                "What is the token?\n\n"
                "This is an ads token. If you pass 1 ad, you can use the bot for 12 hours after passing the ad.\n\n"
                f"[Click here]({link}) to refresh your token."
            )
            await message.reply(message_text)


@app.on_message(filters.command('broadcast') & filters.user(ADMINS))
async def broadcast_command(client, message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u></b>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code>"""
        
        await pls_wait.edit(status)
    else:
        msg = await message.reply("Please reply to a message to broadcast it.")
        await asyncio.sleep(8)
        await msg.delete()

@app.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client, message):
    total_users = users_collection.count_documents({})
    verified_users = users_collection.count_documents({"verify_status.is_verified": True})
    unverified_users = total_users - verified_users

    status = f"""<b><u>Verification Stats</u></b>

Total Users: <code>{total_users}</code>
Verified Users: <code>{verified_users}</code>
Unverified Users: <code>{unverified_users}</code>"""

    await message.reply(status)   

@app.on_message(filters.command("check"))
async def check_command(client, message):
    user_id = message.from_user.id

    verify_status = await db_verify_status(user_id)
    logging.info(f"Verify status for user {user_id}: {verify_status}")

    if verify_status['is_verified']:
        expiry_time = get_exp_time(VERIFY_EXPIRE - (time.time() - verify_status['verified_time']))
        await message.reply(f"Your token is verified and valid for {expiry_time}.")
    else:
        await message.reply("Your token is not verified or has expired , /start to generate! Verify token....")

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

def is_terabox_link(link):
    return "terabox" in link

@app.on_message(filters.text)
async def handle_message(client, message: Message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except Exception as e:
            logging.error(f"Failed to add user {user_id} to the database: {e}")

    user_mention = message.from_user.mention
    
    verify_status = await db_verify_status(user_id)

    if not verify_status["is_verified"]:
        await message.reply_text("To use this bot, please verify your identity. Click /start to begin.")
        return

    is_member = await is_user_member(client, user_id)

    if not is_member:
        join_button = InlineKeyboardButton("Join ❤️🚀", url="https://t.me/megafilesofficial")
        reply_markup = InlineKeyboardMarkup([[join_button]])
        await message.reply_text("You must join my channel to use me.", reply_markup=reply_markup)
        return

    terabox_link = message.text.strip()

    if not is_terabox_link(terabox_link):
        await message.reply_text("Please send a valid terabox link.")
        return

    reply_msg = await message.reply_text("Sending you the media...🤤")

    try:
        file_path, thumbnail_path, video_title = await download_video(terabox_link, reply_msg, user_mention, user_id)
        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, dump_id, user_mention, user_id, message)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await reply_msg.edit_text("Failed to process your request.\nIf your file size is more than 120MB, it might fail to download.")


if __name__ == "__main__":
    keep_alive()
    app.run()
