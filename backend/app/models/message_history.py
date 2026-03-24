from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class MessageHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'message_history'

    channel: Mapped[str] = mapped_column(String(50), index=True)
    recipient: Mapped[str] = mapped_column(String(255), index=True)
    direction: Mapped[str] = mapped_column(String(10), default='out', index=True)
    message_text: Mapped[str] = mapped_column(String(4000))
    external_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

    proactive_rule_id: Mapped[str | None] = mapped_column(ForeignKey('proactive_rules.id', ondelete='SET NULL'), nullable=True, index=True)
