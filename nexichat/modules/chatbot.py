import random
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from deep_translator import GoogleTranslator 
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from config import MONGO_URL
from nexichat import nexichat, mongo, db
from pyrogram.types import Message
from nexichat.modules.helpers import CHATBOT_ON
from pymongo import MongoClient
from nexichat import mongo
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
import asyncio
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

translator = GoogleTranslator()  
from nexichat import db

# Simplified access to each collection in a consistent way
chatai = db.Word.WordDb
lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status

@nexichat.on_message(filters.command("status"))
async def status_command(client: Client, message: Message):
    chat_id = message.chat.id

    # Retrieve the status for the given chat_id
    chat_status = await status_db.find_one({"chat_id": chat_id})

    # Check if a status was found
    if chat_status:
        current_status = chat_status.get("status", "not found")
        await message.reply(f"Chatbot status for this chat: **{current_status}**")
    else:
        await message.reply("No status found for this chat.")

# Example usage of Client

languages = {
    # Top 20 languages used on Telegram
    'english': 'en', 'hindi': 'hi', 'Myanmar': 'my', 'russian': 'ru', 'spanish': 'es', 
    'arabic': 'ar', 'turkish': 'tr', 'german': 'de', 'french': 'fr', 
    'italian': 'it', 'persian': 'fa', 'indonesian': 'id', 'portuguese': 'pt',
    'ukrainian': 'uk', 'filipino': 'tl', 'korean': 'ko', 'japanese': 'ja', 
    'polish': 'pl', 'vietnamese': 'vi', 'thai': 'th', 'dutch': 'nl',

    # Top languages spoken in Bihar
    'bhojpuri': 'bho', 'maithili': 'mai', 'urdu': 'ur', 
    'bengali': 'bn', 'angika': 'anp', 'sanskrit': 'sa', 
    'oriya': 'or', 'nepali': 'ne', 'santhali': 'sat', 'khortha': 'kht', 
    'kurmali': 'kyu', 'ho': 'hoc', 'munda': 'unr', 'kharwar': 'kqw', 
    'mundari': 'unr', 'sadri': 'sck', 'pali': 'pi', 'tamil': 'ta',

    # Top languages spoken in India
    'telugu': 'te', 'bengali': 'bn', 'marathi': 'mr', 'tamil': 'ta', 
    'gujarati': 'gu', 'urdu': 'ur', 'kannada': 'kn', 'malayalam': 'ml', 
    'odia': 'or', 'punjabi': 'pa', 'assamese': 'as', 'sanskrit': 'sa', 
    'kashmiri': 'ks', 'konkani': 'gom', 'sindhi': 'sd', 'bodo': 'brx', 
    'dogri': 'doi', 'santali': 'sat', 'meitei': 'mni', 'nepali': 'ne',

    # Other language
    'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'armenian': 'hy', 
    'aymara': 'ay', 'azerbaijani': 'az', 'bambara': 'bm', 
    'basque': 'eu', 'belarusian': 'be', 'bosnian': 'bs', 'bulgarian': 'bg', 
    'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 
    'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 
    'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 
    'dhivehi': 'dv', 'esperanto': 'eo', 'estonian': 'et', 'ewe': 'ee', 
    'finnish': 'fi', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 
    'greek': 'el', 'guarani': 'gn', 'haitian creole': 'ht', 'hausa': 'ha', 
    'hawaiian': 'haw', 'hebrew': 'iw', 'hmong': 'hmn', 'hungarian': 'hu', 
    'icelandic': 'is', 'igbo': 'ig', 'ilocano': 'ilo', 'irish': 'ga', 
    'javanese': 'jw', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 
    'krio': 'kri', 'kurdish (kurmanji)': 'ku', 'kurdish (sorani)': 'ckb', 
    'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 
    'lingala': 'ln', 'lithuanian': 'lt', 'luganda': 'lg', 'luxembourgish': 'lb', 
    'macedonian': 'mk', 'malagasy': 'mg', 'maltese': 'mt', 'maori': 'mi', 
    'mizo': 'lus', 'mongolian': 'mn', 'myanmar': 'my', 'norwegian': 'no', 
    'oromo': 'om', 'pashto': 'ps', 'quechua': 'qu', 'romanian': 'ro', 
    'samoan': 'sm', 'scots gaelic': 'gd', 'sepedi': 'nso', 'serbian': 'sr', 
    'sesotho': 'st', 'shona': 'sn', 'sinhala': 'si', 'slovak': 'sk', 
    'slovenian': 'sl', 'somali': 'so', 'sundanese': 'su', 'swahili': 'sw', 
    'swedish': 'sv', 'tajik': 'tg', 'tatar': 'tt', 'tigrinya': 'ti', 
    'tsonga': 'ts', 'turkmen': 'tk', 'twi': 'ak', 'uyghur': 'ug', 
    'uzbek': 'uz', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 
    'yoruba': 'yo', 'zulu': 'zu'
}



