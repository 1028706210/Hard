from __future__ import annotations

from hard_api.runners.contracts import Submission


MAX_SOURCE_BYTES = 128 * 1024
COMPILE_TIMEOUT_SECONDS = 15
RUN_TIMEOUT_SECONDS = 5
MAX_OUTPUT_BYTES = 64 * 1024
MAX_STDIN_BYTES = 64 * 1024
MAX_CONCURRENT_RUNS = 2


class RunnerLimitError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def validate_submission(submission: Submission) -> None:
    if not submission.idempotency_key or len(submission.idempotency_key) > 128:
        raise RunnerLimitError("invalid_idempotency_key")
    if not submission.files:
        raise RunnerLimitError("missing_source")
    total = 0
    for content in submission.files.values():
        if not isinstance(content, str):
            raise RunnerLimitError("invalid_source")
        total += len(content.encode("utf-8"))
    if total > MAX_SOURCE_BYTES:
        raise RunnerLimitError("source_too_large")
    if not isinstance(submission.stdin, str) or len(submission.stdin.encode("utf-8")) > MAX_STDIN_BYTES:
        raise RunnerLimitError("stdin_too_large")
