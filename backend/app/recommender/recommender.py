"""AI-powered assignee recommender service."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import LLMClient
from app.models import AIRecommendation, Task, User
from app.recommender.schemas import CompetencyScore, Recommendation

_PRIORITY_WEIGHTS: dict[str, float] = {
    "low": 0.2,
    "medium": 0.5,
    "high": 0.8,
    "critical": 1.0,
}


class AIRecommender:
    """Ranks candidate assignees by competency, load, history, and LLM reasoning."""

    def __init__(self, db: AsyncSession, llm_client: LLMClient) -> None:
        self._db = db
        self._llm_client = llm_client

    async def recommend_assignee(self, task: Task, project_id: int | None = None) -> Recommendation:
        """Return top-3 assignee candidates for a task."""

        candidates = await self._load_candidates(project_id=project_id, task_project_id=task.project_id)
        if not candidates:
            return Recommendation(reason="Не найдено ни одного доступного исполнителя.", candidates=[])

        ranked: list[CompetencyScore] = []
        raw_totals: dict[str, float] = {}
        for user in candidates:
            skill_match = self._score_skill_match(task=task, user=user)
            history_match = await self._score_history_match(task=task, user=user)
            load_score = self._score_load(user.load)
            priority_score = self._score_priority(task.priority, user.competency)
            total = self._compose_total(
                competency=user.competency,
                skill_match=skill_match,
                history_match=history_match,
                load_score=load_score,
                priority_score=priority_score,
            )
            user_id = str(user.id)
            raw_totals[user_id] = total
            ranked.append(
                CompetencyScore(
                    user_id=user_id,
                    full_name=user.full_name,
                    competency=round(float(user.competency), 3),
                    load=int(user.load),
                    skill_match_score=round(skill_match, 3),
                    history_match_score=round(history_match, 3),
                    load_score=round(load_score, 3),
                    priority_score=round(priority_score, 3),
                    total_score=round(total, 3),
                    explanation=self._local_explanation(user=user, total_score=total, task_priority=task.priority),
                )
            )
        llm_adjustments = await self._llm_score_adjustments(task=task, candidates=ranked)
        for item in ranked:
            adjustment = llm_adjustments.get(item.user_id, 0.0)
            base_total = raw_totals.get(item.user_id, item.total_score)
            item.llm_score_adjustment = round(adjustment, 3)
            item.total_score = round(min(1.0, max(0.0, base_total + adjustment)), 3)
        ranked.sort(key=lambda item: item.total_score, reverse=True)
        top_candidates = ranked[:3]

        llm_notes = await self._llm_explanation(task=task, candidates=top_candidates)
        top = top_candidates[0]
        return Recommendation(
            recommended_user_id=top.user_id,
            recommended_user_name=top.full_name,
            reason=top.explanation,
            candidates=top_candidates,
            llm_notes=llm_notes,
            metadata={"project_id": str(task.project_id) if task.project_id else None, "priority": task.priority},
        )

    async def _llm_score_adjustments(self, *, task: Task, candidates: list[CompetencyScore]) -> dict[str, float]:
        payload = {
            "task": {
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "tags": task.tags,
            },
            "candidates": [item.model_dump() for item in candidates[:8]],
        }
        prompt = (
            "Ты AI-рекомендер исполнителей. На основе задачи и кандидатов верни только JSON:\n"
            "{\"adjustments\":[{\"user_id\":\"...\",\"delta\":-0.15..0.15}]}\n"
            "delta > 0 если кандидат лучше с учетом скрытых факторов контекста, delta < 0 если хуже.\n"
            "Никакого markdown, только JSON.\n"
            f"input: {json.dumps(payload, ensure_ascii=False)}"
        )
        try:
            raw = await self._llm_client.generate(prompt)
            parsed = json.loads(raw)
            rows = parsed.get("adjustments")
            if not isinstance(rows, list):
                return {}
            result: dict[str, float] = {}
            for row in rows:
                if not isinstance(row, dict):
                    continue
                user_id = row.get("user_id")
                delta = row.get("delta")
                if isinstance(user_id, str) and isinstance(delta, (int, float)):
                    result[user_id] = max(-0.3, min(0.3, float(delta)))
            return result
        except Exception:
            return {}

    async def _load_candidates(self, *, project_id: int | None, task_project_id: str | None) -> list[User]:
        query: Select[tuple[User]] = select(User).where(User.role.in_(["admin", "pm", "engineer"]))
        selected_project_id = str(project_id) if project_id is not None else task_project_id
        if selected_project_id is not None:
            # If workload_profile has scoped project affinity, prioritize users with any profile.
            query = query.order_by(User.load.asc(), User.competency.desc())
        result = await self._db.execute(query.limit(50))
        return list(result.scalars().all())

    async def _score_history_match(self, task: Task, user: User) -> float:
        query = (
            select(Task)
            .where(Task.assignee_id == user.id)
            .where(Task.status == "done")
            .order_by(Task.updated_at.desc())
            .limit(30)
        )
        result = await self._db.execute(query)
        done_tasks = list(result.scalars().all())
        if not done_tasks:
            return 0.0
        task_tokens = self._tokens(task.title, task.description, task.tags)
        overlaps = 0.0
        for item in done_tasks:
            overlap = len(task_tokens.intersection(self._tokens(item.title, item.description, item.tags)))
            overlaps += float(overlap > 0)
        return min(1.0, overlaps / max(1, len(done_tasks)))

    @staticmethod
    def _score_skill_match(task: Task, user: User) -> float:
        user_skills = user.skills if isinstance(user.skills, dict) else {}
        skill_keys = {str(k).strip().lower() for k in user_skills.keys() if str(k).strip()}
        if not skill_keys:
            return 0.0
        task_tokens = AIRecommender._tokens(task.title, task.description, task.tags)
        matched = len(task_tokens.intersection(skill_keys))
        return min(1.0, matched / max(1, len(skill_keys)))

    @staticmethod
    def _score_load(load: int) -> float:
        if load <= 0:
            return 1.0
        if load >= 10:
            return 0.0
        return max(0.0, 1.0 - (load / 10.0))

    @staticmethod
    def _score_priority(priority: str, competency: float) -> float:
        p_weight = _PRIORITY_WEIGHTS.get(priority.lower(), 0.5)
        competency_norm = min(1.0, max(0.0, competency))
        return (p_weight * 0.6) + (competency_norm * 0.4)

    @staticmethod
    def _compose_total(
        *,
        competency: float,
        skill_match: float,
        history_match: float,
        load_score: float,
        priority_score: float,
    ) -> float:
        competency_norm = min(1.0, max(0.0, competency))
        total = (
            competency_norm * 0.30
            + skill_match * 0.20
            + history_match * 0.20
            + load_score * 0.20
            + priority_score * 0.10
        )
        return min(1.0, max(0.0, total))

    async def save_recommendation(self, task_id: str, recommendation: Recommendation) -> AIRecommendation:
        """Persist recommendation payload for audit/history."""

        item = AIRecommendation(
            recommendation_type="assignee",
            rationale=recommendation.reason,
            payload=recommendation.model_dump(),
            status="proposed",
            task_id=task_id,
        )
        self._db.add(item)
        await self._db.commit()
        await self._db.refresh(item)
        return item

    async def _llm_explanation(self, *, task: Task, candidates: list[CompetencyScore]) -> str:
        if not candidates:
            return "Нет кандидатов для объяснения."
        payload = {
            "task": {
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "tags": task.tags,
            },
            "candidates": [item.model_dump() for item in candidates],
        }
        prompt = (
            "Ты PM-ассистент. На русском кратко объясни, почему выбран первый кандидат и чем "
            "отличаются остальные. Формат: 2-4 предложения, без markdown.\n"
            f"Данные: {json.dumps(payload, ensure_ascii=False)}"
        )
        try:
            response = (await self._llm_client.generate(prompt)).strip()
            if response:
                return response
        except Exception:
            pass
        names = ", ".join(item.full_name for item in candidates)
        return f"Рекомендация сформирована на основе компетенций, загрузки и истории похожих задач. Кандидаты: {names}."

    @staticmethod
    def _tokens(title: str, description: str, tags: Iterable[str]) -> set[str]:
        base_text = " ".join([title, description, " ".join(tags or [])]).lower()
        cleaned = re.sub(r"[^a-zа-я0-9_ ]+", " ", base_text, flags=re.IGNORECASE)
        return {part for part in cleaned.split() if len(part) > 2}

    @staticmethod
    def _local_explanation(*, user: User, total_score: float, task_priority: str) -> str:
        return (
            f"{user.full_name} рекомендован с итоговым скором {total_score:.2f}: "
            f"компетенция {float(user.competency):.2f}, загрузка {int(user.load)}, приоритет задачи '{task_priority}'."
        )

