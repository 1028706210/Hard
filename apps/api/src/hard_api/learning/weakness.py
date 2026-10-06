from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
import json
from pathlib import Path

from sqlalchemy import text

from hard_api.content.repository import ContentRepository
from hard_api.db import session


def weaknesses(
    database_path: Path, *, repository: ContentRepository, today: date | None = None
) -> list[dict[str, object]]:
    current_day = today or date.today()
    cutoff = datetime.combine(current_day - timedelta(days=30), datetime.min.time())
    scores: dict[str, int] = defaultdict(int)
    latest: dict[str, str] = {}
    links: dict[str, tuple[str, str]] = {}
    with session.database_connection(database_path) as connection:
        attempts = connection.execute(
            text(
                "SELECT lesson_id, exercise_id, hint_level, raw_score, normalized_result, created_at "
                "FROM attempts WHERE created_at >= :cutoff"
            ),
            {"cutoff": cutoff},
        ).mappings().all()
        review_items = connection.execute(
            text(
                "SELECT concept_id, lesson_id, exercise_id, due_on, updated_at FROM review_items "
                "WHERE status = 'scheduled' AND due_on < :today"
            ),
            {"today": current_day.isoformat()},
        ).mappings().all()
    for attempt in attempts:
        lesson = repository.lesson_for(str(attempt["lesson_id"]))
        if lesson is None:
            continue
        normalized = json.loads(attempt["normalized_result"]) if attempt["normalized_result"] else {}
        hidden_failures = min(max(0, int(normalized.get("hidden_test_failures", 0))) * 2, 6)
        for concept_id in lesson.document.front_matter.concepts:
            if float(attempt["raw_score"] or 0) < 100:
                scores[concept_id] += 4
            scores[concept_id] += {"light": 1, "strong": 2, "revealed": 4}.get(str(attempt["hint_level"]), 0)
            if normalized.get("compile_error_category"):
                scores[concept_id] += 2
            scores[concept_id] += hidden_failures
            latest[concept_id] = max(latest.get(concept_id, ""), str(attempt["created_at"]))
            links[concept_id] = (lesson.document.front_matter.id, str(attempt["exercise_id"] or ""))
    for review in review_items:
        lesson = repository.lesson_for(str(review["lesson_id"]))
        if lesson is None:
            continue
        overdue = min(7, max(0, (current_day - date.fromisoformat(str(review["due_on"]))).days))
        concept_id = str(review["concept_id"])
        scores[concept_id] += overdue
        latest[concept_id] = max(latest.get(concept_id, ""), str(review["updated_at"]))
        links[concept_id] = (lesson.document.front_matter.id, str(review["exercise_id"] or ""))
    ranked = [(concept_id, score) for concept_id, score in scores.items() if concept_id in links]
    ranked.sort(key=lambda item: item[0])
    ranked.sort(key=lambda item: latest.get(item[0], ""), reverse=True)
    ranked.sort(key=lambda item: item[1], reverse=True)
    return [
        {
            "concept_id": concept_id,
            "score": score,
            "lesson_id": links[concept_id][0],
            "exercise_id": links[concept_id][1],
        }
        for concept_id, score in ranked
    ]
