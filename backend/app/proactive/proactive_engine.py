"""Core proactive engine for pings, reminders, and response handling."""

from __future__ import annotations

import json
import re
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import LLMClient
from app.models import ProactiveRule, Task
from app.proactive.schemas import PingMessage, ResponseHandleResult
from app.proactive.rule_engine import RuleEngine


class ProactiveEngine:
    """Service class for proactive automation flows."""

    def __init__(self, db: AsyncSession, llm_client: LLMClient) -> None:
        self._db = db
        self._llm_client = llm_client

    async def list_rules(self) -> list[ProactiveRule]:
        result = await self._db.execute(select(ProactiveRule).order_by(ProactiveRule.created_at.desc()))
        return list(result.scalars().all())

    async def create_rule(self, payload: dict[str, Any]) -> ProactiveRule:
        item = ProactiveRule(**payload)
        self._db.add(item)
        await self._db.commit()
        await self._db.refresh(item)
        return item

    async def update_rule(self, rule_id: str, payload: dict[str, Any]) -> ProactiveRule:
        item = await self.get_rule(rule_id)
        for key, value in payload.items():
            if value is not None:
                setattr(item, key, value)
        await self._db.commit()
        await self._db.refresh(item)
        return item

    async def delete_rule(self, rule_id: str) -> None:
        item = await self.get_rule(rule_id)
        await self._db.delete(item)
        await self._db.commit()

    async def get_rule(self, rule_id: str) -> ProactiveRule:
        item = await self._db.get(ProactiveRule, rule_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proactive rule not found")
        return item

    async def send_proactive_ping(self, rule_id: str, task_id: str) -> PingMessage:
        rule = await self.get_rule(rule_id)
        task = await self._db.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        text = await self._generate_ping_text(rule=rule, task=task)
        return PingMessage(
            rule_id=str(rule.id),
            task_id=str(task.id),
            target_user_id=str(task.assignee_id) if task.assignee_id else None,
            message=text,
        )

    async def handle_response(self, message_text: str, source: str, user_id: str | None) -> ResponseHandleResult:
        del source
        task = await self._resolve_target_task(user_id=user_id)
        if task is None:
            return ResponseHandleResult(
                processed=False,
                action="ignored",
                note="No target in-progress task found for user",
            )

        lowered = message_text.lower()
        if any(token in lowered for token in ("готово", "done", "сделано", "завершил")):
            task.status = "done"
            await self._db.commit()
            await self._db.refresh(task)
            return ResponseHandleResult(
                processed=True,
                action="task_status_updated",
                task_id=str(task.id),
                new_status=task.status,
                note="Task marked as done from proactive response",
            )

        if any(token in lowered for token in ("блок", "blocked", "не могу", "проблема", "риск")):
            task.status = "blocked"
            await self._db.commit()
            await self._db.refresh(task)
            return ResponseHandleResult(
                processed=True,
                action="task_status_updated",
                task_id=str(task.id),
                new_status=task.status,
                note="Task marked as blocked from proactive response",
            )

        # LLM-aided intent extraction fallback.
        llm_result = await self._infer_response_action(message_text)
        if llm_result.get("new_status") in {"done", "blocked", "in-progress"}:
            task.status = llm_result["new_status"]
            await self._db.commit()
            await self._db.refresh(task)
            return ResponseHandleResult(
                processed=True,
                action="task_status_updated",
                task_id=str(task.id),
                new_status=task.status,
                note="Task status updated via LLM interpretation",
            )

        return ResponseHandleResult(
            processed=True,
            action="no_status_change",
            task_id=str(task.id),
            new_status=task.status,
            note="Response processed without task status update",
        )

    async def evaluate_rules(self) -> dict[str, int]:
        """Simple evaluator for built-in rule types."""

        rules = await RuleEngine.list_enabled_rules(self._db)
        triggered = 0
        for rule in rules:
            if rule.trigger_type == "inprogress_overdue_ping":
                days_threshold = int(rule.config.get("days_threshold", 3))
                tasks = await RuleEngine.evaluate_inprogress_overdue_tasks(self._db, days_threshold=days_threshold)
                triggered += len(tasks)
        return {"enabled_rules": len(rules), "triggered_candidates": triggered}

    async def _resolve_target_task(self, *, user_id: str | None) -> Task | None:
        query = select(Task).where(Task.status.in_(["in-progress", "blocked"]))
        if user_id is not None:
            query = query.where(Task.assignee_id == user_id)
        query = query.order_by(Task.updated_at.asc())
        result = await self._db.execute(query.limit(1))
        return result.scalars().first()

    async def _generate_ping_text(self, *, rule: ProactiveRule, task: Task) -> str:
        base = (
            f"Задача: {task.title}\n"
            f"Статус: {task.status}\n"
            f"Приоритет: {task.priority}\n"
            f"Правило: {rule.name} ({rule.trigger_type})\n"
        )
        prompt = (
            "Сгенерируй короткий проактивный пинг на русском для исполнителя. "
            "Тон: деловой, дружелюбный. Уложись в 1-2 предложения.\n"
            f"{base}"
        )
        try:
            text = (await self._llm_client.generate(prompt)).strip()
            if text:
                return text
        except Exception:
            pass
        return f"Напоминание: обновите статус задачи '{task.title}' и сообщите о блокерах."

    async def _infer_response_action(self, message_text: str) -> dict[str, str]:
        prompt = (
            "Ты анализируешь ответ сотрудника на пинг по задаче. "
            "Верни JSON: {\"new_status\":\"done|blocked|in-progress|none\"}.\n"
            f"message: {message_text}"
        )
        try:
            raw = await self._llm_client.generate(prompt)
            payload = json.loads(raw)
            if isinstance(payload, dict):
                status_value = payload.get("new_status")
                if isinstance(status_value, str):
                    normalized = re.sub(r"\s+", "", status_value.lower())
                    if normalized in {"done", "blocked", "in-progress", "none"}:
                        return {"new_status": normalized}
        except Exception:
            pass
        return {"new_status": "none"}
