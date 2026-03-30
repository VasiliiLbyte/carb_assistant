"""SQLAlchemy model: User."""

from __future__ import annotations

from sqlalchemy import Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default='viewer', index=True)
    competency: Mapped[float] = mapped_column(Float, default=0.0)
    load: Mapped[int] = mapped_column(Integer, default=0)
    skills: Mapped[dict] = mapped_column(JSON, default=dict)
    notification_settings: Mapped[dict] = mapped_column(JSON, default=dict)
    workload_profile: Mapped[dict] = mapped_column(JSON, default=dict)

    assigned_tasks = relationship('Task', back_populates='assignee', lazy='selectin')
