from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
import hashlib
import math


class EmbeddingService(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class DummyEmbeddingService(EmbeddingService):
    def __init__(self, dim: int = 128):
        self.dim = dim

    def _text_to_vec(self, text: str) -> List[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [b / 255.0 for b in h]
        # expand/truncate to self.dim
        if len(vec) >= self.dim:
            vec = vec[: self.dim]
        else:
            # repeat pattern
            while len(vec) < self.dim:
                vec += vec
            vec = vec[: self.dim]
        # normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vec(t or "") for t in texts]
