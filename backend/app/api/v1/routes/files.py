from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Response
from fastapi.params import Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import DbSession, CurrentUser
from app.schemas.common import APIResponse, PaginatedResponse, PaginationParams, MessageResponse
from app.schemas.file import UploadedFileResponse
from app.services.file_service import FileService
from app.services.storage_service import UploadTooLargeError

router = APIRouter(prefix="/files", tags=["Files"])


def _file_service(db: AsyncSession) -> FileService:
    return FileService(db)


def _file_to_response(f) -> UploadedFileResponse:
    download_url = f"/api/v1/files/{f.id}/download"
    data = {
        "id": f.id,
        "user_id": f.user_id,
        "subject_id": f.subject_id,
        "filename": f.filename,
        "download_url": download_url,
        "file_size": f.file_size,
        "page_count": f.page_count,
        "status": f.status,
        "mime_type": f.mime_type,
        "checksum_sha256": f.checksum_sha256,
        "uploaded_at": f.uploaded_at,
        "processed_at": f.processed_at,
        "processing_error": f.processing_error,
    }
    return UploadedFileResponse.model_validate(data)


@router.post("/upload", response_model=APIResponse[UploadedFileResponse])
async def upload_file(
    db: DbSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    subject_id: int | None = Form(None),
):

    # Basic checks
    content_type = file.content_type
    # Enforce allowed types via FileService/config
    try:
        created, created_new = await _file_service(db).create_from_upload(current_user.id, file.filename, file.file, subject_id=subject_id, mime_type=content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except UploadTooLargeError:
        raise HTTPException(status_code=413, detail="Uploaded file is too large")
    # If duplicate (created_new == False), return existing resource
    if not created_new:
        return APIResponse(message="File already exists", data=_file_to_response(created))
    return APIResponse(message="File uploaded", data=_file_to_response(created))


@router.get("/", response_model=APIResponse[PaginatedResponse[UploadedFileResponse]])
async def list_files(db: DbSession, current_user: CurrentUser, page: int = 1, page_size: int = 20):
    # Simple listing via BaseRepository - implement pagination
    repo = _file_service(db).repo
    from sqlalchemy import select
    stmt = select(repo.model).where(repo.model.user_id == current_user.id).order_by(repo.model.created_at.desc()).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    # total count
    total = await repo.count()
    return APIResponse(message="Files listed", data=PaginatedResponse[UploadedFileResponse](items=[_file_to_response(r) for r in rows], total=total, page=page, page_size=page_size, total_pages=(total + page_size - 1) // page_size))


@router.get("/{file_id}", response_model=APIResponse[UploadedFileResponse])
async def get_file(file_id: int, db: DbSession, current_user: CurrentUser):
    repo = _file_service(db).repo
    file = await repo.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return APIResponse(message="File retrieved", data=_file_to_response(file))


@router.delete("/{file_id}", response_model=APIResponse[MessageResponse])
async def delete_file(file_id: int, db: DbSession, current_user: CurrentUser):
    repo = _file_service(db).repo
    file = await repo.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # Soft-delete: mark as DELETED and enqueue cleanup
    file.status = "DELETED"
    await db.flush()
    try:
        await _file_service(db).enqueue_cleanup(file.id)
    except Exception:
        # If enqueue fails, log and continue
        pass
    return APIResponse(message="File deletion initiated", data=MessageResponse(message="Delete scheduled"))


@router.get("/{file_id}/download")
async def download_file(file_id: int, db: DbSession, current_user: CurrentUser):
    repo = _file_service(db).repo
    file = await repo.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not file.storage_path:
        raise HTTPException(status_code=404, detail="File not available")
    # Stream file from storage
    try:
        # use storage to open path
        p = file.storage_path
        from fastapi.responses import StreamingResponse
        def iterfile():
            with open(p, "rb") as fh:
                while True:
                    chunk = fh.read(8192)
                    if not chunk:
                        break
                    yield chunk
        return StreamingResponse(iterfile(), media_type=file.mime_type or "application/octet-stream")
    except Exception:
        raise HTTPException(status_code=500, detail="Error streaming file")
