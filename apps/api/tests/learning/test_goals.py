from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_progress import learning_client


def test_daily_goal_summary_notes_and_favorites_use_idempotency(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    with client:
        goal = client.put(
            "/api/progress/daily-goal",
            json={"target_minutes": 5, "target_exercises": 2},
            headers={"Idempotency-Key": "goal-1"},
        )
        client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 10, "time_spent_seconds": 120},
            headers={"Idempotency-Key": "progress-1"},
        )
        note = client.put(
            "/api/progress/notes/python-foundations-hello-world",
            json={"body": "记住 print 的用途"},
            headers={"Idempotency-Key": "note-1"},
        )
        note_replay = client.put(
            "/api/progress/notes/python-foundations-hello-world",
            json={"body": "记住 print 的用途"},
            headers={"Idempotency-Key": "note-1"},
        )
        favorite = client.put(
            "/api/progress/favorites/python-foundations-hello-world",
            headers={"Idempotency-Key": "favorite-1"},
        )
        favorite_replay = client.put(
            "/api/progress/favorites/python-foundations-hello-world",
            headers={"Idempotency-Key": "favorite-1"},
        )
        blank_note = client.put(
            "/api/progress/notes/python-foundations-hello-world",
            json={"body": "   "},
            headers={"Idempotency-Key": "blank-note"},
        )
        summary = client.get("/api/progress/summary")

    assert goal.status_code == 200
    assert note.status_code == 200
    assert note_replay.json() == note.json()
    assert favorite.status_code == favorite_replay.status_code == 200
    assert favorite_replay.json() == favorite.json()
    assert blank_note.status_code == 400
    assert blank_note.json()["error"]["code"] == "blank_note"
    body = summary.json()
    assert body["daily_goal"]["target_minutes"] == 5
    assert body["daily_goal"]["studied_seconds"] == 120
    assert body["daily_goal"]["completed_exercises"] == 0
    assert body["continue_learning"]["lesson_id"] == "python-foundations-hello-world"
    assert body["unlocked_lessons"] == {"python": ["python-foundations-hello-world"]}
    assert body["current_experience"] == 0
    assert body["current_level"] == 1


def test_unconfigured_daily_goal_is_not_reported_as_achieved_and_is_distinct_from_zero_goal(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    with client:
        unconfigured = client.get("/api/progress/summary")
        configured = client.put(
            "/api/progress/daily-goal",
            json={"target_minutes": 0, "target_exercises": 0},
            headers={"Idempotency-Key": "zero-goal"},
        )
        configured_summary = client.get("/api/progress/summary")

    assert unconfigured.json()["daily_goal"] == {
        "date": unconfigured.json()["daily_goal"]["date"],
        "configured": False,
        "target_minutes": 0,
        "target_exercises": 0,
        "studied_seconds": 0,
        "completed_exercises": 0,
        "completion_ratio": 0,
        "achieved": False,
    }
    assert configured.status_code == 200
    assert configured_summary.json()["daily_goal"]["configured"] is True
    assert configured_summary.json()["daily_goal"]["completion_ratio"] == 1
    assert configured_summary.json()["daily_goal"]["achieved"] is True
    with client:
        schema = client.get("/openapi.json").json()
    daily_goal = schema["components"]["schemas"]["DailyGoalSummaryResponse"]
    assert daily_goal["properties"]["configured"] == {"type": "boolean", "title": "Configured"}


def test_first_successful_exercise_advances_the_daily_exercise_goal_once(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    with client:
        client.put(
            "/api/progress/daily-goal",
            json={"target_minutes": 0, "target_exercises": 1},
            headers={"Idempotency-Key": "exercise-goal"},
        )
        payload = {
            "lesson_id": "python-foundations-hello-world",
            "exercise_id": "python-foundations-hello-world-k01",
            "answer": "a",
            "hint_level": "none",
        }
        first = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "exercise-pass"})
        replay = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "exercise-pass"})
        summary = client.get("/api/progress/summary")

    assert first.status_code == replay.status_code == 200
    assert summary.json()["daily_goal"]["completed_exercises"] == 1
    assert summary.json()["daily_goal"]["achieved"] is True
