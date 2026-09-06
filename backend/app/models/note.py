from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import JsonType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.community import Post
    from app.models.flashcard import Flashcard
    from app.models.subject import Subject
    from app.models.user import User


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags: Mapped[Optional[list[Any]]] = mapped_column(JsonType, nullable=True, default=list)

    # Optional link to uploaded file and document chunk
    file_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("uploaded_files.id", ondelete="SET NULL"), nullable=True, index=True)
    chunk_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True, index=True)

    user: Mapped["User"] = relationship(back_populates="notes")
    subject: Mapped[Optional["Subject"]] = relationship(back_populates="notes")
    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="note")
    shared_posts: Mapped[List["Post"]] = relationship(back_populates="shared_note")
    file = relationship("UploadedFile", backref="notes")
    chunk = relationship("DocumentChunk", backref="notes")
