from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "learning"))

from test_progress import learning_client


def test_search_indexes_public_course_text_notes_and_handles_special_input(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    with client:
        course_result = client.get("/api/search", params={"q": "Hello"})
        client.put(
            "/api/progress/notes/python-foundations-hello-world",
            json={"body": "我的自定义复习笔记"},
            headers={"Idempotency-Key": "search-note"},
        )
        note_result = client.get("/api/search", params={"q": "自定义"})
        special_result = client.get("/api/search", params={"q": "\"() *-："})
        blank_result = client.get("/api/search", params={"q": "   "})
        client.delete(
            "/api/progress/notes/python-foundations-hello-world",
            headers={"Idempotency-Key": "delete-note"},
        )
        deleted_note_result = client.get("/api/search", params={"q": "自定义"})

    assert course_result.status_code == 200
    assert any(
        result["source_type"] == "lesson" and result["lesson_id"] == "python-foundations-hello-world"
        for result in course_result.json()["results"]
    )
    assert note_result.status_code == 200
    assert note_result.json()["results"][0]["source_type"] == "note"
    assert "reference_solution" not in note_result.text
    assert special_result.status_code == 200
    assert special_result.json()["results"] == []
    assert blank_result.json()["results"] == []
    assert deleted_note_result.json()["results"] == []
