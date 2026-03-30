"""OpenClaw webhook router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.task_auto_creator import TaskAutoCreator
from app.core.config import settings
from app.crud import tasks as tasks_crud
from app.dependencies import LLMClient, get_db, get_llm_client
from app.schemas.ai import OpenClawWebhookRequest, OpenClawWebhookResponse
from app.schemas.tasks import TaskOut

router = APIRouter(prefix="/openclaw", tags=["openclaw"])


@router.post("/webhook", response_model=OpenClawWebhookResponse)
async def openclaw_webhook(
    payload: OpenClawWebhookRequest,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    x_openclaw_api_key: str | None = Header(default=None, alias="X-OpenClaw-Api-Key"),
) -> OpenClawWebhookResponse:
    """Receive external message and convert it into persisted tasks."""

    expected_api_key = settings.openclaw_api_key
    if not expected_api_key or expected_api_key == "change-me":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenClaw API key is not configured",
        )
    if x_openclaw_api_key != expected_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    creator = TaskAutoCreator(db=session, llm_client=llm_client)
    generated_tasks = await creator.create_tasks_from_message(
        text=payload.message,
        project_id=payload.project_id,
    )

    created: list[TaskOut] = []
    for task_schema in generated_tasks:
        task = await tasks_crud.create_task(session, task_schema.model_dump())
        created.append(TaskOut.model_validate(task))

    return OpenClawWebhookResponse(accepted=True, tasks=created)
