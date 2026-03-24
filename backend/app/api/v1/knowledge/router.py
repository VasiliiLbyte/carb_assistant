from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai.memory_bank_service import put_memory
from app.services.ai.knowledge_base_service import ingest_document
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
async def create_memory(payload: MemoryIn) -> dict:
    return await put_memory(payload.scope_type, payload.scope_id, payload.content)


@router.post('/ingest')
async def ingest(payload: IngestIn) -> dict:
    return await ingest_document(payload.title, payload.text)


@router.get('/search')
async def search(query: str) -> dict:
    return await retrieve_context(query)
