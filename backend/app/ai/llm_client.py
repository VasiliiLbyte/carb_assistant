"""OpenAI-compatible LLM client wrappers."""

from __future__ import annotations

import json
from typing import Any

import httpx


class GrokLLMClient:
    """Async client for Grok/OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        *,
        api_key: str,
        api_base: str = "https://api.x.ai/v1",
        model: str = "grok-3-mini",
        timeout_seconds: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._api_base = api_base.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    async def generate(self, prompt: str) -> str:
        """Generate task extraction JSON from input prompt."""

        system_prompt = (
            "Ты PM-ассистент. Твоя задача: извлечь задачи из текста и вернуть только JSON.\n"
            "Формат ответа строго: "
            '{"tasks":[{"title":"...", "description":"...", "assignee":"...", "due_at":"YYYY-MM-DDTHH:MM:SS|null"}]}.\n'
            "Если задач нет, верни {\"tasks\":[]}.\n"
            "Без markdown, без комментариев, только JSON."
        )
        url = f"{self._api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self._model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return self._extract_content(data)

    @staticmethod
    def _extract_content(response_json: dict[str, Any]) -> str:
        choices = response_json.get("choices")
        if not isinstance(choices, list) or not choices:
            return '{"tasks":[]}'
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            # Some OpenAI-compatible providers return structured chunks.
            merged = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    merged.append(item["text"])
            content = "".join(merged)
        if not isinstance(content, str) or not content.strip():
            return '{"tasks":[]}'
        return content

    @staticmethod
    def parse_tasks_json(raw: str) -> list[dict[str, Any]]:
        """Parse LLM JSON payload and return normalized task rows."""

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return []
        tasks = payload.get("tasks")
        if not isinstance(tasks, list):
            return []
        result: list[dict[str, Any]] = []
        for item in tasks:
            if isinstance(item, dict):
                result.append(item)
        return result
