from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from hard_api.runners.workspace import WorkspaceError, WorkspaceFactory, cleanup_workspace, write_submission_files


def test_workspace_is_unique_below_root_and_is_empty_after_cleanup(tmp_path: Path) -> None:
    root = tmp_path / "runner-work"
    factory = WorkspaceFactory(root)
    first = factory.create()
    second = factory.create()

    assert first != second
    assert first.parent == second.parent == root.resolve()
    write_submission_files(first, {"main.py": "print('safe')"})
    assert (first / "main.py").read_text(encoding="utf-8") == "print('safe')"

    cleanup_workspace(first)
    cleanup_workspace(second)

    assert list(root.iterdir()) == []


@pytest.mark.parametrize("filename", ["../escape.py", "folder/main.py", "C:/escape.py", "..\\escape.py"])
def test_workspace_rejects_user_path_escape(filename: str, tmp_path: Path) -> None:
    workspace = WorkspaceFactory(tmp_path / "runner-work").create()

    with pytest.raises(WorkspaceError, match="invalid_submission_path"):
        write_submission_files(workspace, {filename: "print('no')"})

    cleanup_workspace(workspace)


def test_workspace_rejects_protected_or_reparse_roots(tmp_path: Path) -> None:
    protected = tmp_path / "data"
    with pytest.raises(WorkspaceError, match="unsafe_workspace_root"):
        WorkspaceFactory(protected, protected_paths=(protected,)).create()

    target = tmp_path / "target"
    target.mkdir()
    linked = tmp_path / "runner-link"
    try:
        os.symlink(target, linked, target_is_directory=True)
    except OSError:
        with patch("hard_api.runners.workspace._is_reparse_point", return_value=True):
            with pytest.raises(WorkspaceError, match="unsafe_workspace_root"):
                WorkspaceFactory(tmp_path / "runner-work").create()
    else:
        with pytest.raises(WorkspaceError, match="unsafe_workspace_root"):
            WorkspaceFactory(linked).create()


def test_workspace_rejects_invalid_file_payloads_and_reparse_points_during_lifecycle(tmp_path: Path) -> None:
    workspace = WorkspaceFactory(tmp_path / "runner-work").create()
    for files in ({}, {"main.py": 1}, {"bad name.py": "pass"}):
        with pytest.raises(WorkspaceError, match="invalid_submission_path"):
            write_submission_files(workspace, files)

    with patch("hard_api.runners.workspace._is_reparse_point", side_effect=(False, False, True)):
        with pytest.raises(WorkspaceError, match="unsafe_workspace_root"):
            WorkspaceFactory(tmp_path / "late-reparse").create()

    with patch("hard_api.runners.workspace._is_within", return_value=False):
        with pytest.raises(WorkspaceError, match="invalid_submission_path"):
            write_submission_files(workspace, {"main.py": "pass"})

    with patch("hard_api.runners.workspace._is_reparse_point", return_value=True):
        cleanup_workspace(workspace)
    assert workspace.exists()

    with patch("hard_api.runners.workspace._is_reparse_point", return_value=False):
        cleanup_workspace(workspace)
