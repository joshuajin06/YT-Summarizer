import routers.query as query_router

VALID_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def stub_retrieve(monkeypatch, result=None, exc=None):
    def fake_retrieve(url, question, top_k=5):
        if exc is not None:
            raise exc
        return result if result is not None else []

    monkeypatch.setattr(query_router, "retrieve", fake_retrieve)


# --- POST /query ---

def test_post_returns_200_with_chunks(client, monkeypatch):
    matches = [{"text": "a chunk", "start": 0.0, "end": 1.5, "distance": 0.12}]
    stub_retrieve(monkeypatch, result=matches)

    response = client.post("/query", json={"url": VALID_URL, "question": "what happens?"})

    assert response.status_code == 200
    assert response.json() == {"chunks": matches}


def test_post_returns_empty_chunks_when_no_matches(client, monkeypatch):
    stub_retrieve(monkeypatch, result=[])

    response = client.post("/query", json={"url": VALID_URL, "question": "what happens?"})

    assert response.status_code == 200
    assert response.json() == {"chunks": []}


def test_post_returns_400_on_malformed_url(client, monkeypatch):
    stub_retrieve(monkeypatch, exc=ValueError("Could not find a video ID in the URL."))

    response = client.post("/query", json={"url": "not a video url", "question": "what happens?"})

    assert response.status_code == 400
    assert "video ID" in response.json()["detail"]


# --- request validation ---

def test_missing_question_field_returns_422(client):
    response = client.post("/query", json={"url": VALID_URL})
    assert response.status_code == 422


def test_empty_question_returns_422(client):
    response = client.post("/query", json={"url": VALID_URL, "question": ""})
    assert response.status_code == 422


def test_missing_url_field_returns_422(client):
    response = client.post("/query", json={"question": "what happens?"})
    assert response.status_code == 422


# --- CORS ---

def test_cors_header_on_post(client, monkeypatch):
    stub_retrieve(monkeypatch, result=[])
    response = client.post(
        "/query",
        json={"url": VALID_URL, "question": "what happens?"},
        headers={"Origin": "http://localhost:5500"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
