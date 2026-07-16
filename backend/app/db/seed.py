"""Database seed data for development and testing."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import ClinicalCase, StudentProgram, Subject, User
from app.models.enums import DifficultyLevel

DEFAULT_SUBJECTS = [
    {"name": "Anatomy", "code": "ANAT101", "semester": 1},
    {"name": "Physiology", "code": "PHYS101", "semester": 1},
    {"name": "Biochemistry", "code": "BIOC101", "semester": 1},
    {"name": "Pathology", "code": "PATH201", "semester": 3},
    {"name": "Pharmacology", "code": "PHAR201", "semester": 3},
    {"name": "Microbiology", "code": "MICR201", "semester": 3},
    {"name": "Forensic Medicine", "code": "FMED301", "semester": 5},
    {"name": "Community Medicine", "code": "CMED301", "semester": 5},
    {"name": "General Medicine", "code": "GMED401", "semester": 7},
    {"name": "General Surgery", "code": "GSUR401", "semester": 7},
    {"name": "Obstetrics & Gynecology", "code": "OBGY401", "semester": 7},
    {"name": "Pediatrics", "code": "PEDI401", "semester": 7},
]

SAMPLE_CLINICAL_CASES = [
    {
        "title": "Acute Chest Pain in a 55-Year-Old Male",
        "description": (
            "A 55-year-old male presents to the emergency department with sudden onset "
            "crushing chest pain radiating to the left arm, associated with sweating and nausea. "
            "He has a history of hypertension and smoking."
        ),
        "patient_data": {
            "age": 55,
            "sex": "Male",
            "vitals": {"bp": "160/95", "hr": 110, "rr": 22, "spo2": 94},
            "history": ["Hypertension", "Smoking 20 pack-years"],
        },
        "correct_diagnosis": "Acute Myocardial Infarction (STEMI)",
        "recommended_tests": ["ECG", "Troponin I", "CBC", "Chest X-ray"],
        "recommended_treatment": [
            "Aspirin 325mg",
            "Clopidogrel loading dose",
            "Primary PCI",
            "Heparin",
            "Morphine for pain",
        ],
        "explanation": (
            "Classic presentation of STEMI with crushing chest pain, radiation to left arm, "
            "diaphoresis, and risk factors. ECG will show ST elevation. Immediate reperfusion "
            "therapy is indicated."
        ),
        "difficulty": DifficultyLevel.MEDIUM,
        "specialty": "Cardiology",
    },
    {
        "title": "Fever and Rash in a Child",
        "description": (
            "A 6-year-old girl presents with high-grade fever for 3 days, followed by "
            "appearance of a maculopapular rash starting from the face and spreading downward. "
            "Koplik spots were noted on oral examination."
        ),
        "patient_data": {
            "age": 6,
            "sex": "Female",
            "vitals": {"bp": "90/60", "hr": 120, "temp": "39.5°C"},
            "history": ["Incomplete vaccination"],
        },
        "correct_diagnosis": "Measles (Rubeola)",
        "recommended_tests": ["Clinical diagnosis", "Measles IgM antibody"],
        "recommended_treatment": [
            "Supportive care",
            "Vitamin A supplementation",
            "Isolation",
            "Treat complications",
        ],
        "explanation": (
            "Classic measles presentation: prodromal fever, cough, coryza, conjunctivitis "
            "(3 C's), followed by cephalocaudal rash. Koplik spots are pathognomonic."
        ),
        "difficulty": DifficultyLevel.EASY,
        "specialty": "Pediatrics",
    },
    {
        "title": "Progressive Weakness and Hyperreflexia",
        "description": (
            "A 45-year-old male presents with progressive weakness in both lower limbs over "
            "2 weeks, ascending to upper limbs. Deep tendon reflexes are exaggerated with "
            "bilateral extensor plantar response."
        ),
        "patient_data": {
            "age": 45,
            "sex": "Male",
            "vitals": {"bp": "130/80", "hr": 88, "rr": 18},
            "history": ["Recent upper respiratory tract infection 2 weeks ago"],
        },
        "correct_diagnosis": "Guillain-Barre Syndrome (GBS)",
        "recommended_tests": ["Nerve conduction studies", "CSF analysis", "FVC monitoring"],
        "recommended_treatment": [
            "IV Immunoglobulin (IVIG)",
            "Plasmapheresis",
            "Monitor respiratory function",
            "Physiotherapy",
        ],
        "explanation": (
            "Ascending flaccid paralysis following infection, areflexia progressing to "
            "hyporeflexia then recovery phase. CSF shows albuminocytologic dissociation. "
            "Monitor FVC for respiratory failure."
        ),
        "difficulty": DifficultyLevel.HARD,
        "specialty": "Neurology",
    },
]

DEMO_USER = {
    "email": "demo@medease.ai",
    "password": "Demo@12345",
    "full_name": "Demo Student",
    "program": StudentProgram.MBBS,
    "year_of_study": 2,
}


def seed_subjects(db: Session) -> list[Subject]:
    subjects: list[Subject] = []
    for data in DEFAULT_SUBJECTS:
        existing = db.execute(
            select(Subject).where(Subject.code == data["code"])
        ).scalar_one_or_none()
        if existing:
            subjects.append(existing)
            continue
        subject = Subject(**data, program=StudentProgram.MBBS)
        db.add(subject)
        subjects.append(subject)
    db.flush()
    return subjects


def seed_clinical_cases(db: Session) -> list[ClinicalCase]:
    cases: list[ClinicalCase] = []
    for data in SAMPLE_CLINICAL_CASES:
        existing = db.execute(
            select(ClinicalCase).where(ClinicalCase.title == data["title"])
        ).scalar_one_or_none()
        if existing:
            cases.append(existing)
            continue
        case = ClinicalCase(**data, is_ai_generated=False)
        db.add(case)
        cases.append(case)
    db.flush()
    return cases


def seed_demo_user(db: Session) -> User | None:
    existing = db.execute(select(User).where(User.email == DEMO_USER["email"])).scalar_one_or_none()
    if existing:
        return existing

    user = User(
        email=DEMO_USER["email"],
        hashed_password=get_password_hash(DEMO_USER["password"]),
        full_name=DEMO_USER["full_name"],
        program=DEMO_USER["program"],
        year_of_study=DEMO_USER["year_of_study"],
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.flush()
    return user


def run_seed(db: Session) -> dict[str, int]:
    subjects = seed_subjects(db)
    cases = seed_clinical_cases(db)
    user = seed_demo_user(db)
    db.commit()

    return {
        "subjects": len(subjects),
        "clinical_cases": len(cases),
        "demo_user": 1 if user else 0,
    }


def main() -> None:
    from app.db.sync_session import SyncSessionLocal

    db = SyncSessionLocal()
    try:
        result = run_seed(db)
        print("Seed completed successfully:")
        for key, count in result.items():
            print(f"  {key}: {count}")
        if result.get("demo_user"):
            print(f"\nDemo login: {DEMO_USER['email']} / {DEMO_USER['password']}")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    main()
