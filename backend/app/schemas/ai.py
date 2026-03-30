from pydantic import BaseModel, Field

from app.schemas.tasks import TaskOut


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


class AICreateTasksFromMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    project_id: int | str | None = None


class AICreateTasksFromMessageResponse(BaseModel):
    tasks: list[TaskOut]


class OpenClawWebhookRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    source: str = Field(default="telegram", min_length=1, max_length=64)
    project_id: int | str | None = None


class OpenClawWebhookResponse(BaseModel):
    accepted: bool
    tasks: list[TaskOut]
