from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, UploadFile

from app.documents.chunking import TextChunker
from app.documents.service import DocumentService
from app.embeddings.service import EmbeddingService
from app.retrieval.service import RetrievalService


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

document_service = DocumentService()

embedding_service = EmbeddingService()

chunker = TextChunker(
    chunk_size=1000,
    overlap=100,
)

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {
            "error": "Only PDF files are supported."
        }

    suffix = Path(file.filename or "").suffix

    with NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        temp_file.write(await file.read())
        temp_path = Path(temp_file.name)

    try:
        filename = file.filename or "unknown.pdf"
        content_type = file.content_type or "application/pdf"

        document = document_service.extract_text(
            temp_path,
            filename=filename,
            content_type=content_type,
        )

        chunks = chunker.chunk_pages(
            document_id=document.document_id,
            pages=document.metadata["pages"],
        )

        indexed = retrieval_service.index_chunks(
            chunks,
            filename=document.filename,
            content_type=document.content_type,
        )

        return {
            "document_id": document.document_id,
            "filename": document.filename,
            "content_type": document.content_type,
            "page_count": document.metadata["page_count"],
            "chunk_count": len(chunks),
            "indexed": indexed,
            "duplicate": not indexed,
        }

    finally:
        temp_path.unlink(missing_ok=True)