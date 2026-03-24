from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ''
    status: str = 'to-do'
    priority: str = 'medium'
    estimated_hours: int = 0
    due_at: datetime | None = None
    dependency_ids: list = Field(default_factory=list)
    tags: list = Field(default_factory=list)
    project_id: str | None = None
    assignee_id: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    estimated_hours: int | None = None
    due_at: datetime | None = None
    dependency_ids: list | None = None
    tags: list | None = None
    project_id: str | None = None
    assignee_id: str | None = None


class TaskOut(ORMModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    estimated_hours: int
    due_at: datetime | None
    dependency_ids: list
    tags: list
    project_id: str | None
    assignee_id: str | None
