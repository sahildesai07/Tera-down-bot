from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from datetime import datetime
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
from os import environ
import os
import time
from pymongo import MongoClient
import random
import string
import time
from database.database import present_user, add_user, db_verify_status, db_update_verify_status


load_dotenv('config.env', override=True)
logging.basicConfig(level=logging.INFO)

ADMINS = 6695586027
api_id = os.environ.get('TELEGRAM_API', 22505271)
if len(str(api_id)) == 0:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

api_hash = os.environ.get('TELEGRAM_HASH', 'c89a94fcfda4bc06524d0903977fc81e')
if len(api_hash) == 0:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)
    
bot_token = os.environ.get('BOT_TOKEN', '7156255687:AAEXQtlTzE8Jbwt9VD6NLfcZX08Czu7w7gQ')
if len(bot_token) == 0:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)
dump_id = os.environ.get('DUMP_CHAT_ID', '-1002062925443')
if len(str(dump_id)) == 0:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    dump_id = int(dump_id)

fsub_id = os.environ.get('FSUB_ID', '-1002108419450')
if len(str(fsub_id)) == 0:
    logging.error("FSUB_ID variable is missing! Exiting now")
    exit(1)
else:
    fsub_id = int(fsub_id)

# MongoDB setup
mongo_url = os.environ.get('MONGO_URL', 'mongodb+srv://ultroidxTeam:ultroidxTeam@cluster0.gabxs6m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = MongoClient(mongo_url)
db = client['uphdlust']
users_collection = db['users']

def save_user(user_id, username):
    if users_collection.find_one({'user_id': user_id}) is None:
        users_collection.insert_one({'user_id': user_id, 'username': username})
        logging.info(f"Saved new user {username} with ID {user_id} to the database.")
    else:
        logging.info(f"User {username} with ID {user_id} is already in the database.")

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user(user_id)  # Save user to MongoDB if not already present

    # Save user to MongoDB
    save_user(user_id, username)  

    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEYonplzwrczhVu3I6HqPBzro3L2JU6YAACvAUAAj-VzAoTSKpoG9FPRjQE")
    await asyncio.sleep(2)
    await sticker_message.delete()
    user_mention = message.from_user.mention
    
    # Check if user is verified
    verify_status = await db_verify_status(user_id)
    
    if not verify_status["is_verified"]:
        # Generate token and short link for verification
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/DRM2_bot?start=verify_{token}')
        await db_update_verify_status(user_id, {**verify_status, 'verify_token': token, 'link': link})
        message_text = (
            "Welcome to the bot!\n\n"
            "To use the bot, please verify your identity.\n\n"
            f"Token Timeout: {get_exp_time(VERIFY_EXPIRE)}\n\n"
            "What is the token?\n\n"
            "This is a verification token. Once verified, you can use the bot for 24 hours.\n\n"
            f"[Click here]({link}) to verify your token."
        )
        await message.reply(message_text, parse_mode='markdown')
        return

    # If verified, provide regular welcome message and functionality
    reply_message = f"Welcome, {user_mention}.\n\n🌟 I am a terabox downloader bot. Send me any terabox link and I will download it within a few seconds and send it to you ✨."
    join_button = InlineKeyboardButton("Join ❤️🚀", url="https://t.me/ultroid_official")
    developer_button = InlineKeyboardButton("Developer ⚡️", url="https://t.me/ultroidxTeam")
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

# Message handler for handling incoming messages
@app.on_message(filters.text)
async def handle_message(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user(user_id)  # Save user to MongoDB if not already present

    user_mention = message.from_user.mention
    
    # Check if user is verified
    verify_status = await db_verify_status(user_id)

    if not verify_status["is_verified"]:
        await message.reply_text("To use this bot, please verify your identity. Click /start to begin.")
        return

    # Additional checks or actions based on message content
    is_member = await is_user_member(client, user_id)

    if not is_member:
        join_button = InlineKeyboardButton("Join ❤️🚀", url="https://t.me/ultroid_official")
        reply_markup = InlineKeyboardMarkup([[join_button]])
        await message.reply_text("You must join my channel to use me.", reply_markup=reply_markup)
        return

    terabox_link = message.text.strip()
    if "terabox" not in terabox_link:
        await message.reply_text("Please send a valid terabox link.")
        return

    reply_msg = await message.reply_text("Sending you the media...🤤")

    try:
        file_path, thumbnail_path, video_title = await download_video(terabox_link, reply_msg, user_mention, user_id)
        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, dump_id, user_mention, user_id, message)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await reply_msg.edit_text("Failed to process your request.\nIf your file size is more than 120MB, it might fail to download.")

@app.on_message(filters.command('broadcast') & filters.user(ADMINS))
# @app.on_message(filters.command("broadcast") & filters.user(6695586027))  # Replace <your_user_id> with your actual user ID to restrict this command
async def broadcast_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a message to broadcast.")
        return

    broadcast_message = message.text.split(maxsplit=1)[1]  # Get the message to broadcast

    users = users_collection.find()
    for user in users:
        user_id = user['user_id']
        try:
            await client.send_message(user_id, broadcast_message)
            logging.info(f"Broadcast message sent to user {user_id}.")
        except Exception as e:
            logging.error(f"Failed to send broadcast message to user {user_id}: {e}")
            continue

    await message.reply_text("Broadcast message sent to all users.")

if __name__ == "__main__":
    app.run()
