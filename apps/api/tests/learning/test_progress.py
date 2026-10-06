from __future__ import annotations

import sqlite3
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content"))

from hard_api.db import migrations
from hard_api.main import create_app
from hard_api.runners.contracts import CompileResult, RunResult, RunStatus, Submission, TestResult as RunnerTestResult
from hard_api.runners.manager import RunManager
from test_catalog import make_settings, write_python_fixture


class SnapshotBackup:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def create_snapshot(self, database_path: Path) -> Path:
        self.directory.mkdir(exist_ok=True)
        snapshot = self.directory / f"{database_path.stem}-{len(list(self.directory.glob('*.db')))}.db"
        with closing(sqlite3.connect(database_path)) as source, closing(sqlite3.connect(snapshot)) as destination:
            source.backup(destination)
        return snapshot

    def restore_snapshot(self, snapshot_path: Path, database_path: Path) -> None:
        with closing(sqlite3.connect(snapshot_path)) as source, closing(sqlite3.connect(database_path)) as destination:
            source.backup(destination)


class FixtureRunner:
    """Deterministic server-side runner used by learning API tests only."""

    def run(self, submission: Submission, _workspace: Path, _cancellation: threading.Event) -> RunResult:
        return RunResult(
            status=RunStatus.SUCCEEDED,
            compile=CompileResult(passed=True),
            tests=RunnerTestResult(
                visible_passed=len(submission.visible_tests),
                visible_total=len(submission.visible_tests),
                hidden_passed=len(submission.hidden_tests),
                hidden_total=len(submission.hidden_tests),
            ),
            duration_ms=12,
        )


def learning_client(tmp_path: Path) -> tuple[TestClient, Path]:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    database_path = tmp_path / "database" / "hard.db"
    migrations.migrate_database(database_path, backup_provider=SnapshotBackup(tmp_path / "snapshots"))
    settings = replace(make_settings(content_root), database_path=database_path, data_dir=database_path.parent)
    app = create_app(settings)
    app.state.runner_manager.shutdown()
    app.state.runner_manager = RunManager(settings.runner_work_dir, adapters={"python": FixtureRunner()})
    return TestClient(app), database_path


def submit_trusted_code_job(
    client: TestClient,
    *,
    lesson_id: str,
    exercise_id: str,
    source_code: str,
    idempotency_key: str,
) -> str:
    submitted = client.post(
        "/api/runners/submissions",
        json={"lesson_id": lesson_id, "exercise_id": exercise_id, "source_code": source_code},
        headers={"Idempotency-Key": f"runner:{idempotency_key}"},
    )
    assert submitted.status_code == 200
    job_id = str(submitted.json()["id"])
    client.app.state.runner_manager.wait(job_id, timeout=5)
    return job_id


def record_trusted_code_attempt(
    client: TestClient,
    *,
    lesson_id: str,
    exercise_id: str,
    source_code: str,
    idempotency_key: str,
    hint_level: str = "none",
):
    job_id = submit_trusted_code_job(
        client,
        lesson_id=lesson_id,
        exercise_id=exercise_id,
        source_code=source_code,
        idempotency_key=idempotency_key,
    )
    return client.post(
        "/api/assessment/attempts",
        json={
            "lesson_id": lesson_id,
            "exercise_id": exercise_id,
            "runner_job_id": job_id,
            "hint_level": hint_level,
        },
        headers={"Idempotency-Key": idempotency_key},
    )


def test_progress_is_monotonic_idempotent_and_rejects_key_conflicts(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)
    with client:
        first = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 20, "time_spent_seconds": 120},
            headers={"Idempotency-Key": "read-1"},
        )
        replay = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 20, "time_spent_seconds": 120},
            headers={"Idempotency-Key": "read-1"},
        )
        lower_position = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 10, "time_spent_seconds": 60},
            headers={"Idempotency-Key": "read-2"},
        )
        conflict = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 21, "time_spent_seconds": 1},
            headers={"Idempotency-Key": "read-1"},
        )
        unknown = client.patch(
            "/api/progress/lessons/python-foundations-missing",
            json={"position": 1, "time_spent_seconds": 1},
            headers={"Idempotency-Key": "missing"},
        )

    assert first.status_code == 200
    assert replay.json() == first.json()
    assert lower_position.json()["position"] == 20
    assert lower_position.json()["time_spent_seconds"] == 180
    assert lower_position.json()["status"] == "in_progress"
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "unknown_lesson"
    with closing(sqlite3.connect(database_path)) as connection:
        progress_rows = connection.execute("SELECT COUNT(*) FROM lesson_progress").fetchone()
        key_rows = connection.execute("SELECT COUNT(*) FROM idempotency_keys").fetchone()
    assert progress_rows == (1,)
    assert key_rows == (2,)


def test_concurrent_progress_replays_create_one_business_record(tmp_path: Path) -> None:
    client, database_path = learning_client(tmp_path)

    def submit() -> tuple[int, dict[str, object]]:
        response = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 20, "time_spent_seconds": 120},
            headers={"Idempotency-Key": "concurrent-read"},
        )
        return response.status_code, response.json()

    with client, ThreadPoolExecutor(max_workers=2) as executor:
        first, second = list(executor.map(lambda _index: submit(), range(2)))

    assert first[0] == second[0] == 200
    assert first[1] == second[1]
    with closing(sqlite3.connect(database_path)) as connection:
        progress_rows = connection.execute("SELECT COUNT(*) FROM lesson_progress").fetchone()
        key_rows = connection.execute("SELECT COUNT(*) FROM idempotency_keys").fetchone()
    assert progress_rows == (1,)
    assert key_rows == (1,)
