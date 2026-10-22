from __future__ import annotations

import sys
import threading
import time
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content"))

from hard_api.main import create_app
from hard_api.core.config import Settings
from hard_api.db import migrations
from hard_api.backup.service import LocalBackupService
from hard_api.runners.csharp import CSharpRunner
from hard_api.runners.contracts import RunResult, RunStatus, Submission
from hard_api.runners.manager import RunManager
from test_catalog import make_settings, write_python_fixture


class BlockingAdapter:
    def __init__(self) -> None:
        self.release = threading.Event()
        self.started = threading.Event()
        self.two_running = threading.Event()
        self.running = 0
        self.maximum_running = 0
        self.lock = threading.Lock()

    def run(self, submission: Submission, workspace: Path, cancellation: threading.Event) -> RunResult:
        with self.lock:
            self.running += 1
            self.maximum_running = max(self.maximum_running, self.running)
            if self.running == 2:
                self.two_running.set()
        self.started.set()
        while not self.release.wait(0.01):
            if cancellation.is_set():
                break
        with self.lock:
            self.running -= 1
        return RunResult(status=RunStatus.SUCCEEDED, stdout="ok")


def _submission(key: str, source: str = "print('ok')") -> Submission:
    return Submission(language="fake", files={"main.py": source}, idempotency_key=key)