def generate_language_buttons(languages):
    buttons = []
    current_row = []
    for lang, code in languages.items():
        current_row.append(InlineKeyboardButton(lang.capitalize(), callback_data=f'setlang_{code}'))
        if len(current_row) == 4:
            buttons.append(current_row)
            current_row = []
    if current_row:
        buttons.append(current_row)
    return InlineKeyboardMarkup(buttons)

async def get_chat_language(chat_id):
    # Await the async call to find_one
    chat_lang = await lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else "en"
    
@nexichat.on_message(filters.command(["lang", "language", "setlang"]))
async def set_language(client: Client, message: Message):
    await message.reply_text(
        "Please select your chat language:",
        reply_markup=generate_language_buttons(languages)
    )


@nexichat.on_callback_query(filters.regex(r"setlang_"))
async def language_selection_callback(client: Client, callback_query: CallbackQuery):
    lang_code = callback_query.data.split("_")[1]
    chat_id = callback_query.message.chat.id
    if lang_code in languages.values():
        lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": lang_code}}, upsert=True)
        await callback_query.answer(f"Your chat language has been set to {lang_code.title()}.", show_alert=True)
        await callback_query.message.edit_text(f"Chat language has been set to {lang_code.title()}.")
    else:
        await callback_query.answer("Invalid language selection.", show_alert=True)



@nexichat.on_message(filters.command("status"))
async def status_command(client: Client, message: Message):
    chat_id = message.chat.id

    # Retrieve the status for the given chat_id
    chat_status = await status_db.find_one({"chat_id": chat_id})

    # Check if a status was found
    if chat_status:
        current_status = chat_status.get("status", "not found")
        await message.reply(f"Chatbot status for this chat: **{current_status}**")
    else:
        await message.reply("No status found for this chat.")


@nexichat.on_message(filters.command(["lang", "language", "setlang"]))
async def set_language(client: Client, message: Message):
    await message.reply_text(
        "Please select your chat language:",
        reply_markup=generate_language_buttons(languages)
    )


@nexichat.on_message(filters.command(["resetlang", "nolang"]))
async def reset_language(client: Client, message: Message):
    chat_id = message.chat.id
    lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": "nolang"}}, upsert=True)
    await message.reply_text("**Bot language has been reset in this chat to mix language.**")


@nexichat.on_message(filters.command("chatbot"))
async def chatbot_command(client: Client, message: Message):
    await message.reply_text(
        f"Chat: {message.chat.title}\n**Choose an option to enable/disable the chatbot.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )

@nexichat.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    LOGGER.info(query.data)

    # Help menu
    if query.data == "HELP":
        await query.message.edit_text(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
            disable_web_page_preview=True,
        )

    # Close menu
    elif query.data == "CLOSE":
        await query.message.delete()
        await query.answer("Closed menu!", show_alert=True)

    # Go back to the main menu
    elif query.data == "BACK":
        await query.message.edit(
            text=START,
            reply_markup=InlineKeyboardMarkup(DEV_OP),
        )

    # Show source information
    elif query.data == "SOURCE":
        await query.message.edit(
            text=SOURCE_READ,
            reply_markup=InlineKeyboardMarkup(BACK),
            disable_web_page_preview=True,
        )

    # Show about information
    elif query.data == "ABOUT":
        await query.message.edit(
            text=ABOUT_READ,
            reply_markup=InlineKeyboardMarkup(ABOUT_BTN),
            disable_web_page_preview=True,
        )

    # Show admin information
    elif query.data == "ADMINS":
        await query.message.edit(
            text=ADMIN_READ,
            reply_markup=InlineKeyboardMarkup(MUSIC_BACK_BTN),
        )

    # Show tools information
    elif query.data == "TOOLS_DATA":
        await query.message.edit(
            text=TOOLS_DATA_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
        )

    # Back to the help menu
    elif query.data == "BACK_HELP":
        await query.message.edit(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )

    # Chatbot commands
    elif query.data == "CHATBOT_CMD":
        await query.message.edit(
            text=CHATBOT_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
        )

    # Back to the chatbot menu
    elif query.data == "CHATBOT_BACK":
        await query.message.edit(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )

    # Enable chatbot for the chat
    elif query.data == "enable_chatbot":
        chat_id = query.message.chat.id
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "enabled"}}, upsert=True)
        await query.answer("Chatbot enabled ✅", show_alert=True)
        await query.edit_message_text(
            f"Chat: {query.message.chat.title}\n**Chatbot has been enabled.**"
        )

    # Disable chatbot for the chat
    elif query.data == "disable_chatbot":
        chat_id = query.message.chat.id
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)
        await query.answer("Chatbot disabled!", show_alert=True)
        await query.edit_message_text(
            f"Chat: {query.message.chat.title}\n**Chatbot has been disabled.**"
        )

    # Set chat language
    elif query.data.startswith("setlang_"):
        lang_code = query.data.split("_")[1]
        chat_id = query.message.chat.id
        if lang_code in languages.values():
            lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": lang_code}}, upsert=True)
            await query.answer(f"Your chat language has been set to {lang_code.title()}.", show_alert=True)
            await query.message.edit_text(f"Chat language has been set to {lang_code.title()}.")
        else:
            await query.answer("Invalid language selection.", show_alert=True)

    # Reset language selection to mix language
    elif query.data == "nolang":
        chat_id = query.message.chat.id
        lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": "nolang"}}, upsert=True)
        await query.answer("Bot language has been reset to mix language.", show_alert=True)
        await query.message.edit_text("**Bot language has been reset to mix language.**")

    # Choose language for the chatbot
    elif query.data == "choose_lang":
        await query.answer("Choose chatbot language for this chat.", show_alert=True)
        await query.message.edit_text(
            "**Please select your preferred language for the chatbot.**",
            reply_markup=generate_language_buttons(languages)
        )



        
