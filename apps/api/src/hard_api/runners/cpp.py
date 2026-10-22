"""C++ runner for TRUSTED_LOCAL_LEARNING_ONLY.

This runner limits resources and controls the compile contract,
but it is not a security sandbox for malicious or untrusted code.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import threading
import time

from hard_api.diagnostics.cpp import normalize_cpp_diagnostic
from hard_api.runners.contracts import CompileResult, ExecutableTestCase, RunResult, RunStatus, Submission, TestResult
from hard_api.runners.limits import COMPILE_TIMEOUT_SECONDS, MAX_OUTPUT_BYTES, RUN_TIMEOUT_SECONDS
from hard_api.runners.processes import ProcessStatus, execute_process


GPP_EXECUTABLE = Path("D:/DevTools/msys64/ucrt64/bin/g++.exe")
OUTPUT_NAME = "hard_submission.exe"
MAIN_SOURCE_KEY = "main.py"
MAIN_SOURCE_FILE = "main.cpp"
# g++ 的内部子进程（cc1plus/collect2）依赖 UCRT64 bin 目录下的运行库 DLL。
# 运行环境不提供 PATH，因此把这些 DLL 复制到临时工作区，子进程通过当前目录找到它们。
TOOLCHAIN_SUPPORT_DLLS = (
    "libgcc_s_seh-1.dll",
    "libwinpthread-1.dll",
    "libgmp-10.dll",
    "libisl-23.dll",
    "libmpc-3.dll",
    "libmpfr-6.dll",
    "libzstd.dll",
    "zlib1.dll",
)


class CppRunner:
    def __init__(
        self,
        *,
        gpp_path: Path = GPP_EXECUTABLE,
        compile_timeout_seconds: float = COMPILE_TIMEOUT_SECONDS,
        run_timeout_seconds: float = RUN_TIMEOUT_SECONDS,
    ) -> None:
        self.gpp_path = gpp_path
        self.compile_timeout_seconds = compile_timeout_seconds
        self.run_timeout_seconds = run_timeout_seconds

    def run(self, submission: Submission, workspace: Path, cancellation: threading.Event) -> RunResult:
        if cancellation.is_set():
            return RunResult(status=RunStatus.CANCELLED, error_code="cancelled")
        source = submission.files.get(MAIN_SOURCE_KEY)
        if not isinstance(source, str) or not source.strip():
            return RunResult(status=RunStatus.REJECTED, error_code="missing_main_source")
        if not self.gpp_path.is_file():
            return RunResult(status=RunStatus.TOOL_MISSING, error_code="tool_missing")

        self._prepare_toolchain_support(workspace)
        (workspace / MAIN_SOURCE_FILE).write_text(source, encoding="utf-8", newline="\n")
        extra_sources = sorted(
            name for name in submission.files if name.endswith(".cpp") and name != MAIN_SOURCE_KEY
        )

        compiled = execute_process(
            self._compile_arguments(extra_sources),
            cwd=workspace,
            environment={},
            stdin="",
            timeout_seconds=self.compile_timeout_seconds,
            output_limit_bytes=MAX_OUTPUT_BYTES,
            cancellation=cancellation,
        )
        terminal = self._terminal_result(compiled.status, compiled.duration_ms)
        if terminal is not None:
            return terminal
        compile_result = CompileResult(passed=compiled.return_code == 0)
        if compiled.return_code != 0:
            diagnostic = normalize_cpp_diagnostic(f"{compiled.stdout}\n{compiled.stderr}", workspace)
            return RunResult(
                status=RunStatus.FAILED,
                compile=compile_result,
                stderr=diagnostic,
                diagnostics=(diagnostic,),
                duration_ms=compiled.duration_ms,
                error_code="compile_failed",
            )

        visible_cases = submission.visible_test_cases or tuple(
            ExecutableTestCase(stdin=submission.stdin, stdout=value) for value in submission.visible_tests
        )
        hidden_cases = submission.hidden_test_cases or tuple(
            ExecutableTestCase(stdin=submission.stdin, stdout=value) for value in submission.hidden_tests
        )
        if not visible_cases and not hidden_cases:
            visible_cases = (ExecutableTestCase(stdin=submission.stdin),)

        total_duration = compiled.duration_ms
        visible_passed = hidden_passed = 0
        final_stdout = ""
        executable = workspace / OUTPUT_NAME
        deadline = time.monotonic() + self.run_timeout_seconds
        for case, is_visible in (
            *(((item, True) for item in visible_cases)),
            *(((item, False) for item in hidden_cases)),
        ):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return RunResult(
                    status=RunStatus.TIMED_OUT,
                    compile=compile_result,
                    duration_ms=total_duration,
                    error_code="run_timeout",
                )
            executed = execute_process(
                [str(executable)],
                cwd=workspace,
                environment=self._environment(),
                stdin=case.stdin,
                timeout_seconds=remaining,
                output_limit_bytes=MAX_OUTPUT_BYTES,
                cancellation=cancellation,
            )
            total_duration += executed.duration_ms
            terminal = self._terminal_result(executed.status, total_duration)
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
                diagnostic = normalize_cpp_diagnostic(executed.stderr, workspace)
                return RunResult(
                    status=RunStatus.FAILED,
                    compile=compile_result,
                    stdout=stdout,
                    stderr=diagnostic,
                    diagnostics=(diagnostic,),
                    duration_ms=total_duration,
                    error_code="runtime_failed",
                )
            else:
                passed = True
            if passed:
                if is_visible:
                    visible_passed += 1
                else:
                    hidden_passed += 1

        tests = TestResult(
            visible_passed=visible_passed,
            visible_total=len(visible_cases),
            hidden_passed=hidden_passed,
            hidden_total=len(hidden_cases),
        )
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

    def _compile_arguments(self, extra_sources: list[str]) -> list[str]:
        return [
            str(self.gpp_path),
            "-std=c++20",
            "-Wall",
            "-Wextra",
            "-static",
            "-finput-charset=UTF-8",
            "-fexec-charset=UTF-8",
            # 无 PATH 环境下显式定位 as/ld 等 GCC 子程序。
            "-B",
            str(self.gpp_path.parent) + "\\",
            "-o",
            OUTPUT_NAME,
            MAIN_SOURCE_FILE,
            *extra_sources,
        ]

    @staticmethod
    def _environment() -> dict[str, str]:
        # std::system 等运行库功能依赖 COMSPEC 定位 cmd.exe；
        # 使用固定系统路径，用户无法通过提交控制它。
        return {"COMSPEC": os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe")}

    def _prepare_toolchain_support(self, workspace: Path) -> None:
        toolchain_bin = self.gpp_path.parent
        for dll in TOOLCHAIN_SUPPORT_DLLS:
            source = toolchain_bin / dll
            if source.is_file():
                shutil.copy2(source, workspace / dll)

    @staticmethod
    def _terminal_result(status: ProcessStatus, duration_ms: int) -> RunResult | None:
        mapping = {
            ProcessStatus.CANCELLED: (RunStatus.CANCELLED, "cancelled"),
            ProcessStatus.TIMED_OUT: (RunStatus.TIMED_OUT, "run_timeout"),
            ProcessStatus.OUTPUT_OVERFLOW: (RunStatus.OUTPUT_OVERFLOW, "output_limit_exceeded"),
        }
        if status not in mapping:
            return None
        runner_status, error_code = mapping[status]
        return RunResult(status=runner_status, duration_ms=duration_ms, error_code=error_code)
