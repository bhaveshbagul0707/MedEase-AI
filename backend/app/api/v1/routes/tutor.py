from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import DbSession, CurrentUser
from app.services.tutor_service import TutorService
from app.schemas.common import APIResponse

router = APIRouter(prefix="/tutor", tags=["Tutor"])


@router.post("/ask", response_model=APIResponse[dict])
async def ask_tutor(payload: dict, db: DbSession, current_user: CurrentUser):
    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Missing question")
    svc = TutorService(db)
    result = await svc.ask(current_user.id, question, top_k=payload.get("top_k", 3))
    return APIResponse(message="Tutor reply", data=result)
