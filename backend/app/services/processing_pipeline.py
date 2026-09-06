from __future__ import annotations

from typing import List
from datetime import datetime, timezone

from app.services.text_extractor import extract_text_pages_from_pdf
from app.services.providers import get_embedding_provider
from app.services.vector_store import get_vector_store
from app.models.document_chunk import DocumentChunk
from app.repositories.base import BaseRepository


class ProcessingPipeline:
    def __init__(self, db, embedding_service=None):
        self.db = db
        self.chunk_repo = BaseRepository(DocumentChunk, db)
        # embedding_service may be passed for tests; otherwise use configured provider
        self.embedding = embedding_service or get_embedding_provider()
        self.vstore = get_vector_store(db)

    async def process_uploaded_file(self, uploaded_file) -> None:
        # extract pages
        pages = extract_text_pages_from_pdf(uploaded_file.storage_path)
        chunks = []
        # simple chunker: 1000 chars with 200 overlap
        chunk_size = 1000
        overlap = 200
        for pnum, page_text in enumerate(pages, start=1):
            if not page_text:
                continue
            start = 0
            idx = 0
            while start < len(page_text):
                end = min(start + chunk_size, len(page_text))
                chunk_text = page_text[start:end]
                # create chunk
                chunk = DocumentChunk(file_id=uploaded_file.id, user_id=uploaded_file.user_id, page_number=pnum, chunk_index=idx, text=chunk_text)
                await self.chunk_repo.create(chunk)
                chunks.append(chunk)
                idx += 1
                if end == len(page_text):
                    break
                start = end - overlap

        # embed chunks in batches
        texts = [c.text for c in chunks]
        if texts:
            embeddings = self.embedding.embed(texts)
            for c, emb in zip(chunks, embeddings):
                meta = {"user_id": c.user_id, "file_id": c.file_id, "page_number": c.page_number, "chunk_index": c.chunk_index}
                await self.vstore.add(c.id, emb, meta)

        # mark uploaded_file processed
        uploaded_file.processed_at = datetime.now(timezone.utc)
        uploaded_file.status = "READY"
        await self.db.flush()
