from __future__ import annotations

import os
from pathlib import Path
import sys
import threading


import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

ROOT = Path(__file__).resolve().parents[4]
TOOLS_CONTENT = ROOT / "tools" / "content"
if str(TOOLS_CONTENT) not in sys.path:
    sys.path.insert(0, str(TOOLS_CONTENT))

import report as report_module

from hard_api.core.config import Settings
from hard_api.backup.service import LocalBackupService
from hard_api.db import migrations
from hard_api.main import create_app
from hard_api.runners import java as java_module
from hard_api.runners.contracts import ExecutableTestCase, RunResult, RunStatus, Submission, TestResult
from hard_api.runners.java import JavaRunner, top_level_public_classes
from hard_api.runners.manager import RunManager
from hard_api.runners.processes import ProcessResult, ProcessStatus


FIXTURES = Path(__file__).parent / "fixtures" / "java"


def _run(
    tmp_path: Path,
    source: str,
    *,
    stdin: str = "",
    visible_tests: tuple[str, ...] = (),
    hidden_tests: tuple[str, ...] = (),
    visible_test_cases=(),
    hidden_test_cases=(),
    runner: JavaRunner | None = None,
):
    root = tmp_path / "runner-work"
    manager = RunManager(root, adapters={"java": runner or JavaRunner()})
    job = manager.submit(
        Submission(
            language="java",
            files={"main.py": source},
            stdin=stdin,
            visible_tests=visible_tests,
            hidden_tests=hidden_tests,
            visible_test_cases=visible_test_cases,
            hidden_test_cases=hidden_test_cases,
            idempotency_key="java-test",
        )
    )
    result = manager.wait(job.id, timeout=30).result
    manager.shutdown()
    assert list(root.iterdir()) == []
    assert result is not None
    return result


def _direct(tmp_path: Path, source: str, *, cancellation: threading.Event | None = None, runner: JavaRunner | None = None):
    return (runner or JavaRunner()).run(
        Submission(language="java", files={"main.py": source}, idempotency_key="java-direct"),
        tmp_path,
        cancellation or threading.Event(),
    )


def test_java_runner_executes_locked_toolchain_with_stdin_and_safe_counts(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "Success.java").read_text(encoding="utf-8"),
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


def test_java_runner_derives_source_file_from_top_level_public_class(tmp_path: Path) -> None:
    source = (
        "public class ZebraProbe {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"derived\");\n"
        "    }\n"
        "}\n"
    )

    result = _direct(tmp_path, source)

    assert result.status == RunStatus.SUCCEEDED
    assert (tmp_path / "ZebraProbe.java").is_file()
    assert not (tmp_path / "Main.java").exists()


def test_java_runner_falls_back_to_main_without_public_class(tmp_path: Path) -> None:
    fallback = (
        "class Main {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"fallback\");\n"
        "    }\n"
        "}\n"
    )
    no_entry = (
        "class NoEntryPoint {\n"
        "    int value = 1;\n"
        "}\n"
    )

    ok = _run(tmp_path, fallback)
    missing_main = _run(tmp_path, no_entry)

    assert ok.status == RunStatus.SUCCEEDED
    assert ok.stdout == "fallback\n"
    assert missing_main.status == RunStatus.FAILED
    assert missing_main.error_code == "runtime_failed"


def test_java_runner_normalizes_compile_diagnostics_without_workspace_paths(tmp_path: Path) -> None:
    result = _run(tmp_path, (FIXTURES / "SyntaxError.java").read_text(encoding="utf-8"))

    assert result.status == RunStatus.FAILED
    assert result.compile is not None and not result.compile.passed
    assert result.error_code == "compile_failed"
    diagnostic = result.diagnostics[0]
    assert diagnostic.startswith("编译错误（")
    assert "SyntaxError.java" in diagnostic
    assert "第 3 行" in diagnostic
    assert str(tmp_path) not in diagnostic
    assert "\\" not in diagnostic


