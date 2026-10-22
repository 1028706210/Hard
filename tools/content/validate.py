from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIRECTORY.parents[1]
API_SOURCE = PROJECT_ROOT / "apps" / "api" / "src"
if str(API_SOURCE) not in sys.path:
    sys.path.insert(0, str(API_SOURCE))

from hard_api.content.parser import (  # noqa: E402
    ContentParseError,
    load_json_mapping,
    load_yaml_mapping,
    parse_concepts,
    parse_course,
    parse_exercises,
    parse_lesson,
    resolve_content_path,
)
from report import ValidationIssue, ValidationReport  # noqa: E402
from schema import validate_schema_contracts  # noqa: E402


COURSE_IDS = {"python", "java", "csharp", "cpp"}
STABLE_ID = re.compile(r"^(python|java|csharp|cpp)-[a-z0-9]+(?:-[a-z0-9]+)*$")
PRIVATE_FIELDS = {"reference_answer", "reference_solution", "hidden_tests"}
FENCED_CODE_BLOCK = re.compile(r"^```[^\n]*\n(?P<code>[\s\S]*?)^```", re.MULTILINE)
REQUIRED_LESSON_SECTIONS = ("概念定义与适用场景", "语法、API 与边界", "常见错误与实践建议")
GENERIC_LESSON_EXPLANATION = "解决的是把明确输入转换为可核验结果的问题。"


def add_issue(report: ValidationReport, code: str, path: Path, message: str) -> None:
    report.errors.append(ValidationIssue(code=code, path=path, message=message))


def validate_stable_id(value: str, path: Path, report: ValidationReport) -> None:
    if not STABLE_ID.fullmatch(value):
        add_issue(report, "invalid_id", path, f"稳定 ID 不符合规则：{value}")


