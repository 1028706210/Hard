from __future__ import annotations

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, Field

from hard_api.core.errors import ApiError
from hard_api.learning.progress import validate_idempotency_key
from hard_api.runners.contracts import ExecutableTestCase, Submission


router = APIRouter(prefix="/api/runners", tags=["runners"])


class RunnerSubmissionRequest(BaseModel):
    lesson_id: str = Field(min_length=1, max_length=160)
    exercise_id: str = Field(min_length=1, max_length=192)
    source_code: str
    stdin: str = ""


class PublicCompileResult(BaseModel):
    passed: bool


class PublicTestResult(BaseModel):
    visible_passed: int
    visible_total: int


class PublicRunResult(BaseModel):
    status: str
    compile: PublicCompileResult | None = None
    tests: PublicTestResult | None = None
    diagnostics: list[str]


class RunnerJobResponse(BaseModel):
    id: str
    status: str
    result: PublicRunResult | None


def _job_payload(request: Request, job_id: str) -> dict[str, object]:
    job = request.app.state.runner_manager.get(job_id)
    if job is None:
        raise ApiError("unknown_runner_job", "未找到运行任务。", status_code=404)
    return job.public_payload()


@router.post("/submissions", response_model=RunnerJobResponse)
def submit(
    payload: RunnerSubmissionRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    key = validate_idempotency_key(idempotency_key)
    lesson = request.app.state.content_service.repository.lesson_for(payload.lesson_id)
    if lesson is None:
        raise ApiError("unknown_lesson", "未找到课时。", status_code=404)
    question = next((item for item in lesson.exercises.questions if item.id == payload.exercise_id), None)
    if question is None:
        raise ApiError("unknown_exercise", "未找到练习题。", status_code=404)
    if question.type not in {"code", "challenge"}:
        raise ApiError("invalid_runner_exercise", "该练习不支持代码运行。")
    job = request.app.state.runner_manager.submit(
        Submission(
            language=lesson.language,
            files={"main.py": payload.source_code},
            stdin=payload.stdin,
            visible_tests=tuple(question.visible_tests),
            hidden_tests=tuple(question.private.hidden_tests if question.private is not None else ()),
            visible_test_cases=tuple(ExecutableTestCase(**item.model_dump()) for item in (question.private.visible_test_cases if question.private else ())),
            hidden_test_cases=tuple(ExecutableTestCase(**item.model_dump()) for item in (question.private.hidden_test_cases if question.private else ())),
            idempotency_key=key,
            lesson_id=payload.lesson_id,
            exercise_id=payload.exercise_id,
        )
    )
    return job.public_payload()


@router.get("/jobs/{job_id}", response_model=RunnerJobResponse)
def status(job_id: str, request: Request) -> dict[str, object]:
    return _job_payload(request, job_id)


@router.delete("/jobs/{job_id}", response_model=RunnerJobResponse)
def cancel(job_id: str, request: Request) -> dict[str, object]:
    job = request.app.state.runner_manager.cancel(job_id)
    if job is None:
        raise ApiError("unknown_runner_job", "未找到运行任务。", status_code=404)
    return job.public_payload()