def test_java_runner_reports_runtime_failures_with_normalized_diagnostic(tmp_path: Path) -> None:
    source = (
        "public class Boom {\n"
        "    public static void main(String[] args) {\n"
        "        int boom = 1 / 0;\n"
        "        System.out.println(boom);\n"
        "    }\n"
        "}\n"
    )

    result = _run(tmp_path, source)

    assert result.status == RunStatus.FAILED
    assert result.error_code == "runtime_failed"
    assert "ArithmeticException" in result.diagnostics[0]
    assert result.diagnostics[0].startswith("运行错误（第 3 行）")
    assert str(tmp_path) not in result.diagnostics[0]


def test_java_runner_classifies_constant_output_probe_with_failing_exit_case_as_tests_failed(
    tmp_path: Path,
) -> None:
    probe = (
        "public class Main {\n"
        "    public static void main(String[] args) throws Exception {\n"
        "        System.in.readAllBytes();\n"
        "        System.out.print(\"abc\\n\");\n"
        "    }\n"
        "}\n"
    )

    result = _run(
        tmp_path,
        probe,
        visible_test_cases=(ExecutableTestCase(stdin="abc\n", stdout="abc\n", exit_code=0),),
        hidden_test_cases=(
            ExecutableTestCase(stdin="zz\n", stdout="zz\n", exit_code=0),
            ExecutableTestCase(stdin="__invalid__\n", stdout="", exit_code=1),
        ),
    )

    assert result.status == RunStatus.FAILED
    assert result.error_code == "tests_failed"
    assert result.tests is not None
    assert result.tests.visible_passed == 1
    assert result.tests.hidden_passed == 0
    assert result.tests.hidden_total == 2


def test_java_runner_handles_chinese_io_through_utf8_pipes(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "UnicodeIo.java").read_text(encoding="utf-8"),
        stdin="小明\n",
        visible_tests=("你好，小明！\n",),
    )

    assert result.status == RunStatus.SUCCEEDED
    assert result.stdout == "你好，小明！\n"


def test_java_runner_enforces_timeout_output_and_missing_tools(tmp_path: Path) -> None:
    quick = JavaRunner(run_timeout_seconds=0.6, compile_timeout_seconds=20)
    timed_out = _run(tmp_path, (FIXTURES / "InfiniteLoop.java").read_text(encoding="utf-8"), runner=quick)
    overflow = _run(tmp_path, (FIXTURES / "BigOutput.java").read_text(encoding="utf-8"))
    missing_compiler = _run(
        tmp_path,
        "public class MissingA {}",
        runner=JavaRunner(compiler_path=tmp_path / "no-javac.exe"),
    )
    missing_runtime = _run(
        tmp_path,
        "public class MissingB {}",
        runner=JavaRunner(runtime_path=tmp_path / "no-java.exe"),
    )

    assert timed_out.status == RunStatus.TIMED_OUT
    assert timed_out.error_code == "run_timeout"
    assert overflow.status == RunStatus.OUTPUT_OVERFLOW
    assert overflow.error_code == "output_limit_exceeded"
    assert missing_compiler.status == RunStatus.TOOL_MISSING
    assert missing_runtime.status == RunStatus.TOOL_MISSING


def test_java_runner_rejects_multiple_top_level_public_classes(tmp_path: Path) -> None:
    result = _run(tmp_path, (FIXTURES / "MultiPublic.java").read_text(encoding="utf-8"))

    assert result.status == RunStatus.REJECTED
    assert result.error_code == "invalid_public_class"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("public class One {}", ("One",)),
        ("public final class Two {}", ("Two",)),
        ("class Outer { public class Inner {} }", ()),
        ("public class Outer { public class Inner {} }", ("Outer",)),
        ('// public class Ghost {}\npublic class Real { String s = "public class Fake {}"; }', ("Real",)),
        ("/* public class Blocked {} */\npublic class AfterBlock {}", ("AfterBlock",)),
        ("public class Quotes { char brace = '{'; String half = \"//\"; }", ("Quotes",)),
        ("public class A {}\npublic class B {}", ("A", "B")),
        ("import java.util.List;\npublic sealed class Sealed permits Other {}", ("Sealed",)),
    ],
)
def test_top_level_public_class_extraction_ignores_nested_quoted_and_commented(source: str, expected: tuple[str, ...]) -> None:
    assert top_level_public_classes(source) == expected


