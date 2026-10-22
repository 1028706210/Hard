import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = PROJECT_ROOT / "tools" / "content" / "validate.py"
REPORTER = PROJECT_ROOT / "tools" / "content" / "report.py"
API_SOURCE = PROJECT_ROOT / "apps" / "api" / "src"
if str(API_SOURCE) not in sys.path:
    sys.path.insert(0, str(API_SOURCE))

from hard_api.content import parser as content_parser


def write_valid_content(content_root: Path) -> None:
    (content_root / "python" / "python-basics").mkdir(parents=True)
    (content_root / "concepts.yaml").write_text(
        json.dumps(
            {
                "concepts": [
                    {
                        "id": "variables",
                        "name": "变量",
                        "description": "保存可变值的命名位置。",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (content_root / "python" / "course.yaml").write_text(
        json.dumps(
            {
                "language": "python",
                "title": "Python",
                "growth": {
                    "review_milestone_points": 10,
                    "badge_points": {
                        "first_lesson": 10,
                        "first_module_mastery": 20,
                        "seven_day_streak": 30,
                    },
                },
                "placement_tests": [
                    {
                        "id": "python-basics-placement",
                        "module_id": "python-basics",
                        "question_ids": ["python-basics-print-c01"],
                        "passing_score": 85,
                    }
                ],
                "modules": [
                    {
                        "id": "python-basics",
                        "title": "基础",
                        "prerequisites": [],
                        "source_coverage": [
                            {
                                "source_id": "python-output",
                                "lesson_id": "python-basics-print",
                            }
                        ],
                        "lessons": [
                            {
                                "id": "python-basics-print",
                                "path": "python-basics/print.md",
                            }
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (content_root / "python" / "python-basics" / "print.md").write_text(
        """---
id: python-basics-print
title: 输出
concepts: [variables]
objectives: [使用 print 输出文本, 区分输出与输入]
prerequisites: []
difficulty: beginner
experience_points: 20
source_url: https://www.runoob.com/python3/python3-output.html
source_snapshot_date: 2026-08-23
---

第一个示例：

```python
print("hello")
```

第二个示例：

```python
name = "Hard"
print(name)
```

## 概念定义与适用场景

输出用于把程序结果交给使用者。

## 语法、API 与边界

print 接收明确的公开值；空文本也是一个可验证输入。

## 常见错误与实践建议

不要把私密值写进输出，并为边界输入写测试。
""",
        encoding="utf-8",
    )
    (content_root / "python" / "python-basics" / "print.exercises.json").write_text(
        json.dumps(
            {
                "lesson_id": "python-basics-print",
                "questions": [
                    {
                        "id": "python-basics-print-k01",
                        "type": "knowledge",
                        "prompt": "哪一个函数用于输出文本？",
                        "experience_points": 5,
                        "choices": [
                            {"id": "a", "text": "print"},
                            {"id": "b", "text": "input"},
                            {"id": "c", "text": "return"},
                        ],
                        "private": {"reference_answer": "a"},
                    },
                    {
                        "id": "python-basics-print-k02",
                        "type": "knowledge",
                        "prompt": "输出会显示在哪里？",
                        "experience_points": 5,
                        "choices": [
                            {"id": "a", "text": "浏览器"},
                            {"id": "b", "text": "终端"},
                            {"id": "c", "text": "数据库"},
                        ],
                        "private": {"reference_answer": "b"},
                    },
                    {
                        "id": "python-basics-print-k03",
                        "type": "knowledge",
                        "prompt": "print 可以输出字符串吗？",
                        "experience_points": 5,
                        "choices": [
                            {"id": "a", "text": "不可以"},
                            {"id": "b", "text": "只能输出数字"},
                            {"id": "c", "text": "可以"},
                        ],
                        "private": {"reference_answer": "c"},
                    },
                    {
                        "id": "python-basics-print-c01",
                        "type": "code",
                        "prompt": "实现一个输出函数。",
                        "starter_code": "import sys\nvalue = sys.stdin.read().strip()\nprint(value or 'empty')",
                        "visible_tests": ["输入普通文本后原样输出"],
                        "experience_points": 10,
                        "private": {
                            "reference_solution": "import sys\nvalue = sys.stdin.read().strip()\nif value == 'error':\n    print('ERROR')\nelse:\n    print(value or 'empty')",
                            "hidden_tests": ["空输入输出默认值", "错误输入输出错误标记"],
                            "visible_test_cases": [{"stdin": "hello\n", "stdout": "hello\n", "exit_code": 0}],
                            "hidden_test_cases": [
                                {"stdin": "\n", "stdout": "empty\n", "exit_code": 0},
                                {"stdin": "error\n", "stdout": "ERROR\n", "exit_code": 0},
                            ],
                        },
                    },
                    {
                        "id": "python-basics-print-challenge",
                        "type": "challenge",
                        "prompt": "输出两行欢迎文本。",
                        "starter_code": "import sys\nvalue = sys.stdin.read().strip()\nprint((value or 'empty').upper())",
                        "visible_tests": ["输入文本后输出大写文本"],
                        "experience_points": 20,
                        "private": {
                            "reference_solution": "import sys\nvalue = sys.stdin.read().strip()\nif value == 'error':\n    print('ERROR')\nelse:\n    print((value or 'empty').upper())",
                            "hidden_tests": ["空输入使用默认值", "错误输入输出错误标记"],
                            "visible_test_cases": [{"stdin": "hello\n", "stdout": "HELLO\n", "exit_code": 0}],
                            "hidden_test_cases": [
                                {"stdin": "\n", "stdout": "EMPTY\n", "exit_code": 0},
                                {"stdin": "error\n", "stdout": "ERROR\n", "exit_code": 0},
                            ],
},
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def run_validator(
    content_root: Path, expected_exit_code: int, *arguments: str
) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--content-root", str(content_root), *arguments],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )
    assert result.returncode == expected_exit_code, result.stderr
    return result, json.loads(result.stdout)


def invalid_report(content_root: Path) -> dict[str, object]:
    _, report = run_validator(content_root, 1)
    return report


def add_lesson(content_root: Path, lesson_id: str, prerequisites: list[str]) -> None:
    course_path = content_root / "python" / "course.yaml"
    course = load_json(course_path)
    module = course["modules"][0]  # type: ignore[index]
    module["lessons"].append(  # type: ignore[index]
        {"id": lesson_id, "path": f"python-basics/{lesson_id.removeprefix('python-basics-')}.md"}
    )
    module["source_coverage"].append(  # type: ignore[index]
        {"source_id": lesson_id, "lesson_id": lesson_id}
    )
    write_json(course_path, course)

    lesson_name = lesson_id.removeprefix("python-basics-")
    lesson_path = content_root / "python" / "python-basics" / f"{lesson_name}.md"
    lesson_path.write_text(
        f"""---
id: {lesson_id}
title: {lesson_name}
concepts: [variables]
objectives: [练习前置关系]
prerequisites: {json.dumps(prerequisites, ensure_ascii=False)}
difficulty: beginner
experience_points: 0
source_url: https://www.runoob.com/python3/python3-output.html
source_snapshot_date: 2026-08-23
---

{lesson_name} 正文。
""",
        encoding="utf-8",
    )
    lesson_path.with_suffix(".exercises.json").write_text(
        json.dumps(
            {
                "lesson_id": lesson_id,
                "questions": [
                    {
                        "id": f"{lesson_id}-k01",
                        "type": "knowledge",
                        "prompt": "测试题。",
                        "experience_points": 0,
                        "private": {"reference_answer": "a"},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def issue_codes(report: dict[str, object]) -> set[str]:
    return {issue["code"] for issue in report["errors"]}  # type: ignore[index]


def test_accepts_valid_content_and_emits_machine_and_chinese_reports(tmp_path: Path) -> None:
    write_valid_content(tmp_path)

    result, report = run_validator(tmp_path, 0)

    assert report["valid"] is True
    assert report["counts"] == {"courses": 1, "lessons": 1, "exercises": 1}
    assert result.stderr.strip() == "内容校验通过：1 门课程、1 节课、1 份练习。"


def test_rejects_course_without_experience_metadata(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    del course["growth"]
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "invalid_course" in issue_codes(report)


def test_rejects_negative_float_and_out_of_range_course_growth_points(tmp_path: Path) -> None:
    for index, value in enumerate((-1, 1.5, 1001)):
        content_root = tmp_path / str(index)
        write_valid_content(content_root)
        course_path = content_root / "python" / "course.yaml"
        course = load_json(course_path)
        course["growth"]["review_milestone_points"] = value  # type: ignore[index]
        write_json(course_path, course)

        report = invalid_report(content_root)

        assert "invalid_course" in issue_codes(report)


def test_rejects_missing_or_invalid_lesson_experience_points(tmp_path: Path) -> None:
    for index, value in enumerate((None, -1, 1.5, 1001)):
        content_root = tmp_path / str(index)
        write_valid_content(content_root)
        lesson_path = content_root / "python" / "python-basics" / "print.md"
        lesson = lesson_path.read_text(encoding="utf-8")
        replacement = "" if value is None else f"experience_points: {value}\n"
        lesson_path.write_text(
            lesson.replace("experience_points: 20\n", replacement), encoding="utf-8"
        )

        report = invalid_report(content_root)

        assert "invalid_lesson" in issue_codes(report)


def test_rejects_missing_or_invalid_exercise_experience_points(tmp_path: Path) -> None:
    for index, value in enumerate((None, -1, 1.5, 1001)):
        content_root = tmp_path / str(index)
        write_valid_content(content_root)
        exercises_path = content_root / "python" / "python-basics" / "print.exercises.json"
        exercises = load_json(exercises_path)
        question = exercises["questions"][0]  # type: ignore[index]
        if value is None:
            del question["experience_points"]
        else:
            question["experience_points"] = value
        write_json(exercises_path, exercises)

        report = invalid_report(content_root)

        assert "invalid_exercises" in issue_codes(report)


def test_rejects_an_invalid_module_id(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["modules"][0]["id"] = "python_invalid"  # type: ignore[index]
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "invalid_id" in issue_codes(report)


def test_rejects_duplicate_question_numbers(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"].append(exercises["questions"][0])  # type: ignore[index]
    write_json(exercises_path, exercises)

    report = invalid_report(tmp_path)

    assert "duplicate_question_id" in issue_codes(report)


def test_rejects_a_knowledge_question_with_a_code_id(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"][0]["id"] = "python-basics-print-c02"  # type: ignore[index]
    write_json(exercises_path, exercises)

    report = invalid_report(tmp_path)

    assert "invalid_question_id" in issue_codes(report)


def test_rejects_a_code_question_with_a_knowledge_id(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"][3]["id"] = "python-basics-print-k04"  # type: ignore[index]
    write_json(exercises_path, exercises)

    report = invalid_report(tmp_path)

    assert "invalid_question_id" in issue_codes(report)


def test_rejects_a_challenge_question_with_a_knowledge_id(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"][4]["id"] = "python-basics-print-k04"  # type: ignore[index]
    write_json(exercises_path, exercises)

    report = invalid_report(tmp_path)

    assert "invalid_question_id" in issue_codes(report)


def test_rejects_a_scenario_question_with_an_s_id(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"].append(  # type: ignore[index]
        {
            "id": "python-basics-print-s01",
            "type": "scenario",
            "prompt": "选择正确的输出顺序。",
            "experience_points": 0,
            "private": {"reference_answer": "先输出 hello"},
        }
    )
    write_json(exercises_path, exercises)

    report = invalid_report(tmp_path)

    assert "invalid_question_id" in issue_codes(report)


def test_rejects_cyclic_module_prerequisites(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["modules"].append(  # type: ignore[index]
        {
            "id": "python-advanced",
            "title": "进阶",
            "prerequisites": ["python-basics"],
            "source_coverage": [
                {"source_id": "python-advanced-source", "lesson_id": "python-basics-print"}
            ],
            "lessons": [],
        }
    )
    course["modules"][0]["prerequisites"] = ["python-advanced"]  # type: ignore[index]
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "module_prerequisite_cycle" in issue_codes(report)


def test_rejects_duplicate_module_ids(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["modules"].append(  # type: ignore[index]
        {
            "id": "python-basics",
            "title": "重复",
            "prerequisites": [],
            "source_coverage": [
                {"source_id": "python-basics-duplicate", "lesson_id": "python-basics-print"}
            ],
            "lessons": [],
        }
    )
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "duplicate_module_id" in issue_codes(report)


def test_rejects_a_module_for_another_course_language(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["modules"][0]["id"] = "java-basics"  # type: ignore[index]
    course["modules"][0]["lessons"][0]["id"] = "java-basics-print"  # type: ignore[index]
    course["modules"][0]["source_coverage"][0]["lesson_id"] = "java-basics-print"  # type: ignore[index]
    write_json(course_path, course)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "python-basics-print", "java-basics-print"
        ),
        encoding="utf-8",
    )
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["lesson_id"] = "java-basics-print"
    exercises["questions"][0]["id"] = "java-basics-print-k01"  # type: ignore[index]
    write_json(exercises_path, exercises)

    report = invalid_report(tmp_path)

    assert "invalid_module_id" in issue_codes(report)


def test_rejects_unknown_lesson_concepts(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace("[variables]", "[missing-concept]"),
        encoding="utf-8",
    )

    report = invalid_report(tmp_path)

    assert "unknown_concept" in issue_codes(report)


def test_rejects_a_reference_answer_outside_private_data(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    question = exercises["questions"][0]  # type: ignore[index]
    question["reference_answer"] = question.pop("private")["reference_answer"]  # type: ignore[index]
    write_json(exercises_path, exercises)

    report = invalid_report(tmp_path)

    assert "private_leak" in issue_codes(report)


def test_rejects_lessons_without_a_source_url(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "source_url: https://www.runoob.com/python3/python3-output.html\n", ""
        ),
        encoding="utf-8",
    )

    report = invalid_report(tmp_path)

    assert "invalid_lesson" in issue_codes(report)


def test_rejects_courses_without_explicit_module_prerequisites(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    del course["modules"][0]["prerequisites"]  # type: ignore[index]
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "invalid_course" in issue_codes(report)


def test_rejects_lessons_without_body_text(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    front_matter, _, _ = lesson_path.read_text(encoding="utf-8").partition("---\n\n")
    lesson_path.write_text(
        f"{front_matter}---\n",
        encoding="utf-8",
    )

    report = invalid_report(tmp_path)

    assert "empty_lesson_body" in issue_codes(report)


def test_rejects_lesson_paths_outside_the_content_root(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["modules"][0]["lessons"][0]["path"] = "../outside.md"  # type: ignore[index]
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "path_escape" in issue_codes(report)


def test_rejects_orphaned_content_files(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    (tmp_path / "python" / "orphan.md").write_text("孤立课时", encoding="utf-8")

    report = invalid_report(tmp_path)

    assert "orphan_content" in issue_codes(report)


def test_does_not_treat_schema_files_as_orphaned_content(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    (tmp_path / "schema").mkdir()
    (tmp_path / "schema" / "course.schema.json").write_text("{}", encoding="utf-8")

    _, report = run_validator(tmp_path, 0)

    assert report["errors"] == []


def test_public_exercise_payload_excludes_private_answers(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    document = content_parser.parse_exercises(
        tmp_path / "python" / "python-basics" / "print.exercises.json"
    )

    payload = content_parser.public_exercise_payload(document)

    assert document.questions[0].private is not None
    assert document.questions[0].private.reference_answer == "a"
    assert "private" not in payload["questions"][0]


def test_rejects_courses_without_placement_and_source_coverage_contracts(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    del course["placement_tests"]
    del course["modules"][0]["source_coverage"]  # type: ignore[index]
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "invalid_course" in issue_codes(report)


def test_filters_validation_to_the_selected_language_and_module(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    (tmp_path / "java").mkdir()
    (tmp_path / "java" / "orphan.md").write_text("未选择的内容", encoding="utf-8")

    _, report = run_validator(
        tmp_path, 0, "--language", "python", "--module", "python-basics"
    )

    assert report["counts"] == {"courses": 1, "lessons": 1, "exercises": 1}


def test_require_complete_rejects_a_lesson_without_source_coverage(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    add_lesson(tmp_path, "python-basics-input", [])
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["modules"][0]["source_coverage"].pop()  # type: ignore[index]
    write_json(course_path, course)

    result, report = run_validator(
        tmp_path,
        1,
        "--language",
        "python",
        "--module",
        "python-basics",
        "--require-complete",
    )

    assert "incomplete_source_coverage" in issue_codes(report)
    assert "内容校验失败" in result.stderr


def test_require_complete_rejects_a_lesson_with_fewer_than_two_objectives(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "objectives: [使用 print 输出文本, 区分输出与输入]", "objectives: [使用 print 输出文本]"
        ),
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "incomplete_objectives" in issue_codes(report)


def test_require_complete_rejects_an_empty_objective(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "objectives: [使用 print 输出文本, 区分输出与输入]", "objectives: [使用 print 输出文本, '   ']"
        ),
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "empty_objective" in issue_codes(report)


def test_require_complete_rejects_a_lesson_with_fewer_than_two_examples(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            '''
第二个示例：

```python
name = "Hard"
print(name)
```
''',
            "",
        ),
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "incomplete_examples" in issue_codes(report)


def test_require_complete_rejects_an_empty_fenced_code_example(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace('print("hello")', ""),
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "empty_code_example" in issue_codes(report)


def test_require_complete_rejects_a_lesson_with_fewer_than_three_knowledge_questions(
    tmp_path: Path,
) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"] = [
        question
        for question in exercises["questions"]  # type: ignore[index]
        if question["id"] != "python-basics-print-k03"
    ]
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "incomplete_knowledge_questions" in issue_codes(report)


def test_require_complete_rejects_knowledge_questions_without_server_reference_answers(
    tmp_path: Path,
) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    for question in exercises["questions"]:  # type: ignore[index]
        if question["type"] == "knowledge":
            question["private"]["reference_answer"] = "   "
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "invalid_knowledge_reference_answer" in issue_codes(report)


def test_require_complete_rejects_a_missing_code_question_without_an_exception_reason(
    tmp_path: Path,
) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"] = [
        question for question in exercises["questions"] if question["type"] != "code"  # type: ignore[index]
    ]
    write_json(exercises_path, exercises)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["placement_tests"][0]["question_ids"] = ["python-basics-print-k01"]  # type: ignore[index]
    write_json(course_path, course)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "missing_code_exercise" in issue_codes(report)


def test_require_complete_rejects_a_code_question_without_visible_tests(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    for question in exercises["questions"]:  # type: ignore[index]
        if question["type"] == "code":
            del question["visible_tests"]
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "invalid_code_question" in issue_codes(report)


def test_require_complete_rejects_a_code_question_without_a_private_solution(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    for question in exercises["questions"]:  # type: ignore[index]
        if question["type"] == "code":
            question["private"]["reference_solution"] = ""
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "invalid_code_question" in issue_codes(report)


def test_require_complete_rejects_a_challenge_without_nonempty_hidden_tests(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    for question in exercises["questions"]:  # type: ignore[index]
        if question["type"] == "challenge":
            question["private"]["hidden_tests"] = ["   "]
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "invalid_challenge_question" in issue_codes(report)


def test_require_complete_rejects_uniform_knowledge_answer_positions(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    for question in exercises["questions"]:  # type: ignore[index]
        if question["type"] == "knowledge":
            question["choices"] = [
                {"id": "a", "text": "正确答案"},
                {"id": "b", "text": "干扰项一"},
                {"id": "c", "text": "干扰项二"},
            ]
            question["private"]["reference_answer"] = "a"
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "uniform_knowledge_answer_position" in issue_codes(report)


def test_require_complete_rejects_knowledge_questions_without_three_to_four_choices(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    question = next(item for item in exercises["questions"] if item["type"] == "knowledge")  # type: ignore[index]
    question["choices"] = [
        {"id": "a", "text": "正确答案"},
        {"id": "b", "text": "干扰项"},
    ]
    question["private"]["reference_answer"] = "a"
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "invalid_knowledge_choices" in issue_codes(report)


def test_require_complete_rejects_hidden_cases_that_duplicate_the_visible_case(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    code = next(item for item in exercises["questions"] if item["type"] == "code")  # type: ignore[index]
    code["private"]["hidden_test_cases"] = [
        {"stdin": "visible\n", "stdout": "visible\n", "exit_code": 0},
        {"stdin": "visible\n", "stdout": "visible\n", "exit_code": 0},
    ]
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "invalid_hidden_test_cases" in issue_codes(report)


def test_report_rejects_a_constant_output_program_that_passes_all_hidden_cases(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    code = next(item for item in exercises["questions"] if item["type"] == "code")  # type: ignore[index]
    code["private"]["hidden_test_cases"] = [  # type: ignore[index]
        {"stdin": "other\n", "stdout": "hello\n", "exit_code": 0},
        {"stdin": "again\n", "stdout": "hello\n", "exit_code": 0},
    ]
    write_json(exercises_path, exercises)
    output_path = tmp_path / "coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPORTER),
            "--content-root",
            str(tmp_path),
            "--language",
            "python",
            "--module",
            "python-basics",
            "--json",
            str(output_path),
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )
    report = load_json(output_path)

    assert result.returncode == 1
    assert "constant_output_submission_passed" in issue_codes(report)


def test_require_complete_rejects_reused_generic_lesson_explanation(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "输出用于把程序结果交给使用者。",
            "输出解决的是把明确输入转换为可核验结果的问题。",
        ),
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "generic_lesson_explanation" in issue_codes(report)


def test_require_complete_allows_a_code_question_exception_reason(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"] = [
        question for question in exercises["questions"] if question["type"] != "code"  # type: ignore[index]
    ]
    exercises["questions"].append(  # type: ignore[index]
        {
            "id": "python-basics-print-k04",
            "type": "scenario",
            "prompt": "在无法运行代码时，选择正确的输出顺序。",
            "experience_points": 0,
            "private": {"reference_answer": "先输出 hello"},
        }
    )
    write_json(exercises_path, exercises)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["placement_tests"][0]["question_ids"] = ["python-basics-print-k01"]  # type: ignore[index]
    write_json(course_path, course)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "difficulty: beginner",
            "difficulty: beginner\ncode_exercise_exception_reason: 当前课时使用情景题说明受限运行环境。",
        ),
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 0, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert report["errors"] == []


def test_require_complete_rejects_an_unscorable_scenario_replacement(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"] = [
        question for question in exercises["questions"] if question["type"] != "code"  # type: ignore[index]
    ]
    exercises["questions"].append(  # type: ignore[index]
        {
            "id": "python-basics-print-k04",
            "type": "scenario",
            "prompt": "选择正确的输出顺序。",
            "experience_points": 0,
            "private": {"reference_answer": "   "},
        }
    )
    write_json(exercises_path, exercises)
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["placement_tests"][0]["question_ids"] = ["python-basics-print-k01"]  # type: ignore[index]
    write_json(course_path, course)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "difficulty: beginner",
            "difficulty: beginner\ncode_exercise_exception_reason: 当前课时使用情景题说明受限运行环境。",
        ),
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "missing_scenario_replacement" in issue_codes(report)


def test_rejects_a_lesson_path_in_another_module_directory(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    source_directory = tmp_path / "python" / "python-basics"
    other_directory = tmp_path / "python" / "other-module"
    other_directory.mkdir()
    (other_directory / "print.md").write_text(
        (source_directory / "print.md").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (other_directory / "print.exercises.json").write_text(
        (source_directory / "print.exercises.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    course_path = tmp_path / "python" / "course.yaml"
    course = load_json(course_path)
    course["modules"][0]["lessons"][0]["path"] = "other-module/print.md"  # type: ignore[index]
    write_json(course_path, course)

    report = invalid_report(tmp_path)

    assert "module_path_escape" in issue_codes(report)


def test_rejects_duplicate_concept_ids(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    concepts_path = tmp_path / "concepts.yaml"
    concepts = load_json(concepts_path)
    concepts["concepts"].append(concepts["concepts"][0])  # type: ignore[index]
    write_json(concepts_path, concepts)

    report = invalid_report(tmp_path)

    assert "duplicate_concept_id" in issue_codes(report)


def test_rejects_orphaned_yaml_content_files(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    (tmp_path / "python" / "python-basics" / "orphan.yml").write_text("title: 孤立内容", encoding="utf-8")

    report = invalid_report(tmp_path)

    assert "orphan_content" in issue_codes(report)


def test_does_not_treat_schema_concepts_or_sources_yaml_as_orphaned_content(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    (tmp_path / "schema").mkdir()
    (tmp_path / "schema" / "future.schema.yml").write_text("type: object", encoding="utf-8")
    (tmp_path / "sources.yaml").write_text("sources: []", encoding="utf-8")

    _, report = run_validator(tmp_path, 0)

    assert report["errors"] == []


def test_require_complete_rejects_source_manifest_entries_without_exact_course_coverage(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    (tmp_path / "sources.yaml").write_text(
        """sources:
  - title: 输出
    url: https://www.runoob.com/python3/python3-output.html
    group: Python 3 教程
    module_id: python-basics
    content_type: lesson
    snapshot_date: '2026-08-23'
  - title: 额外主题
    url: https://www.runoob.com/python3/python3-extra.html
    group: Python 3 教程
    module_id: python-basics
    content_type: lesson
    snapshot_date: '2026-08-23'
""",
        encoding="utf-8",
    )

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "incomplete_source_coverage" in issue_codes(report)


def test_python_core_types_module_covers_its_entire_source_manifest() -> None:
    """The published core-types module cannot silently omit a listed source."""
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-core-types")

    assert len(module.source_coverage) == 7
    assert len(module.lessons) == 7


def test_python_flow_collections_module_covers_its_entire_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-flow-collections")

    assert len(module.source_coverage) == 11
    assert len(module.lessons) == 11


def test_python_functions_iteration_module_covers_its_entire_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-functions-iteration")

    assert len(module.source_coverage) == 8
    assert len(module.lessons) == 8


def test_python_modules_io_oop_module_covers_its_entire_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-modules-io-oop")

    assert len(module.source_coverage) == 6
    assert len(module.lessons) == 6


def test_python_stdlib_data_module_covers_its_entire_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-stdlib-data")

    assert len(module.source_coverage) == 19
    assert len(module.lessons) == 19


def test_python_stdlib_data_reference_solutions_all_pass_the_real_runner(tmp_path: Path) -> None:
    output_path = tmp_path / "coverage.json"
    result = subprocess.run(
        [
            sys.executable,
            str(REPORTER),
            "--language",
            "python",
            "--module",
            "python-stdlib-data",
            "--json",
            str(output_path),
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )

    assert result.returncode == 0, result.stderr
    report = load_json(output_path)
    assert report["reference_solutions_passed"] == 19


def test_python_concurrency_network_module_covers_its_entire_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-concurrency-network")

    assert len(module.source_coverage) == 8
    assert len(module.lessons) == 8


def test_python_database_deployment_module_covers_its_entire_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-database-deployment")

    assert len(module.source_coverage) == 5
    assert len(module.lessons) == 5


def test_python_automation_ui_web_module_covers_its_entire_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-automation-ui-web")

    assert len(module.source_coverage) == 6
    assert len(module.lessons) == 6


def test_python_capstone_module_completes_the_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    module = next(item for item in course.modules if item.id == "python-capstone")

    assert len(module.source_coverage) == 5
    assert len(module.lessons) == 5


def test_python_route_provides_a_placement_test_for_each_module() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")

    assert {placement.module_id for placement in course.placement_tests} == {
        module.id for module in course.modules
    }


def test_python_capstone_placement_test_samples_all_ten_modules() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "python" / "course.yaml")
    placement = next(item for item in course.placement_tests if item.id == "python-capstone-placement")

    assert {
        "python-foundations-hello-world-k01",
        "python-core-types-basic-syntax-k01",
        "python-flow-collections-lists-k01",
        "python-functions-iteration-functions-k01",
        "python-modules-io-oop-modules-k01",
        "python-stdlib-data-overview-k01",
        "python-concurrency-network-asyncio-k01",
        "python-database-deployment-cgi-k01",
        "python-automation-ui-web-pyecharts-k01",
        "python-capstone-quiz-k01",
    } <= set(placement.question_ids)


def test_csharp_capstone_module_completes_the_source_manifest() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "csharp" / "course.yaml")
    module = next(item for item in course.modules if item.id == "csharp-capstone")

    assert len(module.source_coverage) == 3
    assert len(module.lessons) == 3


def test_csharp_route_provides_a_placement_test_for_each_module() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "csharp" / "course.yaml")

    assert {placement.module_id for placement in course.placement_tests} == {
        module.id for module in course.modules
    }


def test_csharp_capstone_placement_test_samples_all_five_modules() -> None:
    course = content_parser.parse_course(PROJECT_ROOT / "content" / "csharp" / "course.yaml")
    placement = next(item for item in course.placement_tests if item.id == "csharp-capstone-placement")

    assert {
        "csharp-foundations-tutorial-k01",
        "csharp-oop-classes-k01",
        "csharp-io-metadata-exception-handling-k01",
        "csharp-language-features-generics-k01",
        "csharp-capstone-language-quiz-k01",
    } <= set(placement.question_ids)


def test_require_complete_rejects_a_module_without_a_challenge(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    exercises_path = tmp_path / "python" / "python-basics" / "print.exercises.json"
    exercises = load_json(exercises_path)
    exercises["questions"] = [
        question for question in exercises["questions"] if question["type"] != "challenge"  # type: ignore[index]
    ]
    write_json(exercises_path, exercises)

    _, report = run_validator(
        tmp_path, 1, "--language", "python", "--module", "python-basics", "--require-complete"
    )

    assert "missing_module_challenge" in issue_codes(report)


def test_report_records_real_python_runner_evidence_for_reference_solutions(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    output_path = tmp_path / "coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPORTER),
            "--content-root",
            str(tmp_path),
            "--language",
            "python",
            "--module",
            "python-basics",
            "--json",
            str(output_path),
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )

    assert result.returncode == 0, result.stderr
    report = load_json(output_path)
    assert report["language"] == "python"
    assert report["module"] == "python-basics"
    assert report["expected"] == 1
    assert report["implemented"] == 1
    assert report["validated"] == 1
    assert report["reference_solutions_passed"] == 1


def test_report_records_real_csharp_runner_evidence_for_visible_and_hidden_cases(tmp_path: Path) -> None:
    module_dir = tmp_path / "csharp" / "csharp-probe"
    module_dir.mkdir(parents=True)
    (tmp_path / "concepts.yaml").write_text(
        "concepts:\n  - id: variables\n    name: 变量\n    description: 保存可变值的命名位置。\n",
        encoding="utf-8",
    )
    (tmp_path / "csharp" / "course.yaml").write_text(
        """language: csharp
title: C#
growth:
  review_milestone_points: 10
  badge_points:
    first_lesson: 10
    first_module_mastery: 20
    seven_day_streak: 30
placement_tests: []
modules:
  - id: csharp-probe
    title: Probe
    prerequisites: []
    source_coverage:
      - source_id: csharp-probe-source
        lesson_id: csharp-probe-runner
    lessons:
      - id: csharp-probe-runner
        path: csharp-probe/runner.md
""",
        encoding="utf-8",
    )
    (module_dir / "runner.md").write_text(
        """---
id: csharp-probe-runner
title: Runner probe
concepts: [variables]
objectives: [运行 C# 输入输出]
prerequisites: []
difficulty: beginner
experience_points: 20
source_url: https://www.runoob.com/csharp/csharp-tutorial.html
source_snapshot_date: 2026-08-23
---

## 概念定义与适用场景

Runner probe.

## 语法、API 与边界

Runner probe.

## 常见错误与实践建议

Runner probe.
""",
        encoding="utf-8",
    )
    (module_dir / "runner.exercises.json").write_text(
        json.dumps(
            {
                "lesson_id": "csharp-probe-runner",
                "questions": [
                    {
                        "id": "csharp-probe-runner-c01",
                        "type": "code",
                        "prompt": "输出大写文本。",
                        "starter_code": "Console.WriteLine();",
                        "visible_tests": ["普通输入"],
                        "experience_points": 10,
                        "private": {
                            "reference_solution": (
                                "var value = Console.In.ReadToEnd().Trim(); "
                                "Console.WriteLine(value.ToUpperInvariant());"
                            ),
                            "hidden_tests": ["隐藏输入"],
                            "visible_test_cases": [{"stdin": "Ada\n", "stdout": "ADA\n", "exit_code": 0}],
                            "hidden_test_cases": [{"stdin": "bob\n", "stdout": "BOB\n", "exit_code": 0}],
                        },
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPORTER),
            "--content-root",
            str(tmp_path),
            "--language",
            "csharp",
            "--module",
            "csharp-probe",
            "--json",
            str(output_path),
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )

    assert output_path.is_file(), result.stderr
    report = load_json(output_path)
    assert report["reference_solutions_passed"] == 1
    assert report["constant_output"] == {"attempted": 1, "rejected": 1}


def test_report_records_source_sections_and_distinct_assessment_case_counts(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    output_path = tmp_path / "coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPORTER),
            "--content-root",
            str(tmp_path),
            "--language",
            "python",
            "--module",
            "python-basics",
            "--json",
            str(output_path),
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )

    assert result.returncode == 0, result.stderr
    report = load_json(output_path)
    assert report["question_counts"] == {"knowledge": 3, "code": 1, "challenge": 1}
    assert report["test_case_counts"] == {
        "visible": 2,
        "hidden": 4,
        "hidden_distinct_from_visible": 4,
    }
    assert report["source_section_mapping"] == [
        {
            "source_id": "python-output",
            "lesson_id": "python-basics-print",
            "source_primary_topic": "输出",
            "hard_sections": ["概念定义与适用场景", "语法、API 与边界", "常见错误与实践建议"],
        }
    ]
    assert report["errors"] == []


def test_rejects_an_invalid_lesson_prerequisite_id(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace("prerequisites: []", "prerequisites: [bad_id]"),
        encoding="utf-8",
    )

    report = invalid_report(tmp_path)

    assert "invalid_id" in issue_codes(report)


def test_rejects_an_unknown_lesson_prerequisite(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "prerequisites: []", "prerequisites: [python-basics-missing]"
        ),
        encoding="utf-8",
    )

    report = invalid_report(tmp_path)

    assert "unknown_lesson_prerequisite" in issue_codes(report)


def test_rejects_a_lesson_as_its_own_prerequisite(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "prerequisites: []", "prerequisites: [python-basics-print]"
        ),
        encoding="utf-8",
    )

    report = invalid_report(tmp_path)

    assert "self_lesson_prerequisite" in issue_codes(report)


def test_rejects_cyclic_lesson_prerequisites(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    add_lesson(tmp_path, "python-basics-input", ["python-basics-print"])
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "prerequisites: []", "prerequisites: [python-basics-input]"
        ),
        encoding="utf-8",
    )

    report = invalid_report(tmp_path)

    assert "lesson_prerequisite_cycle" in issue_codes(report)


def test_report_does_not_count_a_cyclic_lesson_as_validated(tmp_path: Path) -> None:
    write_valid_content(tmp_path)
    add_lesson(tmp_path, "python-basics-input", ["python-basics-print"])
    lesson_path = tmp_path / "python" / "python-basics" / "print.md"
    lesson_path.write_text(
        lesson_path.read_text(encoding="utf-8").replace(
            "prerequisites: []", "prerequisites: [python-basics-input]"
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPORTER),
            "--content-root",
            str(tmp_path),
            "--language",
            "python",
            "--module",
            "python-basics",
            "--json",
            str(output_path),
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )

    assert result.returncode == 1
    assert load_json(output_path)["validated"] == 0
