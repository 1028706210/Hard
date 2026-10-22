from __future__ import annotations

import re
import shutil
import sys
import threading
import time
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import psutil
import pytest
from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content"))

from hard_api.main import create_app
from hard_api.core.config import Settings
from hard_api.db import migrations
from hard_api.backup.service import LocalBackupService
from hard_api.runners import cpp as cpp_module
from hard_api.runners.contracts import ExecutableTestCase, RunStatus, Submission
from hard_api.runners.cpp import CppRunner
from hard_api.runners.manager import RunManager
from hard_api.runners.processes import ProcessResult, ProcessStatus
from test_catalog import make_settings


FIXTURES = Path(__file__).parent / "fixtures" / "cpp"
ROOT = Path(__file__).resolve().parents[4]

# MSYS2 as.exe/ld.exe 无法在含非 ASCII 字符的路径（本机默认 pytest tmp_path 所在的
# 中文用户名 Temp 目录）创建目标文件；生产 runner-work 位于仓库内 ASCII 路径，不受影响。
# 因此本测试套件把工作区固定到 ASCII 路径下。
_ASCII_WORK_ROOT = Path(r"D:\projects\1\.hard-cpp-test-work")


@pytest.fixture()
def tmp_path() -> Path:
    path = _ASCII_WORK_ROOT / uuid4().hex
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _run(
    tmp_path: Path,
    source: str,
    *,
    files: dict[str, str] | None = None,
    stdin: str = "",
    visible_tests: tuple[str, ...] = (),
    hidden_tests: tuple[str, ...] = (),
    visible_test_cases=(),
    hidden_test_cases=(),
    runner: CppRunner | None = None,
):
    root = tmp_path / "runner-work"
    manager = RunManager(root, adapters={"cpp": runner or CppRunner()})
    job = manager.submit(
        Submission(
            language="cpp",
            files=files if files is not None else {"main.py": source},
            stdin=stdin,
            visible_tests=visible_tests,
            hidden_tests=hidden_tests,
            visible_test_cases=visible_test_cases,
            hidden_test_cases=hidden_test_cases,
            idempotency_key="cpp-test",
        )
    )
    result = manager.wait(job.id, timeout=60).result
    manager.shutdown()
    assert list(root.iterdir()) == []
    assert result is not None
    return result


def _direct(
    tmp_path: Path,
    source: str,
    *,
    cancellation: threading.Event | None = None,
    runner: CppRunner | None = None,
):
    return (runner or CppRunner()).run(
        Submission(language="cpp", files={"main.py": source}, idempotency_key="cpp-direct"),
        tmp_path,
        cancellation or threading.Event(),
    )


def test_cpp_runner_executes_program_with_stdin_utf8_and_counts(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "Hello.cpp").read_text(encoding="utf-8"),
        stdin="小明\n",
        visible_tests=("Hello, 小明!\n",),
        hidden_tests=("Hello, 小明!\n",),
    )

    assert result.status == RunStatus.SUCCEEDED
    assert result.compile is not None and result.compile.passed
    assert result.tests is not None
    assert (result.tests.visible_passed, result.tests.visible_total) == (1, 1)
    assert (result.tests.hidden_passed, result.tests.hidden_total) == (1, 1)
    assert result.stdout == "Hello, 小明!\n"


def test_cpp_runner_compiles_cpp20_features(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "Cpp20.cpp").read_text(encoding="utf-8"),
        visible_tests=("1 4 9 16 25 \n",),
    )

    assert result.status == RunStatus.SUCCEEDED
    assert result.stdout == "1 4 9 16 25 \n"


