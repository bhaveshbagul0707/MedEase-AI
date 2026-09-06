from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import BinaryIO

from pypdf import PdfReader

from app.core.config import get_settings
from app.models.uploaded_file import UploadedFile
from app.repositories.base import BaseRepository
from app.services.storage_service import LocalStorageService, StorageService
from app.services.processing_queue import InProcessQueue, ProcessingQueue


class FileService:
    def __init__(self, db, storage: StorageService | None = None, queue: ProcessingQueue | None = None):
        self.db = db
        self.repo = BaseRepository(UploadedFile, db)
        self.settings = get_settings()
        self.storage = storage or LocalStorageService()
        self.queue = queue or InProcessQueue()

    async def create_from_upload(self, user_id: int, filename: str, stream: BinaryIO, *, subject_id: int | None = None, mime_type: str | None = None) -> tuple[UploadedFile, bool]:
        # Basic validation
        if mime_type and mime_type not in self.settings.allowed_mime_types:
            raise ValueError("Unsupported file type")

        # Save via storage service (streaming)
        meta = self.storage.save(user_id, filename, stream)
        storage_path = meta.get("storage_path")
        file_url = meta.get("file_url")
        file_size = meta.get("file_size", 0)
        checksum = meta.get("checksum_sha256")

        # Duplicate detection: check existing file with same checksum for this user (excluding deleted)
        try:
            from sqlalchemy import select
            result = await self.db.execute(
                select(self.repo.model).where(
                    self.repo.model.checksum_sha256 == checksum,
                    self.repo.model.user_id == user_id,
                    self.repo.model.status != "DELETED",
                )
            )
            existing = result.scalars().first()
            if existing:
                # remove the just-saved file
                try:
                    if storage_path:
                        self.storage.delete(storage_path)
                except Exception:
                    pass
                return existing, False
        except Exception:
            # if any DB error, proceed to create new record
            existing = None

        # Attempt to compute page_count if PDF
        page_count = None
        try:
            # open saved file and read via pypdf
            with open(storage_path, "rb") as fh:
                reader = PdfReader(fh)
                page_count = len(reader.pages)
        except Exception:
            # ignore here; processing will handle parsing for OCR/etc
            page_count = None

        uploaded = UploadedFile(
            user_id=user_id,
            subject_id=subject_id,
            filename=filename,
            file_url=file_url,
            file_size=file_size,
            file_type=None,
            page_count=page_count,
            status="PENDING",
            storage_path=storage_path,
            mime_type=mime_type,
            checksum_sha256=checksum,
            uploaded_at=datetime.now(timezone.utc),
        )
        await self.repo.create(uploaded)

        # Enqueue background processing, pass current DB session so processing runs inline with same session
        await self.queue.enqueue(self._process_file, uploaded.id, session=self.db)

        return uploaded, True

    async def _process_file(self, uploaded_file_id: int, session) -> None:
        """Process the uploaded file using the provided AsyncSession.
        When the queue is running inline in tests or requests, the session will be the same request-scoped session.
        If run as a background task (no session passed), this won't be called inline; a background runner should
        create its own session (not implemented for InProcessQueue inline path)."""
        from app.models.uploaded_file import UploadedFile
        # Use the provided session to update the DB record
        repo = BaseRepository(UploadedFile, session)
        file = await repo.get_by_id(uploaded_file_id)
        if not file:
            return
        file.status = "PROCESSING"
        await session.flush()
        try:
            # Run the full processing pipeline
            from app.services.processing_pipeline import ProcessingPipeline
            pipeline = ProcessingPipeline(session)
            await pipeline.process_uploaded_file(file)
            # pipeline will set processed_at and status
        except Exception as exc:
            file.status = "FAILED"
            file.processing_error = str(exc)
            await session.flush()

    async def enqueue_cleanup(self, uploaded_file_id: int) -> None:
        """Enqueue a background cleanup job to remove vectors and storage for a deleted file.
        Do not run inline — schedule background purge so delete handler can return DELETED immediately."""
        await self.queue.enqueue(self._cleanup_file_background, uploaded_file_id)

    async def _cleanup_file(self, uploaded_file_id: int, session) -> None:
        from app.models.uploaded_file import UploadedFile
        repo = BaseRepository(UploadedFile, session)
        file = await repo.get_by_id(uploaded_file_id)
        if not file:
            return
        # Attempt to remove vectors associated with file (placeholder)
        # TODO: integrate with vector DB to remove vectors by metadata {file_id}
        # Remove storage
        try:
            if file.storage_path:
                self.storage.delete(file.storage_path)
        except Exception:
            pass
        # Mark as PURGED
        file.status = "PURGED"
        await session.flush()

    def _cleanup_file_background(self, uploaded_file_id: int) -> None:
        """Background runner that creates its own session. This will run on the app's default DB engine.
        In tests the background engine may be different from the test's ephemeral engine; that may produce errors
        in the background task, which are logged but do not affect the immediate delete response."""
        from app.db.session import AsyncSessionLocal
        import asyncio

        async def _run():
            async with AsyncSessionLocal() as session:
                await self._cleanup_file(uploaded_file_id, session)
        try:
            asyncio.create_task(_run())
        except Exception:
            try:
                import asyncio as _asyncio
                _asyncio.get_event_loop().run_until_complete(_run())
            except Exception:
                pass
