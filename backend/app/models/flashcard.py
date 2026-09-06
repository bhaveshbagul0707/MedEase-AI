from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.note import Note
    from app.models.subject import Subject
    from app.models.uploaded_file import UploadedFile
    from app.models.user import User


class Flashcard(Base, TimestampMixin):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    note_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("notes.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_file_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("uploaded_files.id", ondelete="SET NULL"), nullable=True
    )
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    is_learned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="flashcards")
    subject: Mapped[Optional["Subject"]] = relationship(back_populates="flashcards")
    note: Mapped[Optional["Note"]] = relationship(back_populates="flashcards")
    uploaded_file: Mapped[Optional["UploadedFile"]] = relationship(back_populates="flashcards")

    # One-to-one schedule
    # Cascade deletions to the schedule and let DB handle ON DELETE CASCADE where possible
    schedule = relationship(
        "FlashcardSchedule",
        back_populates="flashcard",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # review history
    reviews: Mapped[list["FlashcardReview"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
