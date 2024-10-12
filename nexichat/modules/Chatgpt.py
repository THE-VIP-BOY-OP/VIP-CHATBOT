from pyrogram import filters
from pyrogram.enums import ChatAction
from MukeshAPI import api
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

    # Get the user input
    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    # Show typing action
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        # Call to API
        results = api.chatgpt(user_input)
    except Exception as e:
        await message.reply_text(f"Error communicating with AI: {str(e)}")
        return

    # Get chat language from DB
    chat_lang = get_chat_language(message.chat.id)

    # Translate results if language is set
    if chat_lang and chat_lang != "nolang":
        try:
            translated_text = translator.translate(results, target=chat_lang)
        except Exception as e:
            await message.reply_text(f"Error translating response: {str(e)}")
            return
    else:
        translated_text = results

    # Send the response
    await message.reply_text(translated_text)
