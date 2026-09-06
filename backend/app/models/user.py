from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import StudentProgram
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.analytics import Analytics
    from app.models.attendance import Attendance
    from app.models.clinical import ClinicalAttempt
    from app.models.community import Comment, Post
    from app.models.exam import Exam
    from app.models.flashcard import Flashcard
    from app.models.note import Note
    from app.models.quiz import Quiz, QuizResult
    from app.models.study_plan import StudyPlan
    from app.models.uploaded_file import UploadedFile


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    program: Mapped[StudentProgram] = mapped_column(
        Enum(StudentProgram, name="student_program", native_enum=False),
        nullable=False,
    )
    year_of_study: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Email verification
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_verification_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Account lock and failed login tracking
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    notes: Mapped[List["Note"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    uploaded_files: Mapped[List["UploadedFile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    flashcards: Mapped[List["Flashcard"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quiz_results: Mapped[List["QuizResult"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    attendance_records: Mapped[List["Attendance"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    exams: Mapped[List["Exam"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    study_plans: Mapped[List["StudyPlan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    posts: Mapped[List["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    clinical_attempts: Mapped[List["ClinicalAttempt"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    analytics_events: Mapped[List["Analytics"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Refresh tokens for session management (jti-based)
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    # Audit entries relationship
    auth_audit_entries: Mapped[List["AuthAudit"]] = relationship(
        "AuthAudit", back_populates="user", cascade="all, delete-orphan"
    )
