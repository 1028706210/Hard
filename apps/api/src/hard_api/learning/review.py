from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.content.repository import ContentRepository
from hard_api.core.errors import ApiError
from hard_api.learning.experience import award_experience
from hard_api.learning.progress import perform_idempotent


INTERVALS = (1, 3, 7, 14, 30, 60)


def next_interval(current_interval: int, score: Decimal) -> int:
    current_index = INTERVALS.index(current_interval) if current_interval in INTERVALS else 0
    if score >= Decimal("80"):
        return INTERVALS[min(current_index + 1, len(INTERVALS) - 1)]
    if score >= Decimal("60"):
        return INTERVALS[current_index]
    return INTERVALS[max(current_index - 1, 0)]


def due_review_items(database_path: Path, today: date | None = None) -> list[dict[str, object]]:
    current_day = (today or date.today()).isoformat()
    from hard_api.db import session

    with session.database_connection(database_path) as connection:
        rows = connection.execute(
            text(
                "SELECT id, concept_id, lesson_id, exercise_id, due_on, interval_days, last_score "
                "FROM review_items WHERE status IN ('scheduled', 'wrong_answer') AND due_on <= :day ORDER BY due_on, id"
            ),
            {"day": current_day},
        ).mappings().all()
    return [dict(row) for row in rows]


def score_review(
    database_path: Path,
    *,
    repository: ContentRepository,
    review_item_id: int,
    score: Decimal,
    idempotency_key: str | None,
    today: date | None = None,
) -> dict[str, object]:
    if score < 0 or score > 100:
        raise ApiError("invalid_review_score", "复习分数必须在 0 到 100 之间。")
    current_day = today or date.today()

    def action(connection: Connection) -> dict[str, object]:
        item = connection.execute(
            text(
                "SELECT concept_id, lesson_id, exercise_id, interval_days FROM review_items "
                "WHERE id = :id AND status IN ('scheduled', 'wrong_answer')"
            ),
            {"id": review_item_id},
        ).mappings().first()
        if item is None:
            raise ApiError("unknown_review_item", "未找到待复习项目。", status_code=404)
        interval_days = next_interval(int(item["interval_days"]), score)
        due_on = current_day + timedelta(days=interval_days)
        now = datetime.now()
        connection.execute(
            text(
                "UPDATE review_items SET interval_days = :interval_days, due_on = :due_on, "
                "last_score = :last_score, status = 'scheduled', updated_at = :updated_at WHERE id = :id"
            ),
            {
                "id": review_item_id,
                "interval_days": interval_days,
                "due_on": due_on.isoformat(),
                "last_score": float(score),
                "updated_at": now,
            },
        )
        experience_candidate = False
        lesson = repository.lesson_for(str(item["lesson_id"]))
        if score >= Decimal("80") and lesson is not None:
            course = repository.course_for(lesson.language)
            experience_candidate = award_experience(
                connection,
                event_key=f"review_milestone:{lesson.language}:{review_item_id}:{interval_days}",
                event_type="review_milestone",
                course_id=lesson.language,
                lesson_id=str(item["lesson_id"]),
                exercise_id=str(item["exercise_id"]),
                points=int(course.document.growth.review_milestone_points) if course else 0,
            )
        return {
            "id": review_item_id,
            "score": float(score),
            "interval_days": interval_days,
            "due_on": due_on.isoformat(),
            "experience_candidate": experience_candidate,
        }

    return perform_idempotent(
        database_path,
        operation="review.score",
        idempotency_key=idempotency_key,
        payload={"review_item_id": review_item_id, "score": str(score), "today": current_day.isoformat()},
        action=action,
    )
