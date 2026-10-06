from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from hard_api.content.service import ContentService


router = APIRouter(prefix="/api/content", tags=["content"])


class PublicChoiceResponse(BaseModel):
    id: str
    text: str


class PublicExerciseResponse(BaseModel):
    id: str
    type: Literal["knowledge", "code", "challenge", "scenario"]
    prompt: str
    choices: list[PublicChoiceResponse]
    starter_code: str | None
    visible_tests: list[str]
    experience_points: int


class CatalogLessonResponse(BaseModel):
    id: str
    title: str


class CatalogModuleResponse(BaseModel):
    id: str
    title: str
    prerequisites: list[str]
    lessons: list[CatalogLessonResponse]


class CourseResponse(BaseModel):
    content_version: str
    language: str
    title: str
    fixture_only: bool
    modules: list[CatalogModuleResponse]


class CatalogCourseResponse(BaseModel):
    language: str
    title: str
    fixture_only: bool
    modules: list[CatalogModuleResponse]


class IsolatedContentErrorResponse(BaseModel):
    path: str
    code: str
    message: str


class CatalogResponse(BaseModel):
    content_version: str
    courses: list[CatalogCourseResponse]
    isolated_errors: list[IsolatedContentErrorResponse]


class LessonResponse(BaseModel):
    id: str
    title: str
    language: str
    module_id: str
    objectives: list[str]
    concepts: list[str]
    difficulty: str
    experience_points: int
    rendered_html: str
    source_url: str
    source_snapshot_date: str
    content_version: str
    exercises: list[PublicExerciseResponse]


def _content_service(request: Request) -> ContentService:
    return request.app.state.content_service


@router.get(
    "/catalog",
    response_model=CatalogResponse,
    responses={200: {"content": {"application/json": {"schema": {"type": "object", "title": "CatalogResponse", "additionalProperties": True}}}}},
)
def catalog(request: Request) -> dict[str, object]:
    return _content_service(request).catalog()


@router.get(
    "/courses/{language}",
    response_model=CourseResponse,
    responses={200: {"content": {"application/json": {"schema": {"type": "object", "title": "CourseResponse", "additionalProperties": True}}}}},
)
def course(language: str, request: Request) -> dict[str, object]:
    return _content_service(request).course(language)


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonResponse,
    responses={200: {"content": {"application/json": {"schema": {"type": "object", "title": "LessonResponse", "additionalProperties": True}}}}},
)
def lesson(lesson_id: str, request: Request) -> dict[str, object]:
    return _content_service(request).lesson(lesson_id)
