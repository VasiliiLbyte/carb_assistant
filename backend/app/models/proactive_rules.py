from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class ProactiveRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'proactive_rules'

    name: Mapped[str] = mapped_column(String(255), unique=True)
    trigger_type: Mapped[str] = mapped_column(String(100), index=True)
    action_type: Mapped[str] = mapped_column(String(100), default='send_message')
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    buttons: Mapped[list] = mapped_column(JSON, default=list)
    enabled: Mapped[bool] = mapped_column(default=True, index=True)
