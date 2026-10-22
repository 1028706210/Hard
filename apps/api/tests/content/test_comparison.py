from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from hard_api.content.parser import parse_concepts
from hard_api.content.repository import ContentRepository
from hard_api.core.config import Settings
from hard_api.main import create_app


PRIVATE_FIELDS = {"private", "reference_answer", "reference_solution", "hidden_tests"}


def write_lesson_files(
    content_root: Path,
    language: str,
    module_id: str,
    lesson_id: str,
    concepts: list[str],
    title: str,
) -> None:
    module_root = content_root / language / module_id
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / f"{lesson_id}.md").write_text(
        "\n".join(
            [
                "---",
                f"id: {lesson_id}",
                f"title: {title}",
                f"concepts: [{', '.join(concepts)}]",
                "objectives:",
                "  - 理解基本概念",
                "  - 完成基础练习",
                "prerequisites: []",
                "difficulty: beginner",
                "experience_points: 10",
                f"source_url: https://www.runoob.com/{language}/{lesson_id}.html",
                "source_snapshot_date: 2026-08-23",
                "---",
                "",
                f"# {title}",
                "",
                "示例正文。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (module_root / f"{lesson_id}.exercises.json").write_text(
        json.dumps(
            {
                "lesson_id": lesson_id,
                "questions": [
                    {
                        "id": f"{lesson_id}-k01",
                        "type": "knowledge",
                        "prompt": "最符合课程目标的说法是？",
                        "choices": [{"id": "a", "text": "按规则把输入转换为结果"}],
                        "experience_points": 5,
                        "private": {"reference_answer": "a"},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def write_course(
    content_root: Path,
    language: str,
    title: str,
    lessons: list[tuple[str, str, list[str], str]],
) -> None:
    module_id = f"{language}-foundations"
    module_root_entries = []
    coverage = []
    for lesson_id, _slug, concepts, title_text in lessons:
        write_lesson_files(content_root, language, module_id, lesson_id, concepts, title_text)
        module_root_entries.append({"id": lesson_id, "path": f"{module_id}/{lesson_id}.md"})
        coverage.append({"source_id": f"{language}-{lesson_id}", "lesson_id": lesson_id})
    (content_root / language / "course.yaml").write_text(
        json.dumps(
            {
                "language": language,
                "title": title,
                "growth": {
                    "review_milestone_points": 15,
                    "badge_points": {
                        "first_lesson": 20,
                        "first_module_mastery": 30,
                        "seven_day_streak": 40,
                    },
                },
                "placement_tests": [],
                "modules": [
                    {
                        "id": module_id,
                        "title": f"{title} 基础",
                        "prerequisites": [],
                        "source_coverage": coverage,
                        "lessons": module_root_entries,
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def write_concepts(content_root: Path, concepts: list[dict[str, Any]]) -> None:
    (content_root / "concepts.yaml").write_text(
        yaml_dump({"concepts": concepts}), encoding="utf-8"
    )


def yaml_dump(data: dict[str, Any]) -> str:
    try:
        import yaml

        return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    except ImportError as error:  # pragma: no cover - 环境缺失时直接失败
        raise AssertionError("缺少 PyYAML") from error


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


def write_fixture(content_root: Path, *, break_reference: str | None = None) -> None:
    """双语言最小内容夹具：variables 双语、interpreter 仅 Python、legacy 仅 Python。"""
    variables_python = {
        "status": "available",
        "summary": "变量是对象的命名引用，赋值即绑定。",
        "difference": "动态类型，无需声明即可重新绑定不同类型。",
        "code": "count = 10\ncount = 'ten'\n",
        "lesson_id": "python-foundations-variables",
    }
    variables_java = {
        "status": "available",
        "summary": "变量是带静态类型的存储位置。",
        "difference": "编译期固定类型，赋值必须兼容声明类型。",
        "code": "int count = 10;\n",
        "lesson_id": "java-foundations-variables",
    }
    interpreter_python = {
        "status": "available",
        "summary": "解释器逐条读取并执行 Python 源码。",
        "difference": "Python 独有的运行模型，其他语言以编译产物运行。",
        "code": "python -c \"print('hi')\"\n",
        "lesson_id": "python-foundations-interpreter",
    }
    variables: dict[str, Any] = {
        "python": dict(variables_python),
        "java": dict(variables_java),
        "csharp": {
            "status": "missing",
            "note": "夹具 C# 课程未包含可对照课时。",
        },
        "cpp": {
            "status": "missing",
            "note": "夹具 C++ 课程未包含可对照课时。",
        },
    }
    interpreter: dict[str, Any] = {
        "python": dict(interpreter_python),
        "java": {
            "status": "missing",
            "note": "Java 由 JVM 加载字节码，无解释器启动概念。",
        },
        "csharp": {
            "status": "missing",
            "note": "C# 由 CLR 执行，路线内无解释器课时。",
        },
        "cpp": {
            "status": "missing",
            "note": "C++ 为本地编译语言，无解释器课时。",
        },
    }
    if break_reference == "language":
        variables["python"]["lesson_id"] = "java-foundations-variables"
    if break_reference == "missing":
        variables["python"]["lesson_id"] = "python-foundations-not-written"
    write_concepts(
        content_root,
        [
            {"id": "variables", "name": "变量", "description": "保存可变值的命名位置。", "compare": variables},
            {"id": "interpreter", "name": "解释器", "description": "读取并执行源码的程序。", "compare": interpreter},
            {"id": "legacy", "name": "旧概念", "description": "未提供对照元数据的兼容概念。"},
        ],
    )
    write_course(
        content_root,
        "python",
        "Python",
        [
            ("python-foundations-variables", "variables", ["variables", "legacy"], "变量"),
            ("python-foundations-interpreter", "interpreter", ["interpreter"], "解释器"),
        ],
    )
    write_course(
        content_root,
        "java",
        "Java",
        [("java-foundations-variables", "variables", ["variables"], "变量")],
    )


def comparison_response(content_root: Path) -> dict[str, object]:
    with TestClient(create_app(make_settings(content_root))) as client:
        response = client.get("/api/compare/concepts")
    assert response.status_code == 200
    return response.json()


def assert_no_private_fields(value: object) -> None:
    if isinstance(value, dict):
        assert not (PRIVATE_FIELDS & set(value))
        for child in value.values():
            assert_no_private_fields(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_private_fields(child)


def test_comparison_returns_authored_slots_for_four_languages(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir()
    write_fixture(content_root)

    payload = comparison_response(content_root)

    assert payload["concepts"][0]["id"] == "variables"
    slots = payload["concepts"][0]["slots"]
    assert set(slots) == {"python", "java", "csharp", "cpp"}
    assert slots["python"]["status"] == "available"
    assert slots["python"]["lesson_id"] == "python-foundations-variables"
    assert slots["python"]["lesson_title"] == "变量"
    assert "命名引用" in slots["python"]["summary"]
    assert slots["java"]["status"] == "available"
    assert slots["java"]["lesson_id"] == "java-foundations-variables"
    assert slots["csharp"]["status"] == "missing"
    assert "未包含可对照课时" in slots["csharp"]["note"]
    assert_no_private_fields(payload)


def test_missing_slot_only_carries_note(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir()
    write_fixture(content_root)

    payload = comparison_response(content_root)

    java_slot = payload["concepts"][1]["slots"]["java"]
    assert java_slot["status"] == "missing"
    assert "JVM" in java_slot["note"]
    assert java_slot["lesson_id"] is None
    assert java_slot["code"] is None


def test_concept_without_compare_metadata_derives_slots_from_lessons(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir()
    write_fixture(content_root)

    payload = comparison_response(content_root)

    legacy = next(concept for concept in payload["concepts"] if concept["id"] == "legacy")
    assert legacy["slots"]["python"]["status"] == "available"
    assert legacy["slots"]["python"]["lesson_id"] == "python-foundations-variables"
    assert legacy["slots"]["java"]["status"] == "missing"
    assert legacy["slots"]["java"]["note"]


def test_invalid_lesson_reference_degrades_slot_and_reports_isolated_error(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir()
    write_fixture(content_root, break_reference="language")

    with TestClient(create_app(make_settings(content_root))) as client:
        comparison = client.get("/api/compare/concepts").json()
        catalog = client.get("/api/content/catalog").json()

    python_slot = comparison["concepts"][0]["slots"]["python"]
    assert python_slot["status"] == "missing"
    assert "引用无效" in python_slot["note"]
    codes = {error["code"] for error in catalog["isolated_errors"]}
    assert "invalid_comparison_reference" in codes


def test_unknown_lesson_reference_degrades_slot(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    content_root.mkdir()
    write_fixture(content_root, break_reference="missing")

    with TestClient(create_app(make_settings(content_root))) as client:
        comparison = client.get("/api/compare/concepts").json()

    python_slot = comparison["concepts"][0]["slots"]["python"]
    assert python_slot["status"] == "missing"


def test_legacy_concepts_yaml_without_compare_still_parses(tmp_path: Path) -> None:
    concepts_path = tmp_path / "concepts.yaml"
    concepts_path.write_text(
        json.dumps(
            {
                "concepts": [
                    {"id": "variables", "name": "变量", "description": "保存可变值的命名位置。"}
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    document = parse_concepts(concepts_path)

    assert document.concepts[0].compare is None


def test_compare_metadata_requires_exactly_four_language_slots(tmp_path: Path) -> None:
    concepts_path = tmp_path / "concepts.yaml"
    concepts_path.write_text(
        json.dumps(
            {
                "concepts": [
                    {
                        "id": "variables",
                        "name": "变量",
                        "description": "保存可变值的命名位置。",
                        "compare": {
                            "python": {
                                "status": "available",
                                "summary": "说明",
                                "difference": "差异",
                                "code": "x = 1\n",
                                "lesson_id": "python-foundations-variables",
                            }
                        },
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    import pytest

    from hard_api.content.parser import ContentParseError

    with pytest.raises(ContentParseError):
        parse_concepts(concepts_path)


def test_real_content_comparison_has_zero_invalid_references_and_full_slots() -> None:
    project_root = Path(__file__).resolve().parents[4]
    content_root = project_root / "content"
    if not (content_root / "python" / "course.yaml").is_file():
        raise AssertionError("真实内容目录缺失，无法执行全量概念映射检查。")

    repository = ContentRepository(content_root)
    assert repository.comparison_invalid_references == []

    assert len(repository.comparison_concepts) == 45
    for concept in repository.comparison_concepts:
        assert set(concept["slots"]) == {"python", "java", "csharp", "cpp"}
        for language, slot in concept["slots"].items():
            if slot["status"] != "available":
                continue
            lesson = repository.lesson_for(slot["lesson_id"])
            assert lesson is not None, (concept["id"], language)
            assert lesson.language == language, (concept["id"], language)
            assert concept["id"] in lesson.document.front_matter.concepts, (concept["id"], slot["lesson_id"])
            assert slot["lesson_title"] == lesson.document.front_matter.title
            assert slot["summary"] and slot["difference"] and slot["code"]


def test_compare_endpoint_is_registered_in_openapi() -> None:
    application = create_app(make_settings(Path(__file__).resolve().parents[4] / "content"))
    assert "/api/compare/concepts" in application.openapi()["paths"]
