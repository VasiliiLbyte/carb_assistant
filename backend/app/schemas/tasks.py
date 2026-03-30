"""Pydantic schemas: Task."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class TaskStatus(StrEnum):
    TODO = "to-do"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELED = "canceled"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ''
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: int = 0
    due_at: datetime | None = None
    dependency_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    project_id: UUID | None = None
    assignee_id: UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    estimated_hours: int | None = None
    due_at: datetime | None = None
    dependency_ids: list[str] | None = None
    tags: list[str] | None = None
    project_id: UUID | None = None
    assignee_id: UUID | None = None


class TaskOut(ORMModel):
    id: UUID
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    estimated_hours: int
    due_at: datetime | None
    dependency_ids: list[str]
    tags: list[str]
    project_id: UUID | None
    assignee_id: UUID | None
