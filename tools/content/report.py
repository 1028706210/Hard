from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_SOURCE = PROJECT_ROOT / "apps" / "api" / "src"
if str(API_SOURCE) not in sys.path:
    sys.path.insert(0, str(API_SOURCE))

from hard_api.content.parser import parse_course, parse_exercises, parse_lesson, resolve_content_path
from hard_api.runners.contracts import ExecutableTestCase, RunStatus, Submission
from hard_api.runners.python import PythonRunner


REQUIRED_LESSON_SECTIONS = ("概念定义与适用场景", "语法、API 与边界", "常见错误与实践建议")


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    path: Path
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path.as_posix(), "message": self.message}


@dataclass(slots=True)
class ValidationReport:
    courses: int = 0
    lessons: int = 0
    exercises: int = 0
    expected: int = 0
    implemented: int = 0
    validated: int = 0
    reference_solutions_passed: int = 0
    reference_solution_execution_evidence: bool = False
    errors: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "counts": {
                "courses": self.courses,
                "lessons": self.lessons,
                "exercises": self.exercises,
            },
            "errors": [issue.as_dict() for issue in self.errors],
        }

    def coverage_metrics(self) -> dict[str, int]:
        return {
            "expected": self.expected,
            "implemented": self.implemented,
            "validated": self.validated,
            "reference_solutions_passed": self.reference_solutions_passed,
        }

    def chinese_summary(self) -> str:
        if self.valid:
            return f"内容校验通过：{self.courses} 门课程、{self.lessons} 节课、{self.exercises} 份练习。"
        return f"内容校验失败：发现 {len(self.errors)} 个问题。"


def _runner_case(case: object) -> ExecutableTestCase:
    return ExecutableTestCase(
        stdin=str(getattr(case, "stdin")),
        stdout=getattr(case, "stdout"),
        exit_code=int(getattr(case, "exit_code")),
        assertion=getattr(case, "assertion"),
    )


def reference_solution_execution_metrics(
    content_root: Path, language: str, module: str, runner: PythonRunner | None = None
) -> tuple[int, bool]:
    """Run private executable references in a disposable D-drive workspace.

    The returned count is lesson-level: a covered lesson counts only when every
    executable reference in that lesson passes both visible and hidden cases.
    """
    course_path = content_root / language / "course.yaml"
    try:
        course = parse_course(course_path)
    except Exception:
        return 0, False
    selected = next((item for item in course.modules if item.id == module), None)
    if selected is None:
        return 0, False

    active_runner = runner or PythonRunner()
    attempted = False
    passed_lessons = 0
    cache_root = PROJECT_ROOT / ".tool-cache"
    cache_root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="content-runner-", dir=cache_root) as temporary:
        workspace_root = Path(temporary)
        for lesson_entry in selected.lessons:
            try:
                lesson_path = resolve_content_path(content_root / language, lesson_entry.path)
                exercises = parse_exercises(lesson_path.with_suffix(".exercises.json"))
            except Exception:
                continue
            executable = [
                question
                for question in exercises.questions
                if question.type in {"code", "challenge"} and question.private is not None
            ]
            if not executable:
                continue
            lesson_passed = True
            for index, question in enumerate(executable):
                private = question.private
                assert private is not None
                if private.reference_solution is None:
                    lesson_passed = False
                    continue
                attempted = True
                workspace = workspace_root / f"{lesson_entry.id}-{index}"
                workspace.mkdir()
                (workspace / "main.py").write_text(private.reference_solution, encoding="utf-8")
                result = active_runner.run(
                    Submission(
                        language=language,
                        files={"main.py": private.reference_solution},
                        visible_test_cases=tuple(_runner_case(case) for case in private.visible_test_cases),
                        hidden_test_cases=tuple(_runner_case(case) for case in private.hidden_test_cases),
                        lesson_id=lesson_entry.id,
                        exercise_id=question.id,
                        idempotency_key=f"content-{question.id}",
                    ),
                    workspace,
                    Event(),
                )
                expected_visible = len(private.visible_test_cases)
                expected_hidden = len(private.hidden_test_cases)
                if (
                    result.status != RunStatus.SUCCEEDED
                    or result.tests is None
                    or result.tests.visible_passed != expected_visible
                    or result.tests.hidden_passed != expected_hidden
                ):
                    lesson_passed = False
            if lesson_passed:
                passed_lessons += 1
    return passed_lessons, attempted


