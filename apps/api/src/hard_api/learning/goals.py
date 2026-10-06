from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.core.errors import ApiError
from hard_api.learning.progress import perform_idempotent


def set_daily_goal(
    database_path: Path,
    *,
    target_minutes: int,
    target_exercises: int,
    idempotency_key: str | None,
    today: date | None = None,
) -> dict[str, object]:
    if target_minutes < 0 or target_exercises < 0:
        raise ApiError("invalid_daily_goal", "每日目标必须是非负整数。")
    goal_date = (today or date.today()).isoformat()
    payload = {"target_minutes": target_minutes, "target_exercises": target_exercises, "date": goal_date}

    def action(connection: Connection) -> dict[str, object]:
        connection.execute(
            text(
                "INSERT INTO daily_goals (goal_date, target_minutes, target_exercises) "
                "VALUES (:goal_date, :target_minutes, :target_exercises) "
                "ON CONFLICT(goal_date) DO UPDATE SET "
                "target_minutes = excluded.target_minutes, target_exercises = excluded.target_exercises"
            ),
            {"goal_date": goal_date, "target_minutes": target_minutes, "target_exercises": target_exercises},
        )
        return {
            "date": goal_date,
            "configured": True,
            "target_minutes": target_minutes,
            "target_exercises": target_exercises,
        }

    return perform_idempotent(
        database_path,
        operation="progress.daily_goal",
        idempotency_key=idempotency_key,
        payload=payload,
        action=action,
    )
