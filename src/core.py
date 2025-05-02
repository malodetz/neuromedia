import asyncio
import logging

class Core:
    def __init__(self, db, ml_client):
        self.db = db
        self.ml_client = ml_client
        self.pending_tasks = {}

    async def receive_news(self, text: str, source: str):
        logging.info(f"[Core] Received from scraper. {source}: {text}")

        await self.send_to_ml(text, source)

    async def send_to_ml(self, text: str, source: str):
        message = {"text": text, "source": source}

        # TODO: wait for Serega-s ML COMP.

        news_id = await self.ml_client.submit(text, source)
        self.pending_tasks[news_id] = message
        print(f"[Core] Submitted to ML, got ID: {news_id}")

        asyncio.create_task(self.poll_ml_status(news_id))

    async def poll_ml_status(self, news_id: str):
        while True:
            # TODO: wait for Serega-s ML COMP.

            status = await self.ml_client.get_status(news_id)

            if status["state"] == "processing":
                await asyncio.sleep(1)
            elif status["state"] == "drop":
                print(f"[Core] News {news_id} dropped.")
                del self.pending_tasks[news_id]
                return
            elif status["state"] == "ok":
                rewritten = status["rewritten_text"]
                tags = status["tags"]
                await self.db.store(news_id, rewritten, tags)
                print(f"[Core] Stored to DB: {news_id}")
                del self.pending_tasks[news_id]
                return
