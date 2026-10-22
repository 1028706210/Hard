from __future__ import annotations

import sys
import threading
import time
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
import psutil
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content"))

from hard_api.main import create_app
from hard_api.core.config import Settings
from hard_api.db import migrations
from hard_api.backup.service import LocalBackupService
from hard_api.runners import csharp as csharp_module
from hard_api.runners.contracts import ExecutableTestCase, RunResult, RunStatus, Submission
from hard_api.runners.csharp import CSharpRunner
from hard_api.runners.manager import RunManager
from hard_api.runners.processes import ProcessResult, ProcessStatus
from test_catalog import make_settings


FIXTURES = Path(__file__).parent / "fixtures" / "csharp"
ROOT = Path(__file__).resolve().parents[4]


def _msbuild_nodes() -> dict[int, tuple[float, int, tuple[str, ...]]]:
    """Return only observable MSBuild nodes; never mutates process state."""
    nodes: dict[int, tuple[float, int, tuple[str, ...]]] = {}
    for process in psutil.process_iter(("pid", "ppid", "create_time", "cmdline", "name")):
        try:
            info = process.info
            command = tuple(info["cmdline"] or ())
            if (
                str(info["name"] or "").lower() == "dotnet.exe"
                and any(part.lower().endswith("msbuild.dll") for part in command)
            ):
                nodes[process.pid] = (float(info["create_time"]), int(info["ppid"]), command)
        except psutil.Error:
            continue
    return nodes


def _new_msbuild_nodes(before: dict[int, tuple[float, int, tuple[str, ...]]]) -> dict[int, tuple[float, int, tuple[str, ...]]]:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        time.sleep(0.1)
    return {pid: details for pid, details in _msbuild_nodes().items() if pid not in before}


def _run(
    tmp_path: Path,
    source: str,
    *,
    stdin: str = "",
    visible_tests: tuple[str, ...] = (),
    hidden_tests: tuple[str, ...] = (),
    visible_test_cases=(),
    hidden_test_cases=(),
    lesson_id: str = "",
    exercise_id: str = "",
    runner: CSharpRunner | None = None,
):
    root = tmp_path / "runner-work"
    manager = RunManager(root, adapters={"csharp": runner or CSharpRunner()})
    job = manager.submit(
        Submission(
            language="csharp",
            files={"main.py": source},
            stdin=stdin,
            visible_tests=visible_tests,
            hidden_tests=hidden_tests,
            visible_test_cases=visible_test_cases,
            hidden_test_cases=hidden_test_cases,
            idempotency_key="csharp-test",
            lesson_id=lesson_id,
            exercise_id=exercise_id,
        )
    )
    result = manager.wait(job.id, timeout=45).result
    manager.shutdown()
    assert list(root.iterdir()) == []
    assert result is not None
    return result


def _direct(
    tmp_path: Path,
    source: str,
    *,
    cancellation: threading.Event | None = None,
    runner: CSharpRunner | None = None,
):
    source_path = tmp_path / "main.py"
    source_path.write_text(source, encoding="utf-8")
    return (runner or CSharpRunner()).run(
        Submission(language="csharp", files={"main.py": source}, idempotency_key="csharp-direct"),
        tmp_path,
        cancellation or threading.Event(),
    )


def test_csharp_runner_executes_top_level_statements_with_stdin_and_hidden_counts(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "TopLevel.cs").read_text(encoding="utf-8"),
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


def test_csharp_runner_executes_standard_program_main(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "ProgramMain.cs").read_text(encoding="utf-8"),
        stdin="Grace\n",
        visible_tests=("Hello, Grace!\n",),
    )

    assert result.status == RunStatus.SUCCEEDED
    assert result.stdout == "Hello, Grace!\n"


def test_csharp_runner_build_leaves_no_new_msbuild_node_after_success(tmp_path: Path) -> None:
    before = _msbuild_nodes()
    started_at = time.time()

    result = _run(tmp_path, 'Console.WriteLine("clean");', visible_tests=("clean\n",))

    survivors = _new_msbuild_nodes(before)
    assert result.status == RunStatus.SUCCEEDED
    assert not survivors, {
        pid: {"created_at": created_at, "parent_pid": parent_pid, "command": command}
        for pid, (created_at, parent_pid, command) in survivors.items()
        if created_at >= started_at - 1
    }


