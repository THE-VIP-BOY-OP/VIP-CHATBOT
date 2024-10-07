from pyrogram import filters, Client
from pyrogram.types import Message

from nexichat import OWNER, nexichat
from nexichat.database.chats import get_served_chats
from nexichat.database.users import get_served_users
from config import OWNER_ID


import asyncio
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from pyrogram.raw import types

import config
from config import OWNER_ID

from nexichat import nexichat
from nexichat.database.chats import get_served_chats
from nexichat.database.users import get_served_users 

AUTO_SLEEP = 5
IS_BROADCASTING = False





@nexichat.on_message(filters.command(["broadcast", "gcast"]) & filters.user(int(OWNER_ID)))
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("**Please Provide Me A Text After Command Or Reply To Any Messgae For Broadcast**")
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query == "":
            return await message.reply_text("Please provide me a flag : -pin, -nobot, -pinloud, -user")

    IS_BROADCASTING = True
    ok = await message.reply_text("**Started broadcasting...**")
    
    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            if i == message.chat.id:
                continue
            try:
                m = (
                    await nexichat.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await nexichat.send_message(i, text=query)
                )
                sent += 1
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except Exception:
                        pass
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except Exception:
                        pass
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                continue
        try:
            await ok.delete()
            await message.reply_text(f"**Successfully Broadcasted Message In {sent} Chats And Pinned In {pin} Chats.**")
            
        except:
            pass

    
    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                susr += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
        try:
            await message.reply_text(f"**Successfully Broadcasted Message To {susr} Users**")
            
        except:
            pass

    
    IS_BROADCASTING = False
