from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from dataclasses import replace
import json
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content"))

from test_catalog import make_settings, write_python_fixture
from test_progress import FixtureRunner, SnapshotBackup, learning_client, record_trusted_code_attempt

from hard_api.db import migrations
from hard_api.main import create_app
from hard_api.runners.manager import RunManager


def multi_lesson_client(tmp_path: Path) -> tuple[TestClient, Path]:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    (content_root / "python" / "python-foundations" / ".fixture-only").unlink()
    course_path = content_root / "python" / "course.yaml"
    course = json.loads(course_path.read_text(encoding="utf-8"))
    foundations = course["modules"][0]
    foundations["lessons"].append(
        {"id": "python-foundations-next", "path": "python-foundations/next.md"}
    )
    course["modules"].append(
        {
            "id": "python-advanced",
            "title": "Python 进阶",
            "prerequisites": ["python-foundations"],
            "source_coverage": [
                {"source_id": "python-advanced-source", "lesson_id": "python-advanced-intro"}
            ],
            "lessons": [{"id": "python-advanced-intro", "path": "python-advanced/intro.md"}],
        }
    )
    course_path.write_text(json.dumps(course, ensure_ascii=False), encoding="utf-8")
    source_root = content_root / "python" / "python-foundations"
    next_lesson = source_root / "next.md"
    next_lesson.write_text(
        source_root.joinpath("hello-world.md").read_text(encoding="utf-8")
        .replace("python-foundations-hello-world", "python-foundations-next")
        .replace("prerequisites: []", "prerequisites: [python-foundations-hello-world]"),
        encoding="utf-8",
    )
    next_exercises = source_root / "next.exercises.json"
    next_exercises.write_text(
        source_root.joinpath("hello-world.exercises.json").read_text(encoding="utf-8")
        .replace("python-foundations-hello-world", "python-foundations-next"),
        encoding="utf-8",
    )
    advanced_root = content_root / "python" / "python-advanced"
    advanced_root.mkdir()
    advanced_root.joinpath("intro.md").write_text(
        source_root.joinpath("hello-world.md").read_text(encoding="utf-8")
        .replace("python-foundations-hello-world", "python-advanced-intro"),
        encoding="utf-8",
    )
    advanced_root.joinpath("intro.exercises.json").write_text(
        source_root.joinpath("hello-world.exercises.json").read_text(encoding="utf-8")
        .replace("python-foundations-hello-world", "python-advanced-intro"),
        encoding="utf-8",
    )
    database_path = tmp_path / "database" / "hard.db"
    migrations.migrate_database(database_path, backup_provider=SnapshotBackup(tmp_path / "snapshots"))
    settings = replace(make_settings(content_root), database_path=database_path, data_dir=database_path.parent)
    app = create_app(settings)
    app.state.runner_manager.shutdown()
    app.state.runner_manager = RunManager(settings.runner_work_dir, adapters={"python": FixtureRunner()})
    return TestClient(app), database_path


def _pass_lesson(client: TestClient, lesson_id: str) -> list[dict[str, object]]:
    attempts: list[dict[str, object]] = []
    for suffix, payload in (
        ("k01", {"answer": "a"}),
        ("k02", {"answer": "a"}),
        ("k03", {"answer": "a"}),
    ):
        response = client.post(
            "/api/assessment/attempts",
            json={"lesson_id": lesson_id, "exercise_id": f"{lesson_id}-{suffix}", "hint_level": "none", **payload},
            headers={"Idempotency-Key": f"{lesson_id}-{suffix}"},
        )
        assert response.status_code == 200
        attempts.append(response.json())
    for suffix, source in (("c01", "print('Hello, Hard!')"), ("challenge", "print('Hello')\nprint('Hard')")):
        response = record_trusted_code_attempt(
            client,
            lesson_id=lesson_id,
            exercise_id=f"{lesson_id}-{suffix}",
            source_code=source,
            idempotency_key=f"{lesson_id}-{suffix}",
        )
        assert response.status_code == 200
        attempts.append(response.json())
    return attempts


def test_non_fixture_course_unlocks_at_70_and_records_85_module_and_course_mastery(tmp_path: Path) -> None:
    client, database_path = multi_lesson_client(tmp_path)
    with client:
        first = _pass_lesson(client, "python-foundations-hello-world")
        second = _pass_lesson(client, "python-foundations-next")
        third = _pass_lesson(client, "python-advanced-intro")

    assert first[3]["total_score"] == 70.0
    assert first[3]["newly_unlocked"] == ["python-foundations-next"]
    assert second[3]["newly_unlocked"] == ["python-advanced-intro"]
    with closing(sqlite3.connect(database_path)) as connection:
        mastery = connection.execute(
            "SELECT scope_type, scope_id, MAX(score) FROM mastery_snapshots "
            "GROUP BY scope_type, scope_id ORDER BY scope_type, scope_id"
        ).fetchall()
    assert ("module", "python-foundations", 90) in mastery
    assert ("module", "python-advanced", 90) in mastery
    assert ("course", "python", 90) in mastery


def test_placement_uses_85_threshold_marks_validated_and_never_awards_completion_experience(
    tmp_path: Path,
) -> None:
    client, database_path = learning_client(tmp_path)
    with client:
        below_threshold = client.post(
            "/api/assessment/placement",
            json={"language": "python", "module_id": "python-foundations", "score": 84.99},
            headers={"Idempotency-Key": "placement-low"},
        )
        threshold = client.post(
            "/api/assessment/placement",
            json={"language": "python", "module_id": "python-foundations", "score": 85},
            headers={"Idempotency-Key": "placement-pass"},
        )
        replay = client.post(
            "/api/assessment/placement",
            json={"language": "python", "module_id": "python-foundations", "score": 85},
            headers={"Idempotency-Key": "placement-pass"},
        )

    assert below_threshold.status_code == 200
    assert below_threshold.json()["validated"] is False
    assert threshold.status_code == 200
    assert threshold.json()["validated"] is True
    assert threshold.json()["experience_candidate"] is False
    assert replay.json() == threshold.json()
    with closing(sqlite3.connect(database_path)) as connection:
        progress = connection.execute("SELECT status FROM lesson_progress").fetchall()
        events = connection.execute("SELECT COUNT(*) FROM experience_events").fetchone()
    assert progress == [("validated",)]
    assert events == (0,)
