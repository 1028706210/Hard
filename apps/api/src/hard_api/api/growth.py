from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from hard_api.learning import experience, history, weakness


router = APIRouter(prefix="/api/growth", tags=["growth"])


def _response(title: str) -> dict[int, dict[str, object]]:
    return {200: {"content": {"application/json": {"schema": {"type": "object", "title": title, "additionalProperties": True}}}}}


class GrowthSummaryResponse(BaseModel):
    total_experience: int
    level: int
    current_level_progress: int
    next_level_remaining: int
    streak_days: int
    badges: list[str]
    mastery: list[dict[str, object]]
    new_badges: list[str]
    route_completion: list[dict[str, object]]


class WeaknessResponse(BaseModel):
    concept_id: str
    score: int
    lesson_id: str
    exercise_id: str


class WeaknessListResponse(BaseModel):
    items: list[WeaknessResponse]


class HistoryRecordResponse(BaseModel):
    id: str
    exercise_id: str
    language: str | None
    source_code: str
    normalized_result: dict[str, object]
    score: float
    duration_ms: int | None
    created_at: str
    diff: str


class HistoryResponse(BaseModel):
    items: list[HistoryRecordResponse]


@router.get("/summary", response_model=GrowthSummaryResponse, responses=_response("GrowthSummaryResponse"))
def summary(request: Request) -> dict[str, object]:
    return experience.growth_summary(
        request.app.state.settings.database_path, repository=request.app.state.content_service.repository
    )


@router.get("/weaknesses", response_model=WeaknessListResponse, responses=_response("WeaknessListResponse"))
def weaknesses(request: Request) -> dict[str, object]:
    return {
        "items": weakness.weaknesses(
            request.app.state.settings.database_path, repository=request.app.state.content_service.repository
        )
    }


@router.get("/history", response_model=HistoryResponse, responses=_response("HistoryResponse"))
def history_records(request: Request, exercise_id: str | None = None) -> dict[str, object]:
    return {"items": history.code_history(request.app.state.settings.database_path, exercise_id)}
