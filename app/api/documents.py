from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.models import DocumentUploadResponse
from app.core.dependencies import get_retrieval_service
from app.documents.chunking import TextChunker
from app.documents.service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

document_service = DocumentService()

chunker = TextChunker(
    chunk_size=1000,
    overlap=100,
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

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

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="The PDF does not contain extractable text.",
            )

        retrieval_service = get_retrieval_service()

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