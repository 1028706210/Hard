from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.core.errors import ApiError
from hard_api.learning.progress import perform_idempotent


def save_note(
    database_path: Path, *, lesson_id: str, body: str, idempotency_key: str | None
) -> dict[str, object]:
    if not body.strip():
        raise ApiError("blank_note", "笔记不能为空。")
    payload = {"lesson_id": lesson_id, "body": body}

    def action(connection: Connection) -> dict[str, object]:
        updated_at = datetime.now()
        connection.execute(
            text(
                "INSERT INTO notes (lesson_id, body, updated_at) VALUES (:lesson_id, :body, :updated_at) "
                "ON CONFLICT(lesson_id) DO UPDATE SET body = excluded.body, updated_at = excluded.updated_at"
            ),
            {"lesson_id": lesson_id, "body": body, "updated_at": updated_at},
        )
        return {"lesson_id": lesson_id, "body": body, "updated_at": updated_at.isoformat()}

    return perform_idempotent(
        database_path,
        operation="progress.note.put",
        idempotency_key=idempotency_key,
        payload=payload,
        action=action,
    )


def delete_note(database_path: Path, *, lesson_id: str, idempotency_key: str | None) -> dict[str, object]:
    def action(connection: Connection) -> dict[str, object]:
        connection.execute(text("DELETE FROM notes WHERE lesson_id = :lesson_id"), {"lesson_id": lesson_id})
        return {"lesson_id": lesson_id, "deleted": True}

    return perform_idempotent(
        database_path,
        operation="progress.note.delete",
        idempotency_key=idempotency_key,
        payload={"lesson_id": lesson_id},
        action=action,
    )


def save_favorite(database_path: Path, *, lesson_id: str, idempotency_key: str | None) -> dict[str, object]:
    def action(connection: Connection) -> dict[str, object]:
        connection.execute(
            text(
                "INSERT INTO favorites (lesson_id, created_at) VALUES (:lesson_id, :created_at) "
                "ON CONFLICT(lesson_id) DO NOTHING"
            ),
            {"lesson_id": lesson_id, "created_at": datetime.now()},
        )
        return {"lesson_id": lesson_id, "favorite": True}

    return perform_idempotent(
        database_path,
        operation="progress.favorite.put",
        idempotency_key=idempotency_key,
        payload={"lesson_id": lesson_id},
        action=action,
    )


def delete_favorite(database_path: Path, *, lesson_id: str, idempotency_key: str | None) -> dict[str, object]:
    def action(connection: Connection) -> dict[str, object]:
        connection.execute(text("DELETE FROM favorites WHERE lesson_id = :lesson_id"), {"lesson_id": lesson_id})
        return {"lesson_id": lesson_id, "favorite": False}

    return perform_idempotent(
        database_path,
        operation="progress.favorite.delete",
        idempotency_key=idempotency_key,
        payload={"lesson_id": lesson_id},
        action=action,
    )