def test_cpp_runner_supports_multiple_controlled_sources(tmp_path: Path) -> None:
    files = {
        "main.py": (
            '#include <iostream>\n#include <string>\n#include "util.h"\n'
            "int main() {\n"
            "    std::string name;\n"
            "    std::getline(std::cin, name);\n"
            "    std::cout << greet(name) << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        "util.h": "#include <string>\nstd::string greet(const std::string& name);\n",
        "util.cpp": (
            '#include <string>\n#include "util.h"\n'
            "std::string greet(const std::string& name) { return \"你好,\" + name + \"!\"; }\n"
        ),
    }

    result = _run(tmp_path, files["main.py"], files=files, stdin="小明\n", visible_tests=("你好,小明!\n",))

    assert result.status == RunStatus.SUCCEEDED
    assert result.stdout == "你好,小明!\n"


def test_cpp_runner_reports_compile_error_with_normalized_diagnostic(tmp_path: Path) -> None:
    result = _run(tmp_path, (FIXTURES / "SyntaxError.cpp").read_text(encoding="utf-8"))

    assert result.status == RunStatus.FAILED
    assert result.compile is not None and not result.compile.passed
    assert result.error_code == "compile_failed"
    diagnostic = result.diagnostics[0]
    assert "编译错误" in diagnostic
    assert re.search(r"main\.cpp 第 \d+ 行", diagnostic)
    assert str(tmp_path) not in diagnostic
    assert str(tmp_path).replace("\\", "/") not in diagnostic


def test_cpp_runner_classifies_nonzero_exit_as_runtime_failure(tmp_path: Path) -> None:
    result = _run(tmp_path, (FIXTURES / "RuntimeError.cpp").read_text(encoding="utf-8"))

    assert result.status == RunStatus.FAILED
    assert result.error_code == "runtime_failed"
    assert "运行错误" in result.diagnostics[0]
    assert str(tmp_path) not in result.diagnostics[0]


def test_cpp_runner_reports_test_failure_when_stdout_mismatches(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        (FIXTURES / "Hello.cpp").read_text(encoding="utf-8"),
        stdin="Ada\n",
        visible_tests=("WRONG EXPECTATION\n",),
    )

    assert result.status == RunStatus.FAILED
    assert result.error_code == "tests_failed"
    assert result.tests is not None
    assert (result.tests.visible_passed, result.tests.visible_total) == (0, 1)


def test_cpp_runner_enforces_timeout(tmp_path: Path) -> None:
    quick = CppRunner(run_timeout_seconds=0.6)

    result = _run(tmp_path, (FIXTURES / "InfiniteLoop.cpp").read_text(encoding="utf-8"), runner=quick)

    assert result.status == RunStatus.TIMED_OUT
    assert result.error_code == "run_timeout"


def test_cpp_runner_enforces_output_limit(tmp_path: Path) -> None:
    result = _run(tmp_path, (FIXTURES / "BigOutput.cpp").read_text(encoding="utf-8"))

    assert result.status == RunStatus.OUTPUT_OVERFLOW
    assert result.error_code == "output_limit_exceeded"


def test_cpp_runner_stops_when_cancellation_is_requested(tmp_path: Path) -> None:
    cancellation = threading.Event()
    cancellation.set()

    result = _direct(tmp_path, '#include <cstdio>\nint main(){ std::puts("never"); }', cancellation=cancellation)

    assert result.status == RunStatus.CANCELLED
    assert result.error_code == "cancelled"


def test_cpp_runner_terminates_spawned_process_tree(tmp_path: Path) -> None:
    quick = CppRunner(run_timeout_seconds=0.8)

    result = _run(tmp_path, (FIXTURES / "SpawnsChild.cpp").read_text(encoding="utf-8"), runner=quick)

    assert result.status == RunStatus.TIMED_OUT
    time.sleep(1.5)
    survivors = [
        process.pid
        for process in psutil.process_iter(("pid", "name"))
        if str(process.info["name"] or "").lower() == "hard_submission.exe"
    ]
    assert not survivors, survivors


def test_cpp_runner_returns_tool_missing_when_gpp_absent(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        '#include <cstdio>\nint main(){ std::puts("ok"); }',
        runner=CppRunner(gpp_path=tmp_path / "missing-gpp.exe"),
    )

    assert result.status == RunStatus.TOOL_MISSING
    assert result.error_code == "tool_missing"


def test_cpp_runner_rejects_submission_without_primary_source(tmp_path: Path) -> None:
    result = CppRunner().run(
        Submission(language="cpp", files={}, idempotency_key="missing-main"),
        tmp_path,
        threading.Event(),
    )

    assert result.status == RunStatus.REJECTED
    assert result.error_code == "missing_main_source"


def test_cpp_runner_controls_compile_and_link_arguments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    recorded: list[tuple[list[str], dict[str, str], str, Path]] = []

    def fake_execute(arguments, *, cwd, environment, stdin, timeout_seconds, output_limit_bytes, cancellation=None):
        recorded.append((list(arguments), dict(environment), stdin, Path(cwd)))
        if "-o" in arguments:
            assert (Path(cwd) / "main.cpp").read_text(encoding="utf-8").startswith("#include")
            for dll in cpp_module.TOOLCHAIN_SUPPORT_DLLS:
                assert (Path(cwd) / dll).is_file()
        return ProcessResult(ProcessStatus.COMPLETED, "ok\n", "", 0, 5)

    monkeypatch.setattr(cpp_module, "execute_process", fake_execute)

    result = _run(
        tmp_path,
        '#include <cstdio>\nint main(){ std::puts("ok"); }',
        visible_tests=("ok\n",),
    )

    assert result.status == RunStatus.SUCCEEDED
    build_args, build_env, build_stdin, build_cwd = recorded[0]
    run_args, run_env, run_stdin, run_cwd = recorded[1]
    assert build_args == [
        str(cpp_module.GPP_EXECUTABLE),
        "-std=c++20",
        "-Wall",
        "-Wextra",
        "-static",
        "-finput-charset=UTF-8",
        "-fexec-charset=UTF-8",
        "-B",
        str(cpp_module.GPP_EXECUTABLE.parent) + "\\",
        "-o",
        cpp_module.OUTPUT_NAME,
        "main.cpp",
    ]
    assert run_args == [str(build_cwd / cpp_module.OUTPUT_NAME)]
    assert build_stdin == ""
    assert build_cwd == run_cwd
    assert "PATH" not in build_env
    assert "PATH" not in run_env


def test_cpp_runner_keeps_hidden_test_content_server_only(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        '#include <cstdio>\nint main(){ std::puts("visible"); }',
        visible_tests=("visible\n",),
        hidden_tests=("HIDDEN_CPP_SENTINEL",),
    )

    assert result.status == RunStatus.FAILED
    assert result.tests is not None
    assert result.tests.hidden_passed == 0
    assert result.tests.hidden_total == 1
    public = result.public_payload()
    assert "HIDDEN_CPP_SENTINEL" not in str(public)
    assert "hidden_passed" not in str(public)
    assert "hidden_total" not in str(public)


def test_create_app_registers_cpp_alongside_existing_runners(tmp_path: Path) -> None:
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
    assert isinstance(adapters["cpp"], CppRunner)


def _cpp_content_tree(tmp_path: Path) -> Path:
    content_root = tmp_path / "content"
    module_dir = content_root / "cpp" / "cpp-probe"
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
                "id: cpp-probe-probe",
                "title: Probe",
                "concepts: [variables]",
                "objectives:",
                "  - 目标一",
                "prerequisites: []",
                "difficulty: beginner",
                "experience_points: 50",
                "source_url: https://www.runoob.com/cplusplus/cpp-tutorial.html",
                "source_snapshot_date: 2026-09-02",
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
  "lesson_id": "cpp-probe-probe",
  "questions": [
    {
      "id": "cpp-probe-probe-c01",
      "type": "code",
      "prompt": "大写输出",
      "starter_code": "#include <iostream>\\nint main() { }",
      "visible_tests": ["普通输入"],
      "experience_points": 20,
      "private": {
        "reference_solution": "#include <algorithm>\\n#include <cctype>\\n#include <iostream>\\n#include <string>\\nint main() { std::string s; std::getline(std::cin, s); std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::toupper(c); }); std::cout << s << std::endl; }",
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
    (content_root / "cpp" / "course.yaml").write_text(
        "\n".join(
            [
                "language: cpp",
                "title: C++",
                "growth:",
                "  review_milestone_points: 15",
                "  badge_points:",
                "    first_lesson: 20",
                "    first_module_mastery: 30",
                "    seven_day_streak: 40",
                "placement_tests: []",
                "modules:",
                "  - id: cpp-probe",
                "    title: Probe Module",
                "    prerequisites: []",
                "    source_coverage:",
                "      - source_id: probe-source",
                "        lesson_id: cpp-probe-probe",
                "    lessons:",
                "      - id: cpp-probe-probe",
                "        path: cpp-probe/probe.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return content_root


def test_real_api_runs_cpp_without_exposing_hidden_or_reference_data(tmp_path: Path) -> None:
    content_root = _cpp_content_tree(tmp_path)
    settings = replace(make_settings(content_root), runner_work_dir=tmp_path / "runner-work")
    migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))
    app = create_app(settings)

    with TestClient(app) as client:
        created = client.post(
            "/api/runners/submissions",
            json={
                "lesson_id": "cpp-probe-probe",
                "exercise_id": "cpp-probe-probe-c01",
                "source_code": (
                    "#include <algorithm>\n#include <cctype>\n#include <iostream>\n#include <string>\n"
                    "int main() { std::string s; std::getline(std::cin, s); "
                    "std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::toupper(c); }); "
                    "std::cout << s << std::endl; }"
                ),
                "stdin": "",
            },
            headers={"Idempotency-Key": "cpp-api"},
        )
        job_id = created.json()["id"]
        job = app.state.runner_manager.wait(job_id, timeout=60)
        response = client.get(f"/api/runners/jobs/{job_id}")

    assert created.status_code == response.status_code == 200
    assert job.status == RunStatus.SUCCEEDED
    text = response.text
    assert "reference_solution" not in text
    assert "hidden" not in text.lower()
    assert "边界输入" not in text
    assert response.json()["result"]["tests"] == {"visible_passed": 1, "visible_total": 1}
