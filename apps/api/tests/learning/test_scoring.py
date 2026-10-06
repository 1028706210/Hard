from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from decimal import Decimal
import sqlite3
from types import SimpleNamespace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_progress import learning_client, record_trusted_code_attempt, submit_trusted_code_job

from hard_api.core.errors import ApiError
from hard_api.learning.scoring import _raw_score, _stored_normalized_result, apply_hint_penalty, weighted_score
from hard_api.runners.contracts import CompileResult, RunResult, RunStatus, Submission, TestResult as RunnerTestResult
from hard_api.runners.manager import RunManager


class PassingRunner:
    def run(self, submission: Submission, _workspace: Path, _cancellation: object) -> RunResult:
        return RunResult(
            status=RunStatus.SUCCEEDED,
            compile=CompileResult(passed=True),
            tests=RunnerTestResult(
                visible_passed=len(submission.visible_tests),
                visible_total=len(submission.visible_tests),
                hidden_passed=len(submission.hidden_tests),
                hidden_total=len(submission.hidden_tests),
            ),
            duration_ms=7,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("score", True),
        ("score", "100"),
        ("passed", "true"),
        ("visible_tests_passed", True),
        ("visible_tests_total", "4"),
        ("hidden_test_failures", -1),
        ("hidden_test_failures", [3]),
        ("compile_error_category", {"kind": "syntax"}),
        ("compile_error_category", "x" * 129),
    ],
)
def test_attempt_rejects_invalid_normalized_result_field_types(
    tmp_path: Path, field: str, value: object
) -> None:
    client, _database_path = learning_client(tmp_path)
    normalized_result: dict[str, object] = {"score": 100, field: value}

    with client:
        response = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-c01",
                "normalized_result": normalized_result,
                "hint_level": "none",
            },
            headers={"Idempotency-Key": f"invalid-normalized-{field}-{type(value).__name__}"},
        )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_normalized_result"


def test_code_attempt_requires_a_completed_matching_server_runner_job_and_rejects_client_scores(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    manager = RunManager(tmp_path / "trusted-runner-work", adapters={"python": PassingRunner()})
    client.app.state.runner_manager.shutdown()
    client.app.state.runner_manager = manager
    direct_payload = {
        "lesson_id": "python-foundations-hello-world",
        "exercise_id": "python-foundations-hello-world-c01",
        "normalized_result": {"score": 100, "source_code": "print('forged')"},
        "hint_level": "none",
    }

    with client:
        rejected = client.post("/api/assessment/attempts", json=direct_payload, headers={"Idempotency-Key": "forged"})
        queued = client.post(
            "/api/runners/submissions",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-c01",
                "source_code": "print('trusted')",
            },
            headers={"Idempotency-Key": "runner-source"},
        )
        job_id = queued.json()["id"]
        manager.wait(job_id, timeout=5)
        trusted = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-c01",
                "runner_job_id": job_id,
                "hint_level": "none",
            },
            headers={"Idempotency-Key": "trusted"},
        )
        mismatched = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-challenge",
                "runner_job_id": job_id,
                "hint_level": "none",
            },
            headers={"Idempotency-Key": "mismatched"},
        )

    assert rejected.status_code == 400
    assert rejected.json()["error"]["code"] == "runner_result_required"
    assert trusted.status_code == 200
    assert trusted.json()["question_score"] == 100
    assert mismatched.status_code == 400
    assert mismatched.json()["error"]["code"] == "runner_job_mismatch"
    manager.shutdown()


def test_attempt_applies_hint_penalties_and_hides_private_answers(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    with client:
        light_hint = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-k01",
                "answer": "a",
                "hint_level": "light",
            },
            headers={"Idempotency-Key": "attempt-light"},
        )
        revealed = client.post(
            "/api/assessment/attempts",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-k02",
                "answer": "a",
                "hint_level": "revealed",
            },
            headers={"Idempotency-Key": "attempt-revealed"},
        )

    assert light_hint.status_code == 200
    assert light_hint.json()["question_score"] == 85.0
    assert revealed.status_code == 200
    assert revealed.json()["question_score"] == 0.0
    for forbidden in ("reference_answer", "reference_solution", "hidden_tests", "private"):
        assert forbidden not in light_hint.text


