import asyncio
import logging

from pyrogram import filters
from pyrogram.errors import FloodWait

from nexichat import nexichat
from nexichat.database.chats import get_served_chats
from nexichat.database.users import get_served_users

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTO_SLEEP = 5
IS_BROADCASTING = False
broadcast_lock = asyncio.Lock()


@nexichat.on_message(filters.command(["broadcast", "gcast"]))
async def broadcast_message(client, message):
    global IS_BROADCASTING
    async with broadcast_lock:
        if IS_BROADCASTING:
            return await message.reply_text(
                "A broadcast is already in progress. Please wait for it to complete."
            )

        IS_BROADCASTING = True
        try:
            # Determine broadcast content
            if message.reply_to_message:
                broadcast_content = message.reply_to_message
                broadcast_type = "reply"
            else:
                if len(message.command) < 2:
                    return await message.reply_text(
                        "**Please provide text after the command or reply to a message for broadcasting.**"
                    )
                query = message.text.split(None, 1)[1].strip()

                # Extract flags
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nobot": "-nobot" in query,
                    "-user": "-user" in query,
                }

                # Remove flags from the query
                for flag in flags:
                    query = query.replace(flag, "").strip()

                if not query:
                    return await message.reply_text(
                        "Please provide a valid text message or a flag: -pin, -nobot, -pinloud, -user"
                    )

                broadcast_content = query
                broadcast_type = "text"

            # Start broadcasting
            await message.reply_text("**Started broadcasting...**")

            # Broadcast to chats
            if not flags.get("-nobot", False):
                sent = 0
                pin_count = 0
                chats = await get_served_chats()

                for chat in chats:
                    chat_id = int(chat["chat_id"])
                    if chat_id == message.chat.id:
                        continue
                    try:
                        if broadcast_type == "reply":
                            m = await nexichat.forward_messages(
                                chat_id, message.chat.id, broadcast_content.id
                            )
                        else:
                            m = await nexichat.send_message(
                                chat_id, text=broadcast_content
                            )
                        sent += 1

                        # Handle pinning
                        if flags.get("-pin", False) or flags.get("-pinloud", False):
                            try:
                                await m.pin(
                                    disable_notification=flags.get("-pin", False)
                                )
                                pin_count += 1
                            except Exception as e:
                                logger.error(
                                    f"Failed to pin message in chat {chat_id}: {e}"
                                )

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for chat {chat_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping chat {chat_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        logger.error(f"Error broadcasting to chat {chat_id}: {e}")
                        continue

                await message.reply_text(
                    f"**Broadcasted to {sent} chats and pinned in {pin_count} chats.**"
                )

            # Broadcast to users
            if flags.get("-user", False):
                susr = 0
                users = await get_served_users()

                for user in users:
                    user_id = int(user["user_id"])
                    try:
                        if broadcast_type == "reply":
                            m = await nexichat.forward_messages(
                                user_id, message.chat.id, broadcast_content.id
                            )
                        else:
                            m = await nexichat.send_message(
                                user_id, text=broadcast_content
                            )
                        susr += 1

                        # Optionally handle pinning for users if applicable
                        # Note: Pinning messages in user chats isn't typically applicable

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for user {user_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping user {user_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        logger.error(f"Error broadcasting to user {user_id}: {e}")
                        continue

                await message.reply_text(f"**Broadcasted to {susr} users.**")

        finally:
            IS_BROADCASTING = False
