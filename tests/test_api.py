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
            }
        ],
    }


def test_upload_rejects_unsupported_file():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.docx",
                b"unsupported content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only PDF and TXT files are supported."
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