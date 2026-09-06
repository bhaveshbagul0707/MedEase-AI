from datetime import date

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.attendance import Attendance
from app.schemas.common import APIResponse

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/", response_model=APIResponse[list[dict]])
async def list_attendance(db: DbSession, current_user: CurrentUser):
    result = await db.execute(
        select(Attendance)
        .where(Attendance.user_id == current_user.id)
        .order_by(Attendance.date.desc())
    )
    return APIResponse(
        message="Attendance listed",
        data=[
            {"id": row.id, "subject_id": row.subject_id, "date": row.date,
             "status": row.status, "notes": row.notes}
            for row in result.scalars().all()
        ],
    )


@router.post("/", response_model=APIResponse[dict])
async def record_attendance(payload: dict, db: DbSession, current_user: CurrentUser):
    try:
        record_date = date.fromisoformat(payload["date"])
        subject_id = int(payload["subject_id"])
        status = str(payload["status"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="date, subject_id, and status are required") from exc
    if status not in {"Present", "Absent", "Excused"}:
        raise HTTPException(status_code=422, detail="Invalid attendance status")
    record = Attendance(
        user_id=current_user.id,
        subject_id=subject_id,
        date=record_date,
        status=status,
        notes=payload.get("notes"),
    )
    db.add(record)
    await db.flush()
    return APIResponse(message="Attendance recorded", data={"id": record.id})
