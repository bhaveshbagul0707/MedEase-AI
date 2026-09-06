from typing import Optional
from app.services.providers import get_embedding_provider
from app.services.vector_store import get_vector_store
from app.repositories.base import BaseRepository
from app.models.document_chunk import DocumentChunk

class TutorService:
    def __init__(self, db):
        self.db = db
        self.vector_store = get_vector_store(db)
        self.chunk_repo = BaseRepository(DocumentChunk, db)
        self.embedder = get_embedding_provider()

    async def ask(self, user_id: int, question: str, top_k: int = 3):
        qemb = self.embedder.embed([question])[0]
        results = await self.vector_store.query(qemb, top_k=top_k)
        texts = []
        for r in results:
            cid = r.get("chunk_id")
            if isinstance(cid, int):
                chunk = await self.chunk_repo.get_by_id(cid)
                if chunk and chunk.user_id == user_id:
                    texts.append(chunk.text)
        # simple answer: return concatenated contexts
        answer = "\n\n".join(texts) or "I don't know."
        suggestions = [t[:120] for t in texts[:3]]
        return {"answer": answer, "suggestions": suggestions}
