from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.content.repository import ContentRepository
from hard_api.core.errors import ApiError
from hard_api.db import session
from hard_api.learning.mastery import mastered
from hard_api.learning.progress import perform_idempotent


def unlocked_lessons(repository: ContentRepository, database_path: Path, language: str) -> list[str]:
    course = repository.course_for(language)
    if course is None:
        return []
    with session.database_connection(database_path) as connection:
        return unlocked_lessons_for_connection(repository, connection, language)


def unlocked_lessons_for_connection(
    repository: ContentRepository, connection: Connection, language: str
) -> list[str]:
    course = repository.course_for(language)
    if course is None:
        return []
    statuses = dict(connection.execute(text("SELECT lesson_id, status FROM lesson_progress")).all())
    unlocked: list[str] = []
    for module in course.modules:
        if any(
            not all(
                statuses.get(lesson.document.front_matter.id) in {"completed", "validated"}
                for lesson in next(candidate for candidate in course.modules if candidate.id == prerequisite).lessons
            )
            for prerequisite in module.prerequisites
        ):
            continue
        for lesson in module.lessons:
            if all(statuses.get(prerequisite) in {"completed", "validated"} for prerequisite in lesson.document.front_matter.prerequisites):
                unlocked.append(lesson.document.front_matter.id)
    return unlocked


def record_placement(
    database_path: Path,
    *,
    repository: ContentRepository,
    language: str,
    module_id: str,
    score: Decimal,
    idempotency_key: str | None,
) -> dict[str, object]:
    course = repository.course_for(language)
    if course is None:
        raise ApiError("unknown_language", "未找到课程语言。", status_code=404)
    module = next((candidate for candidate in course.modules if candidate.id == module_id), None)
    if module is None:
        raise ApiError("unknown_module", "未找到课程模块。", status_code=404)
    if score < 0 or score > 100:
        raise ApiError("invalid_placement_score", "分级测试分数必须在 0 到 100 之间。")

    def action(connection: Connection) -> dict[str, object]:
        if not mastered(score):
            return {"module_id": module_id, "score": float(score), "validated": False, "experience_candidate": False}
        now = datetime.now()
        for lesson in module.lessons:
            connection.execute(
                text(
                    "INSERT INTO lesson_progress "
                    "(lesson_id, course_id, module_id, position, time_spent_seconds, status, updated_at) "
                    "VALUES (:lesson_id, :course_id, :module_id, 0, 0, 'validated', :updated_at) "
                    "ON CONFLICT(lesson_id) DO UPDATE SET status = 'validated', updated_at = excluded.updated_at"
                ),
                {
                    "lesson_id": lesson.document.front_matter.id,
                    "course_id": language,
                    "module_id": module_id,
                    "updated_at": now,
                },
            )
        connection.execute(
            text(
                "INSERT INTO mastery_snapshots (course_id, scope_type, scope_id, status, score, recorded_at) "
                "VALUES (:course_id, 'module', :scope_id, 'validated', :score, :recorded_at)"
            ),
            {"course_id": language, "scope_id": module_id, "score": float(score), "recorded_at": now},
        )
        return {"module_id": module_id, "score": float(score), "validated": True, "experience_candidate": False}

    return perform_idempotent(
        database_path,
        operation="assessment.placement",
        idempotency_key=idempotency_key,
        payload={"language": language, "module_id": module_id, "score": str(score)},
        action=action,
    )
