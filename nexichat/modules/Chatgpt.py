from pyrogram import filters
from pyrogram.enums import ChatAction
from MukeshApi import api
from nexichat import nexichat
from deep_translator import GoogleTranslator
from pymongo import MongoClient
from config import MONGO_URL

translator = GoogleTranslator()  
chatdb = MongoClient(MONGO_URL)
lang_db = chatdb["ChatLangDb"]["LangCollection"]

def get_chat_language(chat_id):
    chat_lang = lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else None
    

@nexichat.on_message(filters.command(["chatgpt", "ai", "ask"]))
async def chatgpt_chat(bot, message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Example:\n\n`/ask write simple website code using html css, js?`"
        )
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    results = api.chatgpt(user_input)
    chat_lang = get_chat_language(message.chat.id)

    if not chat_lang or chat_lang == "nolang":
        translated_text = results
    else:
        translated_text = GoogleTranslator(source='auto', target=chat_lang).translate(results)
        await message.reply_text(translated_text)
