"""Pydantic schemas for assignee recommendation flows."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TaskInput(BaseModel):
    """Task payload used when no persisted task_id is provided."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    priority: str = Field(default="medium", min_length=1, max_length=50)
    project_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    estimated_hours: int = Field(default=0, ge=0)


class RecommenderRequest(BaseModel):
    """Request schema for recommendation endpoint."""

    task_id: str | None = None
    project_id: str | None = None
    task: TaskInput | None = None


class CompetencyScore(BaseModel):
    """Per-candidate score breakdown."""

    user_id: str
    full_name: str
    competency: float
    load: int
    skill_match_score: float = Field(ge=0.0, le=1.0)
    history_match_score: float = Field(ge=0.0, le=1.0)
    load_score: float = Field(ge=0.0, le=1.0)
    priority_score: float = Field(ge=0.0, le=1.0)
    llm_score_adjustment: float = Field(default=0.0, ge=-0.3, le=0.3)
    total_score: float = Field(ge=0.0, le=1.0)
    explanation: str


class Recommendation(BaseModel):
    """Top recommendation response."""

    recommended_user_id: str | None = None
    recommended_user_name: str | None = None
    reason: str
    candidates: list[CompetencyScore] = Field(default_factory=list)
    llm_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApplyRecommendationRequest(BaseModel):
    """Apply endpoint payload."""

    task_id: str = Field(min_length=1)
    assignee_id: str = Field(min_length=1)

