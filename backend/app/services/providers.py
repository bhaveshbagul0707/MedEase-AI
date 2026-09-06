from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import List, Optional

from .embedding_service import DummyEmbeddingService


# LLM provider interfaces and basic mock/scaffold implementations
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def batch_generate(self, prompts: list[str], **kwargs) -> list[str]:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def generate(self, prompt: str, **kwargs) -> str:
        return f"MOCK_ANSWER: {prompt[:200]}"

    def batch_generate(self, prompts: list[str], **kwargs) -> list[str]:
        return [self.generate(p, **kwargs) for p in prompts]


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("OpenAIProvider.generate not implemented in scaffold")

    def batch_generate(self, prompts: list[str], **kwargs) -> list[str]:
        raise NotImplementedError("OpenAIProvider.batch_generate not implemented in scaffold")


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("AnthropicProvider.generate not implemented in scaffold")

    def batch_generate(self, prompts: list[str], **kwargs) -> list[str]:
        raise NotImplementedError("AnthropicProvider.batch_generate not implemented in scaffold")


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("GeminiProvider.generate not implemented in scaffold")

    def batch_generate(self, prompts: list[str], **kwargs) -> list[str]:
        raise NotImplementedError("GeminiProvider.batch_generate not implemented in scaffold")


# Embedding provider interface and implementations
class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dim: int = 128):
        # reuse existing DummyEmbeddingService for deterministic embeddings
        self._impl = DummyEmbeddingService(dim=dim)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self._impl.embed(texts)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("OpenAIEmbeddingProvider.embed not implemented in scaffold")


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("GeminiEmbeddingProvider.embed not implemented in scaffold")


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("SentenceTransformerEmbeddingProvider.embed not implemented in scaffold")


# Provider factory functions: read configuration from environment
def get_llm_provider() -> LLMProvider:
    name = os.getenv("LLM_PROVIDER", "mock").lower()
    api_key = os.getenv("LLM_API_KEY")
    if name == "openai":
        return OpenAIProvider(api_key=api_key)
    if name == "anthropic":
        return AnthropicProvider(api_key=api_key)
    if name == "gemini":
        return GeminiProvider(api_key=api_key)
    # default: mock
    return MockLLMProvider()


def get_embedding_provider() -> EmbeddingProvider:
    name = os.getenv("EMBEDDING_PROVIDER", "mock").lower()
    api_key = os.getenv("EMBEDDING_API_KEY")
    if name == "openai":
        return OpenAIEmbeddingProvider(api_key=api_key)
    if name == "gemini":
        return GeminiEmbeddingProvider(api_key=api_key)
    if name == "sentence_transformer":
        return SentenceTransformerEmbeddingProvider()
    return MockEmbeddingProvider()
