from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from hard_api.content.repository import ContentRepository, LessonRecord
from hard_api.core.errors import ApiError
from hard_api.learning import achievements, unlocking
from hard_api.learning.experience import award_experience
from hard_api.learning.mastery import lesson_passed, mastered, record_aggregate_mastery
from hard_api.learning.progress import perform_idempotent
from hard_api.learning.history import public_normalized_result


WEIGHTS = {
    "knowledge": Decimal("30"),
    "code": Decimal("40"),
    "challenge": Decimal("20"),
    "scenario": Decimal("10"),
}
HINT_MULTIPLIERS = {
    "none": Decimal("1.00"),
    "light": Decimal("0.85"),
    "strong": Decimal("0.60"),
    "revealed": Decimal("0"),
}
_STORED_NORMALIZED_FIELDS = {
    "score",
    "passed",
    "compile_error_category",
    "visible_tests_passed",
    "visible_tests_total",
    "hidden_test_failures",
}
_MAX_COMPILE_ERROR_CATEGORY_LENGTH = 128


def apply_hint_penalty(raw_score: Decimal, hint_level: str) -> Decimal:
    if hint_level not in HINT_MULTIPLIERS:
        raise ApiError("invalid_hint_level", "提示级别不合法。")
    return (raw_score * HINT_MULTIPLIERS[hint_level]).quantize(Decimal("0.01"), ROUND_HALF_UP)


def weighted_score(questions: list[object], highest_scores: dict[str, Decimal]) -> tuple[Decimal, dict[str, Decimal]]:
    category_scores: dict[str, Decimal] = {}
    total = Decimal("0")
    for question_type, weight in WEIGHTS.items():
        required = [question for question in questions if question.type == question_type]
        if not required:
            category_scores[question_type] = Decimal("0")
            continue
        average = sum((highest_scores.get(question.id, Decimal("0")) for question in required), Decimal("0")) / len(required)
        category_scores[question_type] = average.quantize(Decimal("0.01"), ROUND_HALF_UP)
        total += (average / Decimal("100")) * weight
    return total.quantize(Decimal("0.01"), ROUND_HALF_UP), category_scores


def _question(lesson: LessonRecord, exercise_id: str):
    question = next((candidate for candidate in lesson.exercises.questions if candidate.id == exercise_id), None)
    if question is None:
        raise ApiError("unknown_exercise", "未找到练习题。", status_code=404)
    return question


def _invalid_normalized_result() -> ApiError:
    return ApiError("invalid_normalized_result", "规范化评分结果不合法。")


def _stored_normalized_result(
    value: dict[str, object] | None, *, requires_score: bool
) -> dict[str, object] | None:
    if value is None:
        if requires_score:
            raise ApiError("missing_normalized_result", "代码题必须提供受信的规范化评分结果。")
        return None

    result: dict[str, object] = {}
    if "score" in value:
        score = value["score"]
        if isinstance(score, bool) or not isinstance(score, (int, float, Decimal)):
            raise _invalid_normalized_result()
        try:
            decimal_score = Decimal(str(score))
        except Exception as error:
            raise _invalid_normalized_result() from error
        if not decimal_score.is_finite() or decimal_score < 0 or decimal_score > 100:
            raise _invalid_normalized_result()
        result["score"] = float(decimal_score.quantize(Decimal("0.01"), ROUND_HALF_UP))
    elif requires_score:
        raise ApiError("missing_normalized_result", "代码题必须提供受信的规范化评分结果。")

    if "passed" in value:
        if not isinstance(value["passed"], bool):
            raise _invalid_normalized_result()
        result["passed"] = value["passed"]

    for field in ("visible_tests_passed", "visible_tests_total", "hidden_test_failures"):
        if field not in value:
            continue
        count = value[field]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise _invalid_normalized_result()
        result[field] = count

    if "compile_error_category" in value:
        category = value["compile_error_category"]
        if (
            not isinstance(category, str)
            or not category
            or len(category) > _MAX_COMPILE_ERROR_CATEGORY_LENGTH
            or any(ord(character) < 32 for character in category)
        ):
            raise _invalid_normalized_result()
        result["compile_error_category"] = category

    return {field: result[field] for field in _STORED_NORMALIZED_FIELDS if field in result}


def _submission_values(value: dict[str, object] | None, default_language: str) -> dict[str, object]:
    result = value or {}
    return {
        "source_code": str(result.get("source_code", "")),
        "language": str(result.get("language", default_language)),
        "duration_ms": int(result.get("duration_ms", 0)),
    }


