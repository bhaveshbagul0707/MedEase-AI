from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import DbSession, CurrentUser
from app.services.spaced_repetition import SpacedRepetitionService
from app.schemas.common import APIResponse
from app.schemas.flashcard import FlashcardResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/due", response_model=APIResponse[list[FlashcardResponse]])
async def get_due_reviews(db: DbSession, current_user: CurrentUser):
    svc = SpacedRepetitionService(db)
    scheds = await svc.get_due_flashcards(current_user.id)
    # return flashcard objects for each schedule
    items = [FlashcardResponse(**s.flashcard.__dict__) for s in scheds]
    return APIResponse(message="Due flashcards", data=items)


@router.post("/{flashcard_id}/answer", response_model=APIResponse[FlashcardResponse])
async def submit_review(flashcard_id: int, payload: dict, db: DbSession, current_user: CurrentUser):
    # payload expects {'correct': True/False}
    correct = bool(payload.get("correct"))
    svc = SpacedRepetitionService(db)
    # ensure ownership
    fc = await svc.fc_repo.get_by_id(flashcard_id)
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if fc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    sched = await svc.record_review(flashcard_id, correct)
    # also append review history
    from app.models.flashcard_review import FlashcardReview
    from app.repositories.base import BaseRepository
    import datetime
    review = FlashcardReview(flashcard_id=flashcard_id, correct=correct, notes=None, reviewed_at=datetime.datetime.utcnow())
    await BaseRepository(FlashcardReview, db).create(review)
    await db.flush()
    # return updated flashcard
    updated = await svc.fc_repo.get_by_id(flashcard_id)
    return APIResponse(message="Review recorded", data=FlashcardResponse(**updated.__dict__))
