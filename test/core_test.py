import pytest
import asyncio
from unittest.mock import AsyncMock
from src.core import Core

@pytest.mark.asyncio
async def test_core_processes_news_ok():
    mock_db = AsyncMock()
    mock_db.store = AsyncMock()

    mock_ml = AsyncMock()
    mock_ml.submit = AsyncMock(return_value="id123")
    mock_ml.get_status = AsyncMock(side_effect=[
        {"state": "processing"},
        {"state": "ok", "rewritten_text": "rewritten!", "tags": ["tag1", "tag2"]}
    ])

    core = Core(db=mock_db, ml_client=mock_ml)

    task = asyncio.create_task(core.receive_news("original text", "test.com"))

    await asyncio.sleep(3)

    mock_ml.submit.assert_called_once()
    mock_db.store.assert_called_with("id123", "rewritten!", ["tag1", "tag2"])

    task.cancel()


@pytest.mark.asyncio
async def test_core_drops_news():
    mock_db = AsyncMock()
    mock_db.store = AsyncMock()

    mock_ml = AsyncMock()
    mock_ml.submit = AsyncMock(return_value="id456")
    mock_ml.get_status = AsyncMock(side_effect=[
        {"state": "processing"},
        {"state": "drop"}
    ])

    core = Core(db=mock_db, ml_client=mock_ml)

    task = asyncio.create_task(core.receive_news("drop this", "spam.com"))

    await asyncio.sleep(3)

    mock_db.store.assert_not_called()

    task.cancel()
