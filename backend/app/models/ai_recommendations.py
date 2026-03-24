from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class AIRecommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'ai_recommendations'

    recommendation_type: Mapped[str] = mapped_column(String(100), index=True)
    rationale: Mapped[str] = mapped_column(String(2000), default='')
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(50), default='proposed', index=True)

    task_id: Mapped[str | None] = mapped_column(ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True, index=True)

    task = relationship('Task', back_populates='recommendations', lazy='selectin')
