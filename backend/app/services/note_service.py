from __future__ import annotations

from typing import Optional
from app.repositories.base import BaseRepository
from app.models.note import Note
from datetime import datetime


class NoteService:
    def __init__(self, db):
        self.db = db
        self.repo = BaseRepository(Note, db)

    async def create(self, user_id: int, title: str, content: str, subject_id: int | None = None, file_id: int | None = None, chunk_id: int | None = None, tags: list | None = None) -> Note:
        note = Note(user_id=user_id, title=title, content=content, subject_id=subject_id, file_id=file_id, chunk_id=chunk_id, tags=tags or [])
        await self.repo.create(note)
        return note

    async def get(self, note_id: int) -> Note | None:
        return await self.repo.get_by_id(note_id)

    async def update(self, note: Note, **fields) -> Note:
        for k, v in fields.items():
            if hasattr(note, k) and v is not None:
                setattr(note, k, v)
        note.updated_at = datetime.utcnow()
        await self.repo.update(note)
        return note

    async def delete(self, note: Note) -> None:
        await self.repo.delete(note)

    async def list_for_user(self, user_id: int, skip: int = 0, limit: int = 20):
        query = self.repo.model.__table__.select().where(self.repo.model.user_id == user_id).limit(limit).offset(skip)
        result = await self.db.execute(query)
        rows = result.scalars().all()
        return rows

    async def search(self, user_id: int, q: str, skip: int = 0, limit: int = 20):
        # simple SQL LIKE search on title/content
        stmt = self.repo.model.__table__.select().where(self.repo.model.user_id == user_id).where((self.repo.model.title.ilike(f"%{q}%")) | (self.repo.model.content.ilike(f"%{q}%"))).limit(limit).offset(skip)
        result = await self.db.execute(stmt)
        return result.scalars().all()
