from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from hard_api.content.models import CourseDocument, ExerciseDocument, LessonDocument
from hard_api.content.parser import (
    ContentParseError,
    parse_concepts,
    parse_course,
    parse_exercises,
    parse_lesson,
    resolve_content_path,
)
from hard_api.content.validation import ContentSemanticError, LoadedLesson, validate_course_semantics


@dataclass(frozen=True, slots=True)
class IsolatedContentError:
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class LessonRecord:
    language: str
    module_id: str
    document: LessonDocument
    exercises: ExerciseDocument
    markdown_path: Path
    exercises_path: Path


@dataclass(frozen=True, slots=True)
class ModuleRecord:
    id: str
    title: str
    prerequisites: tuple[str, ...]
    lessons: tuple[LessonRecord, ...]


@dataclass(frozen=True, slots=True)
class CourseRecord:
    document: CourseDocument
    fixture_only: bool
    modules: tuple[ModuleRecord, ...]
    course_path: Path


class ContentRepositoryError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


_SAFE_MESSAGES = {
    "invalid_course": "课程文件无效。",
    "invalid_lesson": "课时文件无效。",
    "invalid_exercises": "练习文件无效。",
    "missing_lesson": "课时文件缺失。",
    "missing_exercises": "练习文件缺失。",
    "module_path_escape": "课时路径必须位于声明的模块目录。",
    "invalid_content_path": "内容路径无效。",
    "duplicate_module_id": "课程模块 ID 重复。",
    "unknown_module_prerequisite": "模块前置引用不存在。",
    "module_prerequisite_cycle": "模块前置关系存在循环。",
    "duplicate_lesson_id": "课时 ID 重复。",
    "lesson_id_mismatch": "课时与练习 ID 不一致。",
    "unknown_concept": "课时引用了未知知识点。",
    "self_lesson_prerequisite": "课时不能以前置自己。",
    "unknown_lesson_prerequisite": "课时前置引用不存在。",
    "lesson_prerequisite_cycle": "课时前置关系存在循环。",
    "duplicate_question_id": "练习题号重复。",
    "invalid_question_id": "练习题号不符合类型规则。",
    "unknown_source_coverage": "来源覆盖引用了未知课时。",
    "unknown_placement_question": "分级测试引用了未知题目。",
}


