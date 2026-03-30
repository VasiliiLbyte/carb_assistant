"""Assignee recommender router for Stage 7."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tasks as tasks_crud
from app.dependencies import LLMClient, get_db, get_llm_client, require_roles
from app.models import Task
from app.recommender.recommender import AIRecommender
from app.recommender.schemas import ApplyRecommendationRequest, Recommendation, RecommenderRequest

router = APIRouter(prefix="/recommender", tags=["recommender"])


def _to_int_project_id(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value) if value.isdigit() else None


@router.post("/recommend", response_model=Recommendation)
async def recommend_assignee(
    payload: RecommenderRequest,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> Recommendation:
    """Recommend top-3 assignees for an existing or ad-hoc task."""

    recommender = AIRecommender(db=session, llm_client=llm_client)
    if payload.task_id:
        task = await tasks_crud.get_task(session, payload.task_id)
        recommendation = await recommender.recommend_assignee(task=task, project_id=_to_int_project_id(payload.project_id))
        await recommender.save_recommendation(task_id=str(task.id), recommendation=recommendation)
        return recommendation
    if payload.task is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either task_id or task payload is required",
        )

    virtual_task = Task(
        title=payload.task.title,
        description=payload.task.description,
        priority=payload.task.priority,
        project_id=payload.project_id or payload.task.project_id,
        tags=payload.task.tags,
        estimated_hours=payload.task.estimated_hours,
    )
    return await recommender.recommend_assignee(task=virtual_task, project_id=_to_int_project_id(payload.project_id))


@router.post("/apply")
async def apply_recommendation(
    payload: ApplyRecommendationRequest,
    session: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> dict[str, str]:
    """Apply selected assignee recommendation to task."""

    task = await tasks_crud.get_task(session, payload.task_id)
    updated_task = await tasks_crud.update_assignee(session, task, payload.assignee_id)
    return {"task_id": str(updated_task.id), "assignee_id": str(updated_task.assignee_id)}

