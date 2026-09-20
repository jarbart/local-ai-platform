from app.documents.chunking import TextChunker


def test_text_chunking():
    text = "A" * 2500

    chunker = TextChunker(
        chunk_size=1000,
        overlap=100,
    )

    chunks = chunker.chunk(
        document_id="doc-001",
        text=text,
    )

    assert len(chunks) == 3

    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2

    assert chunks[0].document_id == "doc-001"
    assert chunks[1].document_id == "doc-001"
    assert chunks[2].document_id == "doc-001"

    assert len(chunks[0].text) == 1000
    assert len(chunks[1].text) == 1000
    assert len(chunks[2].text) == 700


def test_chunking_pages():
    chunker = TextChunker(
        chunk_size=10,
        overlap=2,
    )

    pages = [
        {
            "page_number": 1,
            "text": "A" * 15,
        },
        {
            "page_number": 2,
            "text": "B" * 15,
        },
    ]

    chunks = chunker.chunk_pages(
        document_id="doc-001",
        pages=pages,
    )

    assert chunks

    assert all(
        chunk.document_id == "doc-001"
        for chunk in chunks
    )

    assert any(
        chunk.page_number == 1
        for chunk in chunks
    )

    assert any(
        chunk.page_number == 2
        for chunk in chunks
    )