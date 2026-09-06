from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.flashcard import Flashcard


class FlashcardSchedule(Base):
    __tablename__ = "flashcard_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flashcard_id: Mapped[int] = mapped_column(Integer, ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True)
    ef: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    repetition: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Use passive_deletes so SQLAlchemy does not try to nullify the FK before deletion
    flashcard = relationship("Flashcard", back_populates="schedule", passive_deletes=True)
