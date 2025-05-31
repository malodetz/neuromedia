import asyncio
import threading
from typing import Any, Dict

from ollama import chat
from pydantic import BaseModel, Field

from src.utils import get_logger

logger = get_logger("ML CLient")


class NewsTags(BaseModel):
    tags: list[str] = Field(
        description="List of most important entities in text")


class RewrittenNews(BaseModel):
    rewritten_text: str = Field(description="Rewritten news text")
    comment: str = Field(description="Comments in news modification")
    is_duplicate: bool = Field(default=False, description="Indicates if the news is a duplicate")


class MLClient:
    def __init__(self, db):
        self.db = db
        self.llm = "gemma3:12b"
        self.tasks = {}
        self._counter = 0
        self._lock = threading.Lock()

        logger.info("ML client started")

    async def submit(self, text: str, source: str) -> int:
        """Submit text for rewriting and return an integer ID"""
        with self._lock:
            task_id = self._counter
            self._counter += 1

        self.tasks[task_id] = {
            "text": text,
            "source": source,
            "state": "processing",
            "rewritten_text": None,
            "tags": [],
        }
        logger.info(f"Received update. Id = {task_id}, text = {text}")

        asyncio.create_task(self._process_task(task_id))

        return task_id

    def _get_tags(self, text: str) -> list[str]:
        template = f"Extract 3-5 key entities from the following news text. Return only a JSON object with the required format.\n\nNews text: {text}"
        response = chat(
            messages=[{"role": "user", "content": template}],
            model=self.llm,
            format=NewsTags.model_json_schema(),
        )
        tags = NewsTags.model_validate_json(response.message.content)
        return tags.tags

    def _rewrite_text(self, text: str, context_news: list[dict]) -> RewrittenNews:
        context_str = "\n\n".join([news.get("text", "") for news in context_news])
        template = f"""
Rewrite the following news text to be more concise, using the context news below to avoid duplication.
If the news is essentially the same as any of the context news, mark it as duplicate.

Context news:
{context_str}

Original text:
{text}

Instructions:
- Rewrite the text to be more concise and clear
- Avoid duplicating information already present in context news
- Set is_duplicate to true if this news essentially repeats information from context
- Provide comments explaining your changes

Return only a JSON object with the required format.
"""
        response = chat(
            messages=[{"role": "user", "content": template}],
            model=self.llm,
            format=RewrittenNews.model_json_schema(),
        )
        return RewrittenNews.model_validate_json(response.message.content)

    async def _process_task(self, task_id: int):
        """Process the task and update its status"""
        task = self.tasks[task_id]
        text = task["text"]

        try:
            tags = self._get_tags(text)
            logger.info(f"Generated tags. Id = {task_id}, tags = {tags}")

            all_news = list(dict(news) for tag in tags for news in self.db.get_by_tag(tag))
            unique_news_dict = {}
            for news in all_news:
                unique_news_dict[news['id']] = news
            unique_news = list(unique_news_dict.values())
            similar_news = sorted(unique_news, key=lambda x: x['id'])[-10:]

            rewritten_news = self._rewrite_text(text, similar_news)
            logger.info(
                f"Text rewritten. Id = {task_id}, new_text = {rewritten_news.rewritten_text}, is_duplicate = {rewritten_news.is_duplicate}")
            
            
            self.tasks[task_id]["rewritten_text"] = rewritten_news.rewritten_text
            self.tasks[task_id]["tags"] = tags
            if rewritten_news.is_duplicate:
                self.tasks[task_id]["state"] = "drop"
            else:
                self.tasks[task_id]["state"] = "ok"

        except Exception as e:
            self.tasks[task_id]["state"] = "drop"
            logger.error(f"Error processing task {task_id}: {e}")

        logger.info(f"Finished processing task {task_id}")

    async def get_status(self, task_id: int) -> Dict[str, Any]:
        """Get the current status of a task"""
        if task_id not in self.tasks:
            return {"state": "not_found"}

        task = self.tasks[task_id]

        if task["state"] == "processing":
            return {"state": "processing"}
        elif task["state"] == "drop":
            return {"state": "drop"}
        elif task["state"] == "ok":
            return {
                "state": "ok",
                "rewritten_text": task["rewritten_text"],
                "tags": task["tags"],
                "is_duplicate": task.get("is_duplicate", False),
            }
