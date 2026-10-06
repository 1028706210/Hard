from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_progress import learning_client, record_trusted_code_attempt

from hard_api.learning.mastery import lesson_passed, mastered


def test_lesson_pass_uses_weighted_categories_and_retries_do_not_lower_mastery_or_repeat_experience(
    tmp_path: Path,
) -> None:
    client, database_path = learning_client(tmp_path)
    knowledge_payloads = [
        {"exercise_id": "python-foundations-hello-world-k01", "answer": "a"},
        {"exercise_id": "python-foundations-hello-world-k02", "answer": "a"},
        {"exercise_id": "python-foundations-hello-world-k03", "answer": "a"},
    ]
    with client:
        responses = [
            client.post(
                "/api/assessment/attempts",
                json={
                    "lesson_id": "python-foundations-hello-world",
                    "hint_level": "none",
                    **payload,
                },
                headers={"Idempotency-Key": f"pass-{index}"},
            )
            for index, payload in enumerate(knowledge_payloads)
        ]
        responses.extend(
            [
                record_trusted_code_attempt(
                    client,
                    lesson_id="python-foundations-hello-world",
                    exercise_id="python-foundations-hello-world-c01",
                    source_code="print('Hello, Hard!')",
                    idempotency_key="pass-3",
                ),
                record_trusted_code_attempt(
                    client,
                    lesson_id="python-foundations-hello-world",
                    exercise_id="python-foundations-hello-world-challenge",
                    source_code="print('Hello')\nprint('Hard')",
                    idempotency_key="pass-4",
                ),
            ]
        )
        retry = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-k01",
                "answer": "b",
                "hint_level": "none",
            },
            headers={"Idempotency-Key": "lower-retry"},
        )

    assert all(response.status_code == 200 for response in responses)
    assert responses[-1].json()["total_score"] == 90.0
    assert responses[-1].json()["passed"] is True
    assert responses[3].json()["total_score"] == 70.0
    assert responses[3].json()["experience_candidate"] is True
    assert responses[-1].json()["experience_candidate"] is True
    assert retry.status_code == 200
    assert retry.json()["total_score"] == 90.0
    assert retry.json()["experience_candidate"] is False
    with closing(sqlite3.connect(database_path)) as connection:
        snapshots = connection.execute("SELECT COUNT(*) FROM mastery_snapshots").fetchone()
        events = connection.execute("SELECT COUNT(*) FROM experience_events").fetchone()
        progress = connection.execute("SELECT status FROM lesson_progress").fetchone()
    assert snapshots == (18,)
    assert events == (8,)
    assert progress == ("completed",)


def test_pass_and_mastery_thresholds_use_unformatted_decimal_boundaries() -> None:
    from decimal import Decimal

    assert lesson_passed(Decimal("69.99")) is False
    assert lesson_passed(Decimal("70")) is True
    assert mastered(Decimal("84.99")) is False
    assert mastered(Decimal("85")) is True


def test_scoring_transaction_rolls_back_every_record_when_snapshot_write_fails(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    client = TestClient(client.app, raise_server_exceptions=False)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "CREATE TRIGGER reject_mastery_snapshot BEFORE INSERT ON mastery_snapshots "
                "BEGIN SELECT RAISE(ABORT, 'snapshot failure'); END"
            )

    with client:
        response = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-k01",
                "answer": "a",
                "hint_level": "none",
            },
            headers={"Idempotency-Key": "rollback-attempt"},
        )

    assert response.status_code == 500
    with closing(sqlite3.connect(database_path)) as connection:
        attempts = connection.execute("SELECT COUNT(*) FROM attempts").fetchone()
        progress = connection.execute("SELECT COUNT(*) FROM lesson_progress").fetchone()
        events = connection.execute("SELECT COUNT(*) FROM experience_events").fetchone()
        keys = connection.execute("SELECT COUNT(*) FROM idempotency_keys").fetchone()
    assert attempts == progress == events == keys == (0,)


def test_scoring_transaction_rolls_back_all_writes_when_badge_grant_fails(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    client = TestClient(client.app, raise_server_exceptions=False)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "CREATE TRIGGER reject_achievement BEFORE INSERT ON achievements "
                "BEGIN SELECT RAISE(ABORT, 'achievement failure'); END"
            )

    with client:
        for suffix, payload in (
            ("k01", {"answer": "a"}),
            ("k02", {"answer": "a"}),
            ("k03", {"answer": "a"}),
        ):
            response = client.post(
                "/api/assessment/attempts",
                json={
                    "lesson_id": "python-foundations-hello-world",
                    "exercise_id": f"python-foundations-hello-world-{suffix}",
                    "hint_level": "none",
                    **payload,
                },
                headers={"Idempotency-Key": f"before-badge-{suffix}"},
            )
            assert response.status_code == 200
        with closing(sqlite3.connect(database_path)) as connection:
            before = {
                table: connection.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
                for table in (
                    "attempts",
                    "submissions",
                    "lesson_progress",
                    "review_items",
                    "mastery_snapshots",
                    "experience_events",
                    "achievements",
                    "idempotency_keys",
                )
            }
        failed = record_trusted_code_attempt(
            client,
            lesson_id="python-foundations-hello-world",
            exercise_id="python-foundations-hello-world-c01",
            source_code="print('x')",
            idempotency_key="achievement-rollback",
        )

    assert failed.status_code == 500
    with closing(sqlite3.connect(database_path)) as connection:
        after = {
            table: connection.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
            for table in (
                "attempts",
                "submissions",
                "lesson_progress",
                "review_items",
                "mastery_snapshots",
                "experience_events",
                "achievements",
                "idempotency_keys",
            )
        }
    assert after == before
