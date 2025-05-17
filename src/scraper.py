from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from pyrogram import Client
from pyrogram.types import Message

from src.core import Core
from src.scraper_config import (FETCH_INTERVAL, SESSION_NAME, api_hash, api_id,
                                chats_to_follow)
from src.utils import get_logger

logger = get_logger("Scraper")


class Scraper:

    def __init__(
        self,
        chats: List[Any],
        api_id: int,
        api_hash: str,
        session_name: str = "scraper",
        fetch_interval: int = 5,
        core: Core = None,
    ) -> None:
        self.chats = chats
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.fetch_interval = fetch_interval
        self.core = core
        self._client: Client | None = None
        self._last_ids: Dict[Any, int] = {}
        logger.info("Scraper initialized")

    async def submit_to_core(self, source: str, text: str) -> None:
        self.core.receive_news(text, source)
        logger.info(f"[{source}]: {text}")

    async def _process_message(self, message: Message) -> None:
        source = message.chat.title or message.chat.first_name or str(
            message.chat.id)
        text = message.text or message.caption or "[no text]"
        await self.submit_to_core(source, text)
        logger.info(f"[{source}]: {text} ({message.date})")

    async def _prime_last_ids(self) -> None:
        assert self._client is not None
        logger.info("Priming last message IDs")
        for chat in self.chats:
            try:
                async for msg in self._client.get_chat_history(chat, limit=1):
                    self._last_ids[chat] = msg.id
                    break
                else:
                    self._last_ids[chat] = 0
            except Exception as exc:
                logger.error(f"Init fetch error for {chat}: {exc}")
                self._last_ids[chat] = 0

    async def _watch_loop(self) -> None:
        assert self._client is not None
        await self._prime_last_ids()
        logger.info("Starting watch loop")

        while True:
            for chat in self.chats:
                try:
                    new_messages: List[Message] = []
                    async for msg in self._client.get_chat_history(chat, limit=100):
                        if msg.id <= self._last_ids[chat]:
                            break
                        new_messages.append(msg)

                    if new_messages:
                        logger.info(
                            f"Found {len(new_messages)} new messages in {chat}")

                    for msg in reversed(new_messages):
                        await self._process_message(msg)
                        self._last_ids[chat] = msg.id
                except Exception as exc:
                    logger.error(f"Fetch error for {chat}: {exc}")
            await asyncio.sleep(self.fetch_interval)

    async def run(self) -> None:
        logger.info("Starting Scraper")
        async with Client(self.session_name, self.api_id, self.api_hash) as client:
            self._client = client
            logger.info("Connected to Telegram")
            async for _ in client.get_dialogs():
                pass
            await self._watch_loop()


def get_scraper(core: Core) -> Scraper:
    logger.info("Initializing scraper")
    watcher = Scraper(
        chats=chats_to_follow,
        api_id=api_id,
        api_hash=api_hash,
        session_name=SESSION_NAME,
        fetch_interval=FETCH_INTERVAL,
        core=core,
    )

    asyncio.run(watcher.run())

    return watcher
