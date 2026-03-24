from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class RiskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    probability: int = 1
    impact: int = 1
    mitigation_plan: str = ''
    status: str = 'open'
    project_id: str | None = None


class RiskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    probability: int | None = None
    impact: int | None = None
    mitigation_plan: str | None = None
    status: str | None = None
    project_id: str | None = None


class RiskOut(ORMModel):
    id: str
    title: str
    probability: int
    impact: int
    mitigation_plan: str
    status: str
    project_id: str | None
