from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from hard_api.core.config import Settings
from hard_api.main import create_app


def write_python_fixture(content_root: Path) -> None:
    module_root = content_root / "python" / "python-foundations"
    module_root.mkdir(parents=True)
    (content_root / "concepts.yaml").write_text(
        json.dumps(
            {
                "concepts": [
                    {"id": "variables", "name": "变量", "description": "保存命名数据。"},
                    {"id": "io", "name": "输入输出", "description": "与终端交互。"},
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
                    "review_milestone_points": 15,
                    "badge_points": {
                        "first_lesson": 20,
                        "first_module_mastery": 30,
                        "seven_day_streak": 40,
                    },
                },
                "placement_tests": [
                    {
                        "id": "python-foundations-placement",
                        "module_id": "python-foundations",
                        "question_ids": ["python-foundations-hello-world-k01"],
                        "passing_score": 85,
                    }
                ],
                "modules": [
                    {
                        "id": "python-foundations",
                        "title": "Python 基础",
                        "prerequisites": [],
                        "source_coverage": [
                            {
                                "source_id": "python3-tutorial",
                                "lesson_id": "python-foundations-hello-world",
                            }
                        ],
                        "lessons": [
                            {
                                "id": "python-foundations-hello-world",
                                "path": "python-foundations/hello-world.md",
                            }
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (module_root / ".fixture-only").write_text("Task 22 must replace this fixture.\n", encoding="utf-8")
    (module_root / "hello-world.md").write_text(
        """---
id: python-foundations-hello-world
title: Hello World
concepts: [variables, io]
objectives: [理解程序输出, 编写第一个 Python 程序]
prerequisites: []
difficulty: beginner
experience_points: 50
source_url: https://www.runoob.com/python3/python3-tutorial.html
source_snapshot_date: 2026-08-23
---

# Hello World

用 `print` 把清晰的信息写到终端。

- 程序从上到下执行。
- 输出是学习程序反馈的第一步。

```python
print("Hello, Hard!")
```

<script>alert("not rendered")</script>

[不安全链接](javascript:alert(1))
""",
        encoding="utf-8",
    )
    (module_root / "hello-world.exercises.json").write_text(
        json.dumps(
            {
                "lesson_id": "python-foundations-hello-world",
                "questions": [
                    {
                        "id": "python-foundations-hello-world-k01",
                        "type": "knowledge",
                        "prompt": "哪个函数可以输出文本？",
                        "choices": [{"id": "a", "text": "print"}, {"id": "b", "text": "input"}],
                        "experience_points": 10,
                        "private": {"reference_answer": "a"},
                    },
                    {
                        "id": "python-foundations-hello-world-k02",
                        "type": "knowledge",
                        "prompt": "输出默认显示在哪里？",
                        "choices": [{"id": "a", "text": "终端"}],
                        "experience_points": 10,
                        "private": {"reference_answer": "a"},
                    },
                    {
                        "id": "python-foundations-hello-world-k03",
                        "type": "knowledge",
                        "prompt": "字符串要用引号包围吗？",
                        "choices": [{"id": "a", "text": "是"}],
                        "experience_points": 10,
                        "private": {"reference_answer": "a"},
                    },
                    {
                        "id": "python-foundations-hello-world-c01",
                        "type": "code",
                        "prompt": "输出 Hello, Hard!。",
                        "starter_code": "print('')",
                        "visible_tests": ["输出 Hello, Hard!"],
                        "experience_points": 20,
                        "private": {
                            "reference_solution": "print('Hello, Hard!')",
                            "hidden_tests": ["精确匹配输出"],
                        },
                    },
                    {
                        "id": "python-foundations-hello-world-challenge",
                        "type": "challenge",
                        "prompt": "输出两行欢迎语。",
                        "starter_code": "print('')",
                        "visible_tests": ["输出两行"],
                        "experience_points": 30,
                        "private": {
                            "reference_solution": "print('Hello')\nprint('Hard')",
                            "hidden_tests": ["两行顺序正确"],
                        },
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def make_settings(content_root: Path) -> Settings:
    project_root = content_root.parent
    data_dir = project_root / "data"
    return Settings(
        project_root=project_root,
        data_dir=data_dir,
        database_path=data_dir / "hard.db",
        backup_dir=project_root / "backups",
        export_dir=project_root / "exports",
        runner_work_dir=project_root / "runner-work",
        content_dir=content_root,
        toolchain_lock_path=project_root / "toolchain-lock.json",
    )


def catalog_response(content_root: Path) -> dict[str, object]:
    with TestClient(create_app(make_settings(content_root))) as client:
        response = client.get("/api/content/catalog")
    assert response.status_code == 200
    return response.json()


def assert_no_private_fields(value: object) -> None:
    forbidden = {"private", "reference_answer", "reference_solution", "hidden_tests"}
    if isinstance(value, dict):
        assert not (forbidden & set(value))
        for child in value.values():
            assert_no_private_fields(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_private_fields(child)


def test_catalog_preserves_course_order_fixture_marker_and_public_exercises(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)

    with TestClient(create_app(make_settings(content_root))) as client:
        catalog = client.get("/api/content/catalog")
        lesson = client.get("/api/content/lessons/python-foundations-hello-world")

    assert catalog.status_code == 200
    body = catalog.json()
    assert body["content_version"] == lesson.json()["content_version"]
    assert len(body["content_version"]) == 64
    assert body["courses"] == [
        {
            "language": "python",
            "title": "Python",
            "fixture_only": True,
            "modules": [
                {
                    "id": "python-foundations",
                    "title": "Python 基础",
                    "prerequisites": [],
                    "lessons": [{"id": "python-foundations-hello-world", "title": "Hello World"}],
                }
            ],
        }
    ]
    assert lesson.status_code == 200
    assert lesson.json()["source_url"] == "https://www.runoob.com/python3/python3-tutorial.html"
    assert lesson.json()["source_snapshot_date"] == "2026-08-23"
    assert_no_private_fields(lesson.json())
    assert "print('Hello, Hard!')" not in lesson.text
    assert "精确匹配输出" not in lesson.text


def test_content_version_is_root_independent_and_changes_for_each_content_file(tmp_path: Path) -> None:
    first_root = tmp_path / "first" / "content"
    second_root = tmp_path / "second" / "content"
    write_python_fixture(first_root)
    write_python_fixture(second_root)

    initial = catalog_response(first_root)["content_version"]
    assert initial == catalog_response(second_root)["content_version"]

    files = [
        first_root / "python" / "course.yaml",
        first_root / "python" / "python-foundations" / "hello-world.md",
        first_root / "python" / "python-foundations" / "hello-world.exercises.json",
    ]
    for path in files:
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        changed = catalog_response(first_root)["content_version"]
        assert changed != initial
        initial = changed


def test_content_version_includes_fixture_only_sentinel(tmp_path: Path) -> None:
    first_root = tmp_path / "first" / "content"
    second_root = tmp_path / "second" / "content"
    write_python_fixture(first_root)
    write_python_fixture(second_root)

    initial = catalog_response(first_root)["content_version"]
    assert initial == catalog_response(second_root)["content_version"]

    sentinel = first_root / "python" / "python-foundations" / ".fixture-only"
    sentinel.unlink()

    assert catalog_response(first_root)["content_version"] != initial


def _write_java_fixture(content_root: Path) -> None:
    source_root = content_root / "python"
    target_root = content_root / "java"
    shutil.copytree(source_root, target_root)
    (target_root / "python-foundations").rename(target_root / "java-foundations")
    for path in target_root.rglob("*"):
        if path.is_file():
            path.write_text(path.read_text(encoding="utf-8").replace("python", "java"), encoding="utf-8")
    course_path = target_root / "course.yaml"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    course["title"] = "Java"
    course_path.write_text(json.dumps(course, ensure_ascii=False), encoding="utf-8")


def _java_course(content_root: Path) -> tuple[Path, dict[str, object]]:
    course_path = content_root / "java" / "course.yaml"
    return course_path, json.loads(course_path.read_text(encoding="utf-8"))


def _write_java_course(content_root: Path, course: dict[str, object]) -> None:
    (content_root / "java" / "course.yaml").write_text(
        json.dumps(course, ensure_ascii=False), encoding="utf-8"
    )


def _append_java_lesson(content_root: Path) -> None:
    module_root = content_root / "java" / "java-foundations"
    source = module_root / "hello-world.md"
    target = module_root / "next.md"
    target.write_text(
        source.read_text(encoding="utf-8").replace("java-foundations-hello-world", "java-foundations-next"),
        encoding="utf-8",
    )
    source = module_root / "hello-world.exercises.json"
    target = module_root / "next.exercises.json"
    target.write_text(
        source.read_text(encoding="utf-8").replace("java-foundations-hello-world", "java-foundations-next"),
        encoding="utf-8",
    )
    _course_path, course = _java_course(content_root)
    course["modules"][0]["lessons"].append(
        {"id": "java-foundations-next", "path": "java-foundations/next.md"}
    )
    _write_java_course(content_root, course)


def _mutate_unknown_concept(content_root: Path) -> str:
    path = content_root / "java" / "java-foundations" / "hello-world.md"
    path.write_text(path.read_text(encoding="utf-8").replace("[variables, io]", "[unknown-concept]"), encoding="utf-8")
    return "unknown_concept"


def _mutate_unknown_lesson_prerequisite(content_root: Path) -> str:
    path = content_root / "java" / "java-foundations" / "hello-world.md"
    path.write_text(path.read_text(encoding="utf-8").replace("prerequisites: []", "prerequisites: [java-foundations-missing]"), encoding="utf-8")
    return "unknown_lesson_prerequisite"


def _mutate_self_lesson_prerequisite(content_root: Path) -> str:
    path = content_root / "java" / "java-foundations" / "hello-world.md"
    path.write_text(path.read_text(encoding="utf-8").replace("prerequisites: []", "prerequisites: [java-foundations-hello-world]"), encoding="utf-8")
    return "self_lesson_prerequisite"


def _mutate_lesson_prerequisite_cycle(content_root: Path) -> str:
    _append_java_lesson(content_root)
    first = content_root / "java" / "java-foundations" / "hello-world.md"
    second = content_root / "java" / "java-foundations" / "next.md"
    first.write_text(first.read_text(encoding="utf-8").replace("prerequisites: []", "prerequisites: [java-foundations-next]"), encoding="utf-8")
    second.write_text(second.read_text(encoding="utf-8").replace("prerequisites: []", "prerequisites: [java-foundations-hello-world]"), encoding="utf-8")
    return "lesson_prerequisite_cycle"


def _mutate_module_prerequisite_cycle(content_root: Path) -> str:
    _course_path, course = _java_course(content_root)
    course["modules"][0]["prerequisites"] = ["java-advanced"]
    course["modules"].append(
        {
            "id": "java-advanced",
            "title": "进阶",
            "prerequisites": ["java-foundations"],
            "source_coverage": [{"source_id": "java-tutorial", "lesson_id": "java-foundations-hello-world"}],
            "lessons": [],
        }
    )
    _write_java_course(content_root, course)
    return "module_prerequisite_cycle"


def _mutate_unknown_placement_question(content_root: Path) -> str:
    _course_path, course = _java_course(content_root)
    course["placement_tests"][0]["question_ids"] = ["java-foundations-missing-k01"]
    _write_java_course(content_root, course)
    return "unknown_placement_question"


def _mutate_duplicate_question_id(content_root: Path) -> str:
    path = content_root / "java" / "java-foundations" / "hello-world.exercises.json"
    exercises = json.loads(path.read_text(encoding="utf-8"))
    exercises["questions"][1]["id"] = exercises["questions"][0]["id"]
    path.write_text(json.dumps(exercises, ensure_ascii=False), encoding="utf-8")
    return "duplicate_question_id"


def _mutate_question_type_id_mismatch(content_root: Path) -> str:
    path = content_root / "java" / "java-foundations" / "hello-world.exercises.json"
    exercises = json.loads(path.read_text(encoding="utf-8"))
    exercises["questions"][0]["type"] = "code"
    path.write_text(json.dumps(exercises, ensure_ascii=False), encoding="utf-8")
    return "invalid_question_id"


def _mutate_unknown_source_coverage(content_root: Path) -> str:
    _course_path, course = _java_course(content_root)
    course["modules"][0]["source_coverage"][0]["lesson_id"] = "java-foundations-missing"
    _write_java_course(content_root, course)
    return "unknown_source_coverage"


def _mutate_lesson_exercises_mismatch(content_root: Path) -> str:
    path = content_root / "java" / "java-foundations" / "hello-world.exercises.json"
    exercises = json.loads(path.read_text(encoding="utf-8"))
    exercises["lesson_id"] = "java-foundations-other"
    path.write_text(json.dumps(exercises, ensure_ascii=False), encoding="utf-8")
    return "lesson_id_mismatch"


@pytest.mark.parametrize(
    "mutate",
    [
        _mutate_unknown_concept,
        _mutate_unknown_lesson_prerequisite,
        _mutate_self_lesson_prerequisite,
        _mutate_lesson_prerequisite_cycle,
        _mutate_module_prerequisite_cycle,
        _mutate_unknown_placement_question,
        _mutate_duplicate_question_id,
        _mutate_question_type_id_mismatch,
        _mutate_unknown_source_coverage,
        _mutate_lesson_exercises_mismatch,
    ],
)
def test_catalog_isolates_each_semantically_invalid_course_without_leaking_private_data(
    tmp_path: Path, mutate
) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    _write_java_fixture(content_root)
    expected_code = mutate(content_root)

    body = catalog_response(content_root)

    assert [course["language"] for course in body["courses"]] == ["python"]
    error = next(error for error in body["isolated_errors"] if error["path"] == "java/course.yaml")
    assert error["code"] == expected_code
    serialized = json.dumps(body, ensure_ascii=False)
    assert str(content_root) not in serialized
    assert "Traceback" not in serialized
    assert "reference_solution" not in serialized
    validator = Path(__file__).resolve().parents[4] / "tools" / "content" / "validate.py"
    result = subprocess.run(
        [sys.executable, str(validator), "--content-root", str(content_root)],
        capture_output=True,
        check=False,
        encoding="utf-8",
        text=True,
    )
    assert result.returncode == 1
    assert expected_code in {issue["code"] for issue in json.loads(result.stdout)["errors"]}


def test_catalog_isolates_broken_courses_and_never_uses_network(tmp_path: Path, monkeypatch) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    (content_root / "java").mkdir()
    (content_root / "java" / "course.yaml").write_text("not: [valid", encoding="utf-8")
    monkeypatch.setattr(socket, "create_connection", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("network")))

    body = catalog_response(content_root)

    assert [course["language"] for course in body["courses"]] == ["python"]
    assert body["isolated_errors"] == [
        {"path": "java/course.yaml", "code": "invalid_course", "message": "课程文件无效。"}
    ]
    assert str(content_root) not in json.dumps(body, ensure_ascii=False)


def test_catalog_rejects_module_path_escape_and_stable_id_errors(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    course_path = content_root / "python" / "course.yaml"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    course["modules"][0]["lessons"][0]["path"] = "../escape.md"
    course_path.write_text(json.dumps(course, ensure_ascii=False), encoding="utf-8")

    with TestClient(create_app(make_settings(content_root))) as client:
        catalog = client.get("/api/content/catalog")
        invalid = client.get("/api/content/lessons/not-a-valid-id!")
        unknown = client.get("/api/content/lessons/python-foundations-not-found")

    assert catalog.status_code == 200
    assert catalog.json()["courses"] == []
    assert catalog.json()["isolated_errors"][0]["code"] == "module_path_escape"
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "invalid_lesson_id"
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "unknown_lesson"
