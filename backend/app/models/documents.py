from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'documents'

    name: Mapped[str] = mapped_column(String(255), index=True)
    object_key: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    project_id: Mapped[str | None] = mapped_column(ForeignKey('projects.id', ondelete='SET NULL'), nullable=True, index=True)

    project = relationship('Project', back_populates='documents', lazy='selectin')
    versions = relationship('DocumentVersion', back_populates='document', lazy='selectin', cascade='all, delete-orphan')
