from __future__ import annotations

from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection

from hard_api.content.repository import ContentRepository
from hard_api.core.errors import ApiError
from hard_api.db import session
from hard_api.learning import achievements


def validate_idempotency_key(value: str | None) -> str:
    if value is None or not value.strip() or len(value) > 128:
        raise ApiError("invalid_idempotency_key", "Idempotency-Key 必须是 1 到 128 个非空字符。")
    return value


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def perform_idempotent(
    database_path: Path,
    *,
    operation: str,
    idempotency_key: str | None,
    payload: dict[str, object],
    action: Callable[[Connection], dict[str, object]],
) -> dict[str, object]:
    raw_key = validate_idempotency_key(idempotency_key)
    storage_key = f"{operation}:{raw_key}"
    fingerprint = _fingerprint(payload)

    def stored_response(connection: Connection) -> dict[str, object] | None:
        stored = connection.execute(
            text(
                "SELECT request_fingerprint, response_body FROM idempotency_keys WHERE key = :key"
            ),
            {"key": storage_key},
        ).mappings().first()
        if stored is None:
            return None
        if stored["request_fingerprint"] != fingerprint:
            raise ApiError("idempotency_conflict", "幂等键不能用于不同的请求内容。", status_code=409)
        return json.loads(stored["response_body"])

    try:
        with session.transaction(database_path) as connection:
            replay = stored_response(connection)
            if replay is not None:
                return replay
            response = action(connection)
            connection.execute(
                text(
                    "INSERT INTO idempotency_keys "
                    "(key, operation, request_fingerprint, response_body, created_at) "
                    "VALUES (:key, :operation, :fingerprint, :response_body, :created_at)"
                ),
                {
                    "key": storage_key,
                    "operation": operation,
                    "fingerprint": fingerprint,
                    "response_body": json.dumps(response, ensure_ascii=False, sort_keys=True),
                    "created_at": datetime.now(),
                },
            )
            return response
    except IntegrityError:
        with session.database_connection(database_path) as connection:
            replay = stored_response(connection)
        if replay is not None:
            return replay
        raise


def update_lesson_progress(
    database_path: Path,
    *,
    course_id: str,
    module_id: str,
    lesson_id: str,
    position: int,
    time_spent_seconds: int,
    idempotency_key: str | None,
    today: date | None = None,
    repository: ContentRepository | None = None,
) -> dict[str, object]:
    if position < 0 or time_spent_seconds < 0:
        raise ApiError("invalid_progress", "阅读位置和学习时长必须为非负整数。")
    activity_date = (today or date.today()).isoformat()
    payload = {"lesson_id": lesson_id, "position": position, "time_spent_seconds": time_spent_seconds}

    def action(connection: Connection) -> dict[str, object]:
        existing = connection.execute(
            text(
                "SELECT position, time_spent_seconds, status FROM lesson_progress WHERE lesson_id = :lesson_id"
            ),
            {"lesson_id": lesson_id},
        ).mappings().first()
        now = datetime.now()
        if existing is None:
            resolved_position = position
            resolved_seconds = time_spent_seconds
            status = "in_progress"
            connection.execute(
                text(
                    "INSERT INTO lesson_progress "
                    "(lesson_id, course_id, module_id, position, time_spent_seconds, status, updated_at) "
                    "VALUES (:lesson_id, :course_id, :module_id, :position, :seconds, :status, :updated_at)"
                ),
                {
                    "lesson_id": lesson_id,
                    "course_id": course_id,
                    "module_id": module_id,
                    "position": resolved_position,
                    "seconds": resolved_seconds,
                    "status": status,
                    "updated_at": now,
                },
            )
        else:
            resolved_position = max(int(existing["position"]), position)
            resolved_seconds = int(existing["time_spent_seconds"]) + time_spent_seconds
            status = str(existing["status"])
            if status == "not_started":
                status = "in_progress"
            connection.execute(
                text(
                    "UPDATE lesson_progress SET position = :position, time_spent_seconds = :seconds, "
                    "status = :status, updated_at = :updated_at WHERE lesson_id = :lesson_id"
                ),
                {
                    "lesson_id": lesson_id,
                    "position": resolved_position,
                    "seconds": resolved_seconds,
                    "status": status,
                    "updated_at": now,
                },
            )
        if time_spent_seconds:
            connection.execute(
                text(
                    "INSERT INTO learning_activity_days "
                    "(activity_date, time_spent_seconds, completed_exercises, updated_at) "
                    "VALUES (:activity_date, :seconds, 0, :updated_at) "
                    "ON CONFLICT(activity_date) DO UPDATE SET "
                    "time_spent_seconds = learning_activity_days.time_spent_seconds + excluded.time_spent_seconds, "
                    "updated_at = excluded.updated_at"
                ),
                {"activity_date": activity_date, "seconds": time_spent_seconds, "updated_at": now},
            )
        if repository is not None:
            activity_dates = connection.execute(
                text("SELECT activity_date FROM learning_activity_days")
            ).scalars().all()
            if streak_for_dates(activity_dates, today or date.today()) >= 7:
                achievements.grant_badge(connection, repository, course_id, "seven_day_streak")
        return {
            "lesson_id": lesson_id,
            "position": resolved_position,
            "time_spent_seconds": resolved_seconds,
            "status": status,
            "updated_at": now.isoformat(),
        }

    return perform_idempotent(
        database_path,
        operation="progress.lesson",
        idempotency_key=idempotency_key,
        payload=payload,
        action=action,
    )


