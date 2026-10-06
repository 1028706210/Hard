from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from hard_api.backup.retention import retain_backups


def test_retention_keeps_seven_newest_daily_and_four_newest_weekly_backups(tmp_path: Path) -> None:
    for day in range(1, 10):
        (tmp_path / f"daily-2026-08-{day:02d}.db").write_text(str(day), encoding="utf-8")
    for week in range(30, 36):
        (tmp_path / f"weekly-2026-W{week:02d}.db").write_text(str(week), encoding="utf-8")

    retained = retain_backups(tmp_path)

    assert [path.name for path in retained.daily] == [f"daily-2026-08-{day:02d}.db" for day in range(3, 10)]
    assert [path.name for path in retained.weekly] == [f"weekly-2026-W{week:02d}.db" for week in range(32, 36)]
    assert not (tmp_path / "daily-2026-08-01.db").exists()
    assert not (tmp_path / "weekly-2026-W30.db").exists()


def test_retention_ignores_migration_snapshots_and_non_backup_files(tmp_path: Path) -> None:
    (tmp_path / "migration-2026-08-25.db").write_text("snapshot", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("keep", encoding="utf-8")

    retain_backups(tmp_path)

    assert (tmp_path / "migration-2026-08-25.db").exists()
    assert (tmp_path / "notes.txt").exists()
