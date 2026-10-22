from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
from tempfile import TemporaryDirectory


MINIMUM_COVERAGE = 95
CORE_TARGETS = {
    "hard_api.runners": ("apps/api/tests/runners",),
    "hard_api.backup": ("apps/api/tests/backup",),
    "hard_api.learning.scoring": ("apps/api/tests/learning/test_scoring.py",),
    "hard_api.learning.review": ("apps/api/tests/learning/test_review.py",),
}


def run_gate(project_root: Path) -> int:
    with TemporaryDirectory() as temporary_directory:
        environment = {**os.environ, "COVERAGE_FILE": str(Path(temporary_directory) / ".coverage")}
        for module, tests in CORE_TARGETS.items():
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    *tests,
                    f"--cov={module}",
                    "--cov-branch",
                    f"--cov-fail-under={MINIMUM_COVERAGE}",
                    "--cov-report=term-missing",
                    "-p",
                    "no:cacheprovider",
                    "--disable-warnings",
                ],
                cwd=project_root,
                env=environment,
                check=False,
            )
            if completed.returncode:
                return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(run_gate(Path(__file__).resolve().parents[3]))
