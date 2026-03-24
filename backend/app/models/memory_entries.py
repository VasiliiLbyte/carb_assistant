from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class MemoryEntry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'memory_entries'

    scope_type: Mapped[str] = mapped_column(String(50), index=True)
    scope_id: Mapped[str] = mapped_column(String(100), index=True)
    memory_type: Mapped[str] = mapped_column(String(50), default='short_term', index=True)
    content: Mapped[str] = mapped_column(String(4000))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
