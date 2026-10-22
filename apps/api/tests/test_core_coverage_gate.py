from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from core_coverage_gate import CORE_TARGETS, MINIMUM_COVERAGE, run_gate


def test_core_coverage_gate_requires_95_percent_for_every_target(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fail_first(command: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=17)

    monkeypatch.setattr("core_coverage_gate.subprocess.run", fail_first)

    assert run_gate(tmp_path) == 17
    assert len(calls) == 1
    assert f"--cov={next(iter(CORE_TARGETS))}" in calls[0]
    assert f"--cov-fail-under={MINIMUM_COVERAGE}" in calls[0]


def test_core_coverage_gate_covers_runner_backup_scoring_and_review(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def pass_all(command: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("core_coverage_gate.subprocess.run", pass_all)

    assert run_gate(tmp_path) == 0
    assert [next(value.removeprefix("--cov=") for value in command if value.startswith("--cov=")) for command in calls] == list(CORE_TARGETS)
