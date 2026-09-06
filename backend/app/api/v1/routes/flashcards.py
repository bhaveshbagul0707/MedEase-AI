from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import DbSession, CurrentUser
from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardResponse,
    FlashcardListResponse,
    FlashcardUpdate,
    FlashcardFromChunkRequest,
    FlashcardReviewRequest,
)
from app.services.flashcard_service import FlashcardService
from app.schemas.common import APIResponse, MessageResponse

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


@router.post("/", response_model=APIResponse[FlashcardResponse])
async def create_flashcard(payload: FlashcardCreate, db: DbSession, current_user: CurrentUser):
    svc = FlashcardService(db)
    fc = await svc.create(current_user.id, payload.front, payload.back, subject_id=payload.subject_id, note_id=payload.note_id, uploaded_file_id=payload.uploaded_file_id)
    return APIResponse(message="Flashcard created", data=FlashcardResponse(**fc.__dict__))


@router.post("/from-chunk", response_model=APIResponse[FlashcardResponse])
async def create_from_chunk(payload: FlashcardFromChunkRequest, db: DbSession, current_user: CurrentUser):
    # validate chunk exists and belongs to user
    from app.repositories.base import BaseRepository
    from app.models.document_chunk import DocumentChunk

    repo = BaseRepository(DocumentChunk, db)
    chunk = await repo.get_by_id(payload.chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    if chunk.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    svc = FlashcardService(db)
    fc = await svc.create_from_chunk(current_user.id, chunk, subject_id=payload.subject_id)
    return APIResponse(message="Flashcard created from chunk", data=FlashcardResponse(**fc.__dict__))


@router.get("/", response_model=APIResponse[FlashcardListResponse])
async def list_flashcards(db: DbSession, current_user: CurrentUser, page: int = 1, page_size: int = 20):
    svc = FlashcardService(db)
    skip = (page - 1) * page_size
    rows = await svc.list_for_user(current_user.id, skip=skip, limit=page_size)
    total = await svc.repo.count()
    items = [FlashcardResponse(**r.__dict__) for r in rows]
    return APIResponse(message="Flashcards listed", data=FlashcardListResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/{flashcard_id}", response_model=APIResponse[FlashcardResponse])
async def get_flashcard(flashcard_id: int, db: DbSession, current_user: CurrentUser):
    svc = FlashcardService(db)
    fc = await svc.get(flashcard_id)
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if fc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return APIResponse(message="Flashcard retrieved", data=FlashcardResponse(**fc.__dict__))


@router.put("/{flashcard_id}", response_model=APIResponse[FlashcardResponse])
async def update_flashcard(flashcard_id: int, payload: FlashcardUpdate, db: DbSession, current_user: CurrentUser):
    svc = FlashcardService(db)
    fc = await svc.get(flashcard_id)
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if fc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    updated = await svc.update(fc, **payload.dict())
    return APIResponse(message="Flashcard updated", data=FlashcardResponse(**updated.__dict__))


@router.delete("/{flashcard_id}", response_model=APIResponse[MessageResponse])
async def delete_flashcard(flashcard_id: int, db: DbSession, current_user: CurrentUser):
    svc = FlashcardService(db)
    fc = await svc.get(flashcard_id)
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if fc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await svc.delete(fc)
    return APIResponse(message="Flashcard deleted", data=MessageResponse(message="Deleted"))


@router.post("/{flashcard_id}/review", response_model=APIResponse[FlashcardResponse])
async def review_flashcard(flashcard_id: int, payload: FlashcardReviewRequest, db: DbSession, current_user: CurrentUser):
    svc = FlashcardService(db)
    fc = await svc.get(flashcard_id)
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if fc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    reviewed = await svc.review(fc, payload.correct)
    return APIResponse(message="Flashcard reviewed", data=FlashcardResponse(**reviewed.__dict__))