def test_java_runner_keeps_hidden_test_content_server_only(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "Success.java").read_text(encoding="utf-8"),
        stdin="Ada\n",
        visible_tests=("Hello, Ada!\n",),
        hidden_tests=("HIDDEN_SENTINEL",),
    )

    assert result.status == RunStatus.FAILED
    assert result.tests is not None
    assert result.tests.hidden_passed == 0
    assert result.tests.hidden_total == 1
    public = result.public_payload()
    assert "HIDDEN_SENTINEL" not in str(public)
    assert "hidden_passed" not in str(public)
    assert "hidden_total" not in str(public)


def _java_read_source(path_expression: str) -> str:
    return (
        "public class Main {\n"
        "    public static void main(String[] args) throws Exception {\n"
        f"        String value = java.nio.file.Files.readString({path_expression}, java.nio.charset.StandardCharsets.UTF_8);\n"
        "        System.out.print(value);\n"
        "    }\n"
        "}\n"
    )


def test_java_runner_blocks_windows_file_read_through_fully_qualified_nio_and_hides_path(tmp_path: Path) -> None:
    win_ini = Path(os.environ.get("WINDIR", r"C:\\Windows")) / "win.ini"
    assert win_ini.is_file()
    escaped = str(win_ini).replace("\\", "\\\\")

    result = _run(
        tmp_path,
        _java_read_source(f'java.nio.file.Path.of("{escaped}")'),
        visible_test_cases=(ExecutableTestCase(stdout=None),),
    )

    assert result.status == RunStatus.FAILED
    assert result.error_code == "runtime_failed"
    public = result.public_payload()
    assert "win.ini" not in str(public)
    assert str(win_ini) not in str(public)


@pytest.mark.parametrize(
    "file_access",
    [
        (
            "System.setSecurityManager(null);\n"
            "        java.nio.file.Files.readString(java.nio.file.Path.of(\"C:\\\\Windows\\\\win.ini\"), java.nio.charset.StandardCharsets.UTF_8);"
        ),
        (
            "Class<?> files = Class.forName(\"java.nio.file.Files\");\n"
            "        java.lang.reflect.Method read = files.getMethod(\"readString\", java.nio.file.Path.class, java.nio.charset.Charset.class);\n"
            "        read.invoke(null, java.nio.file.Path.of(\"C:\\\\Windows\\\\win.ini\"), java.nio.charset.StandardCharsets.UTF_8);"
        ),
    ],
)
def test_java_runner_security_boundary_cannot_be_disabled_or_bypassed_by_reflection(
    tmp_path: Path, file_access: str
) -> None:
    source = (
        "public class Main {\n"
        "    public static void main(String[] args) throws Exception {\n"
        f"        {file_access}\n"
        "        System.out.print(\"unreachable\");\n"
        "    }\n"
        "}\n"
    )

    result = _run(tmp_path, source, visible_test_cases=(ExecutableTestCase(stdout=None),))

    assert result.status == RunStatus.FAILED
    assert result.error_code == "runtime_failed"
    assert "win.ini" not in str(result.public_payload())


