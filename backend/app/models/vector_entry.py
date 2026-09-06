from __future__ import annotations

from datetime import datetime
import json
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class VectorEntry(Base):
    __tablename__ = "vector_entries"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=False, index=True)
    embedding = Column(Text, nullable=False)  # JSON list of floats
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunk = relationship("DocumentChunk", backref="vector")
