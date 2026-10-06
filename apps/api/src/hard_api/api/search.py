from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from hard_api.search.service import SearchService


router = APIRouter(prefix="/api/search", tags=["search"])


class SearchResultResponse(BaseModel):
    source_type: str
    language: str
    lesson_id: str
    title: str
    snippet: str
    anchor: str


class SearchResponse(BaseModel):
    results: list[SearchResultResponse]


@router.get(
    "",
    response_model=SearchResponse,
    responses={200: {"content": {"application/json": {"schema": {"type": "object", "title": "SearchResponse", "additionalProperties": True}}}}},
)
def search(request: Request, q: str = "") -> dict[str, object]:
    service: SearchService = request.app.state.search_service
    return {"results": service.search(q)}
