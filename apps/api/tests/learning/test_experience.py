from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_progress import learning_client, record_trusted_code_attempt

from hard_api.learning.experience import growth_summary


def test_growth_summary_uses_unique_content_metadata_events_levels_and_first_lesson_badge(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    attempts = [
        {"exercise_id": "python-foundations-hello-world-k01", "answer": "a"},
        {"exercise_id": "python-foundations-hello-world-k02", "answer": "a"},
        {"exercise_id": "python-foundations-hello-world-k03", "answer": "a"},
    ]
    with client:
        for index, payload in enumerate(attempts):
            response = client.post(
                "/api/assessment/attempts",
                json={"lesson_id": "python-foundations-hello-world", "hint_level": "none", **payload},
                headers={"Idempotency-Key": f"experience-{index}"},
            )
            assert response.status_code == 200
        response = record_trusted_code_attempt(
            client,
            lesson_id="python-foundations-hello-world",
            exercise_id="python-foundations-hello-world-c01",
            source_code="print('Hello, Hard!')",
            idempotency_key="experience-3",
        )
        assert response.status_code == 200
        summary = client.get("/api/growth/summary")
        replayed_summary = client.get("/api/growth/summary")

    assert summary.status_code == 200
    assert summary.json()["total_experience"] == 120
    assert summary.json()["level"] == 2
    assert summary.json()["next_level_remaining"] == 80
    assert summary.json()["badges"] == ["first_lesson"]
    assert {key: value for key, value in replayed_summary.json().items() if key != "new_badges"} == {
        key: value for key, value in summary.json().items() if key != "new_badges"
    }
    assert replayed_summary.json()["new_badges"] == []
    with closing(sqlite3.connect(database_path)) as connection:
        events = connection.execute("SELECT COUNT(*) FROM experience_events").fetchone()
        badges = connection.execute("SELECT COUNT(*) FROM achievements").fetchone()
    assert events == (6,)
    assert badges == (1,)


def test_injected_streak_awards_once_on_the_seventh_progress_write(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    from hard_api.learning.progress import update_lesson_progress

    start = date(2026, 8, 18)
    for offset in range(7):
        update_lesson_progress(
            database_path,
            repository=client.app.state.content_service.repository,
            course_id="python",
            module_id="python-foundations",
            lesson_id="python-foundations-hello-world",
            position=offset,
            time_spent_seconds=1,
            idempotency_key=f"streak-{offset}",
            today=start + timedelta(days=offset),
        )

    summary = growth_summary(
        database_path, repository=client.app.state.content_service.repository, today=start + timedelta(days=6)
    )
    replay = growth_summary(database_path, repository=client.app.state.content_service.repository, today=start + timedelta(days=6))

    assert summary["streak_days"] == 7
    assert "seven_day_streak" in summary["badges"]
    assert replay["total_experience"] == summary["total_experience"]


def test_fixture_only_course_is_never_reported_as_a_complete_route(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)

    with client:
        summary = client.get("/api/growth/summary")

    route = summary.json()["route_completion"][0]
    assert route == {"language": "python", "fixture_only": True, "complete": False}


def test_activity_summary_keeps_real_counts_within_the_inclusive_90_day_window(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    today = date(2026, 10, 1)
    start = today - timedelta(days=89)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            for activity_date, seconds, exercises in [(start - timedelta(days=1), 99, 9), (start, 60, 2), (today, 0, 0), (today + timedelta(days=1), 42, 3)]:
                connection.execute(
                    "INSERT INTO learning_activity_days (activity_date, time_spent_seconds, completed_exercises, updated_at) VALUES (?, ?, ?, ?)",
                    (activity_date.isoformat(), seconds, exercises, datetime(2026, 10, 1)),
                )
    summary = growth_summary(database_path, repository=client.app.state.content_service.repository, today=today)
    assert summary["activity_start_date"] == start.isoformat()
    assert summary["activity_end_date"] == today.isoformat()
    assert summary["activity_days"] == [
        {"date": start.isoformat(), "time_spent_seconds": 60, "completed_exercises": 2},
        {"date": today.isoformat(), "time_spent_seconds": 0, "completed_exercises": 0},
    ]
    with client:
        response = client.get("/api/growth/summary")
        assert response.status_code == 200
        assert "activity_days" in response.json()


def test_growth_summary_is_read_only_even_when_all_initial_badges_are_eligible(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    today = date(2026, 8, 24)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO lesson_progress "
                "(lesson_id, course_id, module_id, position, time_spent_seconds, status, updated_at) "
                "VALUES ('python-foundations-hello-world', 'python', 'python-foundations', 0, 0, 'completed', ?)",
                (datetime(2026, 8, 24),),
            )
            connection.execute(
                "INSERT INTO mastery_snapshots (course_id, scope_type, scope_id, status, score, recorded_at) "
                "VALUES ('python', 'lesson', 'python-foundations-hello-world', 'completed', 90, ?)",
                (datetime(2026, 8, 24),),
            )
            for offset in range(7):
                connection.execute(
                    "INSERT INTO learning_activity_days "
                    "(activity_date, time_spent_seconds, completed_exercises, updated_at) VALUES (?, 1, 0, ?)",
                    ((today - timedelta(days=offset)).isoformat(), datetime(2026, 8, 24)),
                )
        before = {
            table: connection.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
            for table in ("achievements", "experience_events", "mastery_snapshots", "learning_activity_days")
        }

    with client:
        first = client.get("/api/growth/summary")
        second = client.get("/api/growth/summary")

    with closing(sqlite3.connect(database_path)) as connection:
        after = {
            table: connection.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
            for table in ("achievements", "experience_events", "mastery_snapshots", "learning_activity_days")
        }
    assert first.status_code == second.status_code == 200
    assert before == after
    assert first.json()["new_badges"] == []
