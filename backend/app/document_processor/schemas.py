"""Schemas for document upload and processing flows."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.tasks import TaskOut


class DocumentUploadResponse(BaseModel):
    """Upload response with stored object details."""

    file_key: str
    filename: str
    content_type: str
    size_bytes: int
    project_id: int | str | None = None


class DocumentProcessRequest(BaseModel):
    """Request payload for document processing."""

    file_key: str = Field(min_length=1, max_length=1024)
    project_id: int | str | None = None


class DocumentProcessResponse(BaseModel):
    """Processing result with extracted entities."""

    file_key: str
    tasks: list[TaskOut]
    risks: list[str] = Field(default_factory=list)
