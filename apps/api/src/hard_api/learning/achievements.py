from __future__ import annotations

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.content.repository import ContentRepository


def _course_badge_points(repository: ContentRepository, course_id: str, badge: str) -> int:
    course = repository.course_for(course_id)
    if course is None:
        return 0
    return int(course.document.growth.badge_points[badge])


def grant_badge(connection: Connection, repository: ContentRepository, course_id: str, badge: str) -> bool:
    inserted = connection.execute(
        text("INSERT INTO achievements (code, earned_at) VALUES (:code, :earned_at) ON CONFLICT(code) DO NOTHING"),
        {"code": badge, "earned_at": datetime.now()},
    )
    if inserted.rowcount != 1:
        return False
    connection.execute(
        text(
            "INSERT INTO experience_events "
            "(event_key, event_type, course_id, lesson_id, exercise_id, points, created_at) "
            "VALUES (:event_key, 'badge', :course_id, NULL, :badge, :points, :created_at) "
            "ON CONFLICT(event_key) DO NOTHING"
        ),
        {
            "event_key": f"badge:{course_id}:{badge}",
            "course_id": course_id,
            "badge": badge,
            "points": _course_badge_points(repository, course_id, badge),
            "created_at": datetime.now(),
        },
    )
    return True
