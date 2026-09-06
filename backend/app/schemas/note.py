from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class NoteCreate(BaseModel):
    title: str
    content: str
    subject_id: Optional[int] = None
    file_id: Optional[int] = None
    chunk_id: Optional[int] = None
    tags: Optional[List[str]] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_shared: Optional[bool] = None
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    id: int
    user_id: int
    subject_id: Optional[int]
    file_id: Optional[int]
    chunk_id: Optional[int]
    title: str
    content: str
    is_shared: bool
    tags: Optional[List[str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int
    page: int
    page_size: int
