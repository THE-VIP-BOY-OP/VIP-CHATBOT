import random

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message

from config import MONGO_URL
from nexichat import nexichat
from nexichat.modules.helpers import CHATBOT_ON

chatdb = MongoClient(MONGO_URL)
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]
chatai = chatdb["Word"]["WordDb"]


@nexichat.on_message(filters.command("chatbot"))
async def chaton(client: Client, message: Message):
    await message.reply_text(
        f"ᴄʜᴀᴛ: {message.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )


@nexichat.on_message(
    (filters.text | filters.sticker | filters.photo | filters.video | filters.audio)
)
async def chatbot_response(client: Client, message: Message):
    chat_status = status_db.find_one({"chat_id": message.chat.id})
    if chat_status and chat_status.get("status") == "disabled":
        return

    if message.text:
        if any(
            message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]
        ):
            return

    if (
        message.reply_to_message
        and message.reply_to_message.from_user.id == client.me.id
    ) or not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        reply_data = await get_reply(message.text if message.text else "")

        if reply_data:
            if reply_data["check"] == "sticker":
                await message.reply_sticker(reply_data["text"])
            elif reply_data["check"] == "photo":
                await message.reply_photo(reply_data["text"])
            elif reply_data["check"] == "video":
                await message.reply_video(reply_data["text"])
            elif reply_data["check"] == "audio":
                await message.reply_audio(reply_data["text"])
            else:
                await message.reply_text(reply_data["text"])
        else:
            await message.reply_text("**what??**")

    if message.reply_to_message:
        await save_reply(message.reply_to_message, message)


async def save_reply(original_message: Message, reply_message: Message):
    if reply_message.sticker:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.sticker.file_id,
                "check": "sticker",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.sticker.file_id,
                    "check": "sticker",
                }
            )
    elif reply_message.photo:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.photo.file_id,
                "check": "photo",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.photo.file_id,
                    "check": "photo",
                }
            )
    elif reply_message.video:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.video.file_id,
                "check": "video",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.video.file_id,
                    "check": "video",
                }
            )
    elif reply_message.audio:
        is_chat = chatai.find_one(
            {
                "word": original_message.text,
                "text": reply_message.audio.file_id,
                "check": "audio",
            }
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.audio.file_id,
                    "check": "audio",
                }
            )
    elif reply_message.text:
        is_chat = chatai.find_one(
            {"word": original_message.text, "text": reply_message.text}
        )
        if not is_chat:
            chatai.insert_one(
                {
                    "word": original_message.text,
                    "text": reply_message.text,
                    "check": "none",
                }
            )


async def get_reply(word: str):
    is_chat = list(chatai.find({"word": word}))
    if not is_chat:
        is_chat = list(chatai.find())
    if is_chat:
        random_reply = random.choice(is_chat)
        return random_reply
    return None
