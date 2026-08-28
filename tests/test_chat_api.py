import routers.chat as chat_router

VALID_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def stub_chat_deps(monkeypatch, chunks=None, answer="a generated answer", exc=None):
    def fake_retrieve(url, question, top_k=5):
        if exc is not None:
            raise exc
        return chunks if chunks is not None else []

    def fake_answer_question(question, passed_chunks):
        return answer

    monkeypatch.setattr(chat_router, "retrieve", fake_retrieve)
    monkeypatch.setattr(chat_router, "answer_question", fake_answer_question)


# --- POST /chat ---

def test_post_returns_200_with_answer_and_citations(client, monkeypatch):
    chunks = [{"text": "a chunk", "start": 0.0, "end": 1.5, "distance": 0.12}]
    stub_chat_deps(monkeypatch, chunks=chunks, answer="cells make energy [00:00]")

    response = client.post("/chat", json={"url": VALID_URL, "question": "what happens?"})

    assert response.status_code == 200
    assert response.json() == {"answer": "cells make energy [00:00]", "citations": chunks}


def test_post_returns_empty_citations_when_no_matches(client, monkeypatch):
    stub_chat_deps(
        monkeypatch,
        chunks=[],
        answer="I don't have any indexed transcript content to answer that from.",
    )

    response = client.post("/chat", json={"url": VALID_URL, "question": "what happens?"})

    assert response.status_code == 200
    assert response.json()["citations"] == []


def test_post_returns_400_on_malformed_url(client, monkeypatch):
    stub_chat_deps(monkeypatch, exc=ValueError("Could not find a video ID in the URL."))

    response = client.post("/chat", json={"url": "not a video url", "question": "what happens?"})

    assert response.status_code == 400
    assert "video ID" in response.json()["detail"]


# --- request validation ---

def test_missing_question_field_returns_422(client):
    response = client.post("/chat", json={"url": VALID_URL})
    assert response.status_code == 422


def test_empty_question_returns_422(client):
    response = client.post("/chat", json={"url": VALID_URL, "question": ""})
    assert response.status_code == 422


def test_missing_url_field_returns_422(client):
    response = client.post("/chat", json={"question": "what happens?"})
    assert response.status_code == 422


# --- CORS ---

def test_cors_header_on_post(client, monkeypatch):
    stub_chat_deps(monkeypatch, chunks=[])
    response = client.post(
        "/chat",
        json={"url": VALID_URL, "question": "what happens?"},
        headers={"Origin": "http://localhost:5500"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
