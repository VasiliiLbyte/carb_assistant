"""Task extraction service backed by an LLM client interface."""

from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import LLMClient
from app.schemas.tasks import TaskCreate


class TaskAutoCreator:
    """Create task drafts from a free-form message."""

    def __init__(self, db: AsyncSession, llm_client: LLMClient) -> None:
        self._db = db
        self._llm_client = llm_client

    @staticmethod
    def _build_prompt(text: str, project_id: int | str | None) -> str:
        return (
            "Ты ассистент PM. Извлеки из сообщения список задач.\n"
            "Для каждой задачи определи: title, description, assignee(если есть), due_at(если есть).\n"
            "Если срок неясен — оставь due_at = null.\n"
            "Если исполнитель не указан — оставь assignee = null.\n"
            "Верни структурированный список задач.\n\n"
            f"project_id: {project_id}\n"
            f"message:\n{text.strip()}"
        )

    @staticmethod
    def _split_candidates(text: str) -> list[str]:
        lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
        if not lines:
            return []
        if len(lines) == 1:
            return [part.strip() for part in re.split(r"[;]+", lines[0]) if part.strip()]
        return lines

    @staticmethod
    def _extract_due_at(text: str) -> datetime | None:
        match = re.search(r"до\s+(\d{2}\.\d{2}\.\d{4})", text, flags=re.IGNORECASE)
        if match is None:
            return None
        try:
            return datetime.strptime(match.group(1), "%d.%m.%Y")
        except ValueError:
            return None

    @staticmethod
    def _extract_assignee(text: str) -> str | None:
        match = re.search(r"(?:ответственный|исполнитель)\s*[:\-]\s*([A-Za-zА-Яа-яЁё0-9_.-]+)", text, flags=re.IGNORECASE)
        if match is None:
            return None
        return match.group(1).strip()

    async def create_tasks_from_message(
        self,
        text: str,
        project_id: int | str | None = None,
    ) -> list[TaskCreate]:
        """Extract a list of task drafts from an input message.

        Uses an injected LLM client (stub for now) and deterministic fallback parsing.
        """

        prompt = self._build_prompt(text=text, project_id=project_id)
        _ = await self._llm_client.complete(prompt)

        tasks: list[TaskCreate] = []
        for item in self._split_candidates(text):
            due_at = self._extract_due_at(item)
            assignee = self._extract_assignee(item)
            normalized = re.sub(r"\s+", " ", item).strip()
            title = normalized[:255] if normalized else "Новая задача"
            description_parts: list[str] = [normalized]
            if assignee:
                description_parts.append(f"assignee_hint={assignee}")
            description = "\n".join(description_parts)
            tasks.append(
                TaskCreate(
                    title=title,
                    description=description,
                    due_at=due_at,
                    project_id=str(project_id) if project_id is not None else None,
                )
            )
        return tasks
