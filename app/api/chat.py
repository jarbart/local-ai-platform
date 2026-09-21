from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.dependencies import (
    get_llm_provider,
    get_retrieval_service,
)
from app.retrieval.context import ContextBuilder


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

context_builder = ContextBuilder()


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )
    limit: int = Field(
        default=3,
        ge=1,
        le=10,
    )


@router.post("")
def chat(request: ChatRequest):
    retrieval_service = get_retrieval_service()
    llm = get_llm_provider()

    results = retrieval_service.search(
        request.question,
        limit=request.limit,
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No relevant information was found in the indexed documents.",
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
            "filename": result.get("filename"),
            "page_number": result.get("page_number"),
            "score": result.get("score"),
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }