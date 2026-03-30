"""AI task automation router for Stage 3."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.task_auto_creator import TaskAutoCreator
from app.crud import tasks as tasks_crud
from app.dependencies import get_db, get_llm_client, require_roles
from app.schemas.ai import AICreateTasksFromMessageRequest, AICreateTasksFromMessageResponse
from app.schemas.tasks import TaskOut

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/create-tasks-from-message",
    response_model=AICreateTasksFromMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tasks_from_message(
    payload: AICreateTasksFromMessageRequest,
    session: AsyncSession = Depends(get_db),
    llm_client=Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> AICreateTasksFromMessageResponse:
    """Generate task drafts from a message and persist them."""

    creator = TaskAutoCreator(db=session, llm_client=llm_client)
    generated_tasks = await creator.create_tasks_from_message(
        text=payload.message,
        project_id=payload.project_id,
    )

    created: list[TaskOut] = []
    for task_schema in generated_tasks:
        task = await tasks_crud.create_task(session, task_schema.model_dump())
        created.append(TaskOut.model_validate(task))

    return AICreateTasksFromMessageResponse(tasks=created)
