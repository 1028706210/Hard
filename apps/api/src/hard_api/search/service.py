from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import text

from hard_api.content.repository import ContentRepository
from hard_api.db import session


_FENCED_CODE = re.compile(r"```[^\n]*\n[\s\S]*?```", re.MULTILINE)
_MARKDOWN = re.compile(r"[`#*_>\[\]()]+")
_SEARCH_TOKEN = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


def _plain_markdown(value: str) -> str:
    return _MARKDOWN.sub(" ", _FENCED_CODE.sub(" ", value)).replace("\n", " ")


class SearchService:
    def __init__(self, database_path: Path, repository: ContentRepository) -> None:
        self.database_path = database_path
        self.repository = repository

    def ensure_content_index(self) -> None:
        with session.transaction(self.database_path) as connection:
            current_version = connection.execute(
                text("SELECT version FROM content_versions WHERE content_id = 'catalog'")
            ).scalar_one_or_none()
            if current_version == self.repository.content_version:
                return
            connection.execute(
                text("DELETE FROM search_documents WHERE document_type IN ('course', 'module', 'lesson')")
            )
            for course in self.repository.courses:
                connection.execute(
                    text(
                        "INSERT INTO search_documents (document_type, document_id, content) "
                        "VALUES ('course', :document_id, :content)"
                    ),
                    {"document_id": f"course:{course.document.language}", "content": course.document.title},
                )
                for module in course.modules:
                    connection.execute(
                        text(
                            "INSERT INTO search_documents (document_type, document_id, content) "
                            "VALUES ('module', :document_id, :content)"
                        ),
                        {"document_id": f"module:{module.id}", "content": module.title},
                    )
                    for lesson in module.lessons:
                        connection.execute(
                            text(
                                "INSERT INTO search_documents (document_type, document_id, content) "
                                "VALUES ('lesson', :document_id, :content)"
                            ),
                            {
                                "document_id": lesson.document.front_matter.id,
                                "content": " ".join(
                                    [
                                        lesson.document.front_matter.title,
                                        *lesson.document.front_matter.concepts,
                                        _plain_markdown(lesson.document.body),
                                    ]
                                ),
                            },
                        )
            connection.execute(
                text(
                    "INSERT INTO content_versions (content_id, version, recorded_at) "
                    "VALUES ('catalog', :version, CURRENT_TIMESTAMP) "
                    "ON CONFLICT(content_id) DO UPDATE SET version = excluded.version, "
                    "recorded_at = excluded.recorded_at"
                ),
                {"version": self.repository.content_version},
            )

    def sync_note(self, lesson_id: str, body: str | None) -> None:
        self.ensure_content_index()
        with session.transaction(self.database_path) as connection:
            connection.execute(
                text("DELETE FROM search_documents WHERE document_type = 'note' AND document_id = :document_id"),
                {"document_id": f"note:{lesson_id}"},
            )
            if body:
                connection.execute(
                    text(
                        "INSERT INTO search_documents (document_type, document_id, content) "
                        "VALUES ('note', :document_id, :content)"
                    ),
                    {"document_id": f"note:{lesson_id}", "content": body},
                )

    def sync_favorite(self, lesson_id: str, favorite: bool) -> None:
        self.ensure_content_index()
        with session.transaction(self.database_path) as connection:
            document_id = f"favorite:{lesson_id}"
            connection.execute(
                text("DELETE FROM search_documents WHERE document_type = 'favorite' AND document_id = :document_id"),
                {"document_id": document_id},
            )
            lesson = self.repository.lesson_for(lesson_id)
            if favorite and lesson is not None:
                connection.execute(
                    text(
                        "INSERT INTO search_documents (document_type, document_id, content) "
                        "VALUES ('favorite', :document_id, :content)"
                    ),
                    {"document_id": document_id, "content": lesson.document.front_matter.title},
                )

    def search(self, query: str) -> list[dict[str, str]]:
        terms = _SEARCH_TOKEN.findall(query.strip())
        if not terms:
            return []
        self.ensure_content_index()
        expression = " AND ".join(f'"{term.replace(chr(34), "")}"' for term in terms)
        with session.database_connection(self.database_path) as connection:
            rows = connection.execute(
                text(
                    "SELECT document_type, document_id, "
                    "snippet(search_documents, 2, '[', ']', '…', 12) AS snippet "
                    "FROM search_documents WHERE search_documents MATCH :expression LIMIT 50"
                ),
                {"expression": expression},
            ).mappings().all()
            if not rows and any("\u4e00" <= character <= "\u9fff" for character in query):
                rows = connection.execute(
                    text(
                        "SELECT document_type, document_id, content AS snippet FROM search_documents "
                        "WHERE content LIKE :pattern LIMIT 50"
                    ),
                    {"pattern": f"%{query.strip()}%"},
                ).mappings().all()
        return [self._result(dict(row)) for row in rows]

    def _result(self, row: dict[str, str]) -> dict[str, str]:
        document_type = row["document_type"]
        document_id = row["document_id"]
        lesson_id = document_id.split(":", 1)[-1] if ":" in document_id else document_id
        lesson = self.repository.lesson_for(lesson_id)
        if document_type == "course":
            language = document_id.removeprefix("course:")
            title = self.repository.course_for(language).document.title  # type: ignore[union-attr]
            lesson_id = ""
        elif document_type == "module":
            module_id = document_id.removeprefix("module:")
            language = module_id.split("-", 1)[0]
            title = module_id
            lesson_id = ""
        else:
            language = lesson.language if lesson else ""
            title = lesson.document.front_matter.title if lesson else ""
        return {
            "source_type": document_type,
            "language": language,
            "lesson_id": lesson_id,
            "title": title,
            "snippet": row["snippet"],
            "anchor": "#content" if lesson_id else "",
        }
