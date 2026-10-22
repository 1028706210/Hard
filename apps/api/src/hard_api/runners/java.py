"""Java 课程 runner；它限制资源，但不是针对恶意代码的安全沙箱。"""

from __future__ import annotations

from pathlib import Path
import re
import threading

from hard_api.diagnostics.java import normalize_java_diagnostic
from hard_api.runners.contracts import (
    CompileResult,
    ExecutableTestCase,
    RunResult,
    RunStatus,
    Submission,
    TestResult,
)
from hard_api.runners.limits import COMPILE_TIMEOUT_SECONDS, MAX_OUTPUT_BYTES, RUN_TIMEOUT_SECONDS
from hard_api.runners.processes import ProcessStatus, execute_process


JAVA_COMPILER = Path("C:/Program Files/Common Files/Oracle/Java/javapath/javac.exe")
JAVA_RUNTIME = Path("C:/Program Files/Common Files/Oracle/Java/javapath/java.exe")
_SECURITY_POLICY_NAME = ".hard-java.policy"
_SECURITY_MANAGER_WARNINGS = (
    "WARNING: A command line option has enabled the Security Manager",
    "WARNING: The Security Manager is deprecated and will be removed in a future release",
)

_CLASS_PATTERN = re.compile(
    r"\bpublic\s+(?:(?:final|abstract|sealed|non-sealed|strictfp)\s+)*class\s+([A-Za-z_$][A-Za-z0-9_$]*)"
)


def _mask_non_code(source: str) -> str:
    out: list[str] = []
    index = 0
    length = len(source)
    state = "code"
    while index < length:
        character = source[index]
        following = source[index + 1] if index + 1 < length else ""
        if state == "code":
            if character == "/" and following == "/":
                state = "line"
                out.append("  ")
                index += 2
                continue
            if character == "/" and following == "*":
                state = "block"
                out.append("  ")
                index += 2
                continue
            if character == '"':
                state = "string"
                out.append(" ")
                index += 1
                continue
            if character == "'":
                state = "char"
                out.append(" ")
                index += 1
                continue
            out.append(character)
            index += 1
            continue
        if state == "line":
            if character == "\n":
                state = "code"
                out.append("\n")
            else:
                out.append(" ")
            index += 1
            continue
        if state == "block":
            if character == "*" and following == "/":
                state = "code"
                out.append("  ")
                index += 2
                continue
            out.append("\n" if character == "\n" else " ")
            index += 1
            continue
        if character == "\\":
            out.append("  ")
            index += 2
            continue
        if (state == "string" and character == '"') or (state == "char" and character == "'"):
            state = "code"
            out.append(" ")
            index += 1
            continue
        out.append("\n" if character == "\n" else " ")
        index += 1
    return "".join(out)


def top_level_public_classes(source: str) -> tuple[str, ...]:
    masked = _mask_non_code(source)
    names: list[str] = []

    def evaluate(chunk: str) -> None:
        for match in _CLASS_PATTERN.finditer(chunk):
            if match.group(1) not in names:
                names.append(match.group(1))

    depth = 0
    chunk: list[str] = []
    for character in masked:
        if character == "{":
            depth += 1
            evaluate("".join(chunk))
            chunk.clear()
        elif character == "}":
            depth = max(0, depth - 1)
            chunk.clear()
        elif depth == 0:
            chunk.append(character)
    evaluate("".join(chunk))
    return tuple(names)


class JavaRunner:
    def __init__(
        self,
        *,
        compiler_path: Path = JAVA_COMPILER,
        runtime_path: Path = JAVA_RUNTIME,
        compile_timeout_seconds: float = COMPILE_TIMEOUT_SECONDS,
        run_timeout_seconds: float = RUN_TIMEOUT_SECONDS,
    ) -> None:
        self.compiler_path = compiler_path
        self.runtime_path = runtime_path
        self.compile_timeout_seconds = compile_timeout_seconds
        self.run_timeout_seconds = run_timeout_seconds

    @staticmethod
    def _write_security_policy(workspace: Path) -> Path:
        policy_path = workspace / _SECURITY_POLICY_NAME
        workspace_path = workspace.resolve().as_posix()
        policy_path.write_text(
            "grant {\n"
            f'  permission java.io.FilePermission "{workspace_path}/-", "read,write,delete";\n'
            "};\n",
            encoding="utf-8",
            newline="\n",
        )
        return policy_path

    @staticmethod
    def _runtime_diagnostic(stderr: str, workspace: Path) -> str:
        filtered = "\n".join(
            line for line in stderr.splitlines() if not line.startswith(_SECURITY_MANAGER_WARNINGS)
        )
        return normalize_java_diagnostic(filtered, workspace)

    def run(self, submission: Submission, workspace: Path, cancellation: threading.Event) -> RunResult:
        if not self.compiler_path.is_file() or not self.runtime_path.is_file():
            return RunResult(status=RunStatus.TOOL_MISSING, error_code="tool_missing")
        source = submission.files.get("main.py")
        if not isinstance(source, str) or not source.strip():
            return RunResult(status=RunStatus.REJECTED, error_code="missing_main_source")

        public_classes = top_level_public_classes(source)
        if len(public_classes) > 1:
            return RunResult(
                status=RunStatus.REJECTED,
                error_code="invalid_public_class",
                diagnostics=("一个提交只能包含一个顶层 public 类。",),
            )
        class_name = public_classes[0] if public_classes else "Main"
        source_file = workspace / f"{class_name}.java"
        source_file.write_text(source, encoding="utf-8", newline="\n")

        compiled = execute_process(
            [
                str(self.compiler_path),
                "-encoding",
                "UTF-8",
                "-d",
                str(workspace),
                source_file.name,
            ],
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
            diagnostic = normalize_java_diagnostic(compiled.stderr or compiled.stdout, workspace)
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
        security_policy = self._write_security_policy(workspace)
        for case, is_visible in (
            *(((item, True) for item in visible_cases)),
            *(((item, False) for item in hidden_cases)),
        ):
            executed = execute_process(
                [
                    str(self.runtime_path),
                    "-Dfile.encoding=UTF-8",
                    "-Djava.security.manager",
                    f"-Djava.security.policy=={security_policy.resolve().as_posix()}",
                    "-cp",
                    str(workspace),
                    class_name,
                ],
                cwd=workspace,
                environment={},
                stdin=case.stdin,
                timeout_seconds=self.run_timeout_seconds,
                output_limit_bytes=MAX_OUTPUT_BYTES,
                cancellation=cancellation,
            )
            total_duration += executed.duration_ms
            terminal = self._terminal_result(executed.status, total_duration)
            if terminal is not None:
                return terminal
            stdout = executed.stdout.replace("\r\n", "\n")
            final_stdout = stdout
            expected_stdout = case.stdout
            stdout_matches = expected_stdout is None or stdout == expected_stdout
            exit_code_matches = executed.return_code == case.exit_code

            if not stdout_matches:
                passed = False
            elif not exit_code_matches:
                diagnostic = self._runtime_diagnostic(executed.stderr, workspace)
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