def test_csharp_runner_controls_offline_project_template_and_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    recorded: list[tuple[list[str], dict[str, str], str, Path]] = []

    def fake_execute(arguments, *, cwd, environment, stdin, timeout_seconds, output_limit_bytes, cancellation=None):
        recorded.append((list(arguments), dict(environment), stdin, Path(cwd)))
        if "build" in arguments:
            assert (Path(cwd) / "HardSubmission.csproj").read_text(encoding="utf-8") == csharp_module.PROJECT_TEMPLATE
            assert (Path(cwd) / "Program.cs").read_text(encoding="utf-8") == "Console.WriteLine(\"ok\");"
            assert (Path(cwd) / "HardPrelude.cs").read_text(encoding="utf-8") == csharp_module.PRELUDE_SOURCE
        return ProcessResult(ProcessStatus.COMPLETED, "", "", 0, 5)

    monkeypatch.setattr(csharp_module, "execute_process", fake_execute)

    result = _run(tmp_path, 'Console.WriteLine("ok");', stdin="ignored\n")

    assert result.status == RunStatus.SUCCEEDED
    build_args, build_env, build_stdin, build_cwd = recorded[0]
    run_args, run_env, run_stdin, run_cwd = recorded[1]
    assert build_args == [
        str(csharp_module.DOTNET_EXECUTABLE),
        "build",
        "HardSubmission.csproj",
        "--no-restore",
        "--configuration",
        "Release",
        "-p:UseSharedCompilation=false",
        "--disable-build-servers",
        "-nodeReuse:false",
        "--nologo",
    ]
    assert run_args == [
        str(csharp_module.DOTNET_EXECUTABLE),
        str(build_cwd / "bin" / "Release" / csharp_module.TARGET_FRAMEWORK / "HardSubmission.dll"),
    ]
    assert build_stdin == ""
    assert run_stdin == "ignored\n"
    assert build_cwd == run_cwd
    assert build_env == run_env
    assert build_env["DOTNET_CLI_TELEMETRY_OPTOUT"] == "1"
    assert build_env["DOTNET_SKIP_FIRST_TIME_EXPERIENCE"] == "1"
    assert build_env["DOTNET_NOLOGO"] == "1"
    assert Path(build_env["NUGET_PACKAGES"]).drive.upper() == "D:"
    assert "PATH" not in build_env


def test_csharp_runner_rejects_project_package_source_import_exec_and_build_argument_injection(tmp_path: Path) -> None:
    source = (
        '<Project Sdk="Microsoft.NET.Sdk"><ItemGroup><PackageReference Include="x" Version="1.0.0" />'
        "</ItemGroup><Import Project=\"evil.targets\" /><Target Name=\"x\"><Exec Command=\"calc\" /></Target>"
        '<UsingTask TaskName="x" AssemblyFile="x.dll" /></Project>'
    )

    result = _run(tmp_path, source)

    assert result.status == RunStatus.REJECTED
    assert result.error_code == "invalid_csharp_source"


def test_csharp_runner_does_not_enable_unsafe_from_user_source(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        "unsafe { int* value = null; }",
    )

    assert result.status == RunStatus.FAILED
    assert result.error_code == "compile_failed"
    assert "/unsafe" not in str(result.public_payload()).lower()


def test_csharp_runner_supports_server_only_allow_unsafe_capability(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        "unsafe { int* value = null; Console.WriteLine(value == null); }",
        visible_tests=("True\n",),
        runner=CSharpRunner(allow_unsafe=True),
    )

    assert result.status == RunStatus.SUCCEEDED


def test_csharp_runner_enables_unsafe_only_for_the_server_allowlisted_capstone_exercise(tmp_path: Path) -> None:
    source = "unsafe { int value = 7; int* pointer = &value; Console.WriteLine(*pointer); }"

    allowed = _run(
        tmp_path,
        source,
        visible_tests=("7\n",),
        lesson_id="csharp-capstone-unsafe-code",
        exercise_id="csharp-capstone-unsafe-code-c01",
    )
    blocked = _run(
        tmp_path,
        source,
        visible_tests=("7\n",),
        lesson_id="csharp-foundations-tutorial",
        exercise_id="csharp-foundations-tutorial-c01",
    )

    assert allowed.status == RunStatus.SUCCEEDED
    assert blocked.status == RunStatus.FAILED
    assert blocked.error_code == "compile_failed"


