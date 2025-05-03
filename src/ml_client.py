import asyncio
import uuid
from typing import Any, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_ollama.llms import OllamaLLM


class NewsTags(BaseModel):
    tags: list[str] = Field(description="List of most important entities in text")


class MLClient:
    def __init__(self, db):
        self.db = db
        self.llm = OllamaLLM(model="gemma3:12b")
        self.tasks = {}

    async def submit(self, text: str, source: str) -> str:
        """Submit text for rewriting and return a UUID"""
        task_id = str(uuid.uuid4())

        self.tasks[task_id] = {
            "text": text,
            "source": source,
            "state": "processing",
            "rewritten_text": None,
            "tags": [],
        }

        asyncio.create_task(self._process_task(task_id))

        return task_id

    def _get_tags(self, text: str) -> list[str]:
        template = f"Extract 3-5 key entities from this news text: {text}"
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm.with_structured_output(NewsTags)
        result = chain.invoke({"text": text})
        return result.tags

    def _rewrite_text(self, text: str) -> str:
        template = f"Rewrite the following news text to be more concise Remove all the emotions and make it more objective. Original text: {text}"
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm
        return chain.invoke({"text": text})

    async def _process_task(self, task_id: str):
        """Process the task and update its status"""
        task = self.tasks[task_id]
        text = task["text"]

        try:
            tags = self._get_tags(text)
            rewritten_text = self._rewrite_text(text)
            self.tasks[task_id]["state"] = "ok"
            self.tasks[task_id]["rewritten_text"] = rewritten_text
            self.tasks[task_id]["tags"] = tags

        except Exception as e:
            self.tasks[task_id]["state"] = "drop"
            print(f"Error processing task {task_id}: {e}")

    async def get_status(self, task_id: str) -> Dict[str, Any]:
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
            }
