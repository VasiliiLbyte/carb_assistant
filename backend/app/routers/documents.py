"""Documents upload and processing router for Stage 5."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import LLMClient, get_db, get_llm_client, require_roles
from app.document_processor.document_processor import DocumentProcessor
from app.document_processor.schemas import DocumentProcessRequest, DocumentProcessResponse, DocumentUploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    project_id: int | str | None = Form(default=None),
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> DocumentUploadResponse:
    """Upload a source file for later processing."""

    processor = DocumentProcessor(db=session, llm_client=llm_client)
    data = await processor.upload_document(file=file, project_id=project_id)
    return DocumentUploadResponse.model_validate(data)


@router.post("/process", response_model=DocumentProcessResponse)
async def process_document(
    payload: DocumentProcessRequest,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> DocumentProcessResponse:
    """Process an uploaded document and create tasks."""

    processor = DocumentProcessor(db=session, llm_client=llm_client)
    data = await processor.process_document(file_key=payload.file_key, project_id=payload.project_id)
    return DocumentProcessResponse.model_validate(data)
