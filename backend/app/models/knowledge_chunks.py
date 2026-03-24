from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class KnowledgeChunk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'knowledge_chunks'

    knowledge_document_id: Mapped[str] = mapped_column(ForeignKey('knowledge_documents.id', ondelete='CASCADE'), index=True)
    chunk_text: Mapped[str] = mapped_column(String(4000))
    embedding_ref: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    document = relationship('KnowledgeDocument', back_populates='chunks', lazy='selectin')
