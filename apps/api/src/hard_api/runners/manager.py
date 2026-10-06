from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from pathlib import Path
import threading
from typing import Protocol
from uuid import uuid4

from hard_api.runners.contracts import RunJob, RunResult, RunStatus, Submission
from hard_api.runners.limits import MAX_CONCURRENT_RUNS, RunnerLimitError, validate_submission
from hard_api.runners.workspace import WorkspaceError, WorkspaceFactory, cleanup_workspace, write_submission_files


class RunnerAdapter(Protocol):
    def run(self, submission: Submission, workspace: Path, cancellation: threading.Event) -> RunResult: ...


class RunManager:
    def __init__(
        self,
        workspace_root: Path,
        *,
        adapters: dict[str, RunnerAdapter],
        protected_paths: tuple[Path, ...] = (),
    ) -> None:
        self._adapters = dict(adapters)
        self._workspace_factory = WorkspaceFactory(workspace_root, protected_paths=protected_paths)
        self._jobs: dict[str, RunJob] = {}
        self._keys: dict[str, str] = {}
        self._fingerprints: dict[str, Submission] = {}
        self._events: dict[str, threading.Event] = {}
        self._futures: dict[str, Future[None]] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_RUNS, thread_name_prefix="hard-runner")

    def submit(self, submission: Submission) -> RunJob:
        with self._lock:
            existing = self._keys.get(submission.idempotency_key)
            if existing is not None:
                if self._fingerprints.get(submission.idempotency_key) != submission:
                    return self._terminal_job(submission, RunStatus.REJECTED, "idempotency_conflict", replace_key=False)
                return self._jobs[existing]
            try:
                validate_submission(submission)
            except RunnerLimitError as error:
                return self._terminal_job(submission, RunStatus.REJECTED, error.code)
            if submission.language not in self._adapters:
                return self._terminal_job(submission, RunStatus.TOOL_MISSING, "tool_missing")
            job = RunJob(id=uuid4().hex, status=RunStatus.QUEUED, _submission=submission)
            self._jobs[job.id] = job
            self._keys[submission.idempotency_key] = job.id
            self._fingerprints[submission.idempotency_key] = submission
            self._events[job.id] = threading.Event()
            self._futures[job.id] = self._executor.submit(self._run, job.id)
            return job

    def get(self, job_id: str) -> RunJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> RunJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            if job.status not in {RunStatus.QUEUED, RunStatus.RUNNING}:
                return job
            job.cancellation_requested = True
            self._events[job_id].set()
            job.status = RunStatus.CANCELLED
            job.result = RunResult(status=RunStatus.CANCELLED, error_code="cancelled")
            return job

    def wait(self, job_id: str, *, timeout: float) -> RunJob:
        future = self._futures.get(job_id)
        if future is not None:
            try:
                future.result(timeout=timeout)
            except TimeoutError as error:
                raise TimeoutError(job_id) from error
        job = self.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return job

    def shutdown(self) -> None:
        with self._lock:
            for job_id, event in self._events.items():
                event.set()
                job = self._jobs[job_id]
                if job.status in {RunStatus.QUEUED, RunStatus.RUNNING}:
                    job.status = RunStatus.CANCELLED
                    job.result = RunResult(status=RunStatus.CANCELLED, error_code="cancelled")
        self._executor.shutdown(wait=True, cancel_futures=False)

    def _terminal_job(self, submission: Submission, status: RunStatus, error_code: str, *, replace_key: bool = True) -> RunJob:
        job = RunJob(id=uuid4().hex, status=status, result=RunResult(status=status, error_code=error_code))
        self._jobs[job.id] = job
        if replace_key:
            self._keys[submission.idempotency_key] = job.id
            self._fingerprints[submission.idempotency_key] = submission
        return job

    def _run(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            event = self._events[job_id]
            submission = job._submission
            if event.is_set():
                return
            job.status = RunStatus.RUNNING
        assert submission is not None
        workspace: Path | None = None
        try:
            workspace = self._workspace_factory.create()
            write_submission_files(workspace, dict(submission.files))
            result = self._adapters[submission.language].run(submission, workspace, event)
        except WorkspaceError as error:
            result = RunResult(status=RunStatus.REJECTED, error_code=error.code)
        except FileNotFoundError:
            result = RunResult(status=RunStatus.TOOL_MISSING, error_code="tool_missing")
        except Exception:
            result = RunResult(status=RunStatus.FAILED, error_code="runner_failed")
        finally:
            if workspace is not None:
                cleanup_workspace(workspace)
        with self._lock:
            if event.is_set():
                job.status = RunStatus.CANCELLED
                job.result = RunResult(status=RunStatus.CANCELLED, error_code="cancelled")
            else:
                job.status = result.status
                job.result = result
