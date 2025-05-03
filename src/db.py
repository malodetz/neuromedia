from typing import List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor


class PostgreStorage:
    def __init__(self, dbname, user, password, host="localhost", port=5433):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            cursor_factory=RealDictCursor,
        )
        self._create_table()

    def _create_table(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY,
                    text TEXT NOT NULL,
                    tags TEXT[]
                );
            """
            )
            self.conn.commit()

    def store(self, record_id: str, text: str, tags: Optional[List[str]] = None):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO records (id, text, tags)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET text = EXCLUDED.text, tags = EXCLUDED.tags;
            """,
                (record_id, text, tags),
            )
            self.conn.commit()

    def get(self, record_id: str) -> Optional[Tuple[str, str, List[str]]]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, text, tags FROM records WHERE id = %s;", (record_id,)
            )
            return cur.fetchone()

    def get_by_tag(self, tag: str):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, text, tags FROM records WHERE %s = ANY(tags);", (tag,)
            )
            return cur.fetchall()

    def delete(self, record_id: str):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM records WHERE id = %s;", (record_id,))
            self.conn.commit()

    def close(self):
        self.conn.close()
