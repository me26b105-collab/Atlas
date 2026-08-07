"""Scene domain objects for Atlas' multi-body workspace.

The scene is deliberately independent from Qt widgets and VTK actors.  This
makes the project model serialisable and leaves the viewport as a renderer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from PySide6.QtCore import QObject, Signal


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class SceneObject:
    """A renderable engineering body and its persisted display state."""

    display_name: str
    original_filename: str
    file_path: str
    mesh: Any
    uuid: str = field(default_factory=lambda: str(uuid4()))
    actor: Any = None
    visible: bool = True
    selected: bool = False
    opacity: float = 1.0
    color: str = "#D8DDE6"
    edge_visibility: bool = True
    wireframe: bool = False
    render_mode: str = "surface"
    transform: dict[str, Any] = field(default_factory=dict)
    material: dict[str, Any] = field(default_factory=dict)
    mesh_settings: dict[str, Any] = field(default_factory=dict)
    physics: dict[str, Any] = field(default_factory=dict)
    creation_time: str = field(default_factory=_now)
    last_modified: str = field(default_factory=_now)

    @property
    def bounds(self) -> tuple[float, float, float, float, float, float]:
        return tuple(float(value) for value in self.mesh.bounds)

    @property
    def center(self) -> tuple[float, float, float]:
        return tuple(float(value) for value in self.mesh.center)

    def touch(self) -> None:
        self.last_modified = _now()

    def to_project_dict(self) -> dict[str, Any]:
        """Return data required to rebuild this object from its source file."""
        return {
            "uuid": self.uuid, "display_name": self.display_name,
            "original_filename": self.original_filename, "file_path": self.file_path,
            "visible": self.visible, "opacity": self.opacity, "color": self.color,
            "edge_visibility": self.edge_visibility, "wireframe": self.wireframe,
            "render_mode": self.render_mode, "transform": self.transform,
            "material": self.material, "mesh": self.mesh_settings, "physics": self.physics,
            "creation_time": self.creation_time, "last_modified": self.last_modified,
        }


class SelectionManager(QObject):
    """Maintains one coherent selection across tree, viewport and services."""

    selection_changed = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self._selected_ids: list[str] = []

    @property
    def selected_ids(self) -> list[str]:
        return list(self._selected_ids)

    def set_selection(self, object_ids: list[str]) -> None:
        unique = list(dict.fromkeys(object_ids))
        if unique != self._selected_ids:
            self._selected_ids = unique
            self.selection_changed.emit(self.selected_ids)

    def clear(self) -> None:
        self.set_selection([])


class SceneCollection:
    """Ordered object collection; order is exposed in the project explorer."""

    def __init__(self) -> None:
        self._objects: list[SceneObject] = []

    def __iter__(self):
        return iter(self._objects)

    def __len__(self) -> int:
        return len(self._objects)

    def add(self, scene_object: SceneObject) -> None:
        self._objects.append(scene_object)

    def get(self, object_id: str) -> SceneObject | None:
        return next((obj for obj in self._objects if obj.uuid == object_id), None)

    def remove(self, object_id: str) -> SceneObject | None:
        obj = self.get(object_id)
        if obj:
            self._objects.remove(obj)
        return obj

    def clear(self) -> None:
        self._objects.clear()

    def reorder(self, ordered_ids: list[str]) -> None:
        known = {obj.uuid: obj for obj in self._objects}
        self._objects = [known[item] for item in ordered_ids if item in known]
        self._objects.extend(obj for obj in known.values() if obj.uuid not in ordered_ids)


class SceneManager(QObject):
    """Owns scene bodies and emits changes for presentation adapters."""

    scene_changed = Signal()
    object_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.objects = SceneCollection()
        self.selection = SelectionManager()
        self.selection.selection_changed.connect(self._apply_selection)

    def add_mesh(self, file_path: str, mesh: Any, metadata: dict[str, Any] | None = None) -> SceneObject:
        metadata = metadata or {}
        path = Path(file_path)
        obj = SceneObject(
            display_name=metadata.get("display_name", path.stem),
            original_filename=metadata.get("original_filename", path.name), file_path=str(path), mesh=mesh,
            uuid=metadata.get("uuid", str(uuid4())), visible=metadata.get("visible", True),
            opacity=float(metadata.get("opacity", 1.0)), color=metadata.get("color", "#D8DDE6"),
            edge_visibility=metadata.get("edge_visibility", True), wireframe=metadata.get("wireframe", False),
            render_mode=metadata.get("render_mode", "surface"), transform=metadata.get("transform", {}),
            material=metadata.get("material", {}), mesh_settings=metadata.get("mesh", {}), physics=metadata.get("physics", {}),
            creation_time=metadata.get("creation_time", _now()), last_modified=metadata.get("last_modified", _now()),
        )
        self.objects.add(obj)
        self.scene_changed.emit()
        return obj

    def remove(self, object_ids: list[str]) -> list[SceneObject]:
        removed = [self.objects.remove(item) for item in object_ids]
        self.selection.set_selection([item for item in self.selection.selected_ids if item not in object_ids])
        self.scene_changed.emit()
        return [obj for obj in removed if obj]

    def clear(self) -> None:
        self.objects.clear()
        self.selection.clear()
        self.scene_changed.emit()

    def select(self, object_ids: list[str]) -> None:
        self.selection.set_selection([item for item in object_ids if self.objects.get(item)])

    def selected_objects(self) -> list[SceneObject]:
        return [obj for item in self.selection.selected_ids if (obj := self.objects.get(item))]

    def _apply_selection(self, ids: list[str]) -> None:
        for obj in self.objects:
            obj.selected = obj.uuid in ids
            self.object_changed.emit(obj.uuid)

    def update_object(self, object_id: str, **changes: Any) -> SceneObject | None:
        obj = self.objects.get(object_id)
        if not obj:
            return None
        for key, value in changes.items():
            setattr(obj, key, value)
        obj.touch()
        self.object_changed.emit(object_id)
        return obj

    def statistics(self) -> dict[str, int]:
        return {"objects": len(self.objects), "vertices": sum(obj.mesh.n_points for obj in self.objects),
                "cells": sum(obj.mesh.n_cells for obj in self.objects)}
