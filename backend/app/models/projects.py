from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'projects'

    name: Mapped[str] = mapped_column(String(255), index=True)
    project_type: Mapped[str] = mapped_column(String(100), default='general', index=True)
    stage: Mapped[str] = mapped_column(String(100), default='planned', index=True)
    custom_fields: Mapped[dict] = mapped_column(JSON, default=dict)

    tasks = relationship('Task', back_populates='project', lazy='selectin')
    documents = relationship('Document', back_populates='project', lazy='selectin')
    risks = relationship('Risk', back_populates='project', lazy='selectin')
