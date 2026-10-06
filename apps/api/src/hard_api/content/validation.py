from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from hard_api.content.models import CourseDocument, ExerciseDocument, LessonDocument


@dataclass(frozen=True, slots=True)
class LoadedLesson:
    module_id: str
    entry_id: str
    document: LessonDocument
    exercises: ExerciseDocument


class ContentSemanticError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


_QUESTION_SUFFIX = {
    "knowledge": r"k\d{2}",
    "scenario": r"k\d{2}",
    "code": r"c\d{2}",
    "challenge": "challenge",
}


def _reject_cycle(graph: dict[str, list[str]], code: str) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            raise ContentSemanticError(code)
        visiting.add(node)
        for prerequisite in graph[node]:
            visit(prerequisite)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def validate_course_semantics(
    course: CourseDocument,
    lessons: Iterable[LoadedLesson],
    *,
    concept_ids: set[str],
) -> None:
    records = tuple(lessons)
    module_ids = {module.id for module in course.modules}
    if len(module_ids) != len(course.modules):
        raise ContentSemanticError("duplicate_module_id")
    module_graph: dict[str, list[str]] = {}
    for module in course.modules:
        if any(prerequisite not in module_ids for prerequisite in module.prerequisites):
            raise ContentSemanticError("unknown_module_prerequisite")
        module_graph[module.id] = list(module.prerequisites)
    _reject_cycle(module_graph, "module_prerequisite_cycle")

    lesson_by_id: dict[str, LoadedLesson] = {}
    for record in records:
        if record.entry_id in lesson_by_id:
            raise ContentSemanticError("duplicate_lesson_id")
        if record.document.front_matter.id != record.entry_id:
            raise ContentSemanticError("lesson_id_mismatch")
        if record.exercises.lesson_id != record.entry_id:
            raise ContentSemanticError("lesson_id_mismatch")
        if any(concept_id not in concept_ids for concept_id in record.document.front_matter.concepts):
            raise ContentSemanticError("unknown_concept")
        lesson_by_id[record.entry_id] = record

    lesson_graph: dict[str, list[str]] = {}
    for lesson_id, record in lesson_by_id.items():
        prerequisites = list(record.document.front_matter.prerequisites)
        if lesson_id in prerequisites:
            raise ContentSemanticError("self_lesson_prerequisite")
        if any(prerequisite not in lesson_by_id for prerequisite in prerequisites):
            raise ContentSemanticError("unknown_lesson_prerequisite")
        lesson_graph[lesson_id] = prerequisites
    _reject_cycle(lesson_graph, "lesson_prerequisite_cycle")

    question_ids: set[str] = set()
    for record in records:
        for question in record.exercises.questions:
            if question.id in question_ids:
                raise ContentSemanticError("duplicate_question_id")
            question_ids.add(question.id)
            expected = re.compile(
                rf"^{re.escape(record.entry_id)}-{_QUESTION_SUFFIX[question.type]}$"
            )
            if not expected.fullmatch(question.id):
                raise ContentSemanticError("invalid_question_id")

    for module in course.modules:
        if any(entry.lesson_id not in lesson_by_id for entry in module.source_coverage):
            raise ContentSemanticError("unknown_source_coverage")
    for placement in course.placement_tests:
        if any(question_id not in question_ids for question_id in placement.question_ids):
            raise ContentSemanticError("unknown_placement_question")
