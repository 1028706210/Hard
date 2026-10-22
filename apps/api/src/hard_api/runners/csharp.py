"""C# runner for TRUSTED_LOCAL_LEARNING_ONLY.

This runner limits resources and controls the build contract,
but it is not a security sandbox for malicious or untrusted code.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import threading
import time

from hard_api.diagnostics.csharp import normalize_csharp_diagnostic
from hard_api.runners.contracts import CompileResult, ExecutableTestCase, RunResult, RunStatus, Submission, TestResult
from hard_api.runners.limits import COMPILE_TIMEOUT_SECONDS, MAX_OUTPUT_BYTES, RUN_TIMEOUT_SECONDS
from hard_api.runners.processes import ProcessStatus, execute_process


DOTNET_EXECUTABLE = Path("D:/DevTools/dotnet/dotnet.exe")
EXPECTED_DOTNET_SDK_VERSION = "10.0.100"
TARGET_FRAMEWORK = "net10.0"
NUGET_PACKAGES = Path("D:/projects/1/.hard-nuget/packages")
PROJECT_FILE = "HardSubmission.csproj"
SOURCE_FILE = "Program.cs"
PRELUDE_FILE = "HardPrelude.cs"
PROJECT_TEMPLATE = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <EnableDefaultItems>false</EnableDefaultItems>
    <AllowUnsafeBlocks>false</AllowUnsafeBlocks>
    <RestoreSources></RestoreSources>
    <RestoreAdditionalProjectSources></RestoreAdditionalProjectSources>
    <RestoreIgnoreFailedSources>true</RestoreIgnoreFailedSources>
    <DisableImplicitNuGetFallbackFolder>true</DisableImplicitNuGetFallbackFolder>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="Program.cs" />
    <Compile Include="HardPrelude.cs" />
  </ItemGroup>
</Project>
"""
PRELUDE_SOURCE = """using System;
using System.Runtime.CompilerServices;
using System.Text;

internal static class HardPrelude
{
    [ModuleInitializer]
    internal static void Initialize()
    {
        Console.InputEncoding = Encoding.UTF8;
        Console.OutputEncoding = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false);
        AppDomain.CurrentDomain.UnhandledException += (_, args) =>
        {
            if (args.ExceptionObject is Exception exception)
            {
                Console.Error.WriteLine(exception.GetType().FullName + ": " + exception.Message);
                Environment.Exit(1);
            }
        };
    }
}
"""

_PROJECT_INJECTION_MARKERS = (
    "<Project",
    "<PackageReference",
    "<RestoreSources",
    "<Import",
    "<Exec",
    "<UsingTask",
)

_UNSAFE_EXERCISE_KEYS = frozenset(
    {
        ("csharp-capstone-unsafe-code", "csharp-capstone-unsafe-code-c01"),
    }
)


