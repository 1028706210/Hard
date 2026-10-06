from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hard_api.main import create_app
from test_catalog import make_settings, write_python_fixture


def test_lesson_renders_safe_commonmark_and_openapi_never_describes_private_content(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)

    with TestClient(create_app(make_settings(content_root))) as client:
        response = client.get("/api/content/lessons/python-foundations-hello-world")
        schema = client.get("/openapi.json")

    assert response.status_code == 200
    rendered_html = response.json()["rendered_html"]
    assert "<h1>Hello World</h1>" in rendered_html
    assert "<ul>" in rendered_html
    assert "<code>print</code>" in rendered_html
    assert "<pre><code>" in rendered_html
    assert "<script>" not in rendered_html
    assert "javascript:" not in rendered_html
    assert "onerror=" not in rendered_html
    assert schema.status_code == 200
    schema_text = schema.text
    for forbidden in ("PrivateQuestionData", "reference_answer", "reference_solution", "hidden_tests"):
        assert forbidden not in schema_text


def test_course_endpoint_returns_fixture_course_and_unknown_language_is_not_found(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)

    with TestClient(create_app(make_settings(content_root))) as client:
        course = client.get("/api/content/courses/python")
        unknown = client.get("/api/content/courses/java")

    assert course.status_code == 200
    assert course.json()["fixture_only"] is True
    assert course.json()["modules"][0]["lessons"][0]["id"] == "python-foundations-hello-world"
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "unknown_language"
