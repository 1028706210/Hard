from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.content.repository import ContentRepository
from hard_api.db import session
from hard_api.learning.progress import streak_for_dates


def award_experience(
    connection: Connection,
    *,
    event_key: str,
    event_type: str,
    course_id: str,
    points: int,
    lesson_id: str | None = None,
    exercise_id: str | None = None,
) -> bool:
    result = connection.execute(
        text(
            "INSERT INTO experience_events "
            "(event_key, event_type, course_id, lesson_id, exercise_id, points, created_at) "
            "VALUES (:event_key, :event_type, :course_id, :lesson_id, :exercise_id, :points, :created_at) "
            "ON CONFLICT(event_key) DO NOTHING"
        ),
        {
            "event_key": event_key,
            "event_type": event_type,
            "course_id": course_id,
            "lesson_id": lesson_id,
            "exercise_id": exercise_id,
            "points": points,
            "created_at": datetime.now(),
        },
    )
    return result.rowcount == 1


def growth_summary(
    database_path: Path, *, repository: ContentRepository, today: date | None = None
) -> dict[str, object]:
    current_day = today or date.today()
    with session.database_connection(database_path) as connection:
        total_experience = int(
            connection.execute(text("SELECT COALESCE(SUM(points), 0) FROM experience_events")).scalar_one()
        )
        activity_dates = connection.execute(
            text("SELECT activity_date FROM learning_activity_days")
        ).scalars().all()
        earned_badges = connection.execute(text("SELECT code FROM achievements ORDER BY code")).scalars().all()
        mastery_rows = connection.execute(
            text(
                "SELECT scope_type, scope_id, MAX(score) AS score FROM mastery_snapshots "
                "GROUP BY scope_type, scope_id"
            )
        ).mappings().all()
        progress_statuses = dict(
            connection.execute(text("SELECT lesson_id, status FROM lesson_progress")).all()
        )
        passed_challenges = {
            str(row["exercise_id"])
            for row in connection.execute(
                text(
                    "SELECT DISTINCT exercise_id FROM attempts "
                    "WHERE question_type = 'challenge' AND final_score >= 70"
                )
            ).mappings()
        }

    level = 1 + total_experience // 100
    progress = total_experience % 100
    route_completion: list[dict[str, object]] = []
    for course in repository.courses:
        lesson_ids = [
            lesson.document.front_matter.id
            for module in course.modules
            for lesson in module.lessons
        ]
        final_module = course.modules[-1] if course.modules else None
        final_challenges = [
            question.id
            for lesson in (final_module.lessons if final_module else ())
            for question in lesson.exercises.questions
            if question.type == "challenge"
        ]
        route_completion.append(
            {
                "language": course.document.language,
                "fixture_only": course.fixture_only,
                "complete": (
                    not course.fixture_only
                    and all(progress_statuses.get(lesson_id) in {"completed", "validated"} for lesson_id in lesson_ids)
                    and all(challenge_id in passed_challenges for challenge_id in final_challenges)
                ),
            }
        )
    return {
        "total_experience": total_experience,
        "level": level,
        "current_level_progress": progress,
        "next_level_remaining": 100 - progress if progress else 100,
        "streak_days": streak_for_dates(activity_dates, current_day),
        "badges": list(earned_badges),
        "mastery": [
            {"scope_type": row["scope_type"], "scope_id": row["scope_id"], "score": float(row["score"])}
            for row in mastery_rows
        ],
        "new_badges": [],
        "route_completion": route_completion,
    }
