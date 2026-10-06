from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
from uuid import uuid4


_SAFE_FILE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class WorkspaceError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _is_reparse_point(path: Path) -> bool:
    try:
        attributes = os.lstat(path).st_file_attributes
    except (AttributeError, FileNotFoundError):
        return path.is_symlink()
    return path.is_symlink() or bool(attributes & getattr(os, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


class WorkspaceFactory:
    def __init__(self, root: Path, *, protected_paths: tuple[Path, ...] = ()) -> None:
        self.root = root
        self.protected_paths = protected_paths

    def create(self) -> Path:
        if _is_reparse_point(self.root):
            raise WorkspaceError("unsafe_workspace_root")
        self.root.mkdir(parents=True, exist_ok=True)
        if _is_reparse_point(self.root):
            raise WorkspaceError("unsafe_workspace_root")
        root = self.root.resolve()
        for protected in self.protected_paths:
            resolved = protected.resolve()
            if _is_within(root, resolved) or _is_within(resolved, root):
                raise WorkspaceError("unsafe_workspace_root")
        workspace = root / uuid4().hex
        workspace.mkdir()
        resolved_workspace = workspace.resolve()
        if _is_reparse_point(workspace) or not _is_within(resolved_workspace, root):
            raise WorkspaceError("unsafe_workspace_root")
        return resolved_workspace


def write_submission_files(workspace: Path, files: dict[str, str] | object) -> None:
    if not isinstance(files, dict) or not files:
        raise WorkspaceError("invalid_submission_path")
    resolved_workspace = workspace.resolve()
    for name, content in files.items():
        if not isinstance(name, str) or not _SAFE_FILE_NAME.fullmatch(name) or not isinstance(content, str):
            raise WorkspaceError("invalid_submission_path")
        destination = (resolved_workspace / name).resolve()
        if destination.parent != resolved_workspace or not _is_within(destination, resolved_workspace):
            raise WorkspaceError("invalid_submission_path")
        destination.write_text(content, encoding="utf-8", newline="\n")


def cleanup_workspace(workspace: Path) -> None:
    if workspace.exists() and not _is_reparse_point(workspace):
        shutil.rmtree(workspace)
