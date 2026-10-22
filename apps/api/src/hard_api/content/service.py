from __future__ import annotations

from html import escape
from html.parser import HTMLParser
import re

from markdown_it import MarkdownIt

from hard_api.content.repository import ContentRepository, CourseRecord, LessonRecord
from hard_api.core.errors import ApiError


_STABLE_ID = re.compile(r"^(python|java|csharp|cpp)-[a-z0-9]+(?:-[a-z0-9]+)*$")
_DISALLOWED_URL_SCHEME = re.compile(r"(?i)(?:javascript|data|vbscript):")
_ALLOWED_HTML_TAGS = {
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
}


class _SafeHtmlRenderer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, _attrs: list[tuple[str, str | None]]) -> None:
        if tag in _ALLOWED_HTML_TAGS:
            self.parts.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in _ALLOWED_HTML_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_startendtag(self, tag: str, _attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"br", "hr"}:
            self.parts.append(f"<{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(escape(data))

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")


def render_markdown(body: str) -> str:
    rendered = MarkdownIt("commonmark", {"html": False}).render(body)
    sanitizer = _SafeHtmlRenderer()
    sanitizer.feed(rendered)
    sanitizer.close()
    return _DISALLOWED_URL_SCHEME.sub("", "".join(sanitizer.parts))


class ContentService:
    def __init__(self, repository: ContentRepository) -> None:
        self.repository = repository

    def catalog(self) -> dict[str, object]:
        return {
            "content_version": self.repository.content_version,
            "courses": [self._course_payload(course) for course in self.repository.courses],
            "isolated_errors": [
                {"path": error.path, "code": error.code, "message": error.message}
                for error in self.repository.isolated_errors
            ],
        }

    def course(self, language: str) -> dict[str, object]:
        if language not in {"python", "java", "csharp", "cpp"}:
            raise ApiError("invalid_language_id", "课程语言 ID 不合法。")
        course = self.repository.course_for(language)
        if course is None:
            raise ApiError("unknown_language", "未找到课程语言。", status_code=404)
        return {"content_version": self.repository.content_version, **self._course_payload(course)}

    def lesson(self, lesson_id: str) -> dict[str, object]:
        if not _STABLE_ID.fullmatch(lesson_id):
            raise ApiError("invalid_lesson_id", "课时 ID 不合法。")
        lesson = self.repository.lesson_for(lesson_id)
        if lesson is None:
            raise ApiError("unknown_lesson", "未找到课时。", status_code=404)
        front_matter = lesson.document.front_matter
        return {
            "id": front_matter.id,
            "title": front_matter.title,
            "language": lesson.language,
            "module_id": lesson.module_id,
            "objectives": front_matter.objectives,
            "concepts": front_matter.concepts,
            "difficulty": front_matter.difficulty,
            "experience_points": front_matter.experience_points,
            "rendered_html": render_markdown(lesson.document.body),
            "source_url": str(front_matter.source_url),
            "source_snapshot_date": front_matter.source_snapshot_date.isoformat(),
            "content_version": self.repository.content_version,
            "exercises": [self._exercise_payload(question) for question in lesson.exercises.questions],
        }

    def comparison(self) -> dict[str, object]:
        return {
            "content_version": self.repository.content_version,
            "concepts": list(self.repository.comparison_concepts),
        }

    def _course_payload(self, course: CourseRecord) -> dict[str, object]:
        return {
            "language": course.document.language,
            "title": course.document.title,
            "fixture_only": course.fixture_only,
            "modules": [
                {
                    "id": module.id,
                    "title": module.title,
                    "prerequisites": list(module.prerequisites),
                    "lessons": [
                        {"id": lesson.document.front_matter.id, "title": lesson.document.front_matter.title}
                        for lesson in module.lessons
                    ],
                }
                for module in course.modules
            ],
        }

    @staticmethod
    def _exercise_payload(question: object) -> dict[str, object]:
        return {
            "id": question.id,
            "type": question.type,
            "prompt": question.prompt,
            "choices": [choice.model_dump(mode="json") for choice in question.choices],
            "starter_code": question.starter_code,
            "visible_tests": question.visible_tests,
            "experience_points": question.experience_points,
        }
