from datetime import date
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import JsonType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class StudyPlan(Base, TimestampMixin):
    __tablename__ = "study_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    daily_study_hours: Mapped[float] = mapped_column(Float, nullable=False, default=4.0)
    schedule: Mapped[Optional[dict[str, Any]]] = mapped_column(JsonType, nullable=True)
    subject_ids: Mapped[Optional[List[int]]] = mapped_column(JsonType, nullable=True, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="study_plans")
