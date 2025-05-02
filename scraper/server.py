import asyncio
import sys
import uvloop
from pyrogram import Client, idle
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from config import chats_to_follow, api_id, api_hash

async def on_message_handler(client: Client, message: Message):
    print(message.text or message.caption or "[No text content]")
    submit_to_db(message)

def submit_to_db(message: Message):
    pass

async def set_up():
    client = Client(
        "from_client_name", api_id, api_hash
    )
    
    client.add_handler(
        MessageHandler(on_message_handler,
                       filters.chat(chats_to_follow)))
    
    await client.start()

    print("Clients ready")

    await idle()
    await client.stop()

def main() -> int:
    uvloop.install()
    loop = asyncio.new_event_loop()

    tasks = [
        loop.create_task(set_up()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
    
