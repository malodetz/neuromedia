"""Pytest mock tests for Scraper class in server.py.

No real Telegram connection — we emulate Pyrogram's Client + Message.
"""

from __future__ import annotations

import asyncio
import types
from typing import List, Dict, Any

import pytest

# ---------------------------------------------------------------------------
# Minimal dummies mimicking Pyrogram behaviour
# ---------------------------------------------------------------------------


class DummyChat:
    def __init__(self, chat_id: Any, title: str | None = None, first_name: str | None = None):
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
    """Mimic only `get_chat_history` async‑generator used by Scraper."""

    def __init__(self, history_map: Dict[Any, List[DummyMessage]]):
        self._history_map = history_map

    async def get_chat_history(self, chat: Any, limit: int = 100):  # noqa: D401
        for msg in self._history_map.get(chat, [])[: limit]:
            yield msg

    async def get_dialogs(self):  # noqa: D401
        if False:
            yield  # never executed, just for async iteration compatibility
        return


class DummyCore:
    def __init__(self):
        self.received: list[tuple[str, str]] = []

    def recieve_news(self, text: str, source: str):  # noqa: D401 (name matches user's typo)
        self.received.append((source, text))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prime_last_ids(monkeypatch):
    """_prime_last_ids should fill last_ids with newest message id or 0."""
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
    scraper._client = DummyClient(history)  # inject dummy client

    await scraper._prime_last_ids()

    assert scraper._last_ids == {chat_a: 5, chat_b: 0}


@pytest.mark.asyncio
async def test_watch_processes_only_new(monkeypatch):
    """Scraper should pass only unseen messages to Core."""
    import src.scraper as scraper

    chat_id = -99
    dummy_chat = DummyChat(chat_id)

    # First poll cycle returns 3,2,1; second — 4,3,2,1.
    cycle1 = [DummyMessage(i, dummy_chat) for i in (3, 2, 1)]
    cycle2 = [DummyMessage(i, dummy_chat) for i in (4, 3, 2, 1)]

    call_count = {"n": 0}

    async def dynamic_history(chat, limit=100):  # noqa: D401
        call_count["n"] += 1
        msgs = cycle1 if call_count["n"] == 1 else cycle2
        for m in msgs:
            yield m

    dummy_client = DummyClient({})
    dummy_client.get_chat_history = dynamic_history  # type: ignore

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

    # core.received should contain 1 new msg from cycle1 (id 2,3) + id4 from cycle2? Wait logic:
    # prime_last_ids sets last_id to 3 before loop, so first cycle should emit 2,1? our logic sets if <= break
    # Actually _prime_last_ids not called; we didn't call it separately. We'll call manually.
