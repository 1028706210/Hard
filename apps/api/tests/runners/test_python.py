from __future__ import annotations

from pathlib import Path
import threading


import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from hard_api.content.parser import parse_exercises
from hard_api.runners.contracts import RunStatus, Submission
from hard_api.runners.manager import RunManager
from hard_api.runners.python import PythonRunner


FIXTURES = Path(__file__).parent / "fixtures" / "python"
PYTHON = Path("D:/DevTools/python/python.exe")


def _run(
    tmp_path: Path,
    source: str,
    *,
    stdin: str = "",
    visible_tests: tuple[str, ...] = (),
    hidden_tests: tuple[str, ...] = (),
    visible_test_cases=(),
    hidden_test_cases=(),
    runner: PythonRunner | None = None,
):
    root = tmp_path / "runner-work"
    manager = RunManager(root, adapters={"python": runner or PythonRunner()})
    job = manager.submit(
        Submission(
            language="python",
            files={"main.py": source},
            stdin=stdin,
            visible_tests=visible_tests,
            hidden_tests=hidden_tests,
            visible_test_cases=visible_test_cases,
            hidden_test_cases=hidden_test_cases,
            idempotency_key="python-test",
        )
    )
    result = manager.wait(job.id, timeout=10).result
    manager.shutdown()
    assert list(root.iterdir()) == []
    assert result is not None
    return result


def test_python_runner_executes_fixed_isolated_interpreter_with_stdin_and_safe_test_counts(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "success.py").read_text(encoding="utf-8"),
        stdin="Ada\n",
        visible_tests=("Hello, Ada!\n",),
        hidden_tests=("Hello, Ada!\n",),
    )

    assert result.status == RunStatus.SUCCEEDED
    assert result.compile is not None and result.compile.passed
    assert result.tests is not None
    assert (result.tests.visible_passed, result.tests.visible_total) == (1, 1)
    assert (result.tests.hidden_passed, result.tests.hidden_total) == (1, 1)
    assert result.stdout == "Hello, Ada!\n"


def test_python_runner_normalizes_syntax_and_assertion_failures_without_workspace_paths(tmp_path: Path) -> None:
    syntax = _run(tmp_path, (FIXTURES / "syntax_error.py").read_text(encoding="utf-8"))
    assertion = _run(tmp_path, "raise AssertionError('visible failure')")

    assert syntax.status == RunStatus.FAILED
    assert syntax.compile is not None and not syntax.compile.passed
    assert "语法错误" in syntax.diagnostics[0]
    assert "第 1 行" in syntax.diagnostics[0]
    assert "第 13 列" in syntax.diagnostics[0]
    assert str(tmp_path) not in syntax.diagnostics[0]
    assert assertion.status == RunStatus.FAILED
    assert "断言失败" in assertion.diagnostics[0]
    assert "AssertionError" in assertion.diagnostics[0]


def test_python_runner_enforces_timeout_output_and_missing_tool(tmp_path: Path) -> None:
    quick_limits = PythonRunner(run_timeout_seconds=0.2)
    timed_out = _run(tmp_path, "while True: pass", runner=quick_limits)
    overflow = _run(tmp_path, "print('x' * 70000)")
    missing = _run(tmp_path, "print('x')", runner=PythonRunner(executable=tmp_path / "missing.exe"))

    assert timed_out.status == RunStatus.TIMED_OUT
    assert overflow.status == RunStatus.OUTPUT_OVERFLOW
    assert missing.status == RunStatus.TOOL_MISSING


@pytest.mark.parametrize("module", ["subprocess", "socket", "ctypes"])
def test_python_runner_rejects_each_forbidden_import(module: str, tmp_path: Path) -> None:
    forbidden = _run(tmp_path, f"import {module}\nprint('not allowed')")

    assert forbidden.status == RunStatus.FAILED
    assert forbidden.error_code == "forbidden_import"
    assert forbidden.diagnostics == (f"禁止导入高风险模块：{module}。",)


def test_python_runner_hides_hidden_test_content_but_keeps_aggregate_count(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        "print('visible')",
        visible_tests=("visible\n",),
        hidden_tests=("HIDDEN_SENTINEL",),
    )

    assert result.status == RunStatus.FAILED
    assert result.tests is not None
    assert result.tests.hidden_passed == 0
    assert result.tests.hidden_total == 1
    assert "HIDDEN_SENTINEL" not in str(result.public_payload())


def test_official_reference_solution_uses_private_structured_cases_not_chinese_descriptions(tmp_path: Path) -> None:
    exercises = parse_exercises(Path("content/python/python-foundations/hello-world.exercises.json"))
    question = next(item for item in exercises.questions if item.id.endswith("-c01"))
    assert question.private is not None
    result = _run(
        tmp_path,
        question.private.reference_solution or "",
        visible_test_cases=tuple(question.private.visible_test_cases),
        hidden_test_cases=tuple(question.private.hidden_test_cases),
    )

    assert result.status == RunStatus.SUCCEEDED
    assert result.tests is not None
    assert (result.tests.visible_passed, result.tests.visible_total) == (1, 1)
    assert (result.tests.hidden_passed, result.tests.hidden_total) == (2, 2)


def test_python_runner_rejects_a_workspace_without_main_source(tmp_path: Path) -> None:
    runner = PythonRunner()
    submission = Submission(language="python", files={}, idempotency_key="missing-main")

    result = runner.run(submission, tmp_path, threading.Event())

    assert result.status == RunStatus.REJECTED
    assert result.error_code == "missing_main_source"


def test_python_runner_rejects_forbidden_from_imports(tmp_path: Path) -> None:
    result = _run(tmp_path, "from socket import create_connection")

    assert result.status == RunStatus.FAILED
    assert result.error_code == "forbidden_import"
    assert result.diagnostics == ("禁止导入高风险模块：socket。",)


def test_python_runner_stops_during_compilation_when_cancellation_is_already_requested(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('never runs')", encoding="utf-8")
    cancellation = threading.Event()
    cancellation.set()

    result = PythonRunner().run(
        Submission(language="python", files={"main.py": "print('never runs')"}, idempotency_key="compile-cancelled"),
        tmp_path,
        cancellation,
    )

    assert result.status == RunStatus.CANCELLED
    assert result.error_code == "cancelled"
