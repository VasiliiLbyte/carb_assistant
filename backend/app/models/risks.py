"""SQLAlchemy model: Risk."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Risk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'risks'

    title: Mapped[str] = mapped_column(String(255), index=True)
    probability: Mapped[int] = mapped_column(Integer, default=1)
    impact: Mapped[int] = mapped_column(Integer, default=1)
    mitigation_plan: Mapped[str] = mapped_column(String(2000), default='')
    status: Mapped[str] = mapped_column(String(50), default='open', index=True)
    severity: Mapped[str] = mapped_column(String(20), default='low', index=True)
    source: Mapped[str] = mapped_column(String(30), default='message', index=True)

    project_id: Mapped[str | None] = mapped_column(ForeignKey('projects.id', ondelete='SET NULL'), nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True, index=True)

    project = relationship('Project', back_populates='risks', lazy='selectin')
    task = relationship('Task', back_populates='risks', lazy='selectin')
