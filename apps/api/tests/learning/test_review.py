from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_progress import learning_client

from hard_api.core.errors import ApiError
from hard_api.learning.review import next_interval, score_review
from hard_api.learning.scoring import record_attempt


def test_review_queue_returns_only_due_items_and_scores_move_the_fixed_interval(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO review_items "
                "(concept_id, lesson_id, exercise_id, due_on, interval_days, last_score, status, updated_at) "
                "VALUES ('variables', 'python-foundations-hello-world', "
                "'python-foundations-hello-world-k01', '2026-08-24', 1, 40, 'scheduled', '2026-08-24')"
            )
            connection.execute(
                "INSERT INTO review_items "
                "(concept_id, lesson_id, exercise_id, due_on, interval_days, last_score, status, updated_at) "
                "VALUES ('io', 'python-foundations-hello-world', "
                "'python-foundations-hello-world-k02', '2999-01-01', 1, 40, 'scheduled', '2026-08-24')"
            )

    with client:
        queue = client.get("/api/review/queue")
        scored = client.post(
            "/api/review/items/1",
            json={"score": 80},
            headers={"Idempotency-Key": "review-1"},
        )
        replay = client.post(
            "/api/review/items/1",
            json={"score": 80},
            headers={"Idempotency-Key": "review-1"},
        )

    assert queue.status_code == 200
    assert [item["id"] for item in queue.json()["items"]] == [1]
    assert scored.status_code == 200
    assert scored.json()["interval_days"] == 3
    assert replay.json() == scored.json()


def test_review_intervals_use_an_injected_local_date_and_clamp_at_both_bounds(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO review_items "
                "(concept_id, lesson_id, exercise_id, due_on, interval_days, last_score, status, updated_at) "
                "VALUES ('variables', 'python-foundations-hello-world', "
                "'python-foundations-hello-world-k01', '2026-01-01', 1, 0, 'scheduled', '2026-01-01')"
            )

    result = score_review(
        database_path,
        repository=client.app.state.content_service.repository,
        review_item_id=1,
        score=Decimal("80"),
        idempotency_key="injected-date",
        today=date(2026, 1, 1),
    )

    assert result["interval_days"] == 3
    assert result["due_on"] == "2026-01-04"
    assert next_interval(1, Decimal("59.99")) == 1
    assert next_interval(3, Decimal("60")) == 3
    assert next_interval(60, Decimal("80")) == 60


def test_repeated_wrong_attempts_keep_one_active_review_item(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    payload = {
        "lesson_id": "python-foundations-hello-world",
        "exercise_id": "python-foundations-hello-world-k01",
        "answer": "b",
        "hint_level": "none",
    }
    with client:
        first = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "wrong-one"})
        second = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "wrong-two"})
    with closing(sqlite3.connect(database_path)) as connection:
        attempts = connection.execute("SELECT COUNT(*) FROM attempts").fetchone()
        review_items = connection.execute("SELECT COUNT(*) FROM review_items").fetchone()
    assert first.status_code == second.status_code == 200
    assert attempts == (2,)
    assert review_items == (1,)


def test_assessment_uses_its_injected_date_for_new_wrong_answer_review_items(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    record_attempt(
        database_path,
        repository=client.app.state.content_service.repository,
        lesson_id="python-foundations-hello-world",
        exercise_id="python-foundations-hello-world-k01",
        answer="b",
        normalized_result=None,
        hint_level="none",
        idempotency_key="injected-wrong",
        today=date(2026, 1, 2),
    )
    with closing(sqlite3.connect(database_path)) as connection:
        due_on = connection.execute("SELECT due_on FROM review_items").fetchone()
    assert due_on == ("2026-01-02",)


@pytest.mark.parametrize("score", [Decimal("-0.01"), Decimal("100.01")])
def test_review_scoring_rejects_scores_outside_the_supported_range(tmp_path: Path, score: Decimal) -> None:
    client, database_path = learning_client(tmp_path)

    with pytest.raises(ApiError) as error:
        score_review(
            database_path,
            repository=client.app.state.content_service.repository,
            review_item_id=1,
            score=score,
            idempotency_key=f"invalid-score-{score}",
        )

    assert error.value.code == "invalid_review_score"


def test_review_scoring_rejects_an_item_that_is_not_pending(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)

    with pytest.raises(ApiError) as error:
        score_review(
            database_path,
            repository=client.app.state.content_service.repository,
            review_item_id=999,
            score=Decimal("80"),
            idempotency_key="unknown-review-item",
            today=date(2026, 1, 1),
        )

    assert error.value.code == "unknown_review_item"


def test_review_scoring_keeps_progressing_when_the_original_lesson_is_unavailable(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO review_items "
                "(concept_id, lesson_id, exercise_id, due_on, interval_days, last_score, status, updated_at) "
                "VALUES ('orphaned', 'removed-lesson', 'removed-exercise', '2026-01-01', 1, 0, 'scheduled', '2026-01-01')"
            )

    result = score_review(
        database_path,
        repository=client.app.state.content_service.repository,
        review_item_id=1,
        score=Decimal("80"),
        idempotency_key="orphaned-review-item",
        today=date(2026, 1, 1),
    )

    assert result["experience_candidate"] is False
    assert result["due_on"] == "2026-01-04"
