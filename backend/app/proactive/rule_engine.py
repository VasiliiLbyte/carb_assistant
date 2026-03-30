"""Rule evaluation utilities for proactive automation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProactiveRule, Task


class RuleEngine:
    """Evaluate proactive rules against task data."""

    @staticmethod
    async def list_enabled_rules(session: AsyncSession) -> list[ProactiveRule]:
        result = await session.execute(select(ProactiveRule).where(ProactiveRule.enabled.is_(True)))
        return list(result.scalars().all())

    @staticmethod
    async def evaluate_inprogress_overdue_tasks(session: AsyncSession, *, days_threshold: int) -> list[Task]:
        threshold = datetime.now(timezone.utc) - timedelta(days=days_threshold)
        query = select(Task).where(Task.status == "in-progress", Task.updated_at <= threshold)
        result = await session.execute(query)
        return list(result.scalars().all())