def test_manager_queues_at_two_workers_replays_keys_and_cleans_workspaces(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    root = tmp_path / "runner-work"
    manager = RunManager(root, adapters={"fake": adapter})
    first = manager.submit(_submission("one"))
    second = manager.submit(_submission("two"))
    third = manager.submit(_submission("three"))
    replay = manager.submit(_submission("one"))

    assert replay.id == first.id
    assert first.status in {RunStatus.QUEUED, RunStatus.RUNNING}
    assert third.status == RunStatus.QUEUED
    assert adapter.two_running.wait(timeout=2)
    adapter.release.set()
    first_done = manager.wait(first.id, timeout=5)
    second_done = manager.wait(second.id, timeout=5)
    third_done = manager.wait(third.id, timeout=5)

    assert [first_done.status, second_done.status, third_done.status] == [RunStatus.SUCCEEDED] * 3
    assert adapter.maximum_running == 2
    assert list(root.iterdir()) == []
    manager.shutdown()


def test_manager_returns_stable_limits_missing_tool_and_cancelled_results(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    manager = RunManager(tmp_path / "runner-work", adapters={"fake": adapter})
    too_large = manager.submit(_submission("large", "x" * (128 * 1024 + 1)))
    missing = manager.submit(Submission(language="missing", files={"main.py": "pass"}, idempotency_key="missing"))
    running = manager.submit(_submission("cancel"))
    assert adapter.started.wait(timeout=2)
    cancelled = manager.cancel(running.id)
    adapter.release.set()

    assert too_large.status == RunStatus.REJECTED
    assert too_large.result.error_code == "source_too_large"
    assert missing.status == RunStatus.TOOL_MISSING
    assert missing.result.error_code == "tool_missing"
    assert cancelled.status == RunStatus.CANCELLED
    assert manager.wait(running.id, timeout=5).status == RunStatus.CANCELLED
    manager.shutdown()


def test_runner_api_submits_queries_and_cancels_without_accepting_private_tests(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    settings = replace(make_settings(content_root), runner_work_dir=tmp_path / "runner-work")
    app = create_app(settings)
    adapter = BlockingAdapter()
    app.state.runner_manager = RunManager(settings.runner_work_dir, adapters={"python": adapter})

    with TestClient(app) as client:
        submitted = client.post(
            "/api/runners/submissions",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-c01",
                "source_code": "print('Hello, Hard!')",
                "stdin": "",
            },
            headers={"Idempotency-Key": "runner-api"},
        )
        replayed = client.post(
            "/api/runners/submissions",
            json={
                "lesson_id": "python-foundations-hello-world",
                "exercise_id": "python-foundations-hello-world-c01",
                "source_code": "print('Hello, Hard!')",
                "stdin": "",
            },
            headers={"Idempotency-Key": "runner-api"},
        )
        job_id = submitted.json()["id"]
        status = client.get(f"/api/runners/jobs/{job_id}")
        cancelled = client.delete(f"/api/runners/jobs/{job_id}")
        adapter.release.set()

    assert submitted.status_code == replayed.status_code == status.status_code == cancelled.status_code == 200
    assert submitted.json()["id"] == replayed.json()["id"]
    assert "hidden_tests" not in submitted.text
    assert "reference_solution" not in submitted.text
    app.state.runner_manager.shutdown()


def test_runner_http_and_openapi_keep_hidden_input_output_and_counts_private(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[4]
    settings = Settings(project_root=root, data_dir=tmp_path / "data", database_path=tmp_path / "data" / "hard.db", backup_dir=tmp_path / "backups", export_dir=tmp_path / "exports", runner_work_dir=tmp_path / "runner-work", content_dir=root / "content", toolchain_lock_path=root / "docs/setup/toolchain-lock.json")
    migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))
    app = create_app(settings)
    with TestClient(app) as client:
        created = client.post("/api/runners/submissions", json={"lesson_id": "python-foundations-introduction", "exercise_id": "python-foundations-introduction-c01", "source_code": "import sys\nvalue = sys.stdin.read()\nif value.startswith('__hard_hidden'):\n    print(value, end='')\nelse:\n    print('欢迎使用 Hard Python 课程！')", "stdin": ""}, headers={"Idempotency-Key": "hidden-echo"})
        job_id = created.json()["id"]
        job = app.state.runner_manager.wait(job_id, timeout=10)
        response = client.get(f"/api/runners/jobs/{job_id}")
        openapi = client.get("/openapi.json").json()

    assert created.status_code == response.status_code == 200
    assert job.status == RunStatus.FAILED
    assert "__hard_hidden_boundary__" not in response.text
    assert "__hard_hidden_failure__" not in response.text
    assert "hidden_passed" not in response.text
    assert "hidden_total" not in response.text
    result_schema = openapi["components"]["schemas"]["RunnerJobResponse"]["properties"]["result"]["anyOf"][0]
    assert result_schema == {"$ref": "#/components/schemas/PublicRunResult"}


def test_idempotency_conflict_does_not_displace_the_original_runner_job(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    manager = RunManager(tmp_path / "runner-work", adapters={"fake": adapter})
    original = manager.submit(_submission("same-key", "print('first')"))
    conflicting = manager.submit(_submission("same-key", "print('second')"))
    replay = manager.submit(_submission("same-key", "print('first')"))
    adapter.release.set()

    assert conflicting.status == RunStatus.REJECTED
    assert conflicting.result is not None and conflicting.result.error_code == "idempotency_conflict"
    assert replay.id == original.id
    assert manager.wait(original.id, timeout=5).status == RunStatus.SUCCEEDED
    manager.shutdown()


def test_cancelling_missing_or_finished_jobs_leaves_manager_state_unchanged(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    manager = RunManager(tmp_path / "runner-work", adapters={"fake": adapter})
    completed = manager.submit(_submission("completed"))
    adapter.release.set()
    manager.wait(completed.id, timeout=5)

    assert manager.cancel("missing-job") is None
    assert manager.cancel(completed.id) is completed
    assert completed.status == RunStatus.SUCCEEDED
    manager.shutdown()


def test_wait_reports_timeout_for_running_jobs_and_key_error_for_unknown_jobs(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    manager = RunManager(tmp_path / "runner-work", adapters={"fake": adapter})
    running = manager.submit(_submission("slow"))
    assert adapter.started.wait(timeout=2)

    with pytest.raises(TimeoutError, match=running.id):
        manager.wait(running.id, timeout=0.001)
    with pytest.raises(KeyError, match="missing-job"):
        manager.wait("missing-job", timeout=0.001)

    adapter.release.set()
    manager.wait(running.id, timeout=5)
    manager.shutdown()


@pytest.mark.parametrize(
    ("failure", "expected_status", "expected_code"),
    [
        (FileNotFoundError(), RunStatus.TOOL_MISSING, "tool_missing"),
        (RuntimeError("adapter failed"), RunStatus.FAILED, "runner_failed"),
    ],
)
def test_manager_normalizes_adapter_failures(
    tmp_path: Path, failure: Exception, expected_status: RunStatus, expected_code: str
) -> None:
    class FailingAdapter:
        def run(self, _submission: Submission, _workspace: Path, _cancellation: threading.Event) -> RunResult:
            raise failure

    manager = RunManager(tmp_path / "runner-work", adapters={"fake": FailingAdapter()})
    job = manager.submit(_submission("failing-adapter"))
    completed = manager.wait(job.id, timeout=5)

    assert completed.status == expected_status
    assert completed.result is not None and completed.result.error_code == expected_code
    manager.shutdown()


def test_manager_rejects_unsafe_submission_paths_after_creating_the_workspace(tmp_path: Path) -> None:
    manager = RunManager(tmp_path / "runner-work", adapters={"fake": BlockingAdapter()})
    job = manager.submit(Submission(language="fake", files={"../unsafe.py": "pass"}, idempotency_key="unsafe-path"))
    completed = manager.wait(job.id, timeout=5)

    assert completed.status == RunStatus.REJECTED
    assert completed.result is not None and completed.result.error_code == "invalid_submission_path"
    manager.shutdown()


def test_manager_cancels_a_queued_job_before_its_worker_starts(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    manager = RunManager(tmp_path / "runner-work", adapters={"fake": adapter})
    first = manager.submit(_submission("first"))
    second = manager.submit(_submission("second"))
    queued = manager.submit(_submission("queued"))
    assert adapter.two_running.wait(timeout=2)

    manager.cancel(queued.id)
    adapter.release.set()

    assert manager.wait(first.id, timeout=5).status == RunStatus.SUCCEEDED
    assert manager.wait(second.id, timeout=5).status == RunStatus.SUCCEEDED
    assert manager.wait(queued.id, timeout=5).status == RunStatus.CANCELLED
    manager.shutdown()


def test_manager_shutdown_cancels_active_jobs(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    manager = RunManager(tmp_path / "runner-work", adapters={"fake": adapter})
    running = manager.submit(_submission("shutdown"))
    assert adapter.started.wait(timeout=2)

    manager.shutdown()

    assert running.status == RunStatus.CANCELLED
    assert running.result is not None and running.result.error_code == "cancelled"


def test_manager_cleans_up_after_workspace_factory_rejects_a_protected_root(tmp_path: Path) -> None:
    workspace_root = tmp_path / "runner-work"
    manager = RunManager(
        workspace_root,
        adapters={"fake": BlockingAdapter()},
        protected_paths=(workspace_root,),
    )
    job = manager.submit(_submission("protected-root"))
    completed = manager.wait(job.id, timeout=5)

    assert completed.status == RunStatus.REJECTED
    assert completed.result is not None and completed.result.error_code == "unsafe_workspace_root"
    manager.shutdown()


def test_manager_cancels_queued_csharp_jobs_without_creating_workspace(tmp_path: Path) -> None:
    adapter = BlockingAdapter()
    root = tmp_path / "runner-work"
    manager = RunManager(
        root,
        adapters={"fake": adapter, "csharp": CSharpRunner(run_timeout_seconds=30)},
    )
    first = manager.submit(_submission("first"))
    second = manager.submit(_submission("second"))
    queued = manager.submit(
        Submission(language="csharp", files={"main.py": "while (true) {}"}, idempotency_key="csharp-queued")
    )
    assert adapter.two_running.wait(timeout=2)

    manager.cancel(queued.id)
    adapter.release.set()

    assert manager.wait(first.id, timeout=5).status == RunStatus.SUCCEEDED
    assert manager.wait(second.id, timeout=5).status == RunStatus.SUCCEEDED
    assert manager.wait(queued.id, timeout=5).status == RunStatus.CANCELLED
    assert list(root.iterdir()) == []
    manager.shutdown()


def test_manager_cancels_running_csharp_jobs_and_cleans_workspace(tmp_path: Path) -> None:
    root = tmp_path / "runner-work"
    manager = RunManager(root, adapters={"csharp": CSharpRunner(run_timeout_seconds=30)})
    job = manager.submit(
        Submission(language="csharp", files={"main.py": "while (true) {}"}, idempotency_key="csharp-running")
    )
    for _ in range(200):
        current = manager.get(job.id)
        if current is not None and current.status == RunStatus.RUNNING:
            break
        time.sleep(0.01)

    cancelled = manager.cancel(job.id)
    completed = manager.wait(job.id, timeout=20)

    assert cancelled is not None
    assert completed.status == RunStatus.CANCELLED
    assert completed.result is not None and completed.result.error_code == "cancelled"
    assert list(root.iterdir()) == []
    manager.shutdown()
