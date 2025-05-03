import asyncio
import sys
from typing import Dict, Any, List

from pyrogram import Client
from pyrogram.types import Message
import uvloop
from config import chats_to_follow, api_id, api_hash, FETCH_INTERVAL, SESSION_NAME


async def process_message(message: Message) -> None:
    source = message.chat.title or message.chat.first_name or str(message.chat.id)
    text = message.text or message.caption or "[no text]"
    submit_to_core(source, text)
    print(f"[{source}]: {text} ({message.date})")


def submit_to_core(source, text):
    pass

async def prime_last_ids(app: Client) -> Dict[Any, int]:
    last_ids: Dict[Any, int] = {}
    for chat in chats_to_follow:
        try:
            async for msg in app.get_chat_history(chat, limit=1):
                last_ids[chat] = msg.id
                break
            else:
                last_ids[chat] = 0
        except Exception as exc:
            print(f"Init fetch error for {chat}: {exc}")
            last_ids[chat] = 0
    return last_ids


async def watch(app: Client) -> None:

    last_ids = await prime_last_ids(app)

    while True:
        for chat in chats_to_follow:
            try:
                new_messages: List[Message] = []
                async for msg in app.get_chat_history(chat, limit=100):
                    if msg.id <= last_ids[chat]:
                        break  
                    new_messages.append(msg)

                for msg in reversed(new_messages):  
                    await process_message(msg)
                    last_ids[chat] = msg.id
            except Exception as exc:
                print(f"Fetch error for {chat}: {exc}")
        await asyncio.sleep(FETCH_INTERVAL)


async def main() -> None:
    async with Client(SESSION_NAME, api_id, api_hash) as app:
        async for dialog in app.get_dialogs():
            continue
        await watch(app)


if __name__ == "__main__":
    asyncio.run(main())