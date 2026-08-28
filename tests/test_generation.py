import services.generation as generation_service
from services.generation import NO_CONTEXT_ANSWER, answer_question

CHUNKS = [
    {"text": "the mitochondria is the powerhouse of the cell", "start": 12.0, "end": 15.0, "distance": 0.05},
    {"text": "it produces ATP through respiration", "start": 90.0, "end": 93.0, "distance": 0.11},
]


def stub_complete(monkeypatch, response="a generated answer"):
    calls = {}

    def fake_complete(system_prompt, user_content):
        calls["system_prompt"] = system_prompt
        calls["user_content"] = user_content
        return response

    monkeypatch.setattr(generation_service, "_complete", fake_complete)
    return calls


def test_answer_question_returns_llm_response(monkeypatch):
    stub_complete(monkeypatch, response="cells make energy [00:12]")

    result = answer_question("what does the mitochondria do?", CHUNKS)

    assert result == "cells make energy [00:12]"


def test_answer_question_includes_question_in_prompt(monkeypatch):
    calls = stub_complete(monkeypatch)

    answer_question("what does the mitochondria do?", CHUNKS)

    assert "what does the mitochondria do?" in calls["user_content"]


def test_answer_question_formats_timestamps_as_mmss(monkeypatch):
    calls = stub_complete(monkeypatch)

    answer_question("a question", CHUNKS)

    assert "[00:12]" in calls["user_content"]
    assert "[01:30]" in calls["user_content"]


def test_answer_question_includes_chunk_text(monkeypatch):
    calls = stub_complete(monkeypatch)

    answer_question("a question", CHUNKS)

    assert "the mitochondria is the powerhouse of the cell" in calls["user_content"]
    assert "it produces ATP through respiration" in calls["user_content"]


def test_answer_question_returns_fallback_when_no_chunks(monkeypatch):
    calls = stub_complete(monkeypatch)

    result = answer_question("a question", [])

    assert result == NO_CONTEXT_ANSWER
    assert calls == {}
