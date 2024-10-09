import random
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from deep_translator import GoogleTranslator  # Switched to deep-translator for translations

from config import MONGO_URL
from nexichat import nexichat
from nexichat.modules.helpers import CHATBOT_ON

translator = GoogleTranslator()  # Initialize the translator
chatdb = MongoClient(MONGO_URL)
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]
chatai = chatdb["Word"]["WordDb"]
lang_db = chatdb["ChatLangDb"]["LangCollection"]

# List of languages for buttons (Names in respective languages)
languages = {
    "हिंदी": "hi", "English": "en", "Español": "es", "Français": "fr", "Deutsch": "de",
    "中文": "zh", "العربية": "ar", "Русский": "ru", "日本語": "ja", "한국어": "ko",
    # Add more languages if needed
}

# Function to generate language buttons
def generate_language_buttons():
    buttons = []
    for lang_name, lang_code in languages.items():
        buttons.append([InlineKeyboardButton(lang_name, callback_data=f"setlang_{lang_code}")])
    return buttons


# Command to manually set language using /setlang
@nexichat.on_message(filters.command("setlang"))
async def set_language(client: Client, message: Message):
    await message.reply_text(
        "ᴘʟᴇᴀsᴇ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ:",
        reply_markup=InlineKeyboardMarkup(generate_language_buttons())
    )

# Callback handler for language selection
@nexichat.on_callback_query(filters.regex(r"setlang_"))
async def language_selection_callback(client: Client, callback_query):
    lang_code = callback_query.data.split("_")[1]
    chat_id = callback_query.message.chat.id
    
    # Save selected language for the chat
    lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": lang_code}}, upsert=True)
    
    await callback_query.message.edit_text(f"ʏᴏᴜʀ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ {callback_query.data.split('_')[1].title()}.")

# Function to get the saved language for a chat
def get_chat_language(chat_id):
    chat_lang = lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang else "en"  # Default to English if not set

# Modify chatbot response to translate based on chat's language
@nexichat.on_message((filters.text | filters.sticker | filters.photo | filters.video | filters.audio))
async def chatbot_response(client: Client, message: Message):
    chat_status = status_db.find_one({"chat_id": message.chat.id})
    if chat_status and chat_status.get("status") == "disabled":
        return

    if message.text:
        if any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            return

    if (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id) or not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        reply_data = await get_reply(message.text if message.text else "")

        if reply_data:
            response_text = reply_data["text"]
            chat_lang = get_chat_language(message.chat.id)
            if chat_lang != "en":
                response_text = translator.translate(response_text, target=chat_lang)

            if reply_data["check"] == "sticker":
                await message.reply_sticker(reply_data["text"])
            elif reply_data["check"] == "photo":
                await message.reply_photo(reply_data["text"])
            elif reply_data["check"] == "video":
                await message.reply_video(reply_data["text"])
            elif reply_data["check"] == "audio":
                await message.reply_audio(reply_data["text"])
            else:
                await message.reply_text(response_text)
        else:
            await message.reply_text("**what??**")

    if message.reply_to_message:
        await save_reply(message.reply_to_message, message)

# Example get_reply and save_reply functions (unchanged)
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

from pymongo import MongoClient
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

import config
from nexichat import LOGGER, nexichat
from nexichat.modules.helpers import (
    ABOUT_BTN,
    ABOUT_READ,
    ADMIN_READ,
    BACK,
    CHATBOT_BACK,
    CHATBOT_READ,
    DEV_OP,
    HELP_BTN,
    HELP_READ,
    MUSIC_BACK_BTN,
    SOURCE_READ,
    START,
    TOOLS_DATA_READ,
)

DAXXdb = MongoClient(config.MONGO_URL)
DAXX = DAXXdb["DAXXDb"]["DAXX"]
status_db = DAXXdb["ChatBotStatusDb"]["StatusCollection"]