def test_attempt_replay_is_idempotent_and_reused_key_with_new_body_conflicts(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    payload = {
        "lesson_id": "python-foundations-hello-world",
        "exercise_id": "python-foundations-hello-world-k01",
        "answer": "a",
        "hint_level": "none",
    }
    with client:
        first = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "same"})
        replay = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "same"})
        conflict = client.post(
            "/api/assessment/attempts",
            json={**payload, "answer": "b"},
            headers={"Idempotency-Key": "same"},
        )

    assert first.status_code == replay.status_code == 200
    assert replay.json() == first.json()
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"


def test_code_attempt_rejects_client_normalized_results_before_any_business_write(tmp_path: Path) -> None:
    client, _database_path = learning_client(tmp_path)
    payload = {
        "lesson_id": "python-foundations-hello-world",
        "exercise_id": "python-foundations-hello-world-c01",
        "hint_level": "none",
        "normalized_result": {
            "score": 100,
            "source_code": "print('one')",
            "language": "python",
            "duration_ms": 12,
            "unknown_nested": {"message": "not persisted"},
        },
    }
    with client:
        rejected = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "code-body"})
        trusted = record_trusted_code_attempt(
            client,
            lesson_id="python-foundations-hello-world",
            exercise_id="python-foundations-hello-world-c01",
            source_code="print('one')",
            idempotency_key="code-body",
        )

    assert rejected.status_code == 400
    assert rejected.json()["error"]["code"] == "runner_result_required"
    assert trusted.status_code == 200


def test_fixed_category_weights_include_missing_categories_and_all_hint_levels() -> None:
    questions = [
        SimpleNamespace(id="knowledge", type="knowledge"),
        SimpleNamespace(id="code", type="code"),
        SimpleNamespace(id="challenge", type="challenge"),
        SimpleNamespace(id="scenario", type="scenario"),
    ]
    score, categories = weighted_score(
        questions,
        {"knowledge": 100, "code": 100, "challenge": 100, "scenario": 100},
    )
    missing_score, missing_categories = weighted_score(questions[:-1], {"knowledge": 100, "code": 100, "challenge": 100})

    assert score == 100
    assert categories == {"knowledge": 100, "code": 100, "challenge": 100, "scenario": 100}
    assert missing_score == 90
    assert missing_categories["scenario"] == 0
    assert apply_hint_penalty(100, "none") == 100
    assert apply_hint_penalty(100, "light") == 85
    assert apply_hint_penalty(100, "strong") == 60
    assert apply_hint_penalty(100, "revealed") == 0


def test_hint_penalty_rejects_unknown_hint_levels() -> None:
    with pytest.raises(ApiError) as error:
        apply_hint_penalty(100, "spoiler")

    assert error.value.code == "invalid_hint_level"


@pytest.mark.parametrize(
    ("result", "requires_score", "error_code"),
    [
        ({"score": "NaN"}, False, "invalid_normalized_result"),
        ({}, True, "missing_normalized_result"),
        ({"compile_error_category": "bad\x00category"}, False, "invalid_normalized_result"),
    ],
)
def test_normalized_code_results_reject_nonfinite_missing_and_control_values(
    result: dict[str, object], requires_score: bool, error_code: str
) -> None:
    with pytest.raises(ApiError) as error:
        _stored_normalized_result(result, requires_score=requires_score)

    assert error.value.code == error_code


