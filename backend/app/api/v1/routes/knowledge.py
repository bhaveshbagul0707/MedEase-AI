from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import DbSession, CurrentUser
from app.services.vector_store import get_vector_store
from app.services.providers import get_embedding_provider
from app.repositories.base import BaseRepository
from app.models.document_chunk import DocumentChunk

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


class ChatRequest(BaseModel):
    question: str
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: str
    sources: list


@router.post("/files/{file_id}/chat", response_model=ChatResponse)
async def chat_file(file_id: int, body: ChatRequest, db: DbSession, current_user: CurrentUser):
    """Chat over a specific uploaded file using RAG."""
    # ensure file exists and belongs to user
    from app.repositories.base import BaseRepository
    from app.models.uploaded_file import UploadedFile
    repo = BaseRepository(UploadedFile, db)
    f = await repo.get_by_id(file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    if f.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    vstore = get_vector_store(db)
    # create embedding for question using configured provider
    embedder = get_embedding_provider()
    qemb = embedder.embed([body.question])[0]
    results = await vstore.query(qemb, top_k=body.top_k)
    sources = []
    answer_parts = []
    chunk_repo = BaseRepository(DocumentChunk, db)
    for r in results:
        chunk = await chunk_repo.get_by_id(r["chunk_id"]) if isinstance(r["chunk_id"], int) else None
        if chunk:
            sources.append({"chunk_id": chunk.id, "page_number": chunk.page_number, "chunk_index": chunk.chunk_index})
            answer_parts.append(chunk.text)
    # Dummy LLM: return concatenation of top chunks prefixed
    answer = "\n\n".join(answer_parts) or "I don't know."
    return ChatResponse(answer=answer, sources=sources)


@router.get("/files/{file_id}/chunks")
async def list_file_chunks(file_id: int, db: DbSession, current_user: CurrentUser):
    from app.repositories.base import BaseRepository
    from app.models.document_chunk import DocumentChunk
    repo = BaseRepository(DocumentChunk, db)
    from sqlalchemy import select
    stmt = select(repo.model).where(repo.model.file_id == file_id).where(repo.model.user_id == current_user.id)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    items = []
    for r in rows:
        items.append({"id": r.id, "page_number": r.page_number, "chunk_index": r.chunk_index, "text_preview": (r.text[:200] + "...") if r.text and len(r.text) > 200 else (r.text or "")})
    return {"items": items, "total": len(items)}
