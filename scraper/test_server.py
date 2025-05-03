from __future__ import annotations

import asyncio
import types
from typing import List, Dict, Any

import pytest


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
    """Mimic just one method: `get_chat_history` (async‑generator)."""

    def __init__(self, history_map: Dict[Any, List[DummyMessage]]):
        self._history_map = history_map

    async def get_chat_history(self, chat: Any, limit: int = 100): 
        for msg in self._history_map.get(chat, [])[: limit]: 
            yield msg



@pytest.mark.asyncio
async def test_prime_last_ids(monkeypatch):
    """`prime_last_ids` should return latest IDs per chat (or 0 if empty)."""

    import server 

    chat_a, chat_b = -1001, -1002
    monkeypatch.setattr(server, "chats_to_follow", [chat_a, chat_b])

    dummy_chat_a = DummyChat(chat_a)
    dummy_chat_b = DummyChat(chat_b)

    history = {
        chat_a: [DummyMessage(42, dummy_chat_a)],  
        chat_b: [], 
    }

    client = DummyClient(history)

    result = await server.prime_last_ids(client)

    assert result == {chat_a: 42, chat_b: 0}


@pytest.mark.asyncio
async def test_watch_only_new(monkeypatch):
    """`watch` must emit process_message exactly for unseen messages."""

    import server

    chat_id = -2000
    monkeypatch.setattr(server, "chats_to_follow", [chat_id])

    dummy_chat = DummyChat(chat_id)

    cycle1 = [DummyMessage(i, dummy_chat) for i in (3, 2, 1)]
    cycle2 = [DummyMessage(i, dummy_chat) for i in (4, 3, 2, 1)]

    call_counter = {"n": 0}

    async def dynamic_history(chat, limit=100):  # noqa: D401
        call_counter["n"] += 1
        data = cycle1 if call_counter["n"] == 1 else cycle2
        for msg in data:
            yield msg

    client = DummyClient({})  
    client.get_chat_history = dynamic_history 

    processed: List[int] = []

    async def fake_process(msg):
        processed.append(msg.id)

    monkeypatch.setattr(server, "process_message", fake_process)
    monkeypatch.setattr(server, "FETCH_INTERVAL", 0.01)

    task = asyncio.create_task(server.watch(client))
    await asyncio.sleep(0.05) 
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert processed == [4]
