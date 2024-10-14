import random
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from deep_translator import GoogleTranslator 
from config import MONGO_URL
from nexichat import nexichat
from nexichat.modules.helpers import CHATBOT_ON
from pymongo import MongoClient
from nexichat import mongo, db
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
status_db = mongo["ChatBotStatusDb"]["StatusCollection"]
chatai = mongo["Word"]["WordDb"]
lang_db = mongo["ChatLangDb"]["LangCollection"]



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

def get_chat_language(chat_id):
    chat_lang = lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else None


@nexichat.on_message(filters.command(["lang", "language", "setlang"]))
async def set_language(client: Client, message: Message):
    await message.reply_text(
        "ᴘʟᴇᴀsᴇ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ:",
        reply_markup=generate_language_buttons(languages))


@nexichat.on_callback_query(filters.regex(r"setlang_"))
async def language_selection_callback(client: Client, callback_query):
    lang_code = callback_query.data.split("_")[1]
    chat_id = callback_query.message.chat.id
    if lang_code in languages.values():  # Ensure lang_code is valid
        lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": lang_code}}, upsert=True)
        await callback_query.answer(f"ʏᴏᴜʀ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ {lang_code.title()}.", show_alert=True)
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ", callback_data="choose_lang")]])
        await callback_query.message.edit_text(f"ʏᴏᴜʀ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ {lang_code.title()}.", reply_markup=reply_markup)
    else:
        await callback_query.answer("Invalid language selection.", show_alert=True)

@nexichat.on_message(filters.command(["resetlang", "nolang"]))
async def set_language(client: Client, message: Message):
    chat_id = message.chat.id
    lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": "nolang"}}, upsert=True)
    await message.reply_text(f"**Bot language has been reset in this chat, now mix language is using.**")


@nexichat.on_callback_query(filters.regex("nolang"))
async def language_selection_callback(client: Client, callback_query):
    chat_id = callback_query.message.chat.id
    lang_db.update_one({"chat_id": chat_id}, {"$set": {"language": "nolang"}}, upsert=True)
    await callback_query.answer("Bot language has been reset in this chat, now mix language is using.", show_alert=True)
    await callback_query.message.edit_text(f"**Bot language has been reset in this chat, now mix language is using.**")

@nexichat.on_callback_query(filters.regex("choose_lang"))
async def language_selection_callback(client: Client, callback_query):
    chat_id = callback_query.message.chat.id
    await callback_query.answer("Choose chatbot language for this chat.", show_alert=True)
    await callback_query.message.edit_text(f"**Bot language has been reset in this chat, now mix language is using.**", reply_markup=generate_language_buttons(languages))
    
@nexichat.on_message(filters.command("chatbot"))
async def chaton(client: Client, message: Message):
    await message.reply_text(
        f"ᴄʜᴀᴛ: {message.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )
    
@nexichat.on_message((filters.text | filters.sticker | filters.photo | filters.video | filters.audio))
async def chatbot_response(client: Client, message: Message):
    chat_type = message.chat.type
    if chat_type in ['group', 'supergroup']:
        await add_served_chats(message.chat.id)

    elif chat_type == 'private':
        
        await add_served_users(message.from_user.id)
                              
    chat_status = status_db.find_one({"chat_id": message.chat.id})
    if chat_status and chat_status.get("status") == "disabled":
        return

    if message.text:
        if any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            return

    if (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id) or not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(0.1)
        reply_data = await get_reply(message.text if message.text else "")
        
        if reply_data:
            response_text = reply_data["text"]
            chat_lang = get_chat_language(message.chat.id)

            
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
            else:
                await message.reply_text(translated_text)
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

    elif query.data == "enable_chatbot":
        chat_id = query.message.chat.id
        action = query.data
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "enabled"}})
        await query.answer("Chatbot enabled ✅", show_alert=True)
        await query.edit_message_text(
            f"ᴄʜᴀᴛ: {query.message.chat.title}\n**ᴄʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ.**"
        )

    elif query.data == "disable_chatbot":
        chat_id = query.message.chat.id
        action = query.data
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}})
        await query.answer("Chatbot disabled!", show_alert=True)
        await query.edit_message_text(
            f"ᴄʜᴀᴛ: {query.message.chat.title}\n**ᴄʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.**"
        )
    
