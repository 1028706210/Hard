from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_progress import learning_client


def test_weaknesses_use_only_recent_allowed_signals_and_keep_hidden_details_private(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO attempts "
                "(id, lesson_id, score, exercise_id, question_type, hint_level, raw_score, final_score, passed, placement, normalized_result, created_at) "
                "VALUES ('weak-1', 'python-foundations-hello-world', 0, "
                "'python-foundations-hello-world-k01', 'knowledge', 'revealed', 0, 0, 0, 0, "
                "'{\"compile_error_category\": \"syntax\", \"hidden_test_failures\": 3}', CURRENT_TIMESTAMP)"
            )
            connection.execute(
                "INSERT INTO review_items "
                "(concept_id, lesson_id, exercise_id, due_on, interval_days, last_score, status, updated_at) "
                "VALUES ('variables', 'python-foundations-hello-world', "
                "'python-foundations-hello-world-k01', '2026-01-01', 1, 0, 'scheduled', CURRENT_TIMESTAMP)"
            )

    with client:
        response = client.get("/api/growth/weaknesses")

    assert response.status_code == 200
    weakness = response.json()["items"][0]
    assert weakness["concept_id"] == "variables"
    assert weakness["score"] == 23
    assert weakness["lesson_id"] == "python-foundations-hello-world"
    assert "hidden_tests" not in response.text


def test_weaknesses_exclude_perfect_attempts_without_weakness_signals(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO attempts "
                "(id, lesson_id, score, exercise_id, question_type, hint_level, raw_score, final_score, passed, placement, normalized_result, created_at) "
                "VALUES ('perfect', 'python-foundations-hello-world', 100, "
                "'python-foundations-hello-world-k01', 'knowledge', 'none', 100, 100, 1, 0, "
                "'{\"hidden_test_failures\": 0}', CURRENT_TIMESTAMP)"
            )

    with client:
        response = client.get("/api/growth/weaknesses")

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_a_later_perfect_answer_does_not_move_an_existing_weakness_link(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            for key, exercise, score, created in [
                ("failed", "python-foundations-hello-world-k01", 0, datetime.now() - timedelta(minutes=1)),
                ("perfect", "python-foundations-hello-world-k02", 100, datetime.now()),
            ]:
                connection.execute(
                    "INSERT INTO attempts (id, lesson_id, exercise_id, question_type, hint_level, raw_score, final_score, passed, placement, normalized_result, created_at) "
                    "VALUES (?, 'python-foundations-hello-world', ?, 'knowledge', 'none', ?, ?, ?, 0, '{}', ?)",
                    (key, exercise, score, score, int(score == 100), created),
                )
    with client:
        result = client.get("/api/growth/weaknesses")
    assert result.status_code == 200
    assert result.json()["items"][0]["exercise_id"] == "python-foundations-hello-world-k01"
    assert result.json()["items"][0]["score"] == 4


def test_weakness_link_uses_event_time_when_rows_are_inserted_out_of_order(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            for key, exercise, created in [
                ("newer", "python-foundations-hello-world-k02", datetime.now()),
                ("older", "python-foundations-hello-world-k01", datetime.now() - timedelta(minutes=1)),
            ]:
                connection.execute(
                    "INSERT INTO attempts (id, lesson_id, exercise_id, question_type, hint_level, raw_score, final_score, passed, placement, normalized_result, created_at) "
                    "VALUES (?, 'python-foundations-hello-world', ?, 'knowledge', 'none', 0, 0, 0, 0, '{}', ?)",
                    (key, exercise, created),
                )
    with client:
        items = client.get("/api/growth/weaknesses").json()["items"]
    assert items[0]["exercise_id"] == "python-foundations-hello-world-k02"
    assert items[0]["score"] == 8


@pytest.mark.parametrize(
    ("raw_score", "hint_level", "hidden_failures", "expected_score"),
    [
        (100, "light", 0, 1),
        (0, "none", 0, 4),
        (0, "none", 1, 6),
        (0, "none", 3, 10),
        (0, "none", 4, 10),
        (0, "none", 100, 10),
    ],
)
def test_weakness_score_uses_raw_correctness_and_caps_hidden_failures(
    tmp_path: Path, raw_score: int, hint_level: str, hidden_failures: int, expected_score: int
) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO attempts "
                "(id, lesson_id, exercise_id, question_type, hint_level, raw_score, final_score, passed, placement, normalized_result, created_at) "
                "VALUES ('formula', 'python-foundations-hello-world', 'python-foundations-hello-world-k01', "
                "'knowledge', ?, ?, 85, 0, 0, ?, ?)",
                (hint_level, raw_score, '{"hidden_test_failures": %d}' % hidden_failures, datetime.now()),
            )
    with client:
        response = client.get("/api/growth/weaknesses")
    assert response.json()["items"][0]["score"] == expected_score


def test_weaknesses_exclude_stale_and_unknown_content_links(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO attempts "
                "(id, lesson_id, exercise_id, question_type, hint_level, raw_score, final_score, passed, placement, created_at) "
                "VALUES ('old', 'python-foundations-hello-world', 'python-foundations-hello-world-k01', 'knowledge', 'none', 0, 0, 0, 0, ?)",
                (datetime.now() - timedelta(days=31),),
            )
            connection.execute(
                "INSERT INTO attempts "
                "(id, lesson_id, exercise_id, question_type, hint_level, raw_score, final_score, passed, placement, created_at) "
                "VALUES ('missing', 'python-foundations-removed', 'python-foundations-removed-k01', 'knowledge', 'none', 0, 0, 0, 0, ?)",
                (datetime.now(),),
            )
    with client:
        response = client.get("/api/growth/weaknesses")
    assert response.json()["items"] == []
