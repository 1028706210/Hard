from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.content.repository import ContentRepository


LESSON_PASSING_SCORE = Decimal("70")
MASTERY_SCORE = Decimal("85")


def lesson_passed(score: Decimal) -> bool:
    return score >= LESSON_PASSING_SCORE


def mastered(score: Decimal) -> bool:
    return score >= MASTERY_SCORE


def record_aggregate_mastery(
    connection: Connection, *, repository: ContentRepository, language: str, recorded_at: datetime
) -> dict[str, Decimal]:
    course = repository.course_for(language)
    if course is None:
        return {}
    lesson_scores = {
        str(row["scope_id"]): Decimal(str(row["score"]))
        for row in connection.execute(
            text(
                "SELECT scope_id, MAX(score) AS score FROM mastery_snapshots "
                "WHERE course_id = :course_id AND scope_type = 'lesson' GROUP BY scope_id"
            ),
            {"course_id": language},
        ).mappings()
    }
    module_scores: dict[str, Decimal] = {}
    for module in course.modules:
        scores = [
            lesson_scores.get(lesson.document.front_matter.id, Decimal("0"))
            for lesson in module.lessons
        ]
        score = (
            sum(scores, Decimal("0")) / len(scores) if scores else Decimal("0")
        ).quantize(Decimal("0.01"), ROUND_HALF_UP)
        module_scores[module.id] = score
        connection.execute(
            text(
                "INSERT INTO mastery_snapshots (course_id, scope_type, scope_id, status, score, recorded_at) "
                "VALUES (:course_id, 'module', :scope_id, :status, :score, :recorded_at)"
            ),
            {
                "course_id": language,
                "scope_id": module.id,
                "status": "mastered" if mastered(score) else "in_progress",
                "score": float(score),
                "recorded_at": recorded_at,
            },
        )
    course_score = (
        sum(module_scores.values(), Decimal("0")) / len(module_scores)
        if module_scores
        else Decimal("0")
    ).quantize(Decimal("0.01"), ROUND_HALF_UP)
    connection.execute(
        text(
            "INSERT INTO mastery_snapshots (course_id, scope_type, scope_id, status, score, recorded_at) "
            "VALUES (:course_id, 'course', :scope_id, :status, :score, :recorded_at)"
        ),
        {
            "course_id": language,
            "scope_id": language,
            "status": "mastered" if mastered(course_score) else "in_progress",
            "score": float(course_score),
            "recorded_at": recorded_at,
        },
    )
    return {**module_scores, language: course_score}