def assessment_contract_details(content_root: Path, language: str, module: str) -> dict[str, object]:
    """Aggregate audit evidence without exposing private test text or solutions."""
    course = parse_course(content_root / language / "course.yaml")
    selected = next(item for item in course.modules if item.id == module)
    question_counts = {"knowledge": 0, "code": 0, "challenge": 0}
    visible_count = hidden_count = hidden_distinct_count = 0
    section_by_lesson: dict[str, tuple[str, list[str]]] = {}
    for entry in selected.lessons:
        lesson_path = resolve_content_path(content_root / language, entry.path)
        lesson = parse_lesson(lesson_path)
        section_by_lesson[entry.id] = (
            lesson.front_matter.title,
            [heading for heading in REQUIRED_LESSON_SECTIONS if f"## {heading}" in lesson.body],
        )
        exercises = parse_exercises(lesson_path.with_suffix(".exercises.json"))
        for question in exercises.questions:
            if question.type in question_counts:
                question_counts[question.type] += 1
            if question.type not in {"code", "challenge"} or question.private is None:
                continue
            visible = {
                (case.stdin, case.stdout, case.exit_code, case.assertion)
                for case in question.private.visible_test_cases
            }
            hidden = [
                (case.stdin, case.stdout, case.exit_code, case.assertion)
                for case in question.private.hidden_test_cases
            ]
            visible_count += len(visible)
            hidden_count += len(hidden)
            hidden_distinct_count += sum(case not in visible for case in hidden)
    source_section_mapping = []
    for coverage in selected.source_coverage:
        title, sections = section_by_lesson[coverage.lesson_id]
        source_section_mapping.append(
            {
                "source_id": coverage.source_id,
                "lesson_id": coverage.lesson_id,
                "source_primary_topic": title,
                "hard_sections": sections,
            }
        )
    return {
        "question_counts": question_counts,
        "test_case_counts": {
            "visible": visible_count,
            "hidden": hidden_count,
            "hidden_distinct_from_visible": hidden_distinct_count,
        },
        "source_section_mapping": source_section_mapping,
    }


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    argument_parser = argparse.ArgumentParser(description="生成 Hard 课程覆盖报告。")
    argument_parser.add_argument("--content-root", type=Path, default=PROJECT_ROOT / "content")
    argument_parser.add_argument("--language", required=True, help="课程语言")
    argument_parser.add_argument("--module", required=True, help="模块稳定 ID")
    argument_parser.add_argument("--json", required=True, type=Path, help="JSON 报告路径")
    arguments = argument_parser.parse_args(argv)

    from validate import validate_content

    report = validate_content(
        arguments.content_root,
        language=arguments.language,
        module=arguments.module,
        require_complete=True,
    )
    report.reference_solutions_passed, report.reference_solution_execution_evidence = (
        reference_solution_execution_metrics(arguments.content_root, arguments.language, arguments.module)
    )
    metrics = report.coverage_metrics()
    report_errors = [issue.as_dict() for issue in report.errors]
    if len(set(metrics.values())) != 1:
        report_errors.append(
            {
                "code": "coverage_metrics_mismatch",
                "path": "",
                "message": "覆盖指标必须完全相等。",
            }
        )
    if not report.reference_solution_execution_evidence:
        report_errors.append(
            {
                "code": "reference_solution_execution_unavailable",
                "path": "",
                "message": "没有参考解真实执行通过证据。",
            }
        )
    payload = {
        "language": arguments.language,
        "module": arguments.module,
        **metrics,
        **assessment_contract_details(arguments.content_root, arguments.language, arguments.module),
        "errors": report_errors,
    }
    arguments.json.parent.mkdir(parents=True, exist_ok=True)
    arguments.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if report_errors:
        print(f"覆盖报告失败：发现 {len(report_errors)} 个问题。", file=sys.stderr)
        return 1
    print(report.chinese_summary(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
