from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, Field

from hard_api.learning import review


router = APIRouter(prefix="/api/review", tags=["review"])


def _response(title: str) -> dict[int, dict[str, object]]:
    return {200: {"content": {"application/json": {"schema": {"type": "object", "title": title, "additionalProperties": True}}}}}


class ReviewScoreRequest(BaseModel):
    score: Decimal = Field(ge=0, le=100)


class ReviewItemResponse(BaseModel):
    id: int
    concept_id: str
    lesson_id: str | None
    exercise_id: str | None
    due_on: str
    interval_days: int
    last_score: float | None


class ReviewQueueResponse(BaseModel):
    items: list[ReviewItemResponse]


class ReviewScoreResponse(BaseModel):
    id: int
    score: float
    interval_days: int
    due_on: str
    experience_candidate: bool


@router.get("/queue", response_model=ReviewQueueResponse, responses=_response("ReviewQueueResponse"))
def queue(request: Request) -> dict[str, object]:
    return {"items": review.due_review_items(request.app.state.settings.database_path)}


@router.post("/items/{review_item_id}", response_model=ReviewScoreResponse, responses=_response("ReviewScoreResponse"))
def score_item(
    review_item_id: int,
    payload: ReviewScoreRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    return review.score_review(
        request.app.state.settings.database_path,
        repository=request.app.state.content_service.repository,
        review_item_id=review_item_id,
        score=payload.score,
        idempotency_key=idempotency_key,
    )
