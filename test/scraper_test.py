from __future__ import annotations

import asyncio
import types
from typing import Any, Dict, List

import pytest


class DummyChat:
    def __init__(
        self, chat_id: Any, title: str | None = None, first_name: str | None = None
    ):
        self.id = chat_id
        self.title = title
        self.first_name = first_name


class DummyMessage:
    def __init__(self, msg_id: int, chat: DummyChat, text: str = "hi"):
        self.id = msg_id
        self.chat = chat
        self.text = text
        self.caption = None
        self.date = "2025-05-03"
        self.from_user = types.SimpleNamespace(first_name="Tester")


class DummyClient:

    def __init__(self, history_map: Dict[Any, List[DummyMessage]]):
        self._history_map = history_map

    async def get_chat_history(self, chat: Any, limit: int = 100):
        for msg in self._history_map.get(chat, [])[:limit]:
            yield msg

    async def get_dialogs(self):
        if False:
            yield
        return


class DummyCore:
    def __init__(self):
        self.received: list[tuple[str, str]] = []

    def receive_news(self, text: str, source: str):
        self.received.append((source, text))


@pytest.mark.asyncio
async def test_prime_last_ids(monkeypatch):
    import src.scraper as scraper

    chat_a, chat_b = -10, -20

    dummy_chat_a = DummyChat(chat_a)
    dummy_chat_b = DummyChat(chat_b)

    history = {
        chat_a: [DummyMessage(5, dummy_chat_a)],
        chat_b: [],
    }

    scraper = scraper.Scraper(
        chats=[chat_a, chat_b],
        api_id=123,
        api_hash="hash",
        core=DummyCore(),
    )
    scraper._client = DummyClient(history)

    await scraper._prime_last_ids()

    assert scraper._last_ids == {chat_a: 5, chat_b: 0}


@pytest.mark.asyncio
async def test_watch_processes_only_new(monkeypatch):
    import src.scraper as scraper

    chat_id = -99
    dummy_chat = DummyChat(chat_id)

    cycle1 = [DummyMessage(i, dummy_chat) for i in (3, 2, 1)]
    cycle2 = [DummyMessage(i, dummy_chat) for i in (4, 3, 2, 1)]

    call_count = {"n": 0}

    async def dynamic_history(chat, limit=100):
        call_count["n"] += 1
        msgs = cycle1 if call_count["n"] == 1 else cycle2
        for m in msgs:
            yield m

    dummy_client = DummyClient({})
    dummy_client.get_chat_history = dynamic_history

    core = DummyCore()

    scraper = scraper.Scraper(
        chats=[chat_id],
        api_id=123,
        api_hash="hash",
        fetch_interval=0.01,
        core=core,
    )
    scraper._client = dummy_client

    async def cancel_after_delay():
        await asyncio.sleep(0.05)
        raise asyncio.CancelledError

    loop_task = asyncio.create_task(scraper._watch_loop())
    cancel_task = asyncio.create_task(cancel_after_delay())

    with pytest.raises(asyncio.CancelledError):
        await asyncio.gather(loop_task, cancel_task)
