from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.deps import require_roles
from app.schemas.ai import (
    AIAssigneeRequest,
    AIConfirmCreateTaskRequest,
    AIResponse,
    AISuggestTaskRequest,
)
from app.services.ai.competency_load_manager import load_analysis
from app.services.ai.recommender import suggest_assignee
from app.services.ai.task_auto_creator import confirm_create_task, suggest_task
from app.services.ai.task_updater import reassign_tasks

router = APIRouter(prefix='/ai', tags=['ai'])


@router.post('/suggest_task', response_model=AIResponse)
async def suggest_task_endpoint(
    payload: AISuggestTaskRequest,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    return {
        'result': await suggest_task(
            session,
            payload.text,
            payload.project_id,
            user_id=str(_user['id']),
        )
    }


@router.post('/create_task', response_model=AIResponse)
async def create_task_endpoint(
    payload: AIConfirmCreateTaskRequest,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    return {
        'result': await confirm_create_task(
            session,
            title=payload.title,
            description=payload.description,
            project_id=payload.project_id,
            priority=payload.priority,
            recommendation_id=payload.recommendation_id,
        )
    }


@router.post('/suggest_assignee', response_model=AIResponse)
async def suggest_assignee_endpoint(
    payload: AIAssigneeRequest,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    return {
        'result': await suggest_assignee(
            session,
            payload.task_title,
            payload.required_skills,
            task_id=payload.task_id,
            project_id=payload.project_id,
            user_id=str(_user['id']),
        )
    }


@router.get('/load_analysis', response_model=AIResponse)
async def load_analysis_endpoint(
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer', 'viewer')),
):
    return {'result': await load_analysis(session)}


@router.post('/reassign_tasks', response_model=AIResponse)
async def reassign_tasks_endpoint(
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm')),
):
    return {'result': await reassign_tasks(session)}
