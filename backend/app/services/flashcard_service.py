from __future__ import annotations

from typing import Optional
from datetime import datetime, timezone
from app.repositories.base import BaseRepository
from app.models.flashcard import Flashcard
from app.models.document_chunk import DocumentChunk
from app.models.flashcard_schedule import FlashcardSchedule
from app.repositories.base import BaseRepository


class FlashcardService:
    def __init__(self, db):
        self.db = db
        self.repo = BaseRepository(Flashcard, db)

    async def create(self, user_id: int, front: str, back: str, subject_id: int | None = None, note_id: int | None = None, uploaded_file_id: int | None = None) -> Flashcard:
        fc = Flashcard(user_id=user_id, front=front, back=back, subject_id=subject_id, note_id=note_id, uploaded_file_id=uploaded_file_id)
        await self.repo.create(fc)
        # create initial schedule
        now = datetime.now(timezone.utc)
        sched = FlashcardSchedule(flashcard_id=fc.id, ef=2.5, interval_days=1, repetition=0, next_review_at=now)
        await BaseRepository(FlashcardSchedule, self.db).create(sched)
        return fc

    async def get(self, flashcard_id: int) -> Flashcard | None:
        return await self.repo.get_by_id(flashcard_id)

    async def update(self, flashcard: Flashcard, **fields) -> Flashcard:
        for k, v in fields.items():
            if hasattr(flashcard, k) and v is not None:
                setattr(flashcard, k, v)
        flashcard.updated_at = datetime.utcnow()
        await self.repo.update(flashcard)
        return flashcard

    async def delete(self, flashcard: Flashcard) -> None:
        await self.repo.delete(flashcard)

    async def list_for_user(self, user_id: int, skip: int = 0, limit: int = 20):
        from sqlalchemy import select
        query = select(self.repo.model).where(self.repo.model.user_id == user_id).limit(limit).offset(skip)
        result = await self.db.execute(query)
        rows = result.scalars().all()
        return rows

    async def create_from_chunk(self, user_id: int, chunk: DocumentChunk, subject_id: int | None = None) -> Flashcard:
        # Basic heuristic: first sentence as front, remainder as back. Fall back to truncated text.
        text = (chunk.text or "").strip()
        if not text:
            raise ValueError("Chunk has no text")
        # naive split
        sentences = text.split(".")
        if len(sentences) > 1 and len(sentences[0].strip()) > 20:
            front = sentences[0].strip() + '.'
            back = text[len(front):].strip()
        else:
            # fallback: first 200 chars front, remainder back
            front = text[:200]
            back = text[200:1200] or text
        fc = Flashcard(user_id=user_id, front=front, back=back, subject_id=subject_id, note_id=None, uploaded_file_id=chunk.file_id)
        await self.repo.create(fc)
        now = datetime.now(timezone.utc)
        sched = FlashcardSchedule(flashcard_id=fc.id, ef=2.5, interval_days=1, repetition=0, next_review_at=now)
        await BaseRepository(FlashcardSchedule, self.db).create(sched)
        return fc

    async def review(self, flashcard: Flashcard, correct: bool) -> Flashcard:
        flashcard.last_reviewed_at = datetime.utcnow()
        if correct:
            flashcard.is_learned = True
        else:
            flashcard.is_learned = False
        await self.repo.update(flashcard)
        return flashcard
