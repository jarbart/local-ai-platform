from fastapi import APIRouter
from pydantic import BaseModel

from app.embeddings.service import EmbeddingService
from app.llm.ollama import OllamaProvider
from app.retrieval.context import ContextBuilder
from app.retrieval.service import RetrievalService


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

embedding_service = EmbeddingService()

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
)

llm = OllamaProvider()

context_builder = ContextBuilder()


class ChatRequest(BaseModel):
    question: str
    limit: int = 3


@router.post("")
def chat(request: ChatRequest):
    results = retrieval_service.search(
        request.question,
        limit=request.limit,
    )

    context = context_builder.build(results)

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question using only the provided context.

If the context does not contain enough information to answer the question,
say that the information is not available in the provided documents.

Do not invent facts.

Context:
{context}

Question:
{request.question}

Answer:
""".strip()

    answer = llm.generate(prompt)

    sources = [
        {
            "chunk_id": result.get("chunk_id"),
            "document_id": result.get("document_id"),
            "page_number": result.get("page_number"),
            "score": result.get("score"),
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }