from fastapi.testclient import TestClient

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