import asyncio

from prometheus_client import Counter

from src.utils import get_logger

logger = get_logger("Core")

reviewed_news_counter = Counter("reciewed_news_total", "Total number of reciewed news")
dropped_news_counter = Counter("dropped_news_total", "Total number of dropped news")
successful_news_counter = Counter(
    "successful_news_total", "Total number of successfully processed news"
)


class Core:
    def __init__(self, db, ml_client):
        logger.info("Core init")

        self.db = db
        self.ml_client = ml_client
        self.pending_tasks = {}

    async def receive_news(self, text: str, source: str):
        logger.info(f"Received from scraper. {source}: {text}")

        reviewed_news_counter.inc()

        await self.send_to_ml(text, source)

    async def send_to_ml(self, text: str, source: str):
        message = {"text": text, "source": source}

        news_id = await self.ml_client.submit(text, source)
        self.pending_tasks[news_id] = message
        logger.info(f"Submitted to ML, got ID: {news_id}")

        asyncio.create_task(self.poll_ml_status(news_id))

    async def poll_ml_status(
        self, news_id: str, max_attempts: int = 120, delay: float = 5.0
    ):
        try:
            for attempt in range(max_attempts):
                logger.info(f"Pulling news {news_id}, attempt №{attempt}")

                status = await self.ml_client.get_status(news_id)

                if status["state"] == "processing":
                    await asyncio.sleep(1)
                elif status["state"] == "drop":
                    logger.info(f"News {news_id} dropped.")
                    del self.pending_tasks[news_id]
                    dropped_news_counter.inc()
                    return
                elif status["state"] == "ok":
                    rewritten = status["rewritten_text"]
                    tags = status["tags"]
                    self.db.store(news_id, rewritten, tags)
                    logger.info(f"Stored to DB: {news_id}")
                    del self.pending_tasks[news_id]
                    successful_news_counter.inc()
                    return

            logger.warning(f"News {news_id} timed out after {max_attempts} attempts.")
            del self.pending_tasks[news_id]
        except asyncio.CancelledError:
            logger.warning(f"Polling for {news_id} was cancelled.")
            self.pending_tasks.pop(news_id, None)
            raise
