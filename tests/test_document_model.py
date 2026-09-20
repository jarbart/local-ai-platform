from app.documents.models import NormalizedDocument


def test_normalized_document():
    document = NormalizedDocument(
        document_id="test-001",
        filename="test.pdf",
        content_type="application/pdf",
        text="Hello world",
    )

    assert document.document_id == "test-001"
    assert document.filename == "test.pdf"
    assert document.content_type == "application/pdf"
    assert document.text == "Hello world"
    assert document.metadata == {}