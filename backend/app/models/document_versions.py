from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class DocumentVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'document_versions'

    document_id: Mapped[str] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    object_key: Mapped[str] = mapped_column(String(500), index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    document = relationship('Document', back_populates='versions', lazy='selectin')
