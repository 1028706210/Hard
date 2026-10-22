from __future__ import annotations

import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from hard_api.runners.contracts import Submission
from hard_api.runners.limits import MAX_SOURCE_BYTES, MAX_STDIN_BYTES, RunnerLimitError, validate_submission


@pytest.mark.parametrize(
    ("submission", "code"),
    [
        (Submission(language="python", files={"main.py": "pass"}), "invalid_idempotency_key"),
        (Submission(language="python", files={"main.py": "pass"}, idempotency_key="x" * 129), "invalid_idempotency_key"),
        (Submission(language="python", files={}, idempotency_key="valid"), "missing_source"),
        (Submission(language="python", files={"main.py": 1}, idempotency_key="valid"), "invalid_source"),  # type: ignore[arg-type]
        (Submission(language="python", files={"main.py": "x" * (MAX_SOURCE_BYTES + 1)}, idempotency_key="valid"), "source_too_large"),
        (Submission(language="python", files={"main.py": "pass"}, stdin=1, idempotency_key="valid"), "stdin_too_large"),  # type: ignore[arg-type]
        (Submission(language="python", files={"main.py": "pass"}, stdin="x" * (MAX_STDIN_BYTES + 1), idempotency_key="valid"), "stdin_too_large"),
    ],
)
def test_submission_limits_reject_every_invalid_boundary(submission: Submission, code: str) -> None:
    with pytest.raises(RunnerLimitError) as error:
        validate_submission(submission)

    assert error.value.code == code
