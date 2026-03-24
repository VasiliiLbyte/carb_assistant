from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class KnowledgeDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'knowledge_documents'

    title: Mapped[str] = mapped_column(String(255), index=True)
    source_type: Mapped[str] = mapped_column(String(50), default='document', index=True)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    version: Mapped[int] = mapped_column(default=1)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    chunks = relationship('KnowledgeChunk', back_populates='document', lazy='selectin', cascade='all, delete-orphan')
