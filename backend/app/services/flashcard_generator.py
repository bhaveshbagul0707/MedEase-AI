from typing import Optional
from app.repositories.base import BaseRepository
from app.models.note import Note
from app.models.document_chunk import DocumentChunk
from app.models.flashcard import Flashcard
from app.repositories.base import BaseRepository
from app.services.flashcard_service import FlashcardService
from app.services.providers import get_llm_provider

class FlashcardGeneratorService:
    def __init__(self, db, llm_provider=None):
        self.db = db
        self.note_repo = BaseRepository(Note, db)
        self.chunk_repo = BaseRepository(DocumentChunk, db)
        self.fc_service = FlashcardService(db)
        # allow injection for tests; otherwise use configured provider
        self.llm = llm_provider or get_llm_provider()

    async def generate_from_note(self, user_id: int, note_id: int, count: int = 5):
        note = await self.note_repo.get_by_id(note_id)
        if not note or note.user_id != user_id:
            raise ValueError("Note not found or forbidden")
        # naive: split note content into sentences and produce flashcards
        text = (note.content or "").strip()
        parts = [s.strip() for s in text.split('.') if s.strip()]
        created = []
        for i, p in enumerate(parts[:count]):
            front = (p[:120] + '...') if len(p) > 120 else p
            back = ''
            # attempt to find next sentence as back
            if i + 1 < len(parts):
                back = parts[i+1]
            else:
                # fallback to asking the LLM for a concise summary if available
                try:
                    back = self.llm.generate(f"Summarize the following text into one sentence: {p}")
                except Exception:
                    back = p
            fc = await self.fc_service.create(user_id=user_id, front=front, back=back, note_id=note_id)
            created.append(fc)
        return created

    async def generate_from_chunk(self, user_id: int, chunk_id: int):
        chunk = await self.chunk_repo.get_by_id(chunk_id)
        if not chunk or chunk.user_id != user_id:
            raise ValueError("Chunk not found or forbidden")
        text = (chunk.text or "").strip()
        if not text:
            raise ValueError("Empty chunk")
        # simple heuristic: use LLM to produce improved front/back when available
        try:
            front = self.llm.generate(f"Create a concise flashcard question from: {text[:400]}")
            back = self.llm.generate(f"Create a concise answer for: {text[:400]}")
        except Exception:
            front = text.split('\n')[0][:200]
            back = text[200:600] or text
        fc = await self.fc_service.create(user_id=user_id, front=front, back=back, uploaded_file_id=chunk.file_id)
        return fc
