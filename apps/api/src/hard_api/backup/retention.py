from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_DAILY = re.compile(r"^daily-(\d{4}-\d{2}-\d{2})\.db$")
_WEEKLY = re.compile(r"^weekly-(\d{4}-W\d{2})\.db$")


@dataclass(frozen=True, slots=True)
class RetainedBackups:
    daily: tuple[Path, ...]
    weekly: tuple[Path, ...]


def _retain(directory: Path, pattern: re.Pattern[str], limit: int) -> tuple[Path, ...]:
    matches = sorted(
        (path for path in directory.glob("*.db") if pattern.fullmatch(path.name)),
        key=lambda path: path.name,
        reverse=True,
    )
    for path in matches[limit:]:
        path.unlink()
    return tuple(sorted(matches[:limit], key=lambda path: path.name))


def retain_backups(directory: Path, *, daily_limit: int = 7, weekly_limit: int = 4) -> RetainedBackups:
    directory.mkdir(parents=True, exist_ok=True)
    return RetainedBackups(
        daily=_retain(directory, _DAILY, daily_limit),
        weekly=_retain(directory, _WEEKLY, weekly_limit),
    )
