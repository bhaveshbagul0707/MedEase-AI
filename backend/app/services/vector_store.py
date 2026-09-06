from __future__ import annotations

from typing import List, Dict, Any
import json
import math
import os
import logging
from app.models.vector_entry import VectorEntry
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class DBVectorStore:
    """Naive DB-backed vector store used as a fallback and for tests."""
    def __init__(self, db):
        self.db = db
        self.repo = BaseRepository(VectorEntry, db)

    async def add(self, chunk_id: int, embedding: List[float], metadata: Dict[str, Any]) -> None:
        e = VectorEntry(chunk_id=chunk_id, embedding=json.dumps(embedding), metadata=json.dumps(metadata))
        await self.repo.create(e)

    async def query(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        # naive in-db scan. Load all vectors and compute cosine similarity.
        from sqlalchemy import select
        stmt = select(self.repo.model)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        candidates = []
        for row in rows:
            emb = json.loads(row.embedding) if row.embedding else []
            if not emb:
                continue
            score = self._cosine_similarity(embedding, emb)
            meta = json.loads(row.metadata_json) if getattr(row, "metadata_json", None) else {}
            candidates.append({"id": row.id, "chunk_id": row.chunk_id, "embedding": emb, "score": score, "metadata": meta})
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        # assume same length
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)


class ChromaVectorStore:
    """Chroma-backed vector store adapter. Falls back if chromadb is not installed."""

    def __init__(self, db, collection_name: str = "default"):
        try:
            import chromadb
            from chromadb.config import Settings
        except Exception as e:
            raise ImportError("chromadb is not available") from e
        # simple chroma client using in-process persistence; real config could use chroma server or persistent dir
        self.collection_name = collection_name
        client = chromadb.Client(Settings())
        self.col = client.get_or_create_collection(name=collection_name)

    async def add(self, chunk_id: int, embedding: List[float], metadata: Dict[str, Any]) -> None:
        # chroma client is sync — keep operations simple
        ids = [str(chunk_id)]
        metadatas = [metadata]
        vectors = [embedding]
        self.col.add(ids=ids, metadatas=metadatas, embeddings=vectors)

    async def query(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        # do not pass an explicit include list — let chroma decide what it supports
        res = self.col.query(query_embeddings=[embedding], n_results=top_k)
        # format results to match DBVectorStore style
        items: List[Dict[str, Any]] = []
        ids_list = res.get('ids', [])
        dists_list = res.get('distances', [])
        metads_list = res.get('metadatas', [])
        # res may be nested lists (one query -> list of lists)
        for ids, dists, metads in zip(ids_list, dists_list, metads_list):
            for _id, dist, meta in zip(ids, dists, metads):
                try:
                    cid = int(_id)
                except Exception:
                    cid = None
                items.append({"id": _id, "chunk_id": cid, "embedding": None, "score": 1.0 - dist, "metadata": meta})
        return items


# Factory to select vector store implementation based on environment

def get_vector_store(db):
    # if CHROMA_ENABLED is set to true, attempt to use Chroma and fallback to DBVectorStore
    enabled = os.getenv("CHROMA_ENABLED", "true").lower() in ("1", "true", "yes")
    if enabled:
        try:
            return ChromaVectorStore(db)
        except ImportError:
            logger.warning("Chroma not available; falling back to DBVectorStore")
    return DBVectorStore(db)
