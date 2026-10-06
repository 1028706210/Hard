from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Settings:
    project_root: Path
    data_dir: Path
    database_path: Path
    backup_dir: Path
    export_dir: Path
    runner_work_dir: Path
    content_dir: Path
    toolchain_lock_path: Path

    @classmethod
    def from_environment(
        cls,
        project_root: Path | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> "Settings":
        root = (project_root or Path(__file__).resolve().parents[5]).resolve()
        if root.drive.upper() != "D:":
            raise ValueError(f"项目根目录必须位于 D 盘：{root}")
        values = os.environ if environment is None else environment

        def path_from_root(name: str, default: str) -> Path:
            configured = Path(values.get(name, default))
            if configured.drive.upper() == "C:":
                raise ValueError(f"{name} 不允许使用 C 盘路径：{configured}")
            if configured.drive or configured.root:
                raise ValueError(f"{name} 必须是相对项目根目录的路径：{configured}")

            resolved = (root / configured).resolve()
            try:
                resolved.relative_to(root)
            except ValueError as error:
                raise ValueError(f"{name} 不允许解析到项目根目录之外：{resolved}") from error
            return resolved

        data_dir = path_from_root("HARD_DATA_DIR", "data")
        return cls(
            project_root=root,
            data_dir=data_dir,
            database_path=data_dir / "hard.db",
            backup_dir=path_from_root("HARD_BACKUP_DIR", "backups"),
            export_dir=path_from_root("HARD_EXPORT_DIR", "exports"),
            runner_work_dir=path_from_root("HARD_RUNNER_WORK_DIR", "runner-work"),
            content_dir=path_from_root("HARD_CONTENT_DIR", "content"),
            toolchain_lock_path=path_from_root(
                "HARD_TOOLCHAIN_LOCK", "docs/setup/toolchain-lock.json"
            ),
        )
