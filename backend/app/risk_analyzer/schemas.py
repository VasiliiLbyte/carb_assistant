"""Pydantic schemas for Stage 8 risk analyzer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


RiskSeverity = Literal["high", "medium", "low"]
RiskSource = Literal["task", "document", "message"]


class RiskCreate(BaseModel):
    """Input payload for manual risk creation."""

    title: str = Field(min_length=1, max_length=255)
    probability: int = Field(default=1, ge=1, le=5)
    impact: int = Field(default=1, ge=1, le=5)
    mitigation_plan: str = Field(default="", max_length=2000)
    status: str = Field(default="open", max_length=50)
    severity: RiskSeverity = "low"
    source: RiskSource = "message"
    project_id: str | None = None
    task_id: str | None = None


class RiskOut(BaseModel):
    """API response schema for risks."""

    id: str
    title: str
    probability: int
    impact: int
    mitigation_plan: str
    status: str
    severity: RiskSeverity
    source: RiskSource
    project_id: str | None
    task_id: str | None

    model_config = {"from_attributes": True}


class RiskDetectionRequest(BaseModel):
    """Generic ad-hoc message detection request."""

    message: str = Field(min_length=1, max_length=12000)
    project_id: str | None = None


class RiskDetectFromTaskRequest(BaseModel):
    """Request schema for task-based detection."""

    task_id: str = Field(min_length=1)


class RiskDetectFromDocumentRequest(BaseModel):
    """Request schema for document-based detection."""

    document_key: str = Field(min_length=1, max_length=500)
    project_id: str | None = None


class RiskDetectionResult(BaseModel):
    """Response schema for detection endpoints."""

    created_count: int
    escalated_count: int
    risks: list[RiskOut]
