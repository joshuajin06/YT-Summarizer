import services.retrieval as retrieval_service
from services.retrieval import retrieve

VALID_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def stub_services(monkeypatch, embedding=None, results=None):
    calls = {}

    def fake_embed_text(text):
        calls["embed_text"] = text
        return embedding if embedding is not None else [0.1, 0.2, 0.3]

    def fake_search(video_id, query_embedding, top_k=5):
        calls["search"] = (video_id, query_embedding, top_k)
        return results if results is not None else []

    monkeypatch.setattr(retrieval_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(retrieval_service, "search", fake_search)
    return calls


def test_retrieve_embeds_the_question(monkeypatch):
    calls = stub_services(monkeypatch)

    retrieve(VALID_URL, "what is this video about?")

    assert calls["embed_text"] == "what is this video about?"


def test_retrieve_searches_with_extracted_video_id_and_embedding(monkeypatch):
    calls = stub_services(monkeypatch, embedding=[0.4, 0.5])

    retrieve(VALID_URL, "a question", top_k=3)

    video_id, query_embedding, top_k = calls["search"]
    assert video_id == "dQw4w9WgXcQ"
    assert query_embedding == [0.4, 0.5]
    assert top_k == 3


def test_retrieve_defaults_top_k_to_five(monkeypatch):
    calls = stub_services(monkeypatch)

    retrieve(VALID_URL, "a question")

    assert calls["search"][2] == 5


def test_retrieve_returns_search_results(monkeypatch):
    matches = [{"text": "a chunk", "start": 0.0, "end": 1.5, "distance": 0.12}]
    stub_services(monkeypatch, results=matches)

    assert retrieve(VALID_URL, "a question") == matches


def test_retrieve_raises_on_malformed_url(monkeypatch):
    calls = stub_services(monkeypatch)

    try:
        retrieve("https://www.youtube.com/playlist?list=PL123", "a question")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "video ID" in str(exc)

    # neither downstream call should have happened once extraction fails
    assert "embed_text" not in calls
    assert "search" not in calls
