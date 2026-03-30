"""Pydantic schemas: User."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field
from app.schemas.common import ORMModel

UserRole = Literal["owner", "admin", "manager", "member", "viewer"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = "viewer"
    competency: float = Field(default=0.0, ge=0.0)
    load: int = Field(default=0, ge=0)
    skills: dict = Field(default_factory=dict)
    notification_settings: dict = Field(default_factory=dict)
    workload_profile: dict = Field(default_factory=dict)


class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=128)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    competency: float | None = Field(default=None, ge=0.0)
    load: int | None = Field(default=None, ge=0)
    skills: dict | None = None
    notification_settings: dict | None = None
    workload_profile: dict | None = None


class UserOut(ORMModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    competency: float
    load: int
    skills: dict
    notification_settings: dict
    workload_profile: dict
