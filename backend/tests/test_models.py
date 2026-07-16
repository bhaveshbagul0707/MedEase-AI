import app.models  # noqa: F401
import pytest
from sqlalchemy import create_engine, inspect

from app.db.base import Base

EXPECTED_TABLES = {
    "users",
    "subjects",
    "notes",
    "uploaded_files",
    "flashcards",
    "quizzes",
    "quiz_questions",
    "quiz_results",
    "attendance",
    "exams",
    "study_plans",
    "posts",
    "comments",
    "clinical_cases",
    "clinical_attempts",
    "analytics",
}


def test_all_tables_registered():
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLES


def test_create_all_tables_sqlite():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == EXPECTED_TABLES


def test_user_model_columns():
    columns = {col.name for col in Base.metadata.tables["users"].columns}
    assert "email" in columns
    assert "hashed_password" in columns
    assert "program" in columns
    assert "google_id" in columns


def test_attendance_unique_constraint():
    table = Base.metadata.tables["attendance"]
    constraint_names = {c.name for c in table.constraints if hasattr(c, "name") and c.name}
    assert "uq_attendance_user_subject_date" in constraint_names


def test_foreign_keys_exist():
    notes_table = Base.metadata.tables["notes"]
    fk_targets = {fk.target_fullname for fk in notes_table.foreign_keys}
    assert "users.id" in fk_targets
    assert "subjects.id" in fk_targets
