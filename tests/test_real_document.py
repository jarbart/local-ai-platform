from pathlib import Path

from app.documents.chunking import TextChunker
from app.documents.service import DocumentService


def test_real_pdf_to_chunks():
    service = DocumentService()

    document = service.extract_text(
        Path("test.pdf"),
        filename="test.pdf",
        content_type="application/pdf",
    )

    chunker = TextChunker(
        chunk_size=1000,
        overlap=100,
    )

    chunks = chunker.chunk_pages(
        document_id=document.document_id,
        pages=document.metadata["pages"],
    )

    assert chunks

    print(f"\nDocument ID: {document.document_id}")
    print(f"Characters: {len(document.text)}")
    print(f"Pages: {document.metadata['page_count']}")
    print(f"Chunks: {len(chunks)}")

    for chunk in chunks[:3]:
        print(
            f"\n--- Chunk {chunk.chunk_index} "
            f"(page {chunk.page_number}) ---\n"
            f"{chunk.text[:300]}"
        )