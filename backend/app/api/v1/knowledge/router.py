from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.deps import get_current_user, require_roles
from app.services.ai.knowledge_base_service import ingest_document
from app.services.ai.memory_bank_service import put_memory
from app.services.ai.retrieval_service import retrieve_context

router = APIRouter(prefix='/knowledge', tags=['knowledge'])


class MemoryIn(BaseModel):
    scope_type: str
    scope_id: str
    content: str


class IngestIn(BaseModel):
    title: str
    text: str


@router.post('/memory')
async def create_memory(
    payload: MemoryIn,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    return await put_memory(session, payload.scope_type, payload.scope_id, payload.content)


@router.post('/ingest')
async def ingest(
    payload: IngestIn,
    session: AsyncSession = Depends(get_async_session),
    _user: dict = Depends(require_roles('admin', 'pm', 'engineer')),
):
    return await ingest_document(session, payload.title, payload.text)


@router.get('/search')
async def search(
    query: str = Query(..., min_length=1, max_length=4000),
    project_id: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    user: dict = Depends(get_current_user),
):
    return await retrieve_context(session, query, project_id=project_id, user_id=str(user['id']))