def _raw_score(question: object, answer: str | None, normalized_result: dict[str, object] | None) -> Decimal:
    if question.type in {"knowledge", "scenario"}:
        reference_answer = question.private.reference_answer if question.private is not None else None
        return Decimal("100") if answer is not None and answer == reference_answer else Decimal("0")
    if normalized_result is None or "score" not in normalized_result:
        raise ApiError("missing_normalized_result", "代码题必须提供受信的规范化评分结果。")
    result = Decimal(str(normalized_result["score"]))
    return result.quantize(Decimal("0.01"), ROUND_HALF_UP)


def _highest_scores(connection: Connection, lesson: LessonRecord) -> dict[str, Decimal]:
    rows = connection.execute(
        text(
            "SELECT exercise_id, MAX(final_score) AS final_score FROM attempts "
            "WHERE lesson_id = :lesson_id AND placement = 0 GROUP BY exercise_id"
        ),
        {"lesson_id": lesson.document.front_matter.id},
    ).mappings().all()
    return {str(row["exercise_id"]): Decimal(str(row["final_score"])) for row in rows if row["final_score"] is not None}


def record_attempt(
    database_path: Path,
    *,
    repository: ContentRepository,
    lesson_id: str,
    exercise_id: str,
    answer: str | None,
    normalized_result: dict[str, object] | None,
    hint_level: str,
    idempotency_key: str | None,
    today: date | None = None,
) -> dict[str, object]:
    lesson = repository.lesson_for(lesson_id)
    if lesson is None:
        raise ApiError("unknown_lesson", "未找到课时。", status_code=404)
    question = _question(lesson, exercise_id)
    stored_result = _stored_normalized_result(
        normalized_result, requires_score=question.type in {"code", "challenge"}
    )
    submission_values = (
        _submission_values(normalized_result, lesson.language)
        if question.type in {"code", "challenge"}
        else None
    )
    raw_score = _raw_score(question, answer, stored_result)
    final_score = apply_hint_penalty(raw_score, hint_level)
    payload = {
        "lesson_id": lesson_id,
        "exercise_id": exercise_id,
        "answer": answer,
        "normalized_result": stored_result,
        "submission": submission_values,
        "hint_level": hint_level,
    }

    def action(connection: Connection) -> dict[str, object]:
        now = datetime.now()
        current_day = today or date.today()
        unlocked_before = set(unlocking.unlocked_lessons_for_connection(repository, connection, lesson.language))
        highest_scores = _highest_scores(connection, lesson)
        highest_scores[exercise_id] = max(highest_scores.get(exercise_id, Decimal("0")), final_score)
        total_score, category_scores = weighted_score(list(lesson.exercises.questions), highest_scores)
        passed = lesson_passed(total_score)
        progress_status = connection.execute(
            text("SELECT status FROM lesson_progress WHERE lesson_id = :lesson_id"),
            {"lesson_id": lesson_id},
        ).scalar_one_or_none()
        status = "validated" if progress_status == "validated" else ("completed" if passed else "in_progress")
        attempt_id = str(uuid4())
        connection.execute(
            text(
                "INSERT INTO attempts "
                "(id, lesson_id, score, exercise_id, question_type, hint_level, raw_score, final_score, "
                "passed, placement, idempotency_key, normalized_result, created_at) "
                "VALUES (:id, :lesson_id, :score, :exercise_id, :question_type, :hint_level, :raw_score, "
                ":final_score, :passed, 0, :idempotency_key, :normalized_result, :created_at)"
            ),
            {
                "id": attempt_id,
                "lesson_id": lesson_id,
                "score": float(final_score),
                "exercise_id": exercise_id,
                "question_type": question.type,
                "hint_level": hint_level,
                "raw_score": float(raw_score),
                "final_score": float(final_score),
                "passed": passed,
                "idempotency_key": idempotency_key,
                "normalized_result": json.dumps(stored_result, ensure_ascii=False) if stored_result else None,
                "created_at": now,
            },
        )
        if question.type in {"code", "challenge"}:
            connection.execute(
                text(
                    "INSERT INTO submissions "
                    "(id, attempt_id, source_code, language, normalized_result, duration_ms, created_at) "
                    "VALUES (:id, :attempt_id, :source_code, :language, :normalized_result, :duration_ms, :created_at)"
                ),
                {
                    "id": str(uuid4()),
                    "attempt_id": attempt_id,
                    "source_code": submission_values["source_code"],
                    "language": submission_values["language"],
                    "normalized_result": json.dumps(public_normalized_result(stored_result), ensure_ascii=False),
                    "duration_ms": submission_values["duration_ms"],
                    "created_at": now,
                },
            )
        connection.execute(
            text(
                "INSERT INTO mastery_snapshots (course_id, scope_type, scope_id, status, score, recorded_at) "
                "VALUES (:course_id, 'lesson', :scope_id, :status, :score, :recorded_at)"
            ),
            {"course_id": lesson.language, "scope_id": lesson_id, "status": status, "score": float(total_score), "recorded_at": now},
        )
        connection.execute(
            text(
                "INSERT INTO lesson_progress "
                "(lesson_id, course_id, module_id, position, time_spent_seconds, status, updated_at, completed_at) "
                "VALUES (:lesson_id, :course_id, :module_id, 0, 0, :status, :updated_at, :completed_at) "
                "ON CONFLICT(lesson_id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at, "
                "completed_at = CASE WHEN excluded.status = 'completed' THEN excluded.completed_at ELSE lesson_progress.completed_at END"
            ),
            {
                "lesson_id": lesson_id,
                "course_id": lesson.language,
                "module_id": lesson.module_id,
                "status": status,
                "updated_at": now,
                "completed_at": now if status == "completed" else None,
            },
        )
        review_status = "none"
        if final_score < Decimal("70"):
            review_status = "wrong_answer"
            concept_id = lesson.document.front_matter.concepts[0] if lesson.document.front_matter.concepts else ""
            connection.execute(
                text(
                    "INSERT INTO review_items "
                    "(concept_id, lesson_id, exercise_id, due_on, interval_days, last_score, status, updated_at) "
                    "VALUES (:concept_id, :lesson_id, :exercise_id, :due_on, 1, :last_score, 'wrong_answer', :updated_at) "
                    "ON CONFLICT(lesson_id, exercise_id) WHERE status IN ('wrong_answer', 'scheduled') DO UPDATE SET "
                    "last_score = excluded.last_score, due_on = excluded.due_on, status = 'wrong_answer', updated_at = excluded.updated_at"
                ),
                {
                    "concept_id": concept_id,
                    "lesson_id": lesson_id,
                    "exercise_id": exercise_id,
                    "due_on": current_day.isoformat(),
                    "last_score": float(final_score),
                    "updated_at": now,
                },
            )
        aggregate_scores = record_aggregate_mastery(
            connection, repository=repository, language=lesson.language, recorded_at=now
        )
        unlocked_after = set(unlocking.unlocked_lessons_for_connection(repository, connection, lesson.language))
        experience_candidate = False
        if final_score >= Decimal("70") and status != "validated":
            event_type = "challenge_completed" if question.type == "challenge" else "exercise_completed"
            exercise_event = award_experience(
                connection,
                event_key=f"{event_type}:{lesson.language}:{lesson_id}:{exercise_id}",
                event_type=event_type,
                course_id=lesson.language,
                lesson_id=lesson_id,
                exercise_id=exercise_id,
                points=int(question.experience_points),
            )
            experience_candidate = exercise_event
            if exercise_event:
                connection.execute(
                    text(
                        "INSERT INTO learning_activity_days "
                        "(activity_date, time_spent_seconds, completed_exercises, updated_at) "
                        "VALUES (:activity_date, 0, 1, :updated_at) "
                        "ON CONFLICT(activity_date) DO UPDATE SET "
                        "completed_exercises = learning_activity_days.completed_exercises + 1, "
                        "updated_at = excluded.updated_at"
                    ),
                    {"activity_date": current_day.isoformat(), "updated_at": now},
                )
        if passed and status == "completed":
            lesson_event = award_experience(
                connection,
                event_key=f"lesson_completed:{lesson.language}:{lesson_id}",
                event_type="lesson_completed",
                course_id=lesson.language,
                lesson_id=lesson_id,
                points=int(lesson.document.front_matter.experience_points),
            )
            experience_candidate = lesson_event or experience_candidate
            if lesson_event:
                experience_candidate = achievements.grant_badge(
                    connection, repository, lesson.language, "first_lesson"
                ) or experience_candidate
        module_score = aggregate_scores.get(lesson.module_id, Decimal("0"))
        if mastered(module_score):
            experience_candidate = achievements.grant_badge(
                connection, repository, lesson.language, "first_module_mastery"
            ) or experience_candidate
        return {
            "attempt_id": attempt_id,
            "question_score": float(final_score),
            "category_scores": {category: float(score) for category, score in category_scores.items()},
            "total_score": float(total_score),
            "passed": passed,
            "mastery": "passed" if passed else "in_progress",
            "newly_unlocked": sorted(unlocked_after - unlocked_before),
            "experience_candidate": experience_candidate,
            "review_status": review_status,
        }

    return perform_idempotent(
        database_path,
        operation="assessment.attempt",
        idempotency_key=idempotency_key,
        payload={**payload, "today": (today or date.today()).isoformat()},
        action=action,
    )
