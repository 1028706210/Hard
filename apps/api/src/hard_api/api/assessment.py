from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, ConfigDict, Field

from hard_api.core.errors import ApiError
from hard_api.learning import scoring, unlocking
from hard_api.runners.contracts import RunStatus


router = APIRouter(prefix="/api/assessment", tags=["assessment"])


def _response(title: str) -> dict[int, dict[str, object]]:
    return {200: {"content": {"application/json": {"schema": {"type": "object", "title": title, "additionalProperties": True}}}}}


class AttemptRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    lesson_id: str
    exercise_id: str
    answer: str | None = None
    runner_job_id: str | None = None
    hint_level: Literal["none", "light", "strong", "revealed"]


class AttemptResponse(BaseModel):
    attempt_id: str
    question_score: float
    category_scores: dict[str, float]
    total_score: float
    passed: bool
    mastery: str
    newly_unlocked: list[str]
    experience_candidate: bool
    review_status: str


class PlacementRequest(BaseModel):
    language: str
    module_id: str
    score: Decimal = Field(ge=0, le=100)


class PlacementResponse(BaseModel):
    module_id: str
    score: float
    validated: bool
    experience_candidate: bool


def _trusted_runner_result(request: Request, payload: AttemptRequest) -> dict[str, object]:
    if not payload.runner_job_id:
        raise ApiError("runner_result_required", "代码题必须使用已完成的服务端运行结果。")
    job = request.app.state.runner_manager.get(payload.runner_job_id)
    if job is None or job.submission is None:
        raise ApiError("unknown_runner_job", "未找到运行任务。", status_code=404)
    if job.submission.lesson_id != payload.lesson_id or job.submission.exercise_id != payload.exercise_id:
        raise ApiError("runner_job_mismatch", "运行任务与当前练习不匹配。")
    result = job.result
    if result is None or result.status not in {RunStatus.SUCCEEDED, RunStatus.FAILED}:
        raise ApiError("runner_result_not_ready", "运行结果尚不可用于评分。")

    tests = result.tests
    visible_passed = tests.visible_passed if tests is not None else 0
    visible_total = tests.visible_total if tests is not None else 0
    hidden_total = tests.hidden_total if tests is not None else 0
    hidden_failures = hidden_total - tests.hidden_passed if tests is not None else 0
    total = visible_total + hidden_total
    passed = visible_passed + (tests.hidden_passed if tests is not None else 0)
    score = (
        (Decimal(passed) * Decimal("100") / Decimal(total)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        if total
        else Decimal("0")
    )
    normalized: dict[str, object] = {
        "score": float(score),
        "passed": result.status == RunStatus.SUCCEEDED,
        "visible_tests_passed": visible_passed,
        "visible_tests_total": visible_total,
        "hidden_test_failures": hidden_failures,
        "source_code": job.submission.files.get("main.py", ""),
        "language": job.submission.language,
        "duration_ms": result.duration_ms,
    }
    if result.error_code == "compile_failed":
        normalized["compile_error_category"] = "compile_failed"
    return normalized


@router.post("/attempts", response_model=AttemptResponse, responses=_response("AttemptResponse"))
def attempt(
    payload: AttemptRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    lesson = request.app.state.content_service.repository.lesson_for(payload.lesson_id)
    question = next((item for item in lesson.exercises.questions if item.id == payload.exercise_id), None) if lesson else None
    normalized_result = None
    if question is not None and question.type in {"code", "challenge"}:
        client_result = (payload.model_extra or {}).get("normalized_result")
        if client_result is not None:
            if not isinstance(client_result, dict):
                raise ApiError("invalid_normalized_result", "规范化评分结果不合法。")
            scoring._stored_normalized_result(client_result, requires_score=True)
        normalized_result = _trusted_runner_result(request, payload)
    return scoring.record_attempt(
        request.app.state.settings.database_path,
        repository=request.app.state.content_service.repository,
        lesson_id=payload.lesson_id,
        exercise_id=payload.exercise_id,
        answer=payload.answer,
        normalized_result=normalized_result,
        hint_level=payload.hint_level,
        idempotency_key=idempotency_key,
    )


@router.post("/placement", response_model=PlacementResponse, responses=_response("PlacementResponse"))
def placement(
    payload: PlacementRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    return unlocking.record_placement(
        request.app.state.settings.database_path,
        repository=request.app.state.content_service.repository,
        language=payload.language,
        module_id=payload.module_id,
        score=payload.score,
        idempotency_key=idempotency_key,
    )
