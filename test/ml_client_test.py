import asyncio
import re
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from src.ml_client import MLClient


@pytest.fixture
def dummy_db():
    return {}


@pytest.fixture
def client(dummy_db):
    return MLClient(dummy_db)


@pytest.mark.asyncio
async def test_submit_returns_uuid_and_initial_state(client, monkeypatch):

    monkeypatch.setattr(asyncio, "create_task", lambda coro: None)

    task_id = await client.submit("some text", "source-A")

    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", task_id
    )

    assert client.tasks[task_id]["state"] == "processing"
    status = await client.get_status(task_id)
    assert status == {"state": "processing"}


@pytest.mark.asyncio
async def test_process_task_success(client, monkeypatch):
    SAMPLE_TAGS = ["OpenAI", "AI", "ChatGPT"]
    SAMPLE_REWRITE = "Краткая, объективная версия новости."

    monkeypatch.setattr(client, "_get_tags", lambda text: SAMPLE_TAGS)
    monkeypatch.setattr(client, "_rewrite_text", lambda text: SAMPLE_REWRITE)

    task_id = await client.submit("оригинальная длинная новость", "source-B")

    await client._process_task(task_id)

    status = await client.get_status(task_id)
    assert status["state"] == "ok"
    assert status["tags"] == SAMPLE_TAGS
    assert status["rewritten_text"] == SAMPLE_REWRITE


@pytest.mark.asyncio
async def test_process_task_failure_sets_drop_state(client, monkeypatch):
    monkeypatch.setattr(
        client, "_get_tags", lambda text: (_ for _ in ()).throw(RuntimeError)
    )

    task_id = str(uuid.uuid4())
    client.tasks[task_id] = {"text": "bad text", "source": "src", "state": "processing"}

    await client._process_task(task_id)

    assert client.tasks[task_id]["state"] == "drop"
    status = await client.get_status(task_id)
    assert status == {"state": "drop"}


@pytest.mark.asyncio
async def test_get_status_not_found(client):
    status = await client.get_status("00000000-0000-0000-0000-000000000000")
    assert status == {"state": "not_found"}
