from typing import Any
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings
from app.documents.chunking import TextChunk


class RetrievalService:
    def __init__(
        self,
        embedding_service,
        host: str | None = None,
        port: int | None = None,
        collection_name: str | None = None,
    ):
        self.embedding_service = embedding_service

        self.client = QdrantClient(
            host=host or settings.qdrant_host,
            port=port or settings.qdrant_port,
        )

        self.collection_name = (
            collection_name or settings.qdrant_collection
        )

    def create_collection(self) -> None:
        collections = self.client.get_collections().collections

        existing_names = {
            collection.name
            for collection in collections
        }

        if self.collection_name in existing_names:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedding_service.dimension,
                distance=Distance.COSINE,
            ),
        )

    def _point_id(self, chunk_id: str) -> str:
        return str(
            uuid5(
                NAMESPACE_URL,
                f"local-ai-platform:{chunk_id}",
            )
        )

    def document_exists(self, document_id: str) -> bool:
        self.create_collection()

        result = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
            limit=1,
            with_payload=False,
            with_vectors=False,
        )

        points, _ = result

        return len(points) > 0

    def index_chunks(
        self,
        chunks: list[TextChunk],
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> bool:
        if not chunks:
            return False

        self.create_collection()

        document_id = chunks[0].document_id

        if self.document_exists(document_id):
            return False

        vectors = self.embedding_service.embed_texts(
            [chunk.text for chunk in chunks]
        )

        points = []

        for chunk, vector in zip(chunks, vectors):
            points.append(
                PointStruct(
                    id=self._point_id(chunk.chunk_id),
                    vector=vector,
                    payload={
                        "document_id": chunk.document_id,
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        "text": chunk.text,
                        "filename": filename,
                        "content_type": content_type,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        return True

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        self.create_collection()

        query_vector = self.embedding_service.embed_text(
            query
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
        ).points

        return [
            {
                "score": result.score,
                **result.payload,
            }
            for result in results
        ]