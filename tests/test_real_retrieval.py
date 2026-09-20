from pathlib import Path

from app.documents.chunking import TextChunker
from app.documents.service import DocumentService
from app.embeddings.service import EmbeddingService
from app.retrieval.service import RetrievalService


def test_real_pdf_retrieval():
    document_service = DocumentService()

    document = document_service.extract_text(
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

    embedding_service = EmbeddingService()

    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        collection_name=f"test-real-{document.document_id}",
    )

    retrieval_service.index_chunks(chunks)

    results = retrieval_service.search(
        "Ile kosztował rower Trek Rail 9?",
        limit=3,
    )

    assert results

    print("\n=== RETRIEVAL RESULTS ===")

    for result in results:
        print(
            f"\nScore: {result['score']:.4f}"
            f"\nPage: {result['page_number']}"
            f"\nChunk: {result['chunk_id']}"
            f"\nText:\n{result['text'][:500]}"
        )

    top_result = results[0]

    assert top_result["document_id"] == document.document_id
    assert top_result["page_number"] == 1