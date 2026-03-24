from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIRecommendation


async def log_recommendation(
    session: AsyncSession,
    *,
    recommendation_type: str,
    rationale: str,
    payload: dict,
    task_id: str | None = None,
    status: str = 'proposed',
) -> AIRecommendation:
    rec = AIRecommendation(
        recommendation_type=recommendation_type,
        rationale=rationale[:2000],
        payload=payload,
        status=status,
        task_id=task_id,
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return rec


async def attach_task_to_recommendation(
    session: AsyncSession,
    recommendation_id: str,
    task_id: str,
    status: str = 'accepted',
) -> None:
    from uuid import UUID

    rec = await session.get(AIRecommendation, UUID(str(recommendation_id)))
    if rec is None:
        return
    rec.task_id = UUID(str(task_id)) if not isinstance(task_id, UUID) else task_id
    rec.status = status
    await session.commit()
