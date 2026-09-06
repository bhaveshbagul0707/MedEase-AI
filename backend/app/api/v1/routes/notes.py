from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from app.api.deps import DbSession, CurrentUser
from app.schemas.note import NoteCreate, NoteResponse, NoteListResponse, NoteUpdate
from app.services.note_service import NoteService
from app.schemas.common import APIResponse, MessageResponse

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/", response_model=APIResponse[NoteResponse])
async def create_note(payload: NoteCreate, db: DbSession, current_user: CurrentUser):
    svc = NoteService(db)
    # If chunk_id provided ensure chunk exists and belongs to user
    if payload.chunk_id:
        from app.repositories.base import BaseRepository
        from app.models.document_chunk import DocumentChunk
        repo = BaseRepository(DocumentChunk, db)
        chunk = await repo.get_by_id(payload.chunk_id)
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        if chunk.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    note = await svc.create(current_user.id, payload.title, payload.content, subject_id=payload.subject_id, file_id=payload.file_id, chunk_id=payload.chunk_id, tags=payload.tags)
    return APIResponse(message="Note created", data=NoteResponse(**note.__dict__))


@router.get("/", response_model=APIResponse[NoteListResponse])
async def list_notes(db: DbSession, current_user: CurrentUser, page: int = 1, page_size: int = 20):
    svc = NoteService(db)
    skip = (page - 1) * page_size
    rows = await svc.list_for_user(current_user.id, skip=skip, limit=page_size)
    total = (
        await db.execute(
            select(func.count()).select_from(svc.repo.model).where(
                svc.repo.model.user_id == current_user.id
            )
        )
    ).scalar_one()
    items = [NoteResponse(**r.__dict__) for r in rows]
    return APIResponse(message="Notes listed", data=NoteListResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/{note_id}", response_model=APIResponse[NoteResponse])
async def get_note(note_id: int, db: DbSession, current_user: CurrentUser):
    svc = NoteService(db)
    note = await svc.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return APIResponse(message="Note retrieved", data=NoteResponse(**note.__dict__))


@router.put("/{note_id}", response_model=APIResponse[NoteResponse])
async def update_note(note_id: int, payload: NoteUpdate, db: DbSession, current_user: CurrentUser):
    svc = NoteService(db)
    note = await svc.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    updated = await svc.update(note, **payload.dict())
    return APIResponse(message="Note updated", data=NoteResponse(**updated.__dict__))


@router.delete("/{note_id}", response_model=APIResponse[MessageResponse])
async def delete_note(note_id: int, db: DbSession, current_user: CurrentUser):
    svc = NoteService(db)
    note = await svc.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await svc.delete(note)
    return APIResponse(message="Note deleted", data=MessageResponse(message="Deleted"))
