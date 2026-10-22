from __future__ import annotations

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, Field

from hard_api.content.service import ContentService
from hard_api.learning import goals, notes, progress, unlocking
from hard_api.search.service import SearchService


router = APIRouter(prefix="/api/progress", tags=["progress"])


def _response(title: str) -> dict[int, dict[str, object]]:
    return {200: {"content": {"application/json": {"schema": {"type": "object", "title": title, "additionalProperties": True}}}}}


class ProgressUpdateRequest(BaseModel):
    position: int = Field(ge=0)
    time_spent_seconds: int = Field(ge=0)


class ProgressResponse(BaseModel):
    lesson_id: str
    position: int
    time_spent_seconds: int
    status: str
    updated_at: str


class DailyGoalRequest(BaseModel):
    target_minutes: int = Field(ge=0)
    target_exercises: int = Field(ge=0)


class DailyGoalResponse(BaseModel):
    date: str
    configured: bool
    target_minutes: int
    target_exercises: int


class NoteRequest(BaseModel):
    body: str


class NoteResponse(BaseModel):
    lesson_id: str
    body: str
    updated_at: str


class FavoriteResponse(BaseModel):
    lesson_id: str
    favorite: bool


class DeleteResponse(BaseModel):
    lesson_id: str
    deleted: bool


class DailyGoalSummaryResponse(BaseModel):
    date: str
    configured: bool
    target_minutes: int
    target_exercises: int
    studied_seconds: int
    completed_exercises: int
    completion_ratio: float
    achieved: bool


class SummaryResponse(BaseModel):
    daily_goal: DailyGoalSummaryResponse
    streak_days: int
    continue_learning: dict[str, object] | None
    due_review_count: int
    current_experience: int
    current_level: int
    unlocked_lessons: dict[str, list[str]]
    lesson_statuses: dict[str, str]


def _content(request: Request) -> ContentService:
    return request.app.state.content_service


def _search(request: Request) -> SearchService:
    return request.app.state.search_service


def _lesson(request: Request, lesson_id: str) -> dict[str, object]:
    return _content(request).lesson(lesson_id)


@router.patch("/lessons/{lesson_id}", response_model=ProgressResponse, responses=_response("ProgressResponse"))
def update_lesson(
    lesson_id: str,
    payload: ProgressUpdateRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    lesson = _lesson(request, lesson_id)
    return progress.update_lesson_progress(
        request.app.state.settings.database_path,
        course_id=str(lesson["language"]),
        module_id=str(lesson["module_id"]),
        lesson_id=lesson_id,
        position=payload.position,
        time_spent_seconds=payload.time_spent_seconds,
        idempotency_key=idempotency_key,
        repository=_content(request).repository,
    )


@router.put("/daily-goal", response_model=DailyGoalResponse, responses=_response("DailyGoalResponse"))
def update_daily_goal(
    payload: DailyGoalRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    return goals.set_daily_goal(
        request.app.state.settings.database_path,
        target_minutes=payload.target_minutes,
        target_exercises=payload.target_exercises,
        idempotency_key=idempotency_key,
    )


@router.get("/summary", response_model=SummaryResponse, responses=_response("SummaryResponse"))
def summary(request: Request) -> dict[str, object]:
    repository = _content(request).repository
    result = progress.learning_summary(request.app.state.settings.database_path)
    result["unlocked_lessons"] = {
        course.document.language: unlocking.unlocked_lessons(
            repository, request.app.state.settings.database_path, course.document.language
        )
        for course in repository.courses
    }
    return result


@router.put("/notes/{lesson_id}", response_model=NoteResponse, responses=_response("NoteResponse"))
def put_note(
    lesson_id: str,
    payload: NoteRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    _lesson(request, lesson_id)
    response = notes.save_note(
        request.app.state.settings.database_path,
        lesson_id=lesson_id,
        body=payload.body,
        idempotency_key=idempotency_key,
    )
    _search(request).sync_note(lesson_id, str(response["body"]))
    return response


@router.delete("/notes/{lesson_id}", response_model=DeleteResponse, responses=_response("DeleteNoteResponse"))
def remove_note(
    lesson_id: str,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    _lesson(request, lesson_id)
    response = notes.delete_note(
        request.app.state.settings.database_path, lesson_id=lesson_id, idempotency_key=idempotency_key
    )
    _search(request).sync_note(lesson_id, None)
    return response


@router.put("/favorites/{lesson_id}", response_model=FavoriteResponse, responses=_response("FavoriteResponse"))
def put_favorite(
    lesson_id: str,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    _lesson(request, lesson_id)
    response = notes.save_favorite(
        request.app.state.settings.database_path, lesson_id=lesson_id, idempotency_key=idempotency_key
    )
    _search(request).sync_favorite(lesson_id, True)
    return response


@router.delete("/favorites/{lesson_id}", response_model=FavoriteResponse, responses=_response("DeleteFavoriteResponse"))
def remove_favorite(
    lesson_id: str,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    _lesson(request, lesson_id)
    response = notes.delete_favorite(
        request.app.state.settings.database_path, lesson_id=lesson_id, idempotency_key=idempotency_key
    )
    _search(request).sync_favorite(lesson_id, False)
    return response