class ContentRepository:
    """A startup-only, read-only index of validated local course files."""

    def __init__(self, content_root: Path) -> None:
        self.content_root = content_root.resolve()
        self.courses: tuple[CourseRecord, ...] = ()
        self.lessons: dict[str, LessonRecord] = {}
        self.isolated_errors: tuple[IsolatedContentError, ...] = ()
        self.content_version = sha256(b"").hexdigest()
        try:
            self.concept_ids = {concept.id for concept in parse_concepts(self.content_root / "concepts.yaml").concepts}
        except ContentParseError:
            self.concept_ids = set()
        self._scan()

    def course_for(self, language: str) -> CourseRecord | None:
        return next((course for course in self.courses if course.document.language == language), None)

    def lesson_for(self, lesson_id: str) -> LessonRecord | None:
        return self.lessons.get(lesson_id)

    def _scan(self) -> None:
        courses: list[CourseRecord] = []
        errors: list[IsolatedContentError] = []
        for course_path in sorted(self.content_root.glob("*/course.yaml")):
            try:
                course = self._load_course(course_path)
            except ContentRepositoryError as error:
                errors.append(
                    IsolatedContentError(
                        path=course_path.relative_to(self.content_root).as_posix(),
                        code=error.code,
                        message=_SAFE_MESSAGES[error.code],
                    )
                )
                continue
            courses.append(course)

        lessons: dict[str, LessonRecord] = {}
        for course in courses:
            for module in course.modules:
                for lesson in module.lessons:
                    if lesson.document.front_matter.id in lessons:
                        errors.append(
                            IsolatedContentError(
                                path=course.course_path.relative_to(self.content_root).as_posix(),
                                code="invalid_course",
                                message=_SAFE_MESSAGES["invalid_course"],
                            )
                        )
                        courses.remove(course)
                        lessons = {
                            lesson_id: record
                            for lesson_id, record in lessons.items()
                            if record.language != course.document.language
                        }
                        break
                    lessons[lesson.document.front_matter.id] = lesson

        self.courses = tuple(courses)
        self.lessons = lessons
        self.isolated_errors = tuple(errors)
        self.content_version = self._version_for(courses)

    def _load_course(self, course_path: Path) -> CourseRecord:
        try:
            course = parse_course(course_path)
        except ContentParseError as error:
            raise ContentRepositoryError("invalid_course") from error

        language_root = course_path.parent.resolve()
        if course.language != language_root.name:
            raise ContentRepositoryError("invalid_course")

        module_ids = {module.id for module in course.modules}
        if len(module_ids) != len(course.modules):
            raise ContentRepositoryError("invalid_course")
        loaded_lessons: list[LoadedLesson] = []
        paths_by_lesson: dict[str, tuple[Path, Path]] = {}
        for module in course.modules:
            if not module.id.startswith(f"{course.language}-"):
                raise ContentRepositoryError("invalid_course")
            module_root = (language_root / module.id).resolve()
            for entry in module.lessons:
                if not entry.id.startswith(f"{module.id}-"):
                    raise ContentRepositoryError("invalid_course")
                try:
                    markdown_path = resolve_content_path(language_root, entry.path)
                    markdown_path.relative_to(module_root)
                except (ContentParseError, ValueError) as error:
                    raise ContentRepositoryError("module_path_escape") from error
                try:
                    lesson = parse_lesson(markdown_path)
                except ContentParseError as error:
                    raise ContentRepositoryError("invalid_lesson") from error
                if lesson.front_matter.id != entry.id:
                    raise ContentRepositoryError("invalid_lesson")
                exercises_path = markdown_path.with_suffix(".exercises.json")
                try:
                    exercises = parse_exercises(exercises_path)
                except ContentParseError as error:
                    raise ContentRepositoryError("invalid_exercises") from error
                loaded_lessons.append(LoadedLesson(module.id, entry.id, lesson, exercises))
                paths_by_lesson[entry.id] = (markdown_path, exercises_path)

        try:
            validate_course_semantics(course, loaded_lessons, concept_ids=self.concept_ids)
        except ContentSemanticError as error:
            raise ContentRepositoryError(error.code) from error

        modules: list[ModuleRecord] = []
        by_module: dict[str, list[LoadedLesson]] = {module.id: [] for module in course.modules}
        for loaded in loaded_lessons:
            by_module[loaded.module_id].append(loaded)
        for module in course.modules:
            lessons = [
                LessonRecord(
                    language=course.language,
                    module_id=module.id,
                    document=loaded.document,
                    exercises=loaded.exercises,
                    markdown_path=paths_by_lesson[loaded.entry_id][0],
                    exercises_path=paths_by_lesson[loaded.entry_id][1],
                )
                for loaded in by_module[module.id]
            ]
            modules.append(
                ModuleRecord(
                    id=module.id,
                    title=module.title,
                    prerequisites=tuple(module.prerequisites),
                    lessons=tuple(lessons),
                )
            )
        return CourseRecord(
            document=course,
            fixture_only=(language_root / ".fixture-only").is_file()
            or any((language_root / module.id / ".fixture-only").is_file() for module in modules),
            modules=tuple(modules),
            course_path=course_path.resolve(),
        )

    def _version_for(self, courses: list[CourseRecord]) -> str:
        paths: list[Path] = []
        for course in courses:
            paths.append(course.course_path)
            language_root = course.course_path.parent
            if (language_root / ".fixture-only").is_file():
                paths.append(language_root / ".fixture-only")
            for module in course.modules:
                module_marker = language_root / module.id / ".fixture-only"
                if module_marker.is_file():
                    paths.append(module_marker)
                for lesson in module.lessons:
                    paths.extend((lesson.markdown_path, lesson.exercises_path))
        digest = sha256()
        for path in sorted(paths, key=lambda item: item.relative_to(self.content_root).as_posix()):
            digest.update(path.relative_to(self.content_root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()
