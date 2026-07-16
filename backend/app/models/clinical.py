from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import JsonType
from app.models.enums import DifficultyLevel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ClinicalCase(Base, TimestampMixin):
    __tablename__ = "clinical_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    patient_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JsonType, nullable=True)
    correct_diagnosis: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_tests: Mapped[Optional[list[Any]]] = mapped_column(JsonType, nullable=True)
    recommended_treatment: Mapped[Optional[list[Any]]] = mapped_column(JsonType, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="clinical_difficulty", native_enum=False),
        nullable=False,
    )
    specialty: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    attempts: Mapped[List["ClinicalAttempt"]] = relationship(
        back_populates="clinical_case", cascade="all, delete-orphan"
    )


class ClinicalAttempt(Base, TimestampMixin):
    __tablename__ = "clinical_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clinical_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clinical_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)
    tests_ordered: Mapped[Optional[list[Any]]] = mapped_column(JsonType, nullable=True)
    treatment_plan: Mapped[Optional[list[Any]]] = mapped_column(JsonType, nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_evaluation: Mapped[Optional[dict[str, Any]]] = mapped_column(JsonType, nullable=True)

    clinical_case: Mapped["ClinicalCase"] = relationship(back_populates="attempts")
    user: Mapped["User"] = relationship(back_populates="clinical_attempts")