def streak_for_dates(activity_dates: list[str], today: date | None = None) -> int:
    current_day = today or date.today()
    known_dates = {date.fromisoformat(value) for value in activity_dates}
    if current_day not in known_dates and current_day.fromordinal(current_day.toordinal() - 1) not in known_dates:
        return 0
    cursor = current_day if current_day in known_dates else current_day.fromordinal(current_day.toordinal() - 1)
    streak = 0
    while cursor in known_dates:
        streak += 1
        cursor = cursor.fromordinal(cursor.toordinal() - 1)
    return streak


def learning_summary(database_path: Path, today: date | None = None) -> dict[str, object]:
    current_day = today or date.today()
    day_value = current_day.isoformat()
    with session.database_connection(database_path) as connection:
        goal = connection.execute(
            text("SELECT target_minutes, target_exercises FROM daily_goals WHERE goal_date = :day"),
            {"day": day_value},
        ).mappings().first()
        activity = connection.execute(
            text(
                "SELECT time_spent_seconds, completed_exercises FROM learning_activity_days "
                "WHERE activity_date = :day"
            ),
            {"day": day_value},
        ).mappings().first()
        continuing = connection.execute(
            text(
                "SELECT course_id, module_id, lesson_id, position FROM lesson_progress "
                "WHERE status IN ('in_progress', 'completed', 'validated') "
                "ORDER BY updated_at DESC LIMIT 1"
            )
        ).mappings().first()
        lesson_statuses = dict(connection.execute(text("SELECT lesson_id, status FROM lesson_progress")).all())
        review_count = connection.execute(
            text("SELECT COUNT(*) FROM review_items WHERE status = 'scheduled' AND due_on <= :day"),
            {"day": day_value},
        ).scalar_one()
        total_experience = connection.execute(
            text("SELECT COALESCE(SUM(points), 0) FROM experience_events")
        ).scalar_one()
        activity_dates = connection.execute(
            text("SELECT activity_date FROM learning_activity_days")
        ).scalars().all()

    configured = goal is not None
    target_minutes = int(goal["target_minutes"]) if goal else 0
    target_exercises = int(goal["target_exercises"]) if goal else 0
    studied_seconds = int(activity["time_spent_seconds"]) if activity else 0
    completed_exercises = int(activity["completed_exercises"]) if activity else 0
    time_ratio = 1.0 if target_minutes == 0 else min(1.0, studied_seconds / (target_minutes * 60))
    exercise_ratio = 1.0 if target_exercises == 0 else min(1.0, completed_exercises / target_exercises)
    completion_ratio = min(time_ratio, exercise_ratio) if configured else 0.0
    return {
        "daily_goal": {
            "date": day_value,
            "configured": configured,
            "target_minutes": target_minutes,
            "target_exercises": target_exercises,
            "studied_seconds": studied_seconds,
            "completed_exercises": completed_exercises,
            "completion_ratio": completion_ratio,
            "achieved": configured and time_ratio >= 1 and exercise_ratio >= 1,
        },
        "streak_days": streak_for_dates(activity_dates, current_day),
        "continue_learning": dict(continuing) if continuing else None,
        "lesson_statuses": lesson_statuses,
        "due_review_count": int(review_count),
        "current_experience": int(total_experience),
        "current_level": 1 + int(total_experience) // 100,
    }
