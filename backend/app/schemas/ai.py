from pydantic import BaseModel


class AISuggestTaskRequest(BaseModel):
    text: str
    project_id: str | None = None


class AIAssigneeRequest(BaseModel):
    task_title: str
    required_skills: list[str] = []


class AIResponse(BaseModel):
    result: dict
