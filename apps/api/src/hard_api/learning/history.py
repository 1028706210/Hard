from __future__ import annotations

from difflib import unified_diff
import json
from pathlib import Path

from sqlalchemy import text

from hard_api.db import session


_PUBLIC_NORMALIZED_FIELDS = {
    "score",
    "passed",
    "compile_error_category",
    "visible_tests_passed",
    "visible_tests_total",
}


def public_normalized_result(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {
        key: item
        for key, item in value.items()
        if key in _PUBLIC_NORMALIZED_FIELDS and isinstance(item, (str, int, float, bool))
    }


def code_history(database_path: Path, exercise_id: str | None = None) -> list[dict[str, object]]:
    query = (
        "SELECT submissions.id, attempts.exercise_id, submissions.source_code, submissions.language, "
        "submissions.normalized_result, submissions.duration_ms, attempts.final_score, submissions.created_at "
        "FROM submissions JOIN attempts ON attempts.id = submissions.attempt_id"
    )
    parameters: dict[str, object] = {}
    if exercise_id is not None:
        query += " WHERE attempts.exercise_id = :exercise_id"
        parameters["exercise_id"] = exercise_id
    query += " ORDER BY submissions.created_at, submissions.id"
    with session.database_connection(database_path) as connection:
        rows = connection.execute(text(query), parameters).mappings().all()
    previous_by_exercise: dict[str, str] = {}
    records: list[dict[str, object]] = []
    for row in rows:
        source = str(row["source_code"])
        current_exercise = str(row["exercise_id"])
        previous = previous_by_exercise.get(current_exercise, "")
        diff = "".join(
            unified_diff(
                previous.splitlines(keepends=True),
                source.splitlines(keepends=True),
                fromfile="previous",
                tofile="current",
            )
        )
        previous_by_exercise[current_exercise] = source
        normalized = public_normalized_result(
            json.loads(row["normalized_result"]) if row["normalized_result"] else {}
        )
        records.append(
            {
                "id": row["id"],
                "exercise_id": current_exercise,
                "language": row["language"],
                "source_code": source,
                "normalized_result": normalized,
                "score": float(row["final_score"] or 0),
                "duration_ms": row["duration_ms"],
                "created_at": str(row["created_at"]),
                "diff": diff,
            }
        )
    return records