class CSharpRunner:
    def __init__(
        self,
        *,
        dotnet_path: Path = DOTNET_EXECUTABLE,
        expected_sdk_version: str = EXPECTED_DOTNET_SDK_VERSION,
        compile_timeout_seconds: float = COMPILE_TIMEOUT_SECONDS,
        run_timeout_seconds: float = RUN_TIMEOUT_SECONDS,
        allow_unsafe: bool = False,
        nuget_packages: Path = NUGET_PACKAGES,
    ) -> None:
        self.dotnet_path = dotnet_path
        self.expected_sdk_version = expected_sdk_version
        self.compile_timeout_seconds = compile_timeout_seconds
        self.run_timeout_seconds = run_timeout_seconds
        self.allow_unsafe = allow_unsafe
        self.nuget_packages = nuget_packages

    def run(self, submission: Submission, workspace: Path, cancellation: threading.Event) -> RunResult:
        if cancellation.is_set():
            return RunResult(status=RunStatus.CANCELLED, error_code="cancelled")
        source = submission.files.get("main.py")
        if not isinstance(source, str) or not source.strip():
            return RunResult(status=RunStatus.REJECTED, error_code="missing_main_source")
        if self._looks_like_project_injection(source):
            return RunResult(status=RunStatus.REJECTED, error_code="invalid_csharp_source")
        tool_status = self._toolchain_status(workspace)
        if tool_status is not None:
            return tool_status

        project_path = workspace / PROJECT_FILE
        source_path = workspace / SOURCE_FILE
        project_path.write_text(self._project_template(submission), encoding="utf-8", newline="\n")
        source_path.write_text(source, encoding="utf-8", newline="\n")
        (workspace / PRELUDE_FILE).write_text(PRELUDE_SOURCE, encoding="utf-8", newline="\n")
        self._write_no_restore_assets(workspace)

        environment = self._environment(workspace)
        compiled = execute_process(
            [
                str(self.dotnet_path),
                "build",
                PROJECT_FILE,
                "--no-restore",
                "--configuration",
                "Release",
                "-p:UseSharedCompilation=false",
                "--disable-build-servers",
                "-nodeReuse:false",
                "--nologo",
            ],
            cwd=workspace,
            environment=environment,
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
            diagnostic = normalize_csharp_diagnostic(f"{compiled.stdout}\n{compiled.stderr}", workspace)
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
        deadline = time.monotonic() + self.run_timeout_seconds
        assembly = (workspace / "bin" / "Release" / TARGET_FRAMEWORK / "HardSubmission.dll").resolve()
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
                [str(self.dotnet_path), str(assembly)],
                cwd=workspace,
                environment=environment,
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
                diagnostic = normalize_csharp_diagnostic(executed.stderr, workspace)
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

    def _project_template(self, submission: Submission) -> str:
        server_allows_unsafe = (submission.lesson_id, submission.exercise_id) in _UNSAFE_EXERCISE_KEYS
        if not self.allow_unsafe and not server_allows_unsafe:
            return PROJECT_TEMPLATE
        return PROJECT_TEMPLATE.replace(
            "<AllowUnsafeBlocks>false</AllowUnsafeBlocks>",
            "<AllowUnsafeBlocks>true</AllowUnsafeBlocks>",
        )

    def _toolchain_status(self, workspace: Path) -> RunResult | None:
        if not self.dotnet_path.is_file():
            return RunResult(status=RunStatus.TOOL_MISSING, error_code="tool_missing")
        try:
            completed = subprocess.run(
                [str(self.dotnet_path), "--version"],
                cwd=str(workspace.resolve()),
                env=self._minimal_tool_environment(workspace),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                check=False,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            )
        except (OSError, subprocess.TimeoutExpired):
            return RunResult(status=RunStatus.TOOL_MISSING, error_code="tool_missing")
        version = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else ""
        if completed.returncode != 0 or version != self.expected_sdk_version:
            return RunResult(status=RunStatus.TOOL_MISSING, error_code="wrong_dotnet_sdk_version")
        return None

    def _environment(self, workspace: Path) -> dict[str, str]:
        environment = self._minimal_tool_environment(workspace)
        environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
        environment["DOTNET_SKIP_FIRST_TIME_EXPERIENCE"] = "1"
        environment["DOTNET_NOLOGO"] = "1"
        environment["DOTNET_CLI_UI_LANGUAGE"] = "en"
        environment["DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE"] = "1"
        environment["DOTNET_CLI_HOME"] = str(workspace.resolve())
        environment["NUGET_PACKAGES"] = str(self.nuget_packages)
        return environment

    @staticmethod
    def _minimal_tool_environment(workspace: Path) -> dict[str, str]:
        dotnet_home = workspace.resolve() / ".dotnet-home"
        local_app_data = dotnet_home / "local-app-data"
        app_data = dotnet_home / "app-data"
        local_app_data.mkdir(parents=True, exist_ok=True)
        app_data.mkdir(parents=True, exist_ok=True)
        return {
            "SystemRoot": "C:\\Windows",
            "WINDIR": "C:\\Windows",
            "TEMP": str(workspace.resolve()),
            "TMP": str(workspace.resolve()),
            "USERPROFILE": str(dotnet_home),
            "LOCALAPPDATA": str(local_app_data),
            "APPDATA": str(app_data),
            "DOTNET_CLI_HOME": str(dotnet_home),
            # 防止 dotnet first-run 把重定向后的 <workspace>\.dotnet\tools 绝对路径
            # 写入真实用户 PATH 注册表（曾累积 354 条死路径导致 0xc0000017）。
            "DOTNET_ADD_GLOBAL_TOOLS_TO_PATH": "false",
            "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
            "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
            "DOTNET_NOLOGO": "1",
            "DOTNET_CLI_UI_LANGUAGE": "en",
            "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "1",
        }

    @staticmethod
    def _looks_like_project_injection(source: str) -> bool:
        return any(marker in source for marker in _PROJECT_INJECTION_MARKERS)

    def _write_no_restore_assets(self, workspace: Path) -> None:
        obj = workspace / "obj"
        obj.mkdir(exist_ok=True)
        project_path = workspace / PROJECT_FILE
        packages_path = self.nuget_packages
        assets = {
            "version": 3,
            "targets": {TARGET_FRAMEWORK: {}},
            "libraries": {},
            "projectFileDependencyGroups": {TARGET_FRAMEWORK: []},
            "packageFolders": {str(packages_path) + "\\": {}},
            "project": {
                "version": "1.0.0",
                "restore": {
                    "projectUniqueName": str(project_path),
                    "projectName": "HardSubmission",
                    "projectPath": str(project_path),
                    "packagesPath": str(packages_path),
                    "outputPath": str(obj) + "\\",
                    "projectStyle": "PackageReference",
                    "configFilePaths": [],
                    "originalTargetFrameworks": [TARGET_FRAMEWORK],
                    "sources": [],
                    "frameworks": {
                        TARGET_FRAMEWORK: {
                            "targetAlias": TARGET_FRAMEWORK,
                            "projectReferences": {},
                        }
                    },
                    "warningProperties": {
                        "warnAsError": ["NU1605"],
                    },
                },
                "frameworks": {
                    TARGET_FRAMEWORK: {
                        "targetAlias": TARGET_FRAMEWORK,
                        "dependencies": {},
                    }
                },
            },
        }
        (obj / "project.assets.json").write_text(json.dumps(assets, indent=2), encoding="utf-8", newline="\n")

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
