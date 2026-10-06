from __future__ import annotations

from contextlib import closing
import json
import sqlite3
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_progress import learning_client, submit_trusted_code_job


def test_code_history_returns_raw_json_text_and_adjacent_exercise_diff_without_execution(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    first_source = "print('<script>first</script>')"
    second_source = "print('<script>second</script>')"
    with client:
        for key, source in (("history-1", first_source), ("history-2", second_source)):
            job_id = submit_trusted_code_job(
                client,
                lesson_id="python-foundations-hello-world",
                exercise_id="python-foundations-hello-world-c01",
                source_code=source,
                idempotency_key=key,
            )
            response = client.post(
                "/api/assessment/attempts",
                json={
                    "lesson_id": "python-foundations-hello-world",
                    "exercise_id": "python-foundations-hello-world-c01",
                    "hint_level": "none",
                    "runner_job_id": job_id,
                    "normalized_result": {
                        "score": 100,
                        "passed": True,
                        "language": "python",
                        "source_code": source,
                        "duration_ms": 12,
                        "visible_tests_passed": 4,
                        "visible_tests_total": 4,
        "hidden_test_failures": 0,
                        "hidden_tests": ["private assertion"],
                        "private_runner": "secret trace",
                        "results": [{"visibility": "hidden", "message": "HIDDEN_SENTINEL"}],
                        "diagnostics": {"private_trace": "PRIVATE_SENTINEL"},
                        "unknown_nested": {"message": "UNKNOWN_SENTINEL"},
                        "unknown_array": [{"message": "ARRAY_SENTINEL"}],
                    },
                },
                headers={"Idempotency-Key": key},
            )
            assert response.status_code == 200
        history = client.get("/api/growth/history")

    assert history.status_code == 200
    records = history.json()["items"]
    assert [record["source_code"] for record in records] == [first_source, second_source]
    assert "-print('<script>first</script>')" in records[1]["diff"]
    assert "+print('<script>second</script>')" in records[1]["diff"]
    assert "&lt;script" not in history.text
    assert "private assertion" not in history.text
    assert "secret trace" not in history.text
    assert "hidden_tests" not in history.text
    assert "private_runner" not in history.text
    assert "HIDDEN_SENTINEL" not in history.text
    assert "PRIVATE_SENTINEL" not in history.text
    assert "UNKNOWN_SENTINEL" not in history.text
    assert "ARRAY_SENTINEL" not in history.text
    assert records[0]["normalized_result"] == {
        "score": 100,
        "passed": True,
        "visible_tests_passed": 1,
        "visible_tests_total": 1,
    }

    with closing(sqlite3.connect(database_path)) as connection:
        stored = connection.execute(
            "SELECT attempts.normalized_result AS attempt_result, submissions.normalized_result AS submission_result, "
            "submissions.source_code, submissions.language, submissions.duration_ms "
            "FROM attempts JOIN submissions ON submissions.attempt_id = attempts.id"
        ).fetchall()
    forbidden = (
        "HIDDEN_SENTINEL",
        "PRIVATE_SENTINEL",
        "UNKNOWN_SENTINEL",
        "ARRAY_SENTINEL",
        "private assertion",
        "secret trace",
    )
    assert all(not any(value in result for value in forbidden) for row in stored for result in row[:2])
    assert all(
        json.loads(row[0])
        == {
            "score": 100,
            "passed": True,
            "visible_tests_passed": 1,
            "visible_tests_total": 1,
            "hidden_test_failures": 0,
        }
        for row in stored
    )
    assert all(
        json.loads(row[1])
        == {"score": 100, "passed": True, "visible_tests_passed": 1, "visible_tests_total": 1}
        for row in stored
    )
    assert [row[2:] for row in stored] == [
        (first_source, "python", 12),
        (second_source, "python", 12),
    ]


def test_phase_b_backend_learning_loop_replays_without_duplicate_business_records(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    with client:
        catalog = client.get("/api/content/catalog")
        lesson = client.get("/api/content/lessons/python-foundations-hello-world")
        progress = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 30, "time_spent_seconds": 120},
            headers={"Idempotency-Key": "journey-progress"},
        )
        note = client.put(
            "/api/progress/notes/python-foundations-hello-world",
            json={"body": "纵向流程笔记"},
            headers={"Idempotency-Key": "journey-note"},
        )
        favorite = client.put(
            "/api/progress/favorites/python-foundations-hello-world",
            headers={"Idempotency-Key": "journey-favorite"},
        )
        search = client.get("/api/search", params={"q": "纵向流程"})
        wrong = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-k01",
                "answer": "b",
                "hint_level": "none",
            },
            headers={"Idempotency-Key": "journey-wrong"},
        )
        queue = client.get("/api/review/queue")
        reviewed = client.post(
            f"/api/review/items/{queue.json()['items'][0]['id']}",
            json={"score": 80},
            headers={"Idempotency-Key": "journey-review"},
        )
        for key, exercise_id, answer in (
            ("journey-k1", "python-foundations-hello-world-k01", "a"),
            ("journey-k2", "python-foundations-hello-world-k02", "a"),
            ("journey-k3", "python-foundations-hello-world-k03", "a"),
        ):
            response = client.post(
                "/api/assessment/attempts",
                json={
                    "lesson_id": "python-foundations-hello-world",
                    "exercise_id": exercise_id,
                    "answer": answer,
                    "hint_level": "none",
                },
                headers={"Idempotency-Key": key},
            )
            assert response.status_code == 200
        response = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-c01",
                "runner_job_id": submit_trusted_code_job(
                    client,
                    lesson_id="python-foundations-hello-world",
                    exercise_id="python-foundations-hello-world-c01",
                    source_code="print('Hello, Hard!')",
                    idempotency_key="journey-code",
                ),
                "hint_level": "none",
            },
            headers={"Idempotency-Key": "journey-code"},
        )
        assert response.status_code == 200
        growth = client.get("/api/growth/summary")
        replayed_progress = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 30, "time_spent_seconds": 120},
            headers={"Idempotency-Key": "journey-progress"},
        )

    assert all(
        response.status_code == 200
        for response in (catalog, lesson, progress, note, favorite, search, wrong, queue, reviewed, growth)
    )
    assert search.json()["results"][0]["source_type"] == "note"
    assert wrong.json()["review_status"] == "wrong_answer"
    assert reviewed.json()["interval_days"] == 3
    assert growth.json()["total_experience"] >= 70
    assert replayed_progress.json() == progress.json()
