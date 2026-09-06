from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class FlashcardCreate(BaseModel):
    front: str
    back: str
    subject_id: Optional[int] = None
    note_id: Optional[int] = None
    uploaded_file_id: Optional[int] = None


class FlashcardFromChunkRequest(BaseModel):
    chunk_id: int
    subject_id: Optional[int] = None


class FlashcardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    is_learned: Optional[bool] = None


class FlashcardResponse(BaseModel):
    id: int
    user_id: int
    subject_id: Optional[int]
    note_id: Optional[int]
    uploaded_file_id: Optional[int]
    front: str
    back: str
    is_learned: bool
    last_reviewed_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class FlashcardListResponse(BaseModel):
    items: list[FlashcardResponse]
    total: int
    page: int
    page_size: int


class FlashcardReviewRequest(BaseModel):
    correct: bool