def detect_prerequisite_cycles(
    prerequisites: dict[str, list[str]], path: Path, report: ValidationReport, code: str, label: str
) -> set[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    cyclic: set[str] = set()
    stack: list[str] = []

    def visit(item_id: str) -> None:
        if item_id in visited:
            return
        if item_id in visiting:
            add_issue(report, code, path, f"{label}前置关系存在环：{item_id}")
            cyclic.update(stack[stack.index(item_id) :])
            return
        visiting.add(item_id)
        stack.append(item_id)
        for prerequisite in prerequisites[item_id]:
            if prerequisite in prerequisites:
                visit(prerequisite)
        stack.pop()
        visiting.remove(item_id)
        visited.add(item_id)

    for item_id in prerequisites:
        visit(item_id)
    return cyclic


def find_private_leaks(value: Any, path: Path, report: ValidationReport, in_private: bool = False) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_private = in_private or key == "private"
            if key in PRIVATE_FIELDS and not in_private:
                add_issue(report, "private_leak", path, f"私有字段不得出现在公开练习数据中：{key}")
            find_private_leaks(child, path, report, child_private)
    elif isinstance(value, list):
        for child in value:
            find_private_leaks(child, path, report, in_private)


def validate_static_lesson_contract(
    lesson: Any, exercises: Any, path: Path, report: ValidationReport
) -> bool:
    if len(lesson.front_matter.objectives) < 2:
        add_issue(report, "incomplete_objectives", path, "完整课时至少需要 2 个学习目标。")
    if any(not objective.strip() for objective in lesson.front_matter.objectives):
        add_issue(report, "empty_objective", path, "学习目标不能为空。")
    examples = list(FENCED_CODE_BLOCK.finditer(lesson.body))
    if len(examples) < 2:
        add_issue(report, "incomplete_examples", path, "完整课时至少需要 2 个代码示例。")
    elif any(not example.group("code").strip() for example in examples):
        add_issue(report, "empty_code_example", path, "代码示例不能为空。")
    if any(f"## {heading}" not in lesson.body for heading in REQUIRED_LESSON_SECTIONS):
        add_issue(report, "incomplete_lesson_explanation", path, "课时缺少定义、API 边界或实践建议章节。")
    if GENERIC_LESSON_EXPLANATION in lesson.body:
        add_issue(report, "generic_lesson_explanation", path, "课时说明不得复用与主题无关的泛化段落。")
    knowledge_questions = [question for question in exercises.questions if question.type == "knowledge"]
    if len(knowledge_questions) < 3:
        add_issue(report, "incomplete_knowledge_questions", path, "完整课时至少需要 3 道知识题。")
    if any(
        question.private is None or not _has_text(question.private.reference_answer)
        for question in knowledge_questions
    ):
        add_issue(
            report,
            "invalid_knowledge_reference_answer",
            path,
            "知识题必须具有非空服务端参考答案。",
        )
    if any(not _has_valid_knowledge_choices(question) for question in knowledge_questions):
        add_issue(
            report,
            "invalid_knowledge_choices",
            path,
            "知识题必须提供 3 到 4 个唯一选项，且参考答案必须指向其中一个选项。",
        )
    code_questions = [question for question in exercises.questions if question.type == "code"]
    challenge_questions = [question for question in exercises.questions if question.type == "challenge"]
    if any(not _has_executable_contract(question) for question in code_questions):
        add_issue(report, "invalid_code_question", path, "代码题缺少可执行判定数据。")
    if any(not _has_executable_contract(question) for question in challenge_questions):
        add_issue(report, "invalid_challenge_question", path, "挑战题缺少可执行判定数据。")
    executable_questions = [*code_questions, *challenge_questions]
    if any(not _has_distinct_hidden_cases(question) for question in executable_questions):
        add_issue(
            report,
            "invalid_hidden_test_cases",
            path,
            "可执行题至少需要两个不重复且不同于公开用例的隐藏用例。",
        )
    if not code_questions and not lesson.front_matter.code_exercise_exception_reason:
        add_issue(report, "missing_code_exercise", path, "缺少代码题时必须提供情景替代理由。")
    if not code_questions and lesson.front_matter.code_exercise_exception_reason:
        if not any(_has_scorable_scenario(question) for question in exercises.questions):
            add_issue(report, "missing_scenario_replacement", path, "情景替代必须具有可评分的情景题。")
    return any(_has_executable_contract(question) for question in challenge_questions)


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _has_nonempty_tests(tests: list[str]) -> bool:
    return bool(tests) and all(bool(test.strip()) for test in tests)


def _has_executable_contract(question: Any) -> bool:
    private = question.private
    return (
        _has_text(question.starter_code)
        and _has_nonempty_tests(question.visible_tests)
        and private is not None
        and _has_text(private.reference_solution)
        and _has_nonempty_tests(private.hidden_tests)
        and bool(private.visible_test_cases)
        and bool(private.hidden_test_cases)
    )


def _has_valid_knowledge_choices(question: Any) -> bool:
    if not 3 <= len(question.choices) <= 4 or question.private is None:
        return False
    choice_ids = [choice.id for choice in question.choices]
    choice_texts = [choice.text.strip() for choice in question.choices]
    return (
        len(choice_ids) == len(set(choice_ids))
        and len(choice_texts) == len(set(choice_texts))
        and all(choice_texts)
        and question.private.reference_answer in choice_ids
    )


def _case_signature(case: Any) -> tuple[str, str | None, int, str | None]:
    return (case.stdin, case.stdout, case.exit_code, case.assertion)


def _has_distinct_hidden_cases(question: Any) -> bool:
    private = question.private
    if private is None or len(private.visible_test_cases) < 1 or len(private.hidden_test_cases) < 2:
        return False
    visible = {_case_signature(case) for case in private.visible_test_cases}
    hidden = [_case_signature(case) for case in private.hidden_test_cases]
    return len(hidden) == len(set(hidden)) and not visible.intersection(hidden)


def _has_scorable_scenario(question: Any) -> bool:
    return (
        question.type == "scenario"
        and _has_text(question.prompt)
        and question.private is not None
        and _has_text(question.private.reference_answer)
    )


def _validate_module_prerequisites(
    modules: dict[str, Any], path: Path, report: ValidationReport
) -> None:
    for course_module in modules.values():
        for prerequisite in course_module.prerequisites:
            validate_stable_id(prerequisite, path, report)
            if prerequisite == course_module.id:
                add_issue(report, "self_prerequisite", path, f"模块不能以前置自己：{course_module.id}")
            elif prerequisite not in modules:
                add_issue(report, "unknown_prerequisite", path, f"未知模块前置：{prerequisite}")
    detect_prerequisite_cycles(
        {course_module.id: course_module.prerequisites for course_module in modules.values()},
        path,
        report,
        "module_prerequisite_cycle",
        "模块",
    )


def _validate_source_coverage(
    course_module: Any,
    known_lesson_ids: set[str],
    path: Path,
    report: ValidationReport,
    require_complete: bool,
    content_root: Path,
) -> list[tuple[str, str]]:
    source_ids: set[str] = set()
    covered_lesson_ids: set[str] = set()
    coverage: list[tuple[str, str]] = []
    for entry in course_module.source_coverage:
        if entry.source_id in source_ids:
            add_issue(report, "duplicate_source_coverage", path, f"重复来源覆盖项：{entry.source_id}")
        source_ids.add(entry.source_id)
        if entry.lesson_id not in known_lesson_ids:
            add_issue(
                report,
                "unknown_source_coverage",
                path,
                f"来源覆盖引用未知课时：{entry.lesson_id}",
            )
        if entry.lesson_id in covered_lesson_ids:
            add_issue(
                report,
                "duplicate_source_coverage_lesson",
                path,
                f"多个来源覆盖同一课时：{entry.lesson_id}",
            )
        covered_lesson_ids.add(entry.lesson_id)
        coverage.append((entry.source_id, entry.lesson_id))
    if require_complete:
        missing = known_lesson_ids - covered_lesson_ids
        if missing:
            add_issue(
                report,
                "incomplete_source_coverage",
                path,
                f"来源覆盖缺少课时：{', '.join(sorted(missing))}",
            )
        manifest_source_ids = _manifest_source_ids(content_root, course_module.id, path, report)
        if manifest_source_ids is not None:
            missing_sources = manifest_source_ids - source_ids
            if missing_sources:
                add_issue(
                    report,
                    "incomplete_source_coverage",
                    path,
                    f"来源清单缺少覆盖：{', '.join(sorted(missing_sources))}",
                )
            unknown_sources = source_ids - manifest_source_ids
            if unknown_sources:
                add_issue(
                    report,
                    "unknown_source_coverage",
                    path,
                    f"来源覆盖不在清单中：{', '.join(sorted(unknown_sources))}",
                )
    return coverage


def _manifest_source_ids(
    content_root: Path, module_id: str, path: Path, report: ValidationReport
) -> set[str] | None:
    sources_path = content_root / "sources.yaml"
    if not sources_path.is_file():
        return None
    try:
        payload = load_yaml_mapping(sources_path)
    except ContentParseError:
        add_issue(report, "invalid_sources", sources_path, "来源清单无效。")
        return None
    rows = payload.get("sources")
    if not isinstance(rows, list):
        add_issue(report, "invalid_sources", sources_path, "来源清单缺少 sources 列表。")
        return None
    source_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or row.get("module_id") != module_id:
            continue
        url = row.get("url")
        if not isinstance(url, str):
            add_issue(report, "invalid_sources", sources_path, "来源 URL 无效。")
            continue
        source_id = Path(urlsplit(url).path).stem
        if not source_id:
            add_issue(report, "invalid_sources", sources_path, "来源 URL 缺少稳定标识。")
            continue
        source_ids.add(source_id)
    return source_ids


def _orphan_roots(content_root: Path, language: str | None, module: str | None) -> list[Path]:
    if language is None:
        return [content_root]
    language_root = content_root / language
    if module is None:
        return [language_root]
    return [language_root / module]


def validate_content(
    content_root: Path,
    language: str | None = None,
    module: str | None = None,
    require_complete: bool = False,
) -> ValidationReport:
    report = ValidationReport()
    if language is not None and language not in COURSE_IDS:
        add_issue(report, "invalid_language", content_root, f"不支持的课程语言：{language}")
        return report
    if module is not None and language is None:
        add_issue(report, "missing_language", content_root, "按模块验证时必须指定语言。")
        return report
    try:
        validate_schema_contracts()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        add_issue(report, "invalid_schema", SCRIPT_DIRECTORY, str(error))
        return report

    concepts_path = content_root / "concepts.yaml"
    try:
        concepts = parse_concepts(concepts_path)
    except ContentParseError as error:
        add_issue(report, error.code, concepts_path, str(error))
        return report
    concept_ids: set[str] = set()
    for concept in concepts.concepts:
        if concept.id in concept_ids:
            add_issue(report, "duplicate_concept_id", concepts_path, f"重复概念 ID：{concept.id}")
        concept_ids.add(concept.id)
    referenced_paths = {concepts_path.resolve()}

    course_paths = sorted(content_root.glob("*/course.yaml"))
    if language is not None:
        course_paths = [content_root / language / "course.yaml"]
    selected_modules_found = 0
    for course_path in course_paths:
        referenced_paths.add(course_path.resolve())
        language_directory = course_path.parent
        try:
            course = parse_course(course_path)
        except ContentParseError as error:
            add_issue(report, error.code, course_path, str(error))
            continue
        report.courses += 1
        if course.language not in COURSE_IDS or language_directory.name != course.language:
            add_issue(report, "invalid_course", course_path, "课程语言必须与目录一致。")

        modules: dict[str, Any] = {}
        for course_module in course.modules:
            validate_stable_id(course_module.id, course_path, report)
            if not course_module.id.startswith(f"{course.language}-"):
                add_issue(report, "invalid_module_id", course_path, "模块 ID 必须以课程语言开头。")
            if course_module.id in modules:
                add_issue(report, "duplicate_module_id", course_path, f"重复模块 ID：{course_module.id}")
            else:
                modules[course_module.id] = course_module
        _validate_module_prerequisites(modules, course_path, report)

        lesson_entries: dict[str, Any] = {}
        for course_module in modules.values():
            for lesson_entry in course_module.lessons:
                validate_stable_id(lesson_entry.id, course_path, report)
                if lesson_entry.id in lesson_entries:
                    add_issue(report, "duplicate_lesson_id", course_path, f"重复课时 ID：{lesson_entry.id}")
                else:
                    lesson_entries[lesson_entry.id] = lesson_entry
                if not lesson_entry.id.startswith(f"{course_module.id}-"):
                    add_issue(report, "invalid_lesson_id", course_path, "课时 ID 必须以模块 ID 开头。")

        target_modules = list(modules.values())
        if module is not None:
            selected = modules.get(module)
            if selected is None:
                add_issue(report, "unknown_module", course_path, f"未知模块：{module}")
                continue
            target_modules = [selected]
        selected_modules_found += len(target_modules)

        coverage: list[tuple[str, str]] = []
        for course_module in target_modules:
            module_lesson_ids = {entry.id for entry in course_module.lessons}
            coverage.extend(
                _validate_source_coverage(
                    course_module,
                    module_lesson_ids,
                    course_path,
                    report,
                    require_complete,
                    content_root,
                )
            )
        report.expected += len(coverage)

        implemented_lessons: set[str] = set()
        validated_lessons: set[str] = set()
        module_challenges: set[str] = set()
        knowledge_answer_positions: dict[str, list[int]] = {
            course_module.id: [] for course_module in target_modules
        }
        question_ids: set[str] = set()
        lesson_prerequisites: dict[str, list[str]] = {}
        for course_module in target_modules:
            for lesson_entry in course_module.lessons:
                try:
                    lesson_path = resolve_content_path(language_directory, lesson_entry.path)
                    lesson_path.relative_to((language_directory / course_module.id).resolve())
                except ContentParseError as error:
                    add_issue(report, error.code, course_path, str(error))
                    continue
                except ValueError:
                    add_issue(
                        report,
                        "module_path_escape",
                        course_path,
                        f"课时路径必须位于模块目录：{lesson_entry.path}",
                    )
                    continue
                referenced_paths.add(lesson_path.resolve())
                try:
                    lesson = parse_lesson(lesson_path)
                except ContentParseError as error:
                    add_issue(report, error.code, lesson_path, str(error))
                    continue
                report.lessons += 1
                lesson_error_count = len(report.errors)
                if lesson.front_matter.id != lesson_entry.id:
                    add_issue(report, "lesson_id_mismatch", lesson_path, "front matter 课时 ID 不匹配。")
                for concept_id in lesson.front_matter.concepts:
                    if concept_id not in concept_ids:
                        add_issue(report, "unknown_concept", lesson_path, f"未知概念：{concept_id}")
                lesson_prerequisites[lesson_entry.id] = lesson.front_matter.prerequisites
                for prerequisite in lesson.front_matter.prerequisites:
                    validate_stable_id(prerequisite, lesson_path, report)
                    if prerequisite == lesson_entry.id:
                        add_issue(
                            report,
                            "self_lesson_prerequisite",
                            lesson_path,
                            f"课时不能以前置自己：{lesson_entry.id}",
                        )
                    elif prerequisite not in lesson_entries:
                        add_issue(
                            report,
                            "unknown_lesson_prerequisite",
                            lesson_path,
                            f"未知课时前置：{prerequisite}",
                        )

                exercises_path = lesson_path.with_suffix(".exercises.json")
                referenced_paths.add(exercises_path.resolve())
                try:
                    exercise_payload = load_json_mapping(exercises_path)
                except ContentParseError as error:
                    add_issue(report, error.code, exercises_path, str(error))
                    continue
                find_private_leaks(exercise_payload, exercises_path, report)
                try:
                    exercises = parse_exercises(exercises_path)
                except ContentParseError as error:
                    add_issue(report, error.code, exercises_path, str(error))
                    continue
                report.exercises += 1
                implemented_lessons.add(lesson_entry.id)
                if exercises.lesson_id != lesson_entry.id:
                    add_issue(report, "lesson_id_mismatch", exercises_path, "练习课时 ID 不匹配。")
                for question in exercises.questions:
                    if question.id in question_ids:
                        add_issue(report, "duplicate_question_id", exercises_path, f"重复题号：{question.id}")
                    question_ids.add(question.id)
                    suffix_by_type = {
                        "knowledge": r"k\d{2}",
                        "scenario": r"k\d{2}",
                        "code": r"c\d{2}",
                        "challenge": "challenge",
                    }
                    expected = re.compile(
                        rf"^{re.escape(lesson_entry.id)}-{suffix_by_type[question.type]}$"
                    )
                    if not expected.fullmatch(question.id):
                        add_issue(
                            report,
                            "invalid_question_id",
                            exercises_path,
                            f"题目 ID 不符合规则：{question.id}",
                        )
                    if question.type == "knowledge" and _has_valid_knowledge_choices(question):
                        answer_id = question.private.reference_answer
                        knowledge_answer_positions[course_module.id].append(
                            next(
                                index
                                for index, choice in enumerate(question.choices)
                                if choice.id == answer_id
                            )
                        )
                if require_complete and validate_static_lesson_contract(
                    lesson, exercises, lesson_path, report
                ):
                    module_challenges.add(course_module.id)
                if len(report.errors) == lesson_error_count:
                    validated_lessons.add(lesson_entry.id)

        cyclic_lesson_ids = detect_prerequisite_cycles(
            lesson_prerequisites,
            course_path,
            report,
            "lesson_prerequisite_cycle",
            "课时",
        )
        validated_lessons.difference_update(cyclic_lesson_ids)
        if require_complete:
            for course_module in target_modules:
                if course_module.id not in module_challenges:
                    add_issue(
                        report,
                        "missing_module_challenge",
                        course_path,
                        f"模块缺少综合挑战：{course_module.id}",
                    )
                positions = knowledge_answer_positions[course_module.id]
                if len(positions) > 1 and len(set(positions)) == 1:
                    add_issue(
                        report,
                        "uniform_knowledge_answer_position",
                        course_path,
                        f"模块知识题不能把所有正确答案放在同一选项位置：{course_module.id}",
                    )
        for placement_test in course.placement_tests:
            validate_stable_id(placement_test.id, course_path, report)
            if placement_test.module_id not in modules:
                add_issue(
                    report,
                    "unknown_placement_module",
                    course_path,
                    f"分级测试引用未知模块：{placement_test.module_id}",
                )
            if module is None or placement_test.module_id == module:
                for question_id in placement_test.question_ids:
                    if question_id not in question_ids and (
                        module is None or question_id.startswith(f"{placement_test.module_id}-")
                    ):
                        add_issue(
                            report,
                            "unknown_placement_question",
                            course_path,
                            f"分级测试引用未知题目：{question_id}",
                        )

        report.implemented += sum(lesson_id in implemented_lessons for _, lesson_id in coverage)
        report.validated += sum(lesson_id in validated_lessons for _, lesson_id in coverage)

    if require_complete and selected_modules_found == 0:
        add_issue(report, "incomplete_content", content_root, "完整验证需要至少一个已选择模块。")
    for root in _orphan_roots(content_root, language, module):
        if not root.exists():
            continue
        for candidate in root.rglob("*"):
            if not candidate.is_file() or candidate.suffix not in {".md", ".json", ".yaml", ".yml"}:
                continue
            if candidate.relative_to(content_root).parts[0] == "schema":
                continue
            if candidate.resolve() in {
                concepts_path.resolve(),
                (content_root / "sources.yaml").resolve(),
                (content_root / "sources.yml").resolve(),
            }:
                continue
            if candidate.resolve() not in referenced_paths:
                add_issue(report, "orphan_content", candidate, "内容文件未被课程目录引用。")
    return report


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    argument_parser = argparse.ArgumentParser(description="验证 Hard 课程内容。")
    argument_parser.add_argument(
        "--content-root", type=Path, default=PROJECT_ROOT / "content", help="内容目录"
    )
    argument_parser.add_argument("--language", choices=sorted(COURSE_IDS), help="课程语言")
    argument_parser.add_argument("--module", help="模块稳定 ID")
    argument_parser.add_argument("--require-complete", action="store_true", help="要求模块来源覆盖完整")
    arguments = argument_parser.parse_args(argv)
    if arguments.module is not None and arguments.language is None:
        argument_parser.error("--module 必须与 --language 一起使用。")
    report = validate_content(
        arguments.content_root,
        language=arguments.language,
        module=arguments.module,
        require_complete=arguments.require_complete,
    )
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    print(report.chinese_summary(), file=sys.stderr)
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
