"""Persistence helpers for Atlas projects and recent geometry files."""

import json
from pathlib import Path

from PySide6.QtCore import QSettings


class ProjectManager:
    """Stores lightweight workspace state without owning application UI."""

    RECENT_FILES_KEY = "recent_geometry_files"
    RECENT_PROJECTS_KEY = "recent_projects"
    MAX_RECENT_FILES = 10

    def __init__(self) -> None:
        self.settings = QSettings()

    def recent_files(self) -> list[str]:
        """Return existing recent files, removing stale entries as a side effect."""
        files = self.settings.value(self.RECENT_FILES_KEY, [])
        if isinstance(files, str):
            files = [files]
        valid_files = [str(Path(filename)) for filename in files if Path(filename).is_file()]
        if valid_files != files:
            self.settings.setValue(self.RECENT_FILES_KEY, valid_files)
        return valid_files

    def add_recent_file(self, filename: str) -> None:
        path = str(Path(filename).resolve())
        files = [item for item in self.recent_files() if item != path]
        self.settings.setValue(self.RECENT_FILES_KEY, [path, *files][:self.MAX_RECENT_FILES])

    def recent_projects(self) -> list[str]:
        """Return valid projects separately from imported geometry history."""
        files = self.settings.value(self.RECENT_PROJECTS_KEY, [])
        if isinstance(files, str):
            files = [files]
        valid = [str(Path(item)) for item in files if Path(item).is_file()]
        if valid != files:
            self.settings.setValue(self.RECENT_PROJECTS_KEY, valid)
        return valid

    def add_recent_project(self, filename: str) -> None:
        path = str(Path(filename).resolve())
        self.settings.setValue(self.RECENT_PROJECTS_KEY, [path, *[item for item in self.recent_projects() if item != path]][:self.MAX_RECENT_FILES])

    def save_project(self, filename: str, data: dict) -> None:
        """Save an Atlas workspace as readable JSON."""
        Path(filename).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def open_project(self, filename: str) -> dict:
        """Read and minimally validate an Atlas workspace file."""
        try:
            data = json.loads(Path(filename).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError("Could not read Atlas project file.") from error

        if not isinstance(data, dict) or data.get("format") != "Atlas Project":
            raise ValueError("Invalid Atlas project file.")
        return data
