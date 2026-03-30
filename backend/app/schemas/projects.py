from uuid import UUID

from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    project_type: str = 'general'
    stage: str = 'planned'
    custom_fields: dict = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    project_type: str | None = None
    stage: str | None = None
    custom_fields: dict | None = None


class ProjectOut(ORMModel):
    id: UUID
    name: str
    project_type: str
    stage: str
    custom_fields: dict
