from datetime import date

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.study_plan import StudyPlan
from app.schemas.common import APIResponse

router = APIRouter(prefix="/study-plans", tags=["Study Planner"])


def serialize(plan: StudyPlan) -> dict:
    return {
        "id": plan.id, "title": plan.title, "start_date": plan.start_date,
        "end_date": plan.end_date, "daily_study_hours": plan.daily_study_hours,
        "schedule": plan.schedule, "subject_ids": plan.subject_ids,
        "is_active": plan.is_active,
    }


@router.get("/", response_model=APIResponse[list[dict]])
async def list_plans(db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(StudyPlan).where(StudyPlan.user_id == current_user.id)
        .order_by(StudyPlan.start_date.desc())
    )
    return APIResponse(message="Study plans listed", data=[serialize(item) for item in result.scalars().all()])


@router.post("/", response_model=APIResponse[dict])
async def create_plan(payload: dict, db: DbSession, current_user: CurrentUser):
    try:
        start = date.fromisoformat(payload["start_date"])
        end = date.fromisoformat(payload["end_date"])
        if end < start:
            raise ValueError
        title = str(payload["title"]).strip()
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Valid title, start_date, and end_date are required") from exc
    if not title:
        raise HTTPException(status_code=422, detail="Title is required")
    plan = StudyPlan(
        user_id=current_user.id,
        title=title,
        start_date=start,
        end_date=end,
        daily_study_hours=float(payload.get("daily_study_hours", 4)),
        schedule=payload.get("schedule"),
        subject_ids=payload.get("subject_ids", []),
    )
    db.add(plan)
    await db.flush()
    return APIResponse(message="Study plan created", data=serialize(plan))
