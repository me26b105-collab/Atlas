"""Atlas workspace coordinator. Domain behavior lives in scene/services."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMainWindow

from components.menu_bar import AtlasMenuBar
from components.project_dock import ProjectDock
from components.properties_dock import PropertiesDock
from components.status_bar import AtlasStatusBar
from components.tool_bar import AtlasToolBar
from components.viewport import AtlasViewport
from geometry.geometry_loader import GeometryLoader
from geometry.project_manager import ProjectManager
from geometry.scene import SceneManager


class AtlasMainWindow(QMainWindow):
    """Coordinates scene services and presentation widgets without owning mesh state."""

    GEOMETRY_FILTER = "Geometry Files (*.stl *.obj)"
    PROJECT_FILTER = "Atlas Projects (*.atlas)"

    def __init__(self):
        super().__init__(); self.setWindowTitle("Atlas v0.0.6"); self.resize(1400, 900)
        self.geometry_loader, self.project_manager, self.scene = GeometryLoader(), ProjectManager(), SceneManager()
        self.current_geometry_path: str | None = None  # legacy integration surface
        self.current_project_path: str | None = None
        self._configure_logging(); self._init_layout(); self._connect_signals(); self._refresh_recent_files()
        self.autosave_timer = QTimer(self); self.autosave_timer.timeout.connect(self._autosave); self.autosave_timer.start(180_000)

    def _configure_logging(self) -> None:
        log_dir = Path.cwd() / "logs"; log_dir.mkdir(exist_ok=True)
        logging.basicConfig(filename=log_dir / "atlas.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    def _init_layout(self) -> None:
        self.viewport = AtlasViewport(self.scene, self); self.setCentralWidget(self.viewport)
        self.menu_bar = AtlasMenuBar(self); self.setMenuBar(self.menu_bar)
        self.tool_bar = AtlasToolBar(self); self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar)
        self.project_dock = ProjectDock(self.scene, self); self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)
        self.properties_dock = PropertiesDock(self); self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
        self.status_bar = AtlasStatusBar(self); self.setStatusBar(self.status_bar)

    def _connect_signals(self) -> None:
        m, t, v, d = self.menu_bar, self.tool_bar, self.viewport, self.project_dock
        m.new_project_requested.connect(self.new_project); m.open_geometry_requested.connect(self.open_geometry); m.open_project_requested.connect(self.open_project); m.save_project_requested.connect(self.save_project); m.clear_project_requested.connect(self.new_project); m.exit_requested.connect(self.close)
        m.reset_camera_requested.connect(v.reset_camera); m.fit_to_screen_requested.connect(v.fit_to_screen); m.shaded_view_requested.connect(v.set_shaded); m.toggle_wireframe_requested.connect(v.toggle_wireframe); m.screenshot_requested.connect(self.save_screenshot); m.recent_file_requested.connect(self.load_geometry_file)
        t.new_project_requested.connect(self.new_project); t.open_geometry_requested.connect(self.open_geometry); t.reset_camera_requested.connect(v.reset_camera); t.fit_to_screen_requested.connect(v.fit_to_screen); t.shaded_requested.connect(v.set_shaded); t.wireframe_requested.connect(v.toggle_wireframe); t.screenshot_requested.connect(self.save_screenshot)
        v.geometry_dropped.connect(self.load_geometry_file); v.new_project_requested.connect(self.new_project); v.open_geometry_requested.connect(self.open_geometry); v.recent_file_requested.connect(self.load_geometry_file); v.loading_status_changed.connect(self.status_bar.set_message); v.object_context_requested.connect(self._viewport_command)
        d.selection_requested.connect(self.scene.select); d.rename_requested.connect(self.rename_object); d.delete_requested.connect(self.delete_objects); d.visibility_requested.connect(lambda oid, visible: self.scene.update_object(oid, visible=visible)); d.properties_requested.connect(lambda oid: self.scene.select([oid]))
        self.scene.selection.selection_changed.connect(self._selection_changed); self.scene.scene_changed.connect(self._scene_changed)
        QShortcut(QKeySequence("Delete"), self, activated=self.delete_selected)

    def new_project(self) -> None:
        """Explicitly clears all bodies; imports never clear the scene implicitly."""
        self.scene.clear(); self.viewport.rebuild_scene(); self.project_dock.set_project_name("Atlas Project"); self.properties_dock.clear_properties(); self.current_geometry_path = self.current_project_path = None; self.status_bar.clear_geometry(); self.status_bar.set_project("Untitled Project"); self.status_bar.set_message("New Project")

    def open_geometry(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Geometry",
            "",
            self.GEOMETRY_FILTER,
        )

        if filename:
            self.load_geometry_file(filename)

    def load_geometry_file(self, filename: str, metadata: dict | None = None) -> bool:
        try:
            if len(self.scene.objects):
                self.new_project()

            path = self.geometry_loader.load(filename)
            obj = self.viewport.add_geometry(path, metadata)
            self.current_geometry_path = path

            self.project_manager.add_recent_file(path)
            logging.info("Geometry imported: %s", path)
            self._refresh_recent_files()
            self.status_bar.set_message(f"Imported: {obj.display_name}")
            return True

        except (FileNotFoundError, ValueError) as error:
            self.status_bar.set_error(str(error))
            logging.warning("Geometry import failed: %s", error)

        except Exception as error:
            self.status_bar.set_error(f"Could not read geometry: {error}")
            logging.exception("Geometry import failed")

        return False

    def _selection_changed(self, ids: list[str]) -> None:
        selected = self.scene.selected_objects()
        if len(selected) == 1: self.properties_dock.set_scene_object(selected[0])
        elif not selected: self.properties_dock.clear_properties()
        self._scene_changed()

    def _scene_changed(self) -> None:
        stats = self.scene.statistics(); selected = self.scene.selected_objects(); name = selected[0].display_name if len(selected) == 1 else (f"{len(selected)} objects" if selected else "None")
        self.status_bar.set_scene_statistics(**stats, selected=name)

    def rename_object(self, object_id: str, name: str | None = None) -> None:
        obj = self.scene.objects.get(object_id)
        if not obj: return
        if name is None: name, ok = QInputDialog.getText(self, "Rename Geometry", "Name:", text=obj.display_name); name = name if ok else ""
        if name and name.strip(): self.scene.update_object(object_id, display_name=name.strip())

    def delete_selected(self) -> None: self.delete_objects(self.scene.selection.selected_ids)
    def delete_objects(self, object_ids: list[str]) -> None:
        if not object_ids: return
        removed = self.scene.remove(object_ids); self.viewport.remove_objects(removed); self.status_bar.set_message(f"Deleted {len(removed)} object(s)")
    def _viewport_command(self, object_id: str, command: str) -> None:
        if command == "delete": self.delete_objects([object_id])
        elif command == "rename": self.rename_object(object_id)

    def _refresh_recent_files(self) -> None:
        files = self.project_manager.recent_files(); self.menu_bar.set_recent_files(files); self.viewport.set_recent_files(files)

    def save_screenshot(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "atlas_view.png", "PNG (*.png)")
        if filename: self.viewport.take_screenshot(filename); self.project_dock.add_screenshot(Path(filename).name); self.status_bar.set_message(f"Screenshot saved: {Path(filename).name}")

    def _project_data(self) -> dict:
        return {"format": "Atlas Project", "version": "0.0.6", "objects": [obj.to_project_dict() for obj in self.scene.objects], "camera": self.viewport.camera_state() if len(self.scene.objects) else None, "selection": self.scene.selection.selected_ids, "materials": {}, "mesh": {}, "physics": {}, "results": {}}

    def save_project(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Save Atlas Project", self.current_project_path or "untitled.atlas", self.PROJECT_FILTER)
        if not filename: return
        if not filename.lower().endswith(".atlas"): filename += ".atlas"
        try:
            self.project_manager.save_project(filename, self._project_data()); self.current_project_path = filename; self.project_manager.add_recent_project(filename); self.project_dock.set_project_name(Path(filename).stem); self.status_bar.set_project(Path(filename).stem); self.status_bar.set_message(f"Project saved: {Path(filename).name}"); logging.info("Project saved: %s", filename)
        except OSError as error: self.status_bar.set_error(f"Could not save project: {error}")

    def open_project(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Open Atlas Project", "", self.PROJECT_FILTER)
        if filename: self._load_project(filename)

    def _load_project(self, filename: str) -> bool:
        try:
            data = self.project_manager.open_project(filename); self.new_project()
            objects = data.get("objects")
            if objects is None and data.get("geometry_path"): # v0.0.5 migration
                objects = [{"file_path": data["geometry_path"], "wireframe": data.get("wireframe", False)}]
            for item in objects or []:
                if not self.load_geometry_file(item["file_path"], item): raise ValueError(f"Could not load {item['file_path']}")
            if data.get("camera"): self.viewport.restore_camera(data["camera"])
            self.scene.select(data.get("selection", [])); self.current_project_path = filename; self.project_manager.add_recent_project(filename); self.project_dock.set_project_name(Path(filename).stem); self.status_bar.set_project(Path(filename).stem); self.status_bar.set_message(f"Project opened: {Path(filename).name}"); logging.info("Project opened: %s", filename); return True
        except (ValueError, KeyError) as error: self.status_bar.set_error(str(error)); logging.exception("Project open failed")
        return False

    def _autosave(self) -> None:
        if len(self.scene.objects):
            try: self.project_manager.save_project(str(Path.cwd() / "autosave.atlas"), self._project_data())
            except OSError: logging.exception("Autosave failed")
