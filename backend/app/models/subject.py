from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import StudentProgram
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.exam import Exam
    from app.models.flashcard import Flashcard
    from app.models.note import Note
    from app.models.quiz import Quiz
    from app.models.uploaded_file import UploadedFile


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    program: Mapped[Optional[StudentProgram]] = mapped_column(
        Enum(StudentProgram, name="subject_program", native_enum=False),
        nullable=True,
    )
    semester: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    notes: Mapped[List["Note"]] = relationship(back_populates="subject")
    uploaded_files: Mapped[List["UploadedFile"]] = relationship(back_populates="subject")
    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="subject")
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="subject")
    attendance_records: Mapped[List["Attendance"]] = relationship(back_populates="subject")
    exams: Mapped[List["Exam"]] = relationship(back_populates="subject")
