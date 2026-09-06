from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import DbSession, CurrentUser
from app.services.flashcard_generator import FlashcardGeneratorService
from app.schemas.common import APIResponse
from app.schemas.flashcard import FlashcardResponse

router = APIRouter(prefix="/flashcards/generate", tags=["Flashcards"])


@router.post("/from-note", response_model=APIResponse[list[FlashcardResponse]])
async def generate_from_note(payload: dict, db: DbSession, current_user: CurrentUser):
    note_id = int(payload.get("note_id"))
    count = int(payload.get("count", 5))
    svc = FlashcardGeneratorService(db)
    try:
        created = await svc.generate_from_note(current_user.id, note_id, count=count)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    items = [FlashcardResponse(**c.__dict__) for c in created]
    return APIResponse(message="Flashcards generated", data=items)


@router.post("/from-chunk", response_model=APIResponse[FlashcardResponse])
async def generate_from_chunk(payload: dict, db: DbSession, current_user: CurrentUser):
    chunk_id = int(payload.get("chunk_id"))
    svc = FlashcardGeneratorService(db)
    try:
        fc = await svc.generate_from_chunk(current_user.id, chunk_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return APIResponse(message="Flashcard generated", data=FlashcardResponse(**fc.__dict__))
