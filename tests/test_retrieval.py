from app.documents.chunking import TextChunk
from app.embeddings.service import EmbeddingService
from app.retrieval.service import RetrievalService


def test_embedding_and_retrieval():
    embedding_service = EmbeddingService()

    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        collection_name="test_documents",
    )

    chunks = [
        TextChunk(
            chunk_id="test-1",
            document_id="doc-1",
            text="Trek Rail 9 costs 6814 PLN.",
            chunk_index=0,
            page_number=1,
        ),
        TextChunk(
            chunk_id="test-2",
            document_id="doc-1",
            text="The document contains bicycle equipment.",
            chunk_index=1,
            page_number=1,
        ),
    ]

    retrieval_service.index_chunks(chunks)

    results = retrieval_service.search(
        "How much does Trek Rail 9 cost?",
        limit=2,
    )

    assert results

    assert results[0]["chunk_id"] == "test-1"
    assert results[0]["document_id"] == "doc-1"
    assert results[0]["page_number"] == 1
    assert "6814" in results[0]["text"]