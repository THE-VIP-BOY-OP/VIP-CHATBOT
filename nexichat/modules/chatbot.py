import random
from Abg.chat_status import adminsOnly
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message
from config import MONGO_URL
from nexichat import nexichat
from nexichat.modules.helpers import CHATBOT_ON, is_admins
import requests
import random
import re
from MukeshAPI import api
from pyrogram import filters, Client
from pyrogram.enums import ChatAction

from pymongo import MongoClient
from Abg.chat_status import adminsOnly

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message

from config import MONGO_URL
from nexichat import nexichat
from nexichat.modules.helpers import CHATBOT_ON, is_admins

# MongoDB connection
client = MongoClient(MONGO_URL)
db = client["NexiDB"]
chatai = db["chats"]

# AI-based API response function
from MukeshAPI import api

async def ai_response(user_input):
    try:
        response = api.gemini(user_input)
        x = response.get("results")
        image_url = response.get("image_url")

        if x:
            return x, image_url
        else:
            return "Sorry! Please try again.", None
    except Exception as e:
        return str(e), None

# Function to handle media (stickers, images, videos, etc.)
async def handle_media_response(message: Message):
    K = []
    media_id = message.sticker.file_unique_id if message.sticker else message.photo[0].file_unique_id
    
    # Fetch responses from MongoDB for the given media
    is_media = chatai.find({"word": media_id})
    for x in is_media:
        K.append(x["text"])

    if K:
        response = random.choice(K)
        is_text = chatai.find_one({"text": response})
        media_type = is_text["check"]
        
        # Reply based on media type
        if media_type == "text":
            await message.reply_text(response)
        elif media_type == "sticker":
            await message.reply_sticker(response)
    else:
        # If no response is found
        await message.reply_text("I don't have a response for this sticker or media yet.")

# Function to handle text responses with AI for non-reply messages
async def handle_text_response(client, message):
    user_input = message.text.strip()
    response, image_url = await ai_response(user_input)

    if image_url:
        await message.reply_photo(image_url, caption=response, quote=True)
    else:
        await message.reply_text(response, quote=True)

# Chatbot On/Off handler
@app.on_message(filters.command("chatbot on") & filters.group)
@adminsOnly
async def chatbot_on(_, message: Message):
    if not CHATBOT_ON(message.chat.id):
        CHATBOT_ON[message.chat.id] = True
        await message.reply_text("Chatbot has been turned ON!")

@app.on_message(filters.command("chatbot off") & filters.group)
@adminsOnly
async def chatbot_off(_, message: Message):
    if CHATBOT_ON(message.chat.id):
        del CHATBOT_ON[message.chat.id]
        await message.reply_text("Chatbot has been turned OFF!")

# Main message handler for group messages
@app.on_message(filters.group)
async def group_message_handler(client: Client, message: Message):
    # Check if chatbot is off for the group
    if message.chat.id not in CHATBOT_ON:
        return

    # Get bot's username
    bot_username = (await client.get_me()).username

    # Respond to text messages if not replying to other users
    if message.text and not message.reply_to_message:
        await handle_text_response(client, message)

    # Handle non-text media (stickers, photos, videos)
    elif message.sticker or message.photo or message.video:
        await handle_media_response(message)

# Direct message handler for private chats
@app.on_message(filters.private & ~filters.service)
async def private_message_handler(client, message: Message):
    # Handle text messages
    if message.text:
        await handle_text_response(client, message)

    # Handle media (stickers, photos, etc.)
    elif message.sticker or message.photo or message.video:
        await handle_media_response(message)
