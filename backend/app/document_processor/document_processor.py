"""Document processor for uploads and basic RAG-style extraction."""

from __future__ import annotations

import asyncio
import io
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pdfplumber
from docx import Document as DocxDocument
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm_client import OpenRouterLLMClient
from app.core.config import settings
from app.crud import tasks as tasks_crud
from app.dependencies import LLMClient
from app.integrations.storage.minio_client import get_s3_client
from app.schemas.tasks import TaskCreate, TaskOut


class DocumentProcessor:
    """Upload, parse, and process documents into tasks/risks."""

    def __init__(self, db: AsyncSession, llm_client: LLMClient) -> None:
        self._db = db
        self._llm_client = llm_client

    async def upload_document(
        self,
        *,
        file: UploadFile,
        project_id: int | str | None = None,
    ) -> dict[str, Any]:
        """Upload a document to MinIO and return storage metadata."""

        filename = file.filename or "document.txt"
        extension = Path(filename).suffix.lower()
        object_uuid = uuid.uuid4().hex
        if project_id is not None:
            file_key = f"projects/{project_id}/documents/{object_uuid}{extension}"
        else:
            file_key = f"documents/{object_uuid}{extension}"

        payload = await file.read()
        content_type = file.content_type or "application/octet-stream"

        def _put_object() -> None:
            client = get_s3_client()
            client.put_object(
                Bucket=settings.minio_bucket,
                Key=file_key,
                Body=payload,
                ContentType=content_type,
            )

        await asyncio.to_thread(_put_object)
        return {
            "file_key": file_key,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(payload),
            "project_id": project_id,
        }

    async def process_document(
        self,
        *,
        file_key: str,
        project_id: int | str | None = None,
    ) -> dict[str, Any]:
        """Process a MinIO document and persist extracted tasks."""

        raw_bytes = await self._download_bytes(file_key)
        text = self._extract_text_from_bytes(file_key=file_key, content=raw_bytes)
        llm_payload = await self._extract_structured_data(text=text, project_id=project_id)

        task_rows = llm_payload.get("tasks", [])
        risks_raw = llm_payload.get("risks", [])
        risks = [str(item).strip() for item in risks_raw if str(item).strip()]

        tasks = await self._persist_tasks(task_rows=task_rows, project_id=project_id, fallback_text=text)
        return {"file_key": file_key, "tasks": tasks, "risks": risks}

    async def _download_bytes(self, file_key: str) -> bytes:
        def _get_object() -> bytes:
            client = get_s3_client()
            response = client.get_object(Bucket=settings.minio_bucket, Key=file_key)
            try:
                return response["Body"].read()
            finally:
                response["Body"].close()

        return await asyncio.to_thread(_get_object)

    def _extract_text_from_bytes(self, *, file_key: str, content: bytes) -> str:
        suffix = Path(file_key).suffix.lower()
        if suffix in {".txt", ".md", ".csv"}:
            return content.decode("utf-8", errors="ignore")
        if suffix == ".pdf":
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                parts = [(page.extract_text() or "") for page in pdf.pages]
            return "\n".join(parts).strip()
        if suffix == ".docx":
            doc = DocxDocument(io.BytesIO(content))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
        raise ValueError(f"Unsupported file extension: {suffix or 'unknown'}")

    async def _extract_structured_data(self, *, text: str, project_id: int | str | None) -> dict[str, Any]:
        prompt = (
            "Ты PM-ассистент. Проанализируй текст документа и извлеки задачи и риски.\n"
            "Верни строго JSON без markdown:\n"
            '{"tasks":[{"title":"...", "description":"...", "assignee":"...", "due_at":"YYYY-MM-DDTHH:MM:SS|null"}],'
            '"risks":["...", "..."]}\n'
            "Если задач/рисков нет, верни пустые массивы.\n"
            f"project_id: {project_id}\n"
            f"document_text:\n{text[:12000]}"
        )
        try:
            raw = await self._llm_client.generate(prompt)
            payload = json.loads(raw)
            if isinstance(payload, dict):
                tasks = payload.get("tasks", [])
                risks = payload.get("risks", [])
                if not isinstance(tasks, list):
                    tasks = []
                if not isinstance(risks, list):
                    risks = []
                return {"tasks": tasks, "risks": risks}
        except Exception:
            pass
        # Fallback: parse only tasks with helper from shared client.
        parsed_tasks = OpenRouterLLMClient.parse_tasks_json(raw) if "raw" in locals() else []
        return {"tasks": parsed_tasks, "risks": []}

    async def _persist_tasks(
        self,
        *,
        task_rows: list[Any],
        project_id: int | str | None,
        fallback_text: str,
    ) -> list[TaskOut]:
        schemas: list[TaskCreate] = []
        for row in task_rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title", "")).strip()
            if not title:
                continue
            description = str(row.get("description", "")).strip()[:4000]
            assignee = row.get("assignee")
            if isinstance(assignee, str) and assignee.strip():
                description = f"{description}\nassignee_hint={assignee.strip()}".strip()
            due_at = self._parse_due_at(row.get("due_at"))
            schemas.append(
                TaskCreate(
                    title=title[:255],
                    description=description,
                    due_at=due_at,
                    project_id=str(project_id) if project_id is not None else None,
                )
            )

        if not schemas:
            fallback_title = (fallback_text.splitlines()[0].strip() if fallback_text.strip() else "Задача из документа")[:255]
            schemas.append(
                TaskCreate(
                    title=fallback_title or "Задача из документа",
                    description=fallback_text[:4000],
                    project_id=str(project_id) if project_id is not None else None,
                )
            )

        created: list[TaskOut] = []
        for schema in schemas:
            task = await tasks_crud.create_task(self._db, schema.model_dump())
            created.append(TaskOut.model_validate(task))
        return created

    @staticmethod
    def _parse_due_at(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if not isinstance(value, str):
            return None
        candidate = value.strip()
        if not candidate:
            return None
        try:
            return datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return None