@pytest.mark.parametrize(
    ("lesson_id", "exercise_id", "error_code"),
    [
        ("python-foundations-hello-world", "missing-exercise", "unknown_exercise"),
        ("missing-lesson", "python-foundations-hello-world-k01", "unknown_lesson"),
    ],
)
def test_attempt_rejects_unknown_lesson_and_exercise(
    tmp_path: Path, lesson_id: str, exercise_id: str, error_code: str
) -> None:
    client, _database_path = learning_client(tmp_path)

    with client:
        response = client.post(
            "/api/assessment/attempts",
            json={"lesson_id": lesson_id, "exercise_id": exercise_id, "answer": "a", "hint_level": "none"},
            headers={"Idempotency-Key": f"unknown-{lesson_id}"},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == error_code


def test_code_result_normalization_requires_a_score_rejects_nonfinite_scores_and_preserves_valid_categories() -> None:
    with pytest.raises(ApiError) as missing_score:
        _stored_normalized_result(None, requires_score=True)
    with pytest.raises(ApiError) as nonfinite_score:
        _stored_normalized_result({"score": float("nan")}, requires_score=False)

    stored = _stored_normalized_result({"compile_error_category": "syntax"}, requires_score=False)

    assert missing_score.value.code == "missing_normalized_result"
    assert nonfinite_score.value.code == "invalid_normalized_result"
    assert stored == {"compile_error_category": "syntax"}


def test_code_questions_cannot_be_scored_without_a_trusted_runner_score() -> None:
    question = SimpleNamespace(type="code")

    with pytest.raises(ApiError) as error:
        _raw_score(question, answer=None, normalized_result=None)

    assert error.value.code == "missing_normalized_result"


def test_code_result_normalization_rejects_decimal_values_that_cannot_be_reparsed() -> None:
    class UnparseableDecimal(Decimal):
        def __str__(self) -> str:
            return "not-a-decimal"

    with pytest.raises(ApiError) as error:
        _stored_normalized_result({"score": UnparseableDecimal("1")}, requires_score=False)

    assert error.value.code == "invalid_normalized_result"


def test_completing_every_weighted_category_awards_the_first_module_mastery_badge(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with client:
        for suffix in ("k01", "k02", "k03"):
            response = client.post(
                "/api/assessment/attempts",
                json={
                    "lesson_id": "python-foundations-hello-world",
                    "exercise_id": f"python-foundations-hello-world-{suffix}",
                    "answer": "a",
                    "hint_level": "none",
                },
                headers={"Idempotency-Key": f"mastery-{suffix}"},
            )
            assert response.status_code == 200
        for suffix in ("c01", "challenge"):
            response = record_trusted_code_attempt(
                client,
                lesson_id="python-foundations-hello-world",
                exercise_id=f"python-foundations-hello-world-{suffix}",
                source_code="print('complete')",
                idempotency_key=f"mastery-{suffix}",
            )
            assert response.status_code == 200

    with closing(sqlite3.connect(database_path)) as connection:
        badges = connection.execute("SELECT code FROM achievements ORDER BY code").fetchall()
    assert badges == [("first_lesson",), ("first_module_mastery",)]


def test_concurrent_attempt_replay_creates_one_attempt_and_snapshot(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    payload = {
        "lesson_id": "python-foundations-hello-world",
        "exercise_id": "python-foundations-hello-world-k01",
        "answer": "a",
        "hint_level": "none",
    }

    def submit() -> tuple[int, dict[str, object]]:
        response = client.post("/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "parallel"})
        return response.status_code, response.json()

    with client, ThreadPoolExecutor(max_workers=2) as executor:
        first, second = list(executor.map(lambda _index: submit(), range(2)))

    assert first[0] == second[0] == 200
    assert first[1] == second[1]
    with closing(sqlite3.connect(database_path)) as connection:
        attempts = connection.execute("SELECT COUNT(*) FROM attempts").fetchone()
        snapshots = connection.execute("SELECT COUNT(*) FROM mastery_snapshots").fetchone()
        events = connection.execute("SELECT COUNT(*) FROM experience_events").fetchone()
    assert attempts == (1,)
    assert snapshots == (3,)
    assert events == (1,)


def test_concurrent_lesson_completion_creates_one_unlock_experience_and_badge_group(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with client:
        for suffix in ("k01", "k02", "k03"):
            response = client.post(
                "/api/assessment/attempts",
                json={
                    "lesson_id": "python-foundations-hello-world",
                    "exercise_id": f"python-foundations-hello-world-{suffix}",
                    "answer": "a",
                    "hint_level": "none",
                },
                headers={"Idempotency-Key": f"setup-{suffix}"},
            )
            assert response.status_code == 200

        job_id = submit_trusted_code_job(
            client,
            lesson_id="python-foundations-hello-world",
            exercise_id="python-foundations-hello-world-c01",
            source_code="print('one')",
            idempotency_key="complete-once",
        )
        payload = {
            "lesson_id": "python-foundations-hello-world",
            "exercise_id": "python-foundations-hello-world-c01",
            "runner_job_id": job_id,
            "hint_level": "none",
        }

        def submit() -> tuple[int, dict[str, object]]:
            response = client.post(
                "/api/assessment/attempts", json=payload, headers={"Idempotency-Key": "complete-once"}
            )
            return response.status_code, response.json()

        with ThreadPoolExecutor(max_workers=2) as executor:
            first, second = list(executor.map(lambda _index: submit(), range(2)))

    assert first[0] == second[0] == 200
    assert first[1] == second[1]
    with closing(sqlite3.connect(database_path)) as connection:
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            for table in ("attempts", "mastery_snapshots", "experience_events", "achievements")
        }
    assert counts == {
        "attempts": (4,),
        "mastery_snapshots": (12,),
        "experience_events": (6,),
        "achievements": (1,),
    }
