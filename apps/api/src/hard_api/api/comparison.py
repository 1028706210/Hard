from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from hard_api.content.service import ContentService


router = APIRouter(prefix="/api/compare", tags=["compare"])


class CompareSlotResponse(BaseModel):
    status: Literal["available", "missing"]
    summary: str
    difference: str
    code: str | None
    lesson_id: str | None
    lesson_title: str | None
    note: str | None


class CompareConceptResponse(BaseModel):
    id: str
    name: str
    description: str
    slots: dict[str, CompareSlotResponse]


class ComparisonResponse(BaseModel):
    content_version: str
    concepts: list[CompareConceptResponse]


def _content_service(request: Request) -> ContentService:
    return request.app.state.content_service


@router.get(
    "/concepts",
    response_model=ComparisonResponse,
    responses={200: {"content": {"application/json": {"schema": {"type": "object", "title": "ComparisonResponse", "additionalProperties": True}}}}},
)
def concepts(request: Request) -> dict[str, object]:
    return _content_service(request).comparison()
