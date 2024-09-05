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


# MongoDB setup
client = MongoClient(MONGO_URL)
db = client["ChatBot"]
chatai = db["chat_responses"]
bot_control = db["BotControl"]

# Function to get chatbot status for a group
def is_chatbot_on(chat_id):
    chat_status = bot_control.find_one({"chat_id": chat_id})
    if chat_status:
        return chat_status.get("status", "on") == "on"
    return True  # Default to 'on' if no record exists

# Function to set chatbot status in a group
def set_chatbot_status(chat_id, status):
    bot_control.update_one({"chat_id": chat_id}, {"$set": {"status": status}}, upsert=True)

# Handler to turn chatbot on
@nexichat.on_message(filters.command("chatboton") & filters.group)
@adminsOnly  # Only admins can use this command
async def chatbot_on(client, message):
    set_chatbot_status(message.chat.id, "on")
    await message.reply_text("Chatbot has been turned ON!")

# Handler to turn chatbot off
@nexichat.on_message(filters.command("chatbotoff") & filters.group)
@adminsOnly  # Only admins can use this command
async def chatbot_off(client, message):
    set_chatbot_status(message.chat.id, "off")
    await message.reply_text("Chatbot has been turned OFF!")

# AI-based function for text handling
async def handle_ai_response(client, message):
    user_input = message.text
    try:
        response = api.gemini(user_input)
        x = response.get("results")
        image_url = response.get("image_url")
        if x:
            formatted_response = truncate_text(x)
            if image_url:
                await message.reply_photo(image_url, caption=formatted_response, quote=True)
            else:
                await message.reply_text(formatted_response, quote=True)
        else:
            await message.reply_text(to_small_caps("Sorry, please try again."), quote=True)
    except requests.exceptions.RequestException:
        pass

# Function to truncate text
def truncate_text(text, max_words=50):
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + "..."
    return text

# Function to convert text to small caps (optional)
def to_small_caps(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join(small_caps.get(char, char) for char in text.lower())

# Main handler for group messages
@nexichat.on_message(filters.group & ~filters.service)
async def group_message_handler(client, message):
    bot_username = (await client.get_me()).username

    # Check if chatbot is off for the group
    if not is_chatbot_on(message.chat.id):
        return

    # Skip if message is a reply to someone else (ignore replies to other users)
    if message.reply_to_message and message.reply_to_message.from_user.username != bot_username:
        return

    # MongoDB-based media handling for stickers or other non-text media
    if message.sticker or message.photo or message.video:
        K = []
        media_id = message.sticker.file_unique_id if message.sticker else message.photo[0].file_unique_id
        is_media = chatai.find({"word": media_id})
        if is_media:
            for x in is_media:
                K.append(x["text"])
            response = random.choice(K)
            is_text = chatai.find_one({"text": response})
            media_type = is_text["check"]
            if media_type == "text":
                await message.reply_text(response)
            elif media_type == "sticker":
                await message.reply_sticker(response)
        return

    # AI-based text handling
    if message.text:
        if message.reply_to_message:  # If replying to bot's message
            if message.reply_to_message.from_user.username == bot_username:
                await handle_ai_response(client, message)
        elif f"@{bot_username}" in message.text:  # If bot is mentioned
            await handle_ai_response(client, message)
        else:  # Any other general text
            await handle_ai_response(client, message)

# Private chat handler for AI-based responses
@nexichat.on_message(filters.private & ~filters.service)
async def private_message_handler(client, message):
    await handle_ai_response(client, message)