def test_csharp_runner_normalizes_compile_and_runtime_diagnostics_without_workspace_paths(tmp_path: Path) -> None:
    syntax = _run(tmp_path, (FIXTURES / "SyntaxError.cs").read_text(encoding="utf-8"))
    runtime = _run(tmp_path, (FIXTURES / "RuntimeError.cs").read_text(encoding="utf-8"))

    assert syntax.status == RunStatus.FAILED
    assert syntax.compile is not None and not syntax.compile.passed
    assert syntax.error_code == "compile_failed"
    assert "编译错误" in syntax.diagnostics[0]
    assert str(tmp_path) not in syntax.diagnostics[0]
    assert runtime.status == RunStatus.FAILED
    assert runtime.error_code == "runtime_failed"
    assert "运行错误" in runtime.diagnostics[0]
    assert str(tmp_path) not in runtime.diagnostics[0]


def test_csharp_runner_classifies_uncaught_exceptions_as_runtime_failures(tmp_path: Path) -> None:
    result = _run(tmp_path, 'throw new InvalidOperationException("boom");')

    assert result.status == RunStatus.FAILED
    assert result.error_code == "runtime_failed"
    assert "运行错误" in result.diagnostics[0]
    assert str(tmp_path) not in result.diagnostics[0]


def test_csharp_runner_handles_chinese_io_through_utf8_pipes(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "UnicodeIo.cs").read_text(encoding="utf-8"),
        stdin="\u5c0f\u660e\n",
        visible_tests=("\u4f60\u597d\uff0c\u5c0f\u660e\uff01\n",),
    )

    assert result.status == RunStatus.SUCCEEDED
    assert result.stdout == "\u4f60\u597d\uff0c\u5c0f\u660e\uff01\n"


def test_csharp_runner_enforces_timeout_output_limit_missing_and_wrong_sdk(tmp_path: Path) -> None:
    quick = CSharpRunner(run_timeout_seconds=0.6, compile_timeout_seconds=20)
    timed_out = _run(tmp_path, (FIXTURES / "InfiniteLoop.cs").read_text(encoding="utf-8"), runner=quick)
    overflow = _run(tmp_path, (FIXTURES / "BigOutput.cs").read_text(encoding="utf-8"))
    missing = _run(tmp_path, "Console.WriteLine();", runner=CSharpRunner(dotnet_path=tmp_path / "missing-dotnet.exe"))
    wrong = _run(tmp_path, "Console.WriteLine();", runner=CSharpRunner(expected_sdk_version="0.0.0"))

    assert timed_out.status == RunStatus.TIMED_OUT
    assert timed_out.error_code == "run_timeout"
    assert overflow.status == RunStatus.OUTPUT_OVERFLOW
    assert overflow.error_code == "output_limit_exceeded"
    assert missing.status == RunStatus.TOOL_MISSING
    assert wrong.status == RunStatus.TOOL_MISSING
    assert wrong.error_code == "wrong_dotnet_sdk_version"


def test_csharp_runner_keeps_hidden_test_content_server_only(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        'Console.WriteLine("visible");',
        visible_tests=("visible\n",),
        hidden_tests=("HIDDEN_CSHARP_SENTINEL",),
    )

    assert result.status == RunStatus.FAILED
    assert result.tests is not None
    assert result.tests.hidden_passed == 0
    assert result.tests.hidden_total == 1
    public = result.public_payload()
    assert "HIDDEN_CSHARP_SENTINEL" not in str(public)
    assert "hidden_passed" not in str(public)
    assert "hidden_total" not in str(public)


def test_csharp_runner_does_not_leak_hidden_source_or_workspace_from_compile_diagnostics(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        'Console.WriteLine("visible");',
        visible_test_cases=(ExecutableTestCase(stdout="visible\n"),),
        hidden_test_cases=(ExecutableTestCase(stdin="HIDDEN_STDIN", stdout="HIDDEN_EXPECTED"),),
    )

    assert result.status == RunStatus.FAILED
    public = result.public_payload()
    assert "HIDDEN_STDIN" not in str(public)
    assert "HIDDEN_EXPECTED" not in str(public)
    assert str(tmp_path) not in str(public)


