"""SQLAlchemy model: Task."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'tasks'

    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(String(4000), default='')
    status: Mapped[str] = mapped_column(String(50), default='to-do', index=True)
    priority: Mapped[str] = mapped_column(String(50), default='medium', index=True)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=0)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    dependency_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    project_id: Mapped[str | None] = mapped_column(ForeignKey('projects.id', ondelete='SET NULL'), nullable=True, index=True)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)

    project = relationship('Project', back_populates='tasks', lazy='selectin')
    assignee = relationship('User', back_populates='assigned_tasks', lazy='selectin')
    recommendations = relationship('AIRecommendation', back_populates='task', lazy='selectin')
