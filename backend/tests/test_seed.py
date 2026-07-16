import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core.security import verify_password
from app.db.base import Base
from app.db.seed import run_seed
from app.models import Subject, User


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_seed_populates_data(db_session):
    result = run_seed(db_session)
    assert result["subjects"] == 12
    assert result["clinical_cases"] == 3
    assert result["demo_user"] == 1

    user = db_session.execute(select(User).where(User.email == "demo@medease.ai")).scalar_one()
    assert user.full_name == "Demo Student"
    assert verify_password("Demo@12345", user.hashed_password)


def test_seed_is_idempotent(db_session):
    run_seed(db_session)
    result = run_seed(db_session)
    assert result["subjects"] == 12
    subject_count = db_session.execute(select(Subject)).scalars().all()
    assert len(subject_count) == 12
