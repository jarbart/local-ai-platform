from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.api.main import app


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


def test_upload_rejects_non_pdf():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                b"plain text",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only PDF files are supported."
    }