def test_java_runner_blocks_normalized_parent_escape_from_workspace(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-java-sentinel.txt"
    outside.write_text("OUTSIDE_JAVA_SENTINEL", encoding="utf-8")

    result = _run(
        tmp_path,
        _java_read_source('java.nio.file.Path.of("..", "..", "outside-java-sentinel.txt").normalize()'),
        visible_test_cases=(ExecutableTestCase(stdout=None),),
    )

    assert result.status == RunStatus.FAILED
    assert result.error_code == "runtime_failed"
    assert "OUTSIDE_JAVA_SENTINEL" not in str(result.public_payload())


def test_java_runner_allows_workspace_relative_file_read_write(tmp_path: Path) -> None:
    source = (
        "public class Main {\n"
        "    public static void main(String[] args) throws Exception {\n"
        "        java.nio.file.Path file = java.nio.file.Path.of(\"lesson.txt\");\n"
        "        java.nio.file.Files.writeString(file, \"课程文件\", java.nio.charset.StandardCharsets.UTF_8);\n"
        "        System.out.print(java.nio.file.Files.readString(file, java.nio.charset.StandardCharsets.UTF_8));\n"
        "    }\n"
        "}\n"
    )

    result = _run(tmp_path, source, visible_test_cases=(ExecutableTestCase(stdout="课程文件"),))

    assert result.status == RunStatus.SUCCEEDED


def _java_course_source(file_operation: str) -> str:
    return (
        "public class Main {\n"
        "    public static void main(String[] args) throws Exception {\n"
        f"        {file_operation}\n"
        "        String value = new String(System.in.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).trim();\n"
        "        if (value.isEmpty()) System.exit(1);\n"
        "        System.out.println(\"Hello, \" + value);\n"
        "    }\n"
        "}\n"
    )


def test_real_api_blocks_external_java_read_but_keeps_workspace_file_exercise_working(tmp_path: Path) -> None:
    win_ini = Path(os.environ.get("WINDIR", r"C:\\Windows")) / "win.ini"
    assert win_ini.is_file()
    escaped = str(win_ini).replace("\\", "\\\\")
    settings = Settings(
        project_root=ROOT,
        data_dir=tmp_path / "data",
        database_path=tmp_path / "data" / "hard.db",
        backup_dir=tmp_path / "backups",
        export_dir=tmp_path / "exports",
        runner_work_dir=tmp_path / "runner-work",
        content_dir=ROOT / "content",
        toolchain_lock_path=ROOT / "docs" / "setup" / "toolchain-lock.json",
    )
    migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))
    app = create_app(settings)
    external_source = _java_course_source(
        f'java.nio.file.Files.readString(java.nio.file.Path.of("{escaped}"), java.nio.charset.StandardCharsets.UTF_8);'
    )
    workspace_source = _java_course_source(
        'java.nio.file.Files.writeString(java.nio.file.Path.of("lesson.txt"), "课程文件", java.nio.charset.StandardCharsets.UTF_8);'
    )

    with TestClient(app) as client:
        blocked = client.post(
            "/api/runners/submissions",
            json={
                "lesson_id": "java-foundations-tutorial",
                "exercise_id": "java-foundations-tutorial-c01",
                "source_code": external_source,
            },
            headers={"Idempotency-Key": "java-external-path"},
        )
        blocked_job = app.state.runner_manager.wait(blocked.json()["id"], timeout=30)
        blocked_status = client.get(f"/api/runners/jobs/{blocked.json()['id']}")
        allowed = client.post(
            "/api/runners/submissions",
            json={
                "lesson_id": "java-foundations-tutorial",
                "exercise_id": "java-foundations-tutorial-c01",
                "source_code": workspace_source,
            },
            headers={"Idempotency-Key": "java-workspace-path"},
        )
        allowed_job = app.state.runner_manager.wait(allowed.json()["id"], timeout=30)
        allowed_status = client.get(f"/api/runners/jobs/{allowed.json()['id']}")

    assert blocked.status_code == blocked_status.status_code == 200
    assert blocked_job.status == RunStatus.FAILED
    assert blocked_job.result is not None
    assert blocked_job.result.tests is not None
    assert blocked_job.result.tests.visible_passed == 0
    assert "win.ini" not in blocked_status.text
    assert str(win_ini) not in blocked_status.text
    assert "hidden" not in blocked_status.text.lower()
    assert allowed.status_code == allowed_status.status_code == 200
    assert allowed_job.status == RunStatus.SUCCEEDED
    assert allowed_status.json()["result"]["tests"] == {"visible_passed": 2, "visible_total": 2}


def test_java_runner_stops_when_cancellation_is_already_requested(tmp_path: Path) -> None:
    cancellation = threading.Event()
    cancellation.set()

    result = _direct(tmp_path, "public class Cancelled {}", cancellation=cancellation)

    assert result.status == RunStatus.CANCELLED
    assert result.error_code == "cancelled"


