import os

import pytest

from src.db import PostgreStorage


@pytest.fixture(scope="module")
def db():
    storage = PostgreStorage(
        dbname=os.getenv("DB_NAME", "mydb"),
        user=os.getenv("DB_USER", "pguser"),
        password=os.getenv("DB_PASSWORD", "secret"),
        host=os.getenv("DB_HOST", "localhost"),
        port=5433,
    )
    yield storage

    with storage.conn:
        with storage.conn.cursor() as cur:
            cur.execute("DELETE FROM records;")


def test_store_and_get(db):
    db.store(1, "Hello world", ["tag1", "tag2"])
    result = db.get(1)
    assert result is not None
    assert result["text"] == "Hello world"
    assert "tag1" in result["tags"]


def test_get_by_tag(db):
    db.store(1, "Hello world", ["tag1", "tag2"])
    db.store(2, "Hello world2", ["tag1", "tag3"])

    result = db.get_by_tag("tag2")
    assert result is not None
    assert len(result) == 1
    assert result[0]["text"] == "Hello world"

    result = db.get_by_tag("tag1")
    assert result is not None
    assert len(result) == 2
    assert result[0]["text"] == "Hello world"
    assert result[1]["text"] == "Hello world2"


def test_delete(db):
    db.store(2, "To delete", ["tag"])
    db.delete(2)
    assert db.get(2) is None
