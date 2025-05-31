import asyncio
from unittest.mock import MagicMock

import pytest

from src.ml_client import MLClient, RewrittenNews


@pytest.fixture
def dummy_db():
    """Create a mock database with required methods"""
    db = MagicMock()
    db.get_max_id.return_value = 0  # Start counter from 1
    db.get_by_tag.return_value = []  # Return empty list for any tag
    return db


@pytest.fixture
def client(dummy_db):
    return MLClient(dummy_db)


@pytest.mark.asyncio
async def test_submit_returns_int_and_initial_state(client, monkeypatch):
    """Test that submit returns an integer ID and sets initial processing state"""
    monkeypatch.setattr(asyncio, "create_task", lambda coro: None)

    task_id = await client.submit("some text", "source-A")

    assert isinstance(task_id, int)
    assert client.tasks[task_id]["state"] == "processing"
    assert client.tasks[task_id]["text"] == "some text"
    assert client.tasks[task_id]["source"] == "source-A"

    status = await client.get_status(task_id)
    assert status == {"state": "processing"}


@pytest.mark.asyncio
async def test_process_task_success(client, monkeypatch):
    """Test successful processing of a task"""
    SAMPLE_TAGS = ["OpenAI", "AI", "ChatGPT"]
    SAMPLE_REWRITE = RewrittenNews(
        rewritten_text="Краткая, объективная версия новости.",
        comment="Text was shortened and clarified",
        is_duplicate=False,
    )

    monkeypatch.setattr(client, "_get_tags", lambda text: SAMPLE_TAGS)
    monkeypatch.setattr(client, "_rewrite_text", lambda text, context: SAMPLE_REWRITE)

    task_id = await client.submit("оригинальная длинная новость", "source-B")
    await client._process_task(task_id)

    status = await client.get_status(task_id)
    assert status["state"] == "ok"
    assert status["tags"] == SAMPLE_TAGS
    assert status["rewritten_text"] == SAMPLE_REWRITE.rewritten_text
    assert status["is_duplicate"] == False


@pytest.mark.asyncio
async def test_process_task_duplicate_sets_drop_state(client, monkeypatch):
    """Test that duplicate detection sets state to drop"""
    SAMPLE_TAGS = ["OpenAI", "AI"]
    SAMPLE_REWRITE = RewrittenNews(
        rewritten_text="Duplicate news detected.",
        comment="This news is essentially the same as existing news",
        is_duplicate=True,
    )

    monkeypatch.setattr(client, "_get_tags", lambda text: SAMPLE_TAGS)
    monkeypatch.setattr(client, "_rewrite_text", lambda text, context: SAMPLE_REWRITE)

    task_id = await client.submit("duplicate news text", "source-C")
    await client._process_task(task_id)

    status = await client.get_status(task_id)
    assert status["state"] == "drop"


@pytest.mark.asyncio
async def test_process_task_failure_sets_drop_state(client, monkeypatch):
    """Test that processing failures set state to drop"""

    def failing_get_tags(text):
        raise RuntimeError("Processing failed")

    monkeypatch.setattr(client, "_get_tags", failing_get_tags)

    task_id = await client.submit("bad text", "src")
    await client._process_task(task_id)

    assert client.tasks[task_id]["state"] == "drop"

    status = await client.get_status(task_id)
    assert status == {"state": "drop"}


@pytest.mark.asyncio
async def test_get_status_not_found(client):
    """Test get_status for non-existent task"""
    status = await client.get_status(999)  # Non-existent task ID
    assert status == {"state": "not_found"}


@pytest.mark.asyncio
async def test_counter_increments(client, monkeypatch):
    """Test that task IDs increment properly"""
    monkeypatch.setattr(asyncio, "create_task", lambda coro: None)

    task_id1 = await client.submit("text1", "source1")
    task_id2 = await client.submit("text2", "source2")

    assert task_id2 == task_id1 + 1
    assert task_id1 == 1  # Should start from 1 since db.get_max_id() returns 0


@pytest.mark.asyncio
async def test_database_integration(client, monkeypatch):
    """Test that database methods are called correctly"""
    SAMPLE_TAGS = ["tag1", "tag2"]
    SAMPLE_NEWS = [{"id": 1, "text": "news 1"}, {"id": 2, "text": "news 2"}]
    SAMPLE_REWRITE = RewrittenNews(
        rewritten_text="Rewritten text",
        comment="Rewritten based on context",
        is_duplicate=False,
    )

    # Mock database to return sample news
    client.db.get_by_tag.return_value = SAMPLE_NEWS

    monkeypatch.setattr(client, "_get_tags", lambda text: SAMPLE_TAGS)
    monkeypatch.setattr(client, "_rewrite_text", lambda text, context: SAMPLE_REWRITE)

    task_id = await client.submit("test news", "source-D")
    await client._process_task(task_id)

    # Verify database methods were called
    client.db.get_max_id.assert_called_once()
    assert client.db.get_by_tag.call_count == len(SAMPLE_TAGS)

    status = await client.get_status(task_id)
    assert status["state"] == "ok"
