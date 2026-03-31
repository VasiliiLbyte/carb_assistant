"""Risk analyzer router for Stage 8."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import LLMClient, get_db, get_llm_client, require_roles
from app.models import Document, Risk, Task
from app.risk_analyzer.risk_analyzer import RiskAnalyzer
from app.risk_analyzer.schemas import (
    RiskDetectFromDocumentRequest,
    RiskDetectFromTaskRequest,
    RiskDetectionRequest,
    RiskDetectionResult,
    RiskOut,
)

router = APIRouter(prefix="/risks", tags=["risks"])


async def _assert_engineer_can_access_task(session: AsyncSession, user_id: str, task_id: str) -> None:
    query = select(Task.id).where(and_(Task.id == task_id, Task.assignee_id == user_id))
    result = await session.execute(query.limit(1))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this task")


async def _assert_engineer_can_access_document(session: AsyncSession, user_id: str, document_key: str) -> None:
    doc_query = select(Document).where(Document.object_key == document_key)
    doc_result = await session.execute(doc_query.limit(1))
    document = doc_result.scalars().first()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.project_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for unscoped document")
    task_query = select(Task.id).where(and_(Task.project_id == document.project_id, Task.assignee_id == user_id))
    task_result = await session.execute(task_query.limit(1))
    if task_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this document")


@router.get("", response_model=list[RiskOut])
async def list_risks(
    project_id: str | None = Query(default=None),
    task_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> list[RiskOut]:
    """List risks optionally filtered by project and task."""

    query = select(Risk).order_by(Risk.created_at.desc())
    if project_id:
        query = query.where(Risk.project_id == project_id)
    if task_id:
        query = query.where(Risk.task_id == task_id)
    if _user.get("role") == "engineer":
        user_id = str(_user.get("id"))
        assigned_tasks = select(Task.id).where(Task.assignee_id == user_id)
        assigned_projects = select(Task.project_id).where(
            and_(Task.assignee_id == user_id, Task.project_id.is_not(None))
        )
        query = query.where(
            or_(
                Risk.task_id.in_(assigned_tasks),
                Risk.project_id.in_(assigned_projects),
            )
        )
    result = await session.execute(query.limit(200))
    rows = list(result.scalars().all())
    return [RiskOut.model_validate({**item.__dict__, "id": str(item.id)}) for item in rows]


@router.post("/detect-from-task", response_model=RiskDetectionResult)
async def detect_from_task(
    payload: RiskDetectFromTaskRequest,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> RiskDetectionResult:
    """Run risk detection from task context."""

    if _user.get("role") == "engineer":
        await _assert_engineer_can_access_task(
            session=session,
            user_id=str(_user.get("id")),
            task_id=payload.task_id,
        )
    analyzer = RiskAnalyzer(db=session, llm_client=llm_client)
    created = await analyzer.detect_risks_from_task(task_id=payload.task_id)
    escalated = await analyzer.escalate_high_risks(created)
    out_rows = [RiskOut.model_validate({**item.__dict__, "id": str(item.id)}) for item in created]
    return RiskDetectionResult(created_count=len(created), escalated_count=len(escalated), risks=out_rows)


@router.post("/detect-from-document", response_model=RiskDetectionResult)
async def detect_from_document(
    payload: RiskDetectFromDocumentRequest,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> RiskDetectionResult:
    """Run risk detection from uploaded document."""

    if _user.get("role") == "engineer":
        await _assert_engineer_can_access_document(
            session=session,
            user_id=str(_user.get("id")),
            document_key=payload.document_key,
        )
    analyzer = RiskAnalyzer(db=session, llm_client=llm_client)
    created = await analyzer.detect_risks_from_document(
        document_key=payload.document_key,
        project_id=payload.project_id,
    )
    escalated = await analyzer.escalate_high_risks(created)
    out_rows = [RiskOut.model_validate({**item.__dict__, "id": str(item.id)}) for item in created]
    return RiskDetectionResult(created_count=len(created), escalated_count=len(escalated), risks=out_rows)


@router.post("/detect-from-message", response_model=RiskDetectionResult)
async def detect_from_message(
    payload: RiskDetectionRequest,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> RiskDetectionResult:
    """Run risk detection from free-form message."""

    if _user.get("role") == "engineer":
        if not payload.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="project_id is required for engineer role",
            )
        project_query = select(Task.id).where(
            and_(Task.project_id == payload.project_id, Task.assignee_id == str(_user.get("id")))
        )
        project_result = await session.execute(project_query.limit(1))
        if project_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden for this project")

    analyzer = RiskAnalyzer(db=session, llm_client=llm_client)
    created = await analyzer.detect_risks_from_message(
        message=payload.message,
        project_id=payload.project_id,
    )
    escalated = await analyzer.escalate_high_risks(created)
    out_rows = [RiskOut.model_validate({**item.__dict__, "id": str(item.id)}) for item in created]
    return RiskDetectionResult(created_count=len(created), escalated_count=len(escalated), risks=out_rows)
