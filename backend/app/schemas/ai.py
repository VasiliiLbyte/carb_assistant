from pydantic import BaseModel, Field


class AISuggestTaskRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    project_id: str | None = None


class AIConfirmCreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ''
    project_id: str | None = None
    priority: str = 'medium'
    recommendation_id: str | None = None


class AIAssigneeRequest(BaseModel):
    task_title: str = Field(min_length=1, max_length=255)
    required_skills: list[str] = []
    task_id: str | None = None
    project_id: str | None = None


class AIResponse(BaseModel):
    result: dict
