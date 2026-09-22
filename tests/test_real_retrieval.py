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


def test_search_uses_configured_score_threshold(monkeypatch):
    class FakeEmbeddingService:
        dimension = 3

        def embed_text(self, text: str):
            return [1.0, 0.0, 0.0]

    class FakePoint:
        def __init__(self, score):
            self.score = score
            self.payload = {
                "text": "test",
                "document_id": "doc-1",
                "chunk_id": "chunk-1",
            }

    class FakeQueryResult:
        def __init__(self):
            self.points = [
                FakePoint(0.80),
                FakePoint(0.40),
            ]

    class FakeClient:
        def get_collections(self):
            class Collections:
                collections = []

            return Collections()

        def create_collection(self, **kwargs):
            pass

        def query_points(self, **kwargs):
            return FakeQueryResult()

    service = RetrievalService(
        embedding_service=FakeEmbeddingService(),
    )

    service.client = FakeClient()

    monkeypatch.setattr(
        "app.retrieval.service.settings.rag_score_threshold",
        0.50,
    )

    results = service.search("test")

    assert len(results) == 1
    assert results[0]["score"] == 0.80