from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.models import ChatResponse
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


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    retrieval_service = get_retrieval_service()
    llm = get_llm_provider()

    results = retrieval_service.search(
        request.question,
        limit=request.limit,
    )

    if not results:
        return {
            "answer": (
                "Informacja nie jest dostępna w dostarczonych "
                "dokumentach."
            ),
            "sources": [],
        }

    context = context_builder.build(results)

    prompt = f"""
You are a document question-answering assistant.

Your task is to answer the user's question using ONLY the information
contained in the provided document context.

IMPORTANT RULES:
- The context contains the actual text extracted from documents.
- Treat the text under each [Source] as factual document content.
- If the answer is explicitly present in the context, answer it directly.
- Do not say that information is unavailable when the answer is present.
- Do not invent or add information that is not present in the context.
- Keep the answer concise.
- Answer in the same language as the user's question.

Document context:
{context}

User question:
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
            "text": result.get("text"),
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }