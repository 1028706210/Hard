from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from hard_api.content.models import (
    Choice,
    Concept,
    ConceptsDocument,
    CourseDocument,
    CourseModule,
    ExerciseDocument,
    ExerciseQuestion,
    LessonEntry,
    LessonFrontMatter,
    PlacementTest,
    PrivateQuestionData,
    SourceCoverageEntry,
)


SCHEMA_DIRECTORY = Path(__file__).resolve().parents[2] / "content" / "schema"
SCHEMA_FILES = (
    "concepts.schema.json",
    "course.schema.json",
    "lesson-front-matter.schema.json",
    "exercises.schema.json",
)


def load_schemas() -> dict[str, dict[str, object]]:
    schemas: dict[str, dict[str, object]] = {}
    for filename in SCHEMA_FILES:
        payload = json.loads((SCHEMA_DIRECTORY / filename).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Schema 必须是对象：{filename}")
        schemas[filename] = payload
    return schemas


def _object_at(schema: dict[str, object], *path: str) -> dict[str, object]:
    value: object = schema
    for part in path:
        if not isinstance(value, dict) or part not in value:
            raise ValueError(f"Schema 缺少节点：{'.'.join(path)}")
        value = value[part]
    if not isinstance(value, dict):
        raise ValueError(f"Schema 节点必须是对象：{'.'.join(path)}")
    return value


def _verify_required_fields(schema: dict[str, object], model: type[BaseModel]) -> None:
    required = schema.get("required", [])
    if not isinstance(required, list) or not all(isinstance(field, str) for field in required):
        raise ValueError("Schema required 必须是字符串数组。")
    model_required = {name for name, field in model.model_fields.items() if field.is_required()}
    if set(required) != model_required:
        raise ValueError(f"Schema required 与运行时模型不一致：{model.__name__}")


def validate_schema_contracts() -> None:
    schemas = load_schemas()
    concepts = schemas["concepts.schema.json"]
    course = schemas["course.schema.json"]
    lesson = schemas["lesson-front-matter.schema.json"]
    exercises = schemas["exercises.schema.json"]

    _verify_required_fields(concepts, ConceptsDocument)
    _verify_required_fields(_object_at(concepts, "properties", "concepts", "items"), Concept)
    _verify_required_fields(course, CourseDocument)
    _verify_required_fields(_object_at(course, "properties", "placement_tests", "items"), PlacementTest)
    _verify_required_fields(_object_at(course, "properties", "modules", "items"), CourseModule)
    _verify_required_fields(
        _object_at(course, "properties", "modules", "items", "properties", "source_coverage", "items"),
        SourceCoverageEntry,
    )
    _verify_required_fields(
        _object_at(course, "properties", "modules", "items", "properties", "lessons", "items"),
        LessonEntry,
    )
    _verify_required_fields(lesson, LessonFrontMatter)
    _verify_required_fields(exercises, ExerciseDocument)
    _verify_required_fields(_object_at(exercises, "properties", "questions", "items"), ExerciseQuestion)
    _verify_required_fields(
        _object_at(exercises, "properties", "questions", "items", "properties", "private"),
        PrivateQuestionData,
    )
    _verify_required_fields(
        _object_at(exercises, "properties", "questions", "items", "properties", "choices", "items"),
        Choice,
    )
