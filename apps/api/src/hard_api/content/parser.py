from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from hard_api.content.models import (
    ConceptsDocument,
    CourseDocument,
    ExerciseDocument,
    LessonDocument,
    LessonFrontMatter,
)


class ContentParseError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ContentParseError("invalid_yaml", f"无法读取 YAML：{error}") from error
    if not isinstance(data, dict):
        raise ContentParseError("invalid_yaml", "YAML 根节点必须是对象。")
    return data


def load_json_mapping(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContentParseError("invalid_json", f"无法读取 JSON：{error}") from error
    if not isinstance(data, dict):
        raise ContentParseError("invalid_json", "JSON 根节点必须是对象。")
    return data


def parse_concepts(path: Path) -> ConceptsDocument:
    try:
        return ConceptsDocument.model_validate(load_yaml_mapping(path))
    except ValidationError as error:
        raise ContentParseError("invalid_concepts", str(error)) from error


def parse_course(path: Path) -> CourseDocument:
    try:
        return CourseDocument.model_validate(load_yaml_mapping(path))
    except ValidationError as error:
        raise ContentParseError("invalid_course", str(error)) from error


def parse_lesson(path: Path) -> LessonDocument:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ContentParseError("missing_lesson", f"无法读取课时：{error}") from error

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContentParseError("invalid_lesson", "Markdown 必须以 YAML front matter 开始。")
    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as error:
        raise ContentParseError("invalid_lesson", "Markdown front matter 缺少结束标记。") from error

    try:
        metadata = yaml.safe_load("\n".join(lines[1:closing_index]))
    except yaml.YAMLError as error:
        raise ContentParseError("invalid_lesson", f"front matter 无效：{error}") from error
    if not isinstance(metadata, dict):
        raise ContentParseError("invalid_lesson", "front matter 必须是对象。")

    body = "\n".join(lines[closing_index + 1 :]).strip()
    if not body:
        raise ContentParseError("empty_lesson_body", "课时正文不能为空。")
    try:
        return LessonDocument(front_matter=LessonFrontMatter.model_validate(metadata), body=body)
    except ValidationError as error:
        raise ContentParseError("invalid_lesson", str(error)) from error


def parse_exercises(path: Path) -> ExerciseDocument:
    try:
        return ExerciseDocument.model_validate(load_json_mapping(path))
    except ValidationError as error:
        raise ContentParseError("invalid_exercises", str(error)) from error


def resolve_content_path(content_root: Path, relative_path: str) -> Path:
    root = content_root.resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ContentParseError("path_escape", f"课时路径超出内容目录：{relative_path}") from error
    return candidate


def public_exercise_payload(document: ExerciseDocument) -> dict[str, object]:
    return document.model_dump(exclude={"questions": {"__all__": {"private"}}}, mode="json")
