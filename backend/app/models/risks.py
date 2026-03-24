from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Risk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = 'risks'

    title: Mapped[str] = mapped_column(String(255), index=True)
    probability: Mapped[int] = mapped_column(Integer, default=1)
    impact: Mapped[int] = mapped_column(Integer, default=1)
    mitigation_plan: Mapped[str] = mapped_column(String(2000), default='')
    status: Mapped[str] = mapped_column(String(50), default='open', index=True)

    project_id: Mapped[str | None] = mapped_column(ForeignKey('projects.id', ondelete='SET NULL'), nullable=True, index=True)

    project = relationship('Project', back_populates='risks', lazy='selectin')
