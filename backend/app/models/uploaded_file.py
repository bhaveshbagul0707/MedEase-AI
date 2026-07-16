from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FileType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.flashcard import Flashcard
    from app.models.subject import Subject
    from app.models.user import User


class UploadedFile(Base, TimestampMixin):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType, name="file_type", native_enum=False),
        default=FileType.PDF,
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chroma_collection_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="uploaded_files")
    subject: Mapped[Optional["Subject"]] = relationship(back_populates="uploaded_files")
    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="uploaded_file")
