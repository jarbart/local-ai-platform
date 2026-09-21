from functools import lru_cache

from app.embeddings.service import EmbeddingService
from app.llm.ollama import OllamaProvider
from app.retrieval.service import RetrievalService


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        embedding_service=get_embedding_service(),
    )


@lru_cache
def get_llm_provider() -> OllamaProvider:
    return OllamaProvider()