from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StrictInt, model_validator


class ContentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Concept(ContentModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ConceptsDocument(ContentModel):
    concepts: list[Concept]


class LessonEntry(ContentModel):
    id: str = Field(min_length=1)
    path: str = Field(min_length=1)


class SourceCoverageEntry(ContentModel):
    source_id: str = Field(min_length=1)
    lesson_id: str = Field(min_length=1)


class CourseModule(ContentModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    prerequisites: list[str]
    source_coverage: list[SourceCoverageEntry] = Field(min_length=1)
    lessons: list[LessonEntry]


class PlacementTest(ContentModel):
    id: str = Field(min_length=1)
    module_id: str = Field(min_length=1)
    question_ids: list[str] = Field(min_length=1)
    passing_score: Literal[85]


class GrowthConfig(ContentModel):
    review_milestone_points: StrictInt = Field(ge=0, le=1000)
    badge_points: dict[str, StrictInt] = Field(min_length=3)

    @model_validator(mode="after")
    def require_initial_badges(self) -> "GrowthConfig":
        required_badges = {"first_lesson", "first_module_mastery", "seven_day_streak"}
        if not required_badges <= self.badge_points.keys():
            raise ValueError("badge_points 缺少初始徽章代码。")
        if any(points < 0 or points > 1000 for points in self.badge_points.values()):
            raise ValueError("badge_points 必须在 0 到 1000 之间。")
        return self


class CourseDocument(ContentModel):
    language: Literal["python", "java", "csharp", "cpp"]
    title: str = Field(min_length=1)
    growth: GrowthConfig
    placement_tests: list[PlacementTest]
    modules: list[CourseModule]


class LessonFrontMatter(ContentModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    concepts: list[str]
    objectives: list[str] = Field(min_length=1)
    prerequisites: list[str]
    difficulty: Literal["beginner", "intermediate", "advanced"]
    experience_points: StrictInt = Field(ge=0, le=1000)
    code_exercise_exception_reason: str | None = Field(default=None, min_length=1)
    source_url: HttpUrl
    source_snapshot_date: date


class LessonDocument(ContentModel):
    front_matter: LessonFrontMatter
    body: str = Field(min_length=1)


class Choice(ContentModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ExecutableTestCase(ContentModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)
    stdin: str = ""
    stdout: str | None = None
    exit_code: StrictInt = 0
    assertion: Literal["stdout_nonempty"] | None = None


class PrivateQuestionData(ContentModel):
    reference_answer: str | None = None
    reference_solution: str | None = None
    hidden_tests: list[str] = Field(default_factory=list)
    visible_test_cases: list[ExecutableTestCase] = Field(default_factory=list)
    hidden_test_cases: list[ExecutableTestCase] = Field(default_factory=list)


class ExerciseQuestion(ContentModel):
    id: str = Field(min_length=1)
    type: Literal["knowledge", "code", "challenge", "scenario"]
    prompt: str = Field(min_length=1)
    choices: list[Choice] = Field(default_factory=list)
    starter_code: str | None = None
    visible_tests: list[str] = Field(default_factory=list)
    experience_points: StrictInt = Field(ge=0, le=1000)
    private: PrivateQuestionData | None = None


class ExerciseDocument(ContentModel):
    lesson_id: str = Field(min_length=1)
    questions: list[ExerciseQuestion]
