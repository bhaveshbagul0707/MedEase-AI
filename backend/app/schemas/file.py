from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict

from app.schemas.common import BaseSchema


class UploadedFileResponse(BaseSchema):
    id: int
    user_id: int
    subject_id: Optional[int]
    filename: str
    download_url: Optional[str]
    file_size: int
    page_count: Optional[int]
    status: Optional[str]
    mime_type: Optional[str]
    checksum_sha256: Optional[str]
    uploaded_at: Optional[datetime]
    processed_at: Optional[datetime]
    processing_error: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseSchema):
    message: str
    data: UploadedFileResponse


class UploadListResponse(BaseSchema):
    items: list[UploadedFileResponse]
    total: int
    page: int
    page_size: int
