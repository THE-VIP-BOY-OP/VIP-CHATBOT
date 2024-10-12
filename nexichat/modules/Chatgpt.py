from pyrogram import filters
from pyrogram.enums import ChatAction
from MukeshAPI import api
from nexichat import nexichat
from deep_translator import GoogleTranslator
from pymongo import MongoClient
from config import MONGO_URL

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

    try:
        results = api.chatgpt(user_input)
        if results:
            await message.reply_text(results)
        else:
            await message.reply_text("Sorry, I couldn't find a good response.")
    except Exception as e:
        print(f"Error in chatgpt_chat: {e}")
        await message.reply_text("An error occurred while processing your request.")
