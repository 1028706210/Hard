"""Python 课程 runner；它限制资源，但不是针对恶意代码的安全沙箱。"""

from __future__ import annotations

import ast
from pathlib import Path
import threading
import time

from hard_api.diagnostics.python import normalize_python_diagnostic
from hard_api.runners.contracts import CompileResult, ExecutableTestCase, RunResult, RunStatus, Submission, TestResult
from hard_api.runners.limits import COMPILE_TIMEOUT_SECONDS, MAX_OUTPUT_BYTES, RUN_TIMEOUT_SECONDS
from hard_api.runners.processes import ProcessStatus, execute_process


PYTHON_EXECUTABLE = Path("D:/DevTools/python/python.exe")
_FORBIDDEN_IMPORTS = {"subprocess", "socket", "ctypes"}


class PythonRunner:
    def __init__(
        self,
        *,
        executable: Path = PYTHON_EXECUTABLE,
        compile_timeout_seconds: float = COMPILE_TIMEOUT_SECONDS,
        run_timeout_seconds: float = RUN_TIMEOUT_SECONDS,
    ) -> None:
        self.executable = executable
        self.compile_timeout_seconds = compile_timeout_seconds
        self.run_timeout_seconds = run_timeout_seconds

    def run(self, submission: Submission, workspace: Path, cancellation: threading.Event) -> RunResult:
        if not self.executable.is_file():
            return RunResult(status=RunStatus.TOOL_MISSING, error_code="tool_missing")
        source_path = workspace / "main.py"
        if not source_path.is_file():
            return RunResult(status=RunStatus.REJECTED, error_code="missing_main_source")
        forbidden = self._forbidden_import(source_path.read_text(encoding="utf-8"))
        if forbidden is not None:
            return RunResult(
                status=RunStatus.FAILED,
                error_code="forbidden_import",
                diagnostics=(f"禁止导入高风险模块：{forbidden}。",),
            )
        environment = {
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONSAFEPATH": "1",
            "PYTHONUTF8": "1",
        }
        compiled = execute_process(
            [str(self.executable), "-I", "-X", "utf8", "-m", "py_compile", "main.py"],
            cwd=workspace,
            environment=environment,
            stdin="",
            timeout_seconds=self.compile_timeout_seconds,
            output_limit_bytes=MAX_OUTPUT_BYTES,
            cancellation=cancellation,
        )
        compile_result = CompileResult(passed=compiled.return_code == 0)
        terminal = self._terminal_process_result(compiled.status, compiled.duration_ms)
        if terminal is not None:
            return terminal
        if compiled.return_code != 0:
            diagnostic = normalize_python_diagnostic(compiled.stderr, workspace)
            return RunResult(
                status=RunStatus.FAILED,
                compile=compile_result,
                stderr=diagnostic,
                diagnostics=(diagnostic,),
                duration_ms=compiled.duration_ms,
                error_code="compile_failed",
            )
        visible_cases = submission.visible_test_cases or tuple(ExecutableTestCase(stdin=submission.stdin, stdout=value) for value in submission.visible_tests)
        hidden_cases = submission.hidden_test_cases or tuple(ExecutableTestCase(stdin=submission.stdin, stdout=value) for value in submission.hidden_tests)
        if not visible_cases and not hidden_cases:
            visible_cases = (ExecutableTestCase(stdin=submission.stdin),)
        total_duration = compiled.duration_ms
        final_stdout = ""
        visible_passed = hidden_passed = 0
        deadline = time.monotonic() + self.run_timeout_seconds
        for case, visible in tuple((item, True) for item in visible_cases) + tuple((item, False) for item in hidden_cases):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return RunResult(
                    status=RunStatus.TIMED_OUT,
                    compile=compile_result,
                    duration_ms=total_duration,
                    error_code="run_timeout",
                )
            # Isolated mode ignores PYTHONUTF8; configure the pipe encoding explicitly.
            executed = execute_process([str(self.executable), "-I", "-X", "utf8", "main.py"], cwd=workspace, environment=environment, stdin=case.stdin, timeout_seconds=remaining, output_limit_bytes=MAX_OUTPUT_BYTES, cancellation=cancellation)
            total_duration += executed.duration_ms
            terminal = self._terminal_process_result(executed.status, total_duration)
            if terminal is not None:
                return RunResult(
                    status=terminal.status,
                    compile=compile_result,
                    duration_ms=terminal.duration_ms,
                    error_code=terminal.error_code,
                )
            stdout = executed.stdout.replace("\r\n", "\n")
            final_stdout = stdout
            expected_stdout = case.stdout
            stdout_matches = expected_stdout is None or stdout == expected_stdout
            exit_code_matches = executed.return_code == case.exit_code
            
            if not stdout_matches:
                passed = False
            elif not exit_code_matches:
                diagnostic = normalize_python_diagnostic(executed.stderr, workspace)
                return RunResult(
                    status=RunStatus.FAILED,
                    compile=compile_result,
                    stdout=stdout,
                    stderr=normalize_python_diagnostic(executed.stderr, workspace),
                    diagnostics=(normalize_python_diagnostic(executed.stderr, workspace),),
                    duration_ms=total_duration,
                    error_code="runtime_failed",
                )
            else:
                passed = True
            
            if passed:
                if visible: visible_passed += 1
                else: hidden_passed += 1
        tests = TestResult(visible_passed=visible_passed, visible_total=len(visible_cases), hidden_passed=hidden_passed, hidden_total=len(hidden_cases))
        visible_ok = tests.visible_passed == tests.visible_total
        hidden_ok = tests.hidden_passed == tests.hidden_total
        diagnostics = () if visible_ok else ("可见测试未通过。",)
        return RunResult(
            status=RunStatus.SUCCEEDED if visible_ok and hidden_ok else RunStatus.FAILED,
            compile=compile_result,
            tests=tests,
            stdout=final_stdout,
            diagnostics=diagnostics,
            duration_ms=total_duration,
            error_code=None if visible_ok and hidden_ok else "tests_failed",
        )

    @staticmethod
    def _forbidden_import(source: str) -> str | None:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = (alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names = ((node.module or "").split(".", 1)[0],)
            else:
                continue
            forbidden = next((name for name in names if name in _FORBIDDEN_IMPORTS), None)
            if forbidden is not None:
                return forbidden
        return None

    @staticmethod
    def _terminal_process_result(status: ProcessStatus, duration_ms: int) -> RunResult | None:
        mapping = {
            ProcessStatus.CANCELLED: (RunStatus.CANCELLED, "cancelled"),
            ProcessStatus.TIMED_OUT: (RunStatus.TIMED_OUT, "run_timeout"),
            ProcessStatus.OUTPUT_OVERFLOW: (RunStatus.OUTPUT_OVERFLOW, "output_limit_exceeded"),
        }
        if status not in mapping:
            return None
        runner_status, error_code = mapping[status]
        return RunResult(status=runner_status, duration_ms=duration_ms, error_code=error_code)
