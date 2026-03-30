"""Schemas for proactive rules, triggers, and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProactiveRuleCreate(BaseModel):
    """Create payload for a proactive rule."""

    name: str = Field(min_length=1, max_length=255)
    trigger_type: str = Field(min_length=1, max_length=100)
    action_type: str = Field(default="send_message", min_length=1, max_length=100)
    config: dict[str, Any] = Field(default_factory=dict)
    buttons: list[dict[str, Any]] = Field(default_factory=list)
    enabled: bool = True


class ProactiveRuleUpdate(BaseModel):
    """Patch payload for a proactive rule."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    trigger_type: str | None = Field(default=None, min_length=1, max_length=100)
    action_type: str | None = Field(default=None, min_length=1, max_length=100)
    config: dict[str, Any] | None = None
    buttons: list[dict[str, Any]] | None = None
    enabled: bool | None = None


class ProactiveRuleOut(BaseModel):
    """Public representation of a proactive rule."""

    id: str
    name: str
    trigger_type: str
    action_type: str
    config: dict[str, Any]
    buttons: list[dict[str, Any]]
    enabled: bool
    created_at: datetime
    updated_at: datetime


class PingMessage(BaseModel):
    """Rendered ping message for a task/rule pair."""

    rule_id: str
    task_id: str
    target_user_id: str | None = None
    message: str


class ProactiveTriggerRequest(BaseModel):
    """Manual trigger payload for sending proactive ping."""

    rule_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)


class ProactiveTriggerResponse(BaseModel):
    """Trigger result payload."""

    sent: bool
    ping: PingMessage


class ResponseHandleRequest(BaseModel):
    """Incoming user message to process as proactive response."""

    message_text: str = Field(min_length=1, max_length=8000)
    source: str = Field(default="telegram", min_length=1, max_length=64)
    user_id: str | None = None


class ResponseHandleResult(BaseModel):
    """Result of processing user response."""

    processed: bool
    action: str
    task_id: str | None = None
    new_status: str | None = None
    note: str | None = None
