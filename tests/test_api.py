from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.api.main import app


import app.api.documents as documents_module


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_rejects_empty_question():
    response = client.post(
        "/chat",
        json={
            "question": "",
        },
    )

    assert response.status_code == 422


def test_chat_rejects_invalid_limit():
    response = client.post(
        "/chat",
        json={
            "question": "Test question",
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_chat_response_contract(monkeypatch):
    class FakeRetrievalService:
        def search(self, query: str, limit: int):
            return [
                {
                    "chunk_id": "chunk-1",
                    "document_id": "document-1",
                    "filename": "test.pdf",
                    "page_number": 1,
                    "score": 0.9,
                    "text": "Test context",
                }
            ]

    class FakeLLM:
        def generate(self, prompt: str):
            return "Test answer"

    monkeypatch.setattr(
        chat_module,
        "get_retrieval_service",
        lambda: FakeRetrievalService(),
    )
    monkeypatch.setattr(
        chat_module,
        "get_llm_provider",
        lambda: FakeLLM(),
    )

    response = client.post(
        "/chat",
        json={
            "question": "Test question",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Test answer",
        "sources": [
            {
                "chunk_id": "chunk-1",
                "document_id": "document-1",
                "filename": "test.pdf",
                "page_number": 1,
                "score": 0.9,
                "text": "Test context",
            }
        ],
    }


def test_upload_rejects_unsupported_file():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.exe",
                b"unsupported content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Only PDF, TXT and DOCX files are supported."
        )
    }

def test_upload_accepts_txt(monkeypatch):
    class FakeRetrievalService:
        def index_chunks(
            self,
            chunks,
            *,
            filename,
            content_type,
        ):
            assert filename == "test.txt"
            assert content_type == "text/plain"
            assert len(chunks) == 1
            assert chunks[0].text == "Mój plik tekstowy"

            return True

    class FakeDocumentService:
        def extract_text(
            self,
            file_path,
            filename,
            content_type,
        ):
            from app.documents.models import NormalizedDocument

            return NormalizedDocument(
                document_id="txt-document-1",
                filename=filename,
                content_type=content_type,
                text="Mój plik tekstowy",
                metadata={
                    "page_count": 1,
                    "pages": [
                        {
                            "page_number": 1,
                            "text": "Mój plik tekstowy",
                        }
                    ],
                    "character_count": 18,
                    "extraction_method": "plain_text",
                },
            )


    monkeypatch.setattr(
        documents_module,
        "document_service",
        FakeDocumentService(),
    )

    monkeypatch.setattr(
        documents_module,
        "get_retrieval_service",
        lambda: FakeRetrievalService(),
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                "Mój plik tekstowy".encode("utf-8"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "document_id": "txt-document-1",
        "filename": "test.txt",
        "content_type": "text/plain",
        "page_count": 1,
        "chunk_count": 1,
        "indexed": True,
        "duplicate": False,
    }

def test_chat_returns_message_when_no_relevant_context(monkeypatch):
    class FakeRetrievalService:
        def search(self, query: str, limit: int):
            return []

    class FakeLLM:
        def generate(self, prompt: str):
            raise AssertionError("LLM should not be called")

    monkeypatch.setattr(
        chat_module,
        "get_retrieval_service",
        lambda: FakeRetrievalService(),
    )

    monkeypatch.setattr(
        chat_module,
        "get_llm_provider",
        lambda: FakeLLM(),
    )

    response = client.post(
        "/chat",
        json={
            "question": "Informacja, której nie ma w dokumentach",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": (
            "Informacja nie jest dostępna w dostarczonych "
            "dokumentach."
        ),
        "sources": [],
    }

def test_upload_accepts_docx(tmp_path):
    from docx import Document

    file_path = tmp_path / "test.docx"

    document = Document()
    document.add_paragraph("Dokument DOCX do testu API.")
    document.save(file_path)

    with file_path.open("rb") as file:
        response = client.post(
            "/documents/upload",
            files={
                "file": (
                    "test.docx",
                    file.read(),
                    (
                        "application/"
                        "vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ),
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.docx"
    assert data["content_type"] == (
        "application/"
        "vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert data["page_count"] == 1
    assert data["chunk_count"] >= 1
    assert data["indexed"] is True
    assert data["duplicate"] is False