@nexichat.on_callback_query()
async def cb_handler(_, query: CallbackQuery):
    LOGGER.info(query.data)
    if query.data == "HELP":
        await query.message.edit_text(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
            disable_web_page_preview=True,
        )
    elif query.data == "CLOSE":
        await query.message.delete()
        await query.answer("ᴄʟᴏsᴇᴅ ᴍᴇɴᴜ!", show_alert=True)
    elif query.data == "BACK":
        await query.message.edit(
            text=START,
            reply_markup=InlineKeyboardMarkup(DEV_OP),
        )
    elif query.data == "SOURCE":
        await query.message.edit(
            text=SOURCE_READ,
            reply_markup=InlineKeyboardMarkup(BACK),
            disable_web_page_preview=True,
        )
    elif query.data == "ABOUT":
        await query.message.edit(
            text=ABOUT_READ,
            reply_markup=InlineKeyboardMarkup(ABOUT_BTN),
            disable_web_page_preview=True,
        )
    elif query.data == "ADMINS":
        await query.message.edit(
            text=ADMIN_READ,
            reply_markup=InlineKeyboardMarkup(MUSIC_BACK_BTN),
        )
    elif query.data == "TOOLS_DATA":
        await query.message.edit(
            text=TOOLS_DATA_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
        )
    elif query.data == "BACK_HELP":
        await query.message.edit(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )
    elif query.data == "CHATBOT_CMD":
        await query.message.edit(
            text=CHATBOT_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
        )
    elif query.data == "CHATBOT_BACK":
        await query.message.edit(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )
    elif query.data == "addchat":
        user_id = query.from_user.id
        user_status = (await query.message.chat.get_member(user_id)).status
        if user_status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await query.answer(
                "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴇᴠᴇɴ ᴀɴ ᴀᴅᴍɪɴ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛʜɪs ᴇxᴘʟᴏsɪᴠᴇ sʜɪᴛ!",
                show_alert=True,
            )
        else:
            is_DAXX = DAXX.find_one({"chat_id": query.message.chat.id})
            if not is_DAXX:
                await query.edit_message_text(f"**ᴄʜᴀᴛ-ʙᴏᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.**")
            if is_DAXX:
                DAXX.delete_one({"chat_id": query.message.chat.id})
                await query.edit_message_text(
                    f"**ᴄʜᴀᴛ-ʙᴏᴛ ᴇɴᴀʙʟᴇᴅ ʙʏ** {query.from_user.mention}."
                )
    elif query.data == "rmchat":
        user_id = query.from_user.id
        user_status = (await query.message.chat.get_member(user_id)).status
        if user_status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            await query.answer(
                "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴇᴠᴇɴ ᴀɴ ᴀᴅᴍɪɴ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛʜɪs ᴇxᴘʟᴏsɪᴠᴇ sʜɪᴛ!",
                show_alert=True,
            )
            return
        else:
            is_DAXX = DAXX.find_one({"chat_id": query.message.chat.id})
            if not is_DAXX:
                DAXX.insert_one({"chat_id": query.message.chat.id})
                await query.edit_message_text(
                    f"**ᴄʜᴀᴛ-ʙᴏᴛ ᴅɪsᴀʙʟᴇᴅ ʙʏ** {query.from_user.mention}."
                )
            if is_DAXX:
                await query.edit_message_text("**ᴄʜᴀᴛ-ʙᴏᴛ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ.**")
    elif query.data == "enable_chatbot" or "disable_chatbot":
        action = query.data
        if query.message.chat.type in ["group", "supergroup"]:
            if not await adminsOnly("can_delete_messages")(client, query.message):
                await query.answer(
                    "Only admins can enable or disable the chatbot!", show_alert=True
                )
                return
        status_db.update_one(
            {"chat_id": query.message.chat.id},
            {
                "$set": {
                    "status": "enabled" if action == "enable_chatbot" else "disabled"
                }
            },
            upsert=True,
        )
        await query.answer(
            f"Chatbot has been {'enabled' if action == 'enable_chatbot' else 'disabled'}!"
        )
        await query.edit_message_text(
            f"ᴄʜᴀᴛ: {query.message.chat.title}\n**ᴄʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ {'ᴇɴᴀʙʟᴇᴅ' if action == 'enable_chatbot' else 'ᴅɪsᴀʙʟᴇᴅ'}.**"
        )
