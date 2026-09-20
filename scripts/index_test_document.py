from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.documents.chunking import TextChunker
from app.documents.service import DocumentService
from app.embeddings.service import EmbeddingService
from app.retrieval.service import RetrievalService


def main():
    document_service = DocumentService()

    document = document_service.extract_text(
        PROJECT_ROOT / "test.pdf",
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
    )

    retrieval_service.index_chunks(chunks)

    print("Document indexed successfully.")
    print(f"Document ID: {document.document_id}")
    print(f"Pages: {document.metadata['page_count']}")
    print(f"Chunks: {len(chunks)}")


if __name__ == "__main__":
    main()