def test_csharp_runner_stops_when_cancellation_is_already_requested(tmp_path: Path) -> None:
    cancellation = threading.Event()
    cancellation.set()

    result = _direct(tmp_path, "Console.WriteLine(\"never\");", cancellation=cancellation)

    assert result.status == RunStatus.CANCELLED
    assert result.error_code == "cancelled"


def test_csharp_runner_rejects_submission_without_primary_source(tmp_path: Path) -> None:
    result = CSharpRunner().run(
        Submission(language="csharp", files={}, idempotency_key="missing-main"),
        tmp_path,
        threading.Event(),
    )

    assert result.status == RunStatus.REJECTED
    assert result.error_code == "missing_main_source"


def test_create_app_registers_csharp_alongside_existing_runners(tmp_path: Path) -> None:
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
    assert isinstance(adapters["csharp"], CSharpRunner)


def _csharp_content_tree(tmp_path: Path) -> Path:
    content_root = tmp_path / "content"
    module_dir = content_root / "csharp" / "csharp-probe"
    module_dir.mkdir(parents=True)
    (content_root / "concepts.yaml").write_text(
        """
concepts:
  - id: variables
    name: Variables
    description: Named values.
""",
        encoding="utf-8",
    )
    (module_dir / "probe.md").write_text(
        "\n".join(
            [
                "---",
                "id: csharp-probe-probe",
                "title: Probe",
                "concepts: [variables]",
                "objectives:",
                "  - 目标一",
                "prerequisites: []",
                "difficulty: beginner",
                "experience_points: 50",
                "source_url: https://www.runoob.com/csharp/csharp-tutorial.html",
                "source_snapshot_date: 2026-08-29",
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
  "lesson_id": "csharp-probe-probe",
  "questions": [
    {
      "id": "csharp-probe-probe-c01",
      "type": "code",
      "prompt": "大写输出",
      "starter_code": "Console.WriteLine();",
      "visible_tests": ["普通输入"],
      "experience_points": 20,
      "private": {
        "reference_solution": "var value = Console.ReadLine() ?? \\"\\"; Console.WriteLine(value.ToUpperInvariant());",
        "hidden_tests": ["边界输入"],
        "visible_test_cases": [{"stdin": "abc\\n", "stdout": "ABC\\n", "exit_code": 0}],
        "hidden_test_cases": [{"stdin": "zz\\n", "stdout": "ZZ\\n", "exit_code": 0}]
      }
    }
  ]
}
""",
        encoding="utf-8",
    )
    (content_root / "csharp" / "course.yaml").write_text(
        "\n".join(
            [
                "language: csharp",
                "title: C#",
                "growth:",
                "  review_milestone_points: 15",
                "  badge_points:",
                "    first_lesson: 20",
                "    first_module_mastery: 30",
                "    seven_day_streak: 40",
                "placement_tests: []",
                "modules:",
                "  - id: csharp-probe",
                "    title: Probe Module",
                "    prerequisites: []",
                "    source_coverage:",
                "      - source_id: probe-source",
                "        lesson_id: csharp-probe-probe",
                "    lessons:",
                "      - id: csharp-probe-probe",
                "        path: csharp-probe/probe.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return content_root


def test_real_api_runs_csharp_without_exposing_hidden_or_reference_data(tmp_path: Path) -> None:
    content_root = _csharp_content_tree(tmp_path)
    settings = replace(make_settings(content_root), runner_work_dir=tmp_path / "runner-work")
    migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))
    app = create_app(settings)

    with TestClient(app) as client:
        created = client.post(
            "/api/runners/submissions",
            json={
                "lesson_id": "csharp-probe-probe",
                "exercise_id": "csharp-probe-probe-c01",
                "source_code": 'var value = Console.ReadLine() ?? ""; Console.WriteLine(value.ToUpperInvariant());',
                "stdin": "",
            },
            headers={"Idempotency-Key": "csharp-api"},
        )
        job_id = created.json()["id"]
        job = app.state.runner_manager.wait(job_id, timeout=45)
        response = client.get(f"/api/runners/jobs/{job_id}")

    assert created.status_code == response.status_code == 200
    assert job.status == RunStatus.SUCCEEDED
    text = response.text
    assert "reference_solution" not in text
    assert "hidden" not in text.lower()
    assert "边界输入" not in text
    assert response.json()["result"]["tests"] == {"visible_passed": 1, "visible_total": 1}
