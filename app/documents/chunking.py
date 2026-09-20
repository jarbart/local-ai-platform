from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_id: str
    document_id: str
    text: str
    chunk_index: int
    page_number: int | None = None


class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document_id: str, text: str) -> list[TextChunk]:
        if not text.strip():
            return []

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            chunks.append(
                TextChunk(
                    chunk_id=f"{document_id}-{chunk_index}",
                    document_id=document_id,
                    text=chunk_text,
                    chunk_index=chunk_index,
                )
            )

            start += self.chunk_size - self.overlap
            chunk_index += 1

        return chunks

    def chunk_pages(
        self,
        document_id: str,
        pages: list[dict],
    ) -> list[TextChunk]:
        chunks = []
        chunk_index = 0

        for page in pages:
            page_chunks = self.chunk(
                document_id=document_id,
                text=page["text"],
            )

            for chunk in page_chunks:
                chunk.chunk_id = f"{document_id}-{chunk_index}"
                chunk.chunk_index = chunk_index
                chunk.page_number = page["page_number"]

                chunks.append(chunk)
                chunk_index += 1

        return chunks