def test_java_runner_rejects_submission_without_primary_source(tmp_path: Path) -> None:
    result = JavaRunner().run(
        Submission(language="java", files={}, idempotency_key="missing-main"),
        tmp_path,
        threading.Event(),
    )

    assert result.status == RunStatus.REJECTED
    assert result.error_code == "missing_main_source"


def test_java_runner_pins_compile_and_runtime_arguments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    recorded: list[tuple[list[str], str, Path]] = []

    def fake_execute(arguments, *, cwd, environment, stdin, timeout_seconds, output_limit_bytes, cancellation=None):
        recorded.append((list(arguments), stdin, Path(cwd)))
        if "-encoding" in arguments:
            return ProcessResult(ProcessStatus.COMPLETED, "", "", 0, 5)
        return ProcessResult(ProcessStatus.COMPLETED, "", "", 0, 7)

    monkeypatch.setattr(java_module, "execute_process", fake_execute)

    result = _run(
        tmp_path,
        'public class Main { public static void main(String[] a) {} }',
        stdin="Ada\n",
    )

    assert result.status == RunStatus.SUCCEEDED
    compile_arguments, compile_stdin, compile_cwd = recorded[0]
    runtime_arguments, runtime_stdin, runtime_cwd = recorded[1]
    workspace = str(compile_cwd)
    policy_workspace = compile_cwd.resolve().as_posix()
    assert runtime_cwd == compile_cwd
    assert compile_arguments == [
        str(java_module.JAVA_COMPILER),
        "-encoding",
        "UTF-8",
        "-d",
        workspace,
        "Main.java",
    ]
    assert compile_stdin == ""
    assert runtime_arguments == [
        str(java_module.JAVA_RUNTIME),
        "-Dfile.encoding=UTF-8",
        "-Djava.security.manager",
        f"-Djava.security.policy=={policy_workspace}/.hard-java.policy",
        "-cp",
        workspace,
        "Main",
    ]
    assert runtime_stdin == "Ada\n"
    assert len(recorded) == 2


def test_create_app_registers_java_adapter_alongside_supported_runners(tmp_path: Path) -> None:
    settings = Settings(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        database_path=tmp_path / "data" / "hard.db",
        backup_dir=tmp_path / "backups",
        export_dir=tmp_path / "exports",
        runner_work_dir=tmp_path / "runner-work",
        content_dir=ROOT / "content",
        toolchain_lock_path=ROOT / "docs" / "setup" / "toolchain-lock.json",
    )

    app = create_app(settings=settings)

    adapters = app.state.runner_manager._adapters
    assert set(adapters) == {"python", "java", "csharp", "cpp"}
    assert isinstance(adapters["java"], JavaRunner)


