from app.documents.chunking import TextChunk
from app.retrieval.service import RetrievalService


class FakeEmbeddingService:
    dimension = 3

    def embed_texts(self, texts):
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_text(self, text):
        return [1.0, 0.0, 0.0]


class FakeQdrantClient:
    def __init__(self):
        self.points = []

    def get_collections(self):
        return type(
            "Collections",
            (),
            {"collections": []},
        )()

    def create_collection(self, **kwargs):
        pass

    def scroll(self, **kwargs):
        document_id = (
            kwargs["scroll_filter"]
            .must[0]
            .match.value
        )

        matching = [
            point
            for point in self.points
            if point.payload["document_id"] == document_id
        ]

        return matching[:1], None

    def upsert(self, collection_name, points):
        self.points.extend(points)


def test_same_document_is_not_indexed_twice():
    embedding_service = FakeEmbeddingService()

    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        collection_name="test_documents",
    )

    fake_client = FakeQdrantClient()
    retrieval_service.client = fake_client

    chunks = [
        TextChunk(
            chunk_id="document-123-0",
            document_id="document-123",
            text="Trek Rail 9 costs 5400 PLN.",
            chunk_index=0,
            page_number=1,
        )
    ]

    first_index = retrieval_service.index_chunks(
        chunks,
        filename="invoice.pdf",
        content_type="application/pdf",
    )

    second_index = retrieval_service.index_chunks(
        chunks,
        filename="invoice.pdf",
        content_type="application/pdf",
    )

    assert first_index is True
    assert second_index is False
    assert len(fake_client.points) == 1

    assert fake_client.points[0].payload["filename"] == "invoice.pdf"
    assert (
        fake_client.points[0].payload["content_type"]
        == "application/pdf"
    )