@nexichat.on_message(filters.incoming)
async def chatbot_response(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        chat_status = await status_db.find_one({"chat_id": chat_id})
        
        if chat_status and chat_status.get("status") == "disabled":
            return

        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            if message.chat.type == "group" or message.chat.type == "supergroup":
                return await add_served_chat(message.chat.id)
            else:
                return await add_served_user(message.chat.id)
        
        if (message.reply_to_message and message.reply_to_message.from_user.id == nexichat.id) or not message.reply_to_message:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            reply_data = await get_reply(message.text)

            if reply_data:
                response_text = reply_data["text"]
                chat_lang = await get_chat_language(chat_id)

                if not chat_lang or chat_lang == "nolang":
                    translated_text = response_text
                else:
                    translated_text = GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
                
                if reply_data["check"] == "sticker":
                    await message.reply_sticker(reply_data["text"])
                elif reply_data["check"] == "photo":
                    await message.reply_photo(reply_data["text"])
                elif reply_data["check"] == "video":
                    await message.reply_video(reply_data["text"])
                elif reply_data["check"] == "audio":
                    await message.reply_audio(reply_data["text"])
                elif reply_data["check"] == "gif":
                    await message.reply_animation(reply_data["text"]) 
                else:
                    await message.reply_text(translated_text)
            else:
                await message.reply_text("**I don't understand. what are you saying??**")
        
        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)
    except MessageEmpty as e:
        return await message.reply_text("🙄🙄")
    except Exception as e:
        return

async def save_reply(original_message: Message, reply_message: Message):
    try:
        if reply_message.sticker:
            is_chat = await chatai.find_one({
                "word": original_message.text,
                "text": reply_message.sticker.file_id,
                "check": "sticker",
            })
            if not is_chat:
                await chatai.insert_one({
                    "word": original_message.text,
                    "text": reply_message.sticker.file_id,
                    "check": "sticker",
                })

        elif reply_message.photo:
            is_chat = await chatai.find_one({
                "word": original_message.text,
                "text": reply_message.photo.file_id,
                "check": "photo",
            })
            if not is_chat:
                await chatai.insert_one({
                    "word": original_message.text,
                    "text": reply_message.photo.file_id,
                    "check": "photo",
                })

        elif reply_message.video:
            is_chat = await chatai.find_one({
                "word": original_message.text,
                "text": reply_message.video.file_id,
                "check": "video",
            })
            if not is_chat:
                await chatai.insert_one({
                    "word": original_message.text,
                    "text": reply_message.video.file_id,
                    "check": "video",
                })

        elif reply_message.audio:
            is_chat = await chatai.find_one({
                "word": original_message.text,
                "text": reply_message.audio.file_id,
                "check": "audio",
            })
            if not is_chat:
                await chatai.insert_one({
                    "word": original_message.text,
                    "text": reply_message.audio.file_id,
                    "check": "audio",
                })

        elif reply_message.animation:  
            is_chat = await chatai.find_one({
                "word": original_message.text,
                "text": reply_message.animation.file_id,
                "check": "gif",
            })
            if not is_chat:
                await chatai.insert_one({
                    "word": original_message.text,
                    "text": reply_message.animation.file_id,
                    "check": "gif",
                })

        elif reply_message.text:
            is_chat = await chatai.find_one({
                "word": original_message.text,
                "text": reply_message.text,
                "check": "none",
            })
            if not is_chat:
                await chatai.insert_one({
                    "word": original_message.text,
                    "text": reply_message.text,
                    "check": "none",
                })

    except Exception as e:
        print(f"Error in save_reply: {e}")

async def get_reply(word: str):
    try:
        is_chat = await chatai.find({"word": word}).to_list(length=None)
        if not is_chat:
            is_chat = await chatai.find().to_list(length=None)
        return random.choice(is_chat) if is_chat else None
    except Exception as e:
        print(f"Error in get_reply: {e}")
        return None