def _content_tree(tmp_path: Path) -> Path:
    content_root = tmp_path / "content"
    module_dir = content_root / "java" / "java-probe"
    module_dir.mkdir(parents=True)
    solution = "\n".join(
        [
            "public class Main {",
            "    public static void main(String[] args) throws Exception {",
            "        byte[] all = System.in.readAllBytes();",
            "        String name = new String(all, java.nio.charset.StandardCharsets.UTF_8).strip();",
            "        System.out.println(name.toUpperCase());",
            "    }",
            "}",
            "",
        ]
    )
    (module_dir / "probe.md").write_text(
        "\n".join(
            [
                "---",
                "id: java-probe-probe",
                "title: Probe",
                "concepts: [variables]",
                "objectives:",
                "  - 目标一",
                "prerequisites: []",
                "difficulty: beginner",
                "experience_points: 50",
                "source_url: https://www.runoob.com/java/java-tutorial.html",
                "source_snapshot_date: 2026-08-23",
                "---",
                "",
                "# Probe",
                "",
                "正文示例。",
            ]
        ),
        encoding="utf-8",
    )
    (module_dir / "probe.exercises.json").write_text(
        """
{
  "lesson_id": "java-probe-probe",
  "questions": [
    {
      "id": "java-probe-probe-c01",
      "type": "code",
      "prompt": "大写输出",
      "starter_code": "public class Main {}",
      "visible_tests": ["普通输入"],
      "experience_points": 20,
      "private": {
        "reference_solution": REFERENCE_PLACEHOLDER,
        "hidden_tests": ["边界输入", "无效输入"],
        "visible_test_cases": [{"stdin": "abc\\n", "stdout": "ABC\\n", "exit_code": 0}],
        "hidden_test_cases": [
          {"stdin": "zz\\n", "stdout": "ZZ\\n", "exit_code": 0},
          {"stdin": "b\\n", "stdout": "B\\n", "exit_code": 0}
        ]
      }
    }
  ]
}
""".replace("REFERENCE_PLACEHOLDER", __import__("json").dumps(solution)),
        encoding="utf-8",
    )
    (content_root / "java" / "course.yaml").write_text(
        "\n".join(
            [
                "language: java",
                "title: Java",
                "growth:",
                "  review_milestone_points: 15",
                "  badge_points:",
                "    first_lesson: 20",
                "    first_module_mastery: 30",
                "    seven_day_streak: 40",
                "placement_tests: []",
                "modules:",
                "  - id: java-probe",
                "    title: Probe Module",
                "    prerequisites: []",
                "    source_coverage:",
                "      - source_id: probe-source",
                "        lesson_id: java-probe-probe",
                "    lessons:",
                "      - id: java-probe-probe",
                "        path: java-probe/probe.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return content_root


def test_report_dispatch_rejects_unknown_language_explicitly() -> None:
    with pytest.raises(SystemExit):
        report_module._runner_for("ruby")


def test_report_dispatch_runs_java_reference_solutions_with_real_runner(tmp_path: Path) -> None:
    content_root = _content_tree(tmp_path)

    passed_lessons, attempted = report_module.reference_solution_execution_metrics(
        content_root, "java", "java-probe"
    )

    assert attempted is True
    assert passed_lessons == 1


def test_report_java_constant_output_probe_is_rejected_by_hidden_cases(tmp_path: Path) -> None:
    content_root = _content_tree(tmp_path)

    attempted, rejected, evidence = report_module.constant_output_rejection_metrics(
        content_root, "java", "java-probe"
    )

    assert evidence is True
    assert attempted == 1
    assert rejected == 1


class _StubRunner:
    def __init__(self, result: RunResult) -> None:
        self.result = result

    def run(self, submission, workspace, cancellation) -> RunResult:
        return self.result


@pytest.mark.parametrize(
    ("error_code", "expected_rejected"),
    [("compile_failed", 0), ("runtime_failed", 0), ("tests_failed", 1)],
)
def test_report_only_tests_failed_counts_as_rejection(
    tmp_path: Path, error_code: str, expected_rejected: int
) -> None:
    content_root = _content_tree(tmp_path)

    attempted, rejected, _ = report_module.constant_output_rejection_metrics(
        content_root,
        "java",
        "java-probe",
        runner=_StubRunner(RunResult(status=RunStatus.FAILED, error_code=error_code)),
    )

    assert attempted == 1
    assert rejected == expected_rejected


def test_report_python_dispatch_maps_to_python_runner(tmp_path: Path) -> None:
    from hard_api.runners.python import PythonRunner

    assert isinstance(report_module._runner_for("python"), PythonRunner)
    assert isinstance(report_module._runner_for("java"), JavaRunner)


def test_report_runner_injection_still_counts_python_lesson_results(tmp_path: Path) -> None:
    stub = _StubRunner(
        RunResult(
            status=RunStatus.SUCCEEDED,
            tests=TestResult(visible_passed=1, visible_total=1, hidden_passed=2, hidden_total=2),
        )
    )
    content_root = _content_tree(tmp_path)

    passed_lessons, attempted = report_module.reference_solution_execution_metrics(
        content_root, "java", "java-probe", runner=stub
    )

    assert attempted is True
    assert passed_lessons == 1
