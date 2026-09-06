from fastapi import APIRouter, Depends
from app.api.deps import DbSession, CurrentUser
from app.services.analytics_service import AnalyticsService
from app.schemas.common import APIResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/study-progress", response_model=APIResponse[dict])
async def study_progress(db: DbSession, current_user: CurrentUser):
    svc = AnalyticsService(db)
    data = await svc.study_progress(current_user.id)
    return APIResponse(message="Study progress", data=data)
