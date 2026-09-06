from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.clinical import ClinicalAttempt, ClinicalCase
from app.schemas.common import APIResponse

router = APIRouter(prefix="/clinical-cases", tags=["Clinical Cases"])


def serialize(case: ClinicalCase, include_answer: bool = False) -> dict:
    data = {
        "id": case.id, "title": case.title, "description": case.description,
        "patient_data": case.patient_data, "difficulty": case.difficulty,
        "specialty": case.specialty, "recommended_tests": case.recommended_tests,
    }
    if include_answer:
        data.update({
            "correct_diagnosis": case.correct_diagnosis,
            "recommended_treatment": case.recommended_treatment,
            "explanation": case.explanation,
        })
    return data


@router.get("/", response_model=APIResponse[list[dict]])
async def list_cases(db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(ClinicalCase).order_by(ClinicalCase.created_at.desc()))
    return APIResponse(message="Clinical cases listed", data=[serialize(case) for case in result.scalars().all()])


@router.get("/{case_id}", response_model=APIResponse[dict])
async def get_case(case_id: int, db: DbSession, current_user: CurrentUser):
    case = await db.get(ClinicalCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")
    return APIResponse(message="Clinical case retrieved", data=serialize(case))


@router.post("/{case_id}/attempt", response_model=APIResponse[dict])
async def attempt_case(case_id: int, payload: dict, db: DbSession, current_user: CurrentUser):
    case = await db.get(ClinicalCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Clinical case not found")
    diagnosis = str(payload.get("diagnosis", "")).strip()
    if not diagnosis:
        raise HTTPException(status_code=422, detail="Diagnosis is required")
    score = 1.0 if diagnosis.casefold() == case.correct_diagnosis.casefold() else 0.0
    attempt = ClinicalAttempt(
        clinical_case_id=case_id, user_id=current_user.id, diagnosis=diagnosis,
        tests_ordered=payload.get("tests_ordered", []),
        treatment_plan=payload.get("treatment_plan", []), score=score,
        feedback="Correct diagnosis" if score else "Review the case explanation",
    )
    db.add(attempt)
    await db.flush()
    return APIResponse(message="Attempt recorded", data={"id": attempt.id, "score": score, "feedback": attempt.feedback})
