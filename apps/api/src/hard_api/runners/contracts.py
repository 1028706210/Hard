from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    OUTPUT_OVERFLOW = "output_overflow"
    REJECTED = "rejected"
    TOOL_MISSING = "tool_missing"


@dataclass(frozen=True, slots=True)
class ExecutableTestCase:
    stdin: str = ""
    stdout: str | None = None
    exit_code: int = 0
    assertion: str | None = None


@dataclass(frozen=True, slots=True)
class Submission:
    language: str
    files: Mapping[str, str]
    stdin: str = ""
    visible_tests: tuple[str, ...] = ()
    hidden_tests: tuple[str, ...] = ()
    visible_test_cases: tuple[ExecutableTestCase, ...] = ()
    hidden_test_cases: tuple[ExecutableTestCase, ...] = ()
    idempotency_key: str = ""
    lesson_id: str = ""
    exercise_id: str = ""


@dataclass(frozen=True, slots=True)
class CompileResult:
    passed: bool
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TestResult:
    visible_passed: int = 0
    visible_total: int = 0
    hidden_passed: int = 0
    hidden_total: int = 0


@dataclass(frozen=True, slots=True)
class RunResult:
    status: RunStatus
    compile: CompileResult | None = None
    tests: TestResult | None = None
    stdout: str = ""
    stderr: str = ""
    diagnostics: tuple[str, ...] = ()
    duration_ms: int = 0
    error_code: str | None = None

    def public_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": self.status.value,
            "diagnostics": list(self._public_diagnostics()),
        }
        if self.compile is not None:
            payload["compile"] = {
                "passed": self.compile.passed,
            }
        if self.tests is not None:
            payload["tests"] = {
                "visible_passed": self.tests.visible_passed,
                "visible_total": self.tests.visible_total,
            }
        return payload

    def _public_diagnostics(self) -> tuple[str, ...]:
        if self.status == RunStatus.SUCCEEDED:
            return ()
        if self.error_code == "compile_failed":
            return ("编译未通过，请检查语法和代码结构。",)
        if self.error_code == "forbidden_import":
            return ("代码使用了不允许的高风险模块。",)
        if self.status == RunStatus.TIMED_OUT:
            return ("运行超时。",)
        if self.status == RunStatus.OUTPUT_OVERFLOW:
            return ("输出超过限制。",)
        if self.status == RunStatus.CANCELLED:
            return ("运行已取消。",)
        if self.status == RunStatus.TOOL_MISSING:
            return ("运行工具不可用。",)
        if self.status == RunStatus.REJECTED:
            return ("提交不符合运行要求。",)
        return ("代码未通过全部测试。",)


@dataclass(slots=True)
class RunJob:
    id: str
    status: RunStatus
    result: RunResult | None = None
    cancellation_requested: bool = False
    _submission: Submission | None = field(default=None, repr=False)

    @property
    def submission(self) -> Submission | None:
        """Server-only job provenance; this is never included in public payloads."""
        return self._submission

    def public_payload(self) -> dict[str, object]:
        return {
            "id": self.id,
            "status": self.status.value,
            "result": self.result.public_payload() if self.result is not None else None,
        }
