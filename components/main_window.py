"""Atlas workspace coordinator."""

from __future__ import annotations

import logging
from pathlib import Path

import pyvista as pv

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
)

from components.material_editor import (
    MaterialEditorDialog,
)
from components.menu_bar import AtlasMenuBar
from components.mesh_dock import MeshDock
from components.physics_dialog import (
    PhysicsEditorDialog,
)
from components.project_dock import ProjectDock
from components.properties_dock import PropertiesDock
from components.status_bar import AtlasStatusBar
from components.tool_bar import AtlasToolBar
from components.viewport import AtlasViewport

from geometry.geometry_loader import GeometryLoader
from geometry.mesh_manager import MeshManager
from geometry.project_manager import ProjectManager
from geometry.scene import SceneManager

from materials.material_manager import MaterialManager

from physics.constraint import ConstraintManager
from physics.load import LoadManager


class AtlasMainWindow(QMainWindow):
    """Coordinates Atlas services and presentation widgets."""

    GEOMETRY_FILTER = (
        "Geometry Files (*.stl *.obj)"
    )

    PROJECT_FILTER = (
        "Atlas Projects (*.atlas)"
    )

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Atlas v0.0.9"
        )

        self.resize(
            1400,
            900,
        )

        self.geometry_loader = (
            GeometryLoader()
        )

        self.project_manager = (
            ProjectManager()
        )

        self.scene = SceneManager()

        self.material_manager = (
            MaterialManager()
        )

        self.mesh_manager = (
            MeshManager()
        )

        self.mesh_actor = None

        # NEW v0.0.9
        self.load_manager = (
            LoadManager()
        )

        self.constraint_manager = (
            ConstraintManager()
        )

        self.current_geometry_path = None
        self.current_project_path = None

        self._configure_logging()
        self._init_layout()
        self._connect_signals()
        self._refresh_recent_files()

        self.project_dock.refresh_materials(
            self.material_manager.materials()
        )

        self.project_dock.refresh_physics(
            self.load_manager.all(),
            self.constraint_manager.all(),
        )

        self.autosave_timer = QTimer(
            self
        )

        self.autosave_timer.timeout.connect(
            self._autosave
        )

        self.autosave_timer.start(
            180_000
        )

    # =====================================================
    # SETUP
    # =====================================================

    def _configure_logging(
        self,
    ) -> None:
        log_dir = (
            Path.cwd()
            / "logs"
        )

        log_dir.mkdir(
            exist_ok=True
        )

        logging.basicConfig(
            filename=(
                log_dir
                / "atlas.log"
            ),
            level=logging.INFO,
            format=(
                "%(asctime)s "
                "%(levelname)s "
                "%(message)s"
            ),
        )

    def _init_layout(
        self,
    ) -> None:
        self.viewport = AtlasViewport(
            self.scene,
            self,
        )

        self.setCentralWidget(
            self.viewport
        )

        self.menu_bar = AtlasMenuBar(
            self
        )

        self.setMenuBar(
            self.menu_bar
        )

        self.tool_bar = AtlasToolBar(
            self
        )

        self.addToolBar(
            Qt.ToolBarArea.TopToolBarArea,
            self.tool_bar,
        )

        self.project_dock = ProjectDock(
            self.scene,
            self,
        )

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.project_dock,
        )

        self.properties_dock = (
            PropertiesDock(self)
        )

        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.properties_dock,
        )

        self.mesh_dock = MeshDock(
            self
        )

        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.mesh_dock,
        )

        self.mesh_dock.hide()

        self.status_bar = AtlasStatusBar(
            self
        )

        self.setStatusBar(
            self.status_bar
        )

    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_signals(
        self,
    ) -> None:
        m = self.menu_bar
        t = self.tool_bar
        v = self.viewport
        d = self.project_dock

        # -------------------------------------------------
        # Menu
        # -------------------------------------------------

        m.new_project_requested.connect(
            self.new_project
        )

        m.open_geometry_requested.connect(
            self.open_geometry
        )

        m.open_project_requested.connect(
            self.open_project
        )

        m.save_project_requested.connect(
            self.save_project
        )

        m.clear_project_requested.connect(
            self.new_project
        )

        m.exit_requested.connect(
            self.close
        )

        m.reset_camera_requested.connect(
            v.reset_camera
        )

        m.fit_to_screen_requested.connect(
            v.fit_to_screen
        )

        m.shaded_view_requested.connect(
            v.set_shaded
        )

        m.toggle_wireframe_requested.connect(
            v.toggle_wireframe
        )

        m.screenshot_requested.connect(
            self.save_screenshot
        )

        m.recent_file_requested.connect(
            self.load_geometry_file
        )

        # -------------------------------------------------
        # Toolbar
        # -------------------------------------------------

        t.new_project_requested.connect(
            self.new_project
        )

        t.open_geometry_requested.connect(
            self.open_geometry
        )

        t.reset_camera_requested.connect(
            v.reset_camera
        )

        t.fit_to_screen_requested.connect(
            v.fit_to_screen
        )

        t.shaded_requested.connect(
            v.set_shaded
        )

        t.wireframe_requested.connect(
            v.toggle_wireframe
        )

        t.screenshot_requested.connect(
            self.save_screenshot
        )

        # -------------------------------------------------
        # Viewport
        # -------------------------------------------------

        v.geometry_dropped.connect(
            self.load_geometry_file
        )

        v.new_project_requested.connect(
            self.new_project
        )

        v.open_geometry_requested.connect(
            self.open_geometry
        )

        v.recent_file_requested.connect(
            self.load_geometry_file
        )

        v.loading_status_changed.connect(
            self.status_bar.set_message
        )

        v.object_context_requested.connect(
            self._viewport_command
        )

        # -------------------------------------------------
        # Geometry tree
        # -------------------------------------------------

        d.selection_requested.connect(
            self.scene.select
        )

        d.rename_requested.connect(
            self.rename_object
        )

        d.delete_requested.connect(
            self.delete_objects
        )

        d.visibility_requested.connect(
            lambda object_id, visible:
            self.scene.update_object(
                object_id,
                visible=visible,
            )
        )

        d.properties_requested.connect(
            lambda object_id:
            self.scene.select(
                [object_id]
            )
        )

        # -------------------------------------------------
        # Materials
        # -------------------------------------------------

        d.material_selection_requested.connect(
            self._material_selection_changed
        )

        d.edit_material_requested.connect(
            self._edit_material
        )

        d.reset_material_requested.connect(
            self._reset_material
        )

        d.save_material_requested.connect(
            self._save_material
        )

        # -------------------------------------------------
        # Mesh
        # -------------------------------------------------

        d.mesh_requested.connect(
            self.show_mesh_dock
        )

        self.mesh_dock.surface_mesh_requested.connect(
            self.generate_surface_mesh
        )

        self.mesh_dock.volume_mesh_requested.connect(
            self.generate_volume_mesh
        )

        self.mesh_dock.clear_mesh_requested.connect(
            self.clear_generated_mesh
        )

        # -------------------------------------------------
        # Physics
        # -------------------------------------------------

        d.physics_selection_requested.connect(
            self._physics_selection_changed
        )

        d.add_load_requested.connect(
            self._add_load
        )

        d.edit_load_requested.connect(
            self._edit_load
        )

        d.delete_load_requested.connect(
            self._delete_load
        )

        d.add_constraint_requested.connect(
            self._add_constraint
        )

        d.edit_constraint_requested.connect(
            self._edit_constraint
        )

        d.delete_constraint_requested.connect(
            self._delete_constraint
        )

        # -------------------------------------------------
        # Scene
        # -------------------------------------------------

        self.scene.selection.selection_changed.connect(
            self._selection_changed
        )

        self.scene.scene_changed.connect(
            self._scene_changed
        )

        QShortcut(
            QKeySequence("Delete"),
            self,
            activated=self.delete_selected,
        )

    # =====================================================
    # MESH
    # =====================================================

    def show_mesh_dock(
        self,
    ) -> None:
        if not self.scene.selected_objects():
            QMessageBox.information(
                self,
                "Mesh",
                (
                    "Select a geometry "
                    "object first."
                ),
            )
            return

        self.mesh_dock.show()
        self.mesh_dock.raise_()

        self.status_bar.set_message(
            "Mesh controls opened."
        )

    def _selected_geometry_mesh(
        self,
    ):
        selected = (
            self.scene.selected_objects()
        )

        if not selected:
            raise ValueError(
                "Select a geometry object first."
            )

        return selected[0].mesh

    def generate_surface_mesh(
        self,
        element_size: float,
        refinement: int,
    ) -> None:
        try:
            geometry = (
                self._selected_geometry_mesh()
            )

            mesh = (
                self.mesh_manager
                .generate_surface_mesh(
                    geometry,
                    refinement,
                )
            )

            self._display_generated_mesh(
                mesh,
                wireframe=True,
            )

            stats = (
                self.mesh_manager
                .surface_statistics
            )

            self.mesh_dock.set_statistics(
                stats.points,
                stats.cells,
                stats.surface_cells,
                stats.volume_cells,
                stats.memory_mb,
            )

            quality = (
                self.mesh_manager
                .surface_quality()
            )

            self.mesh_dock.set_quality(
                quality.get(
                    "minimum_area"
                ),
                quality.get(
                    "average_area"
                ),
                quality.get(
                    "maximum_area"
                ),
            )

            self.status_bar.set_message(
                "Surface mesh generated."
            )

        except Exception as error:
            logging.exception(
                "Surface mesh generation failed"
            )

            QMessageBox.warning(
                self,
                "Surface Mesh",
                str(error),
            )

    def generate_volume_mesh(
        self,
        element_size: float,
        refinement: int,
    ) -> None:
        try:
            geometry = (
                self._selected_geometry_mesh()
            )

            mesh = (
                self.mesh_manager
                .generate_volume_mesh(
                    geometry,
                    refinement,
                )
            )

            self._display_generated_mesh(
                mesh,
                wireframe=True,
            )

            stats = (
                self.mesh_manager
                .volume_statistics
            )

            self.mesh_dock.set_statistics(
                stats.points,
                stats.cells,
                stats.surface_cells,
                stats.volume_cells,
                stats.memory_mb,
            )

            quality = (
                self.mesh_manager
                .volume_quality()
            )

            self.mesh_dock.set_quality(
                quality.get(
                    "minimum_volume"
                ),
                quality.get(
                    "average_volume"
                ),
                quality.get(
                    "maximum_volume"
                ),
            )

            self.status_bar.set_message(
                "Volume mesh generated."
            )

        except Exception as error:
            logging.exception(
                "Volume mesh generation failed"
            )

            QMessageBox.warning(
                self,
                "Volume Mesh",
                str(error),
            )

    def _display_generated_mesh(
        self,
        mesh,
        wireframe: bool = True,
    ) -> None:
        self._remove_mesh_actor()

        self.mesh_actor = (
            self.viewport.plotter.add_mesh(
                mesh,
                color="#7DD3FC",
                show_edges=wireframe,
                line_width=1.0,
                opacity=0.95,
            )
        )

        self.viewport.plotter.reset_camera()
        self.viewport.plotter.render()

    def _remove_mesh_actor(
        self,
    ) -> None:
        if self.mesh_actor is not None:
            try:
                self.viewport.plotter.remove_actor(
                    self.mesh_actor,
                    render=False,
                )
            except Exception:
                pass

            self.mesh_actor = None

    def clear_generated_mesh(
        self,
    ) -> None:
        self._remove_mesh_actor()

        self.mesh_manager.clear()

        self.mesh_dock.clear_statistics()

        self.viewport.plotter.render()

        self.status_bar.set_message(
            "Generated mesh cleared."
        )

    # =====================================================
    # PHYSICS
    # =====================================================

    def _physics_selection_changed(
        self,
        physics_type: str,
        physics_id: str,
    ) -> None:
        if physics_type == "load":
            load = (
                self.load_manager.get(
                    physics_id
                )
            )

            if load:
                self.properties_dock.set_physics_load(
                    load
                )

        elif physics_type == "constraint":
            constraint = (
                self.constraint_manager.get(
                    physics_id
                )
            )

            if constraint:
                self.properties_dock.set_physics_constraint(
                    constraint
                )

    def _physics_object_id(self) -> str | None:
        selected = (
            self.scene.selected_objects()
        )

        if not selected:
            QMessageBox.information(
                self,
                "Physics",
                (
                    "Select a geometry "
                    "object first."
                ),
            )

            return None

        return selected[0].uuid

    def _physics_object_name(self) -> str:
        selected = (
            self.scene.selected_objects()
        )

        if not selected:
            return ""

        return selected[0].display_name

    def _add_load(
        self,
        load_type: str,
    ) -> None:
        object_id = (
            self._physics_object_id()
        )

        if object_id is None:
            return

        dialog = PhysicsEditorDialog(
            "Load",
            object_name=self._physics_object_name(),
            parent=self,
        )

        index = dialog.type_box.findText(
            load_type
        )

        if index >= 0:
            dialog.type_box.setCurrentIndex(
                index
            )

        if not dialog.exec():
            return

        values = dialog.values()

        if not values["name"]:
            QMessageBox.warning(
                self,
                "Invalid Load",
                "Load name cannot be empty.",
            )
            return

        try:
            self.load_manager.create(
                load_type=values["type"],
                name=values["name"],
                magnitude=values["magnitude"],
                direction_x=values[
                    "direction_x"
                ],
                direction_y=values[
                    "direction_y"
                ],
                direction_z=values[
                    "direction_z"
                ],
                location_x=values[
                    "location_x"
                ],
                location_y=values[
                    "location_y"
                ],
                location_z=values[
                    "location_z"
                ],
                object_id=object_id,
            )

            self._refresh_physics_ui()

            self.status_bar.set_message(
                f"{values['type']} added."
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Invalid Load",
                str(error),
            )

    def _edit_load(
        self,
        load_id: str,
    ) -> None:
        load = (
            self.load_manager.get(
                load_id
            )
        )

        if load is None:
            return

        object_name = ""

        if load.object_id:
            obj = (
                self.scene.objects.get(
                    load.object_id
                )
            )

            if obj:
                object_name = (
                    obj.display_name
                )

        dialog = PhysicsEditorDialog(
            "Load",
            entity=load,
            object_name=object_name,
            parent=self,
        )

        if not dialog.exec():
            return

        values = dialog.values()

        try:
            self.load_manager.update(
                load_id,
                name=values["name"],
                load_type=values["type"],
                magnitude=values["magnitude"],
                direction_x=values[
                    "direction_x"
                ],
                direction_y=values[
                    "direction_y"
                ],
                direction_z=values[
                    "direction_z"
                ],
                location_x=values[
                    "location_x"
                ],
                location_y=values[
                    "location_y"
                ],
                location_z=values[
                    "location_z"
                ],
            )

            self._refresh_physics_ui()

            self.status_bar.set_message(
                "Load modified."
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Invalid Load",
                str(error),
            )

    def _delete_load(
        self,
        load_id: str,
    ) -> None:
        load = (
            self.load_manager.get(
                load_id
            )
        )

        if load is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete Load",
            (
                f"Delete '{load.name}'?"
            ),
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.load_manager.remove(
            load_id
        )

        self._refresh_physics_ui()

        self.properties_dock.clear_properties()

        self.status_bar.set_message(
            "Load deleted."
        )

    def _add_constraint(
        self,
        constraint_type: str,
    ) -> None:
        object_id = (
            self._physics_object_id()
        )

        if object_id is None:
            return

        dialog = PhysicsEditorDialog(
            "Support",
            object_name=self._physics_object_name(),
            parent=self,
        )

        index = dialog.type_box.findText(
            constraint_type
        )

        if index >= 0:
            dialog.type_box.setCurrentIndex(
                index
            )

        if not dialog.exec():
            return

        values = dialog.values()

        if not values["name"]:
            QMessageBox.warning(
                self,
                "Invalid Support",
                "Support name cannot be empty.",
            )
            return

        try:
            self.constraint_manager.create(
                constraint_type=values[
                    "type"
                ],
                name=values["name"],
                direction_x=values[
                    "direction_x"
                ],
                direction_y=values[
                    "direction_y"
                ],
                direction_z=values[
                    "direction_z"
                ],
                location_x=values[
                    "location_x"
                ],
                location_y=values[
                    "location_y"
                ],
                location_z=values[
                    "location_z"
                ],
                object_id=object_id,
            )

            self._refresh_physics_ui()

            self.status_bar.set_message(
                f"{values['type']} support added."
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Invalid Support",
                str(error),
            )

    def _edit_constraint(
        self,
        constraint_id: str,
    ) -> None:
        constraint = (
            self.constraint_manager.get(
                constraint_id
            )
        )

        if constraint is None:
            return

        object_name = ""

        if constraint.object_id:
            obj = (
                self.scene.objects.get(
                    constraint.object_id
                )
            )

            if obj:
                object_name = (
                    obj.display_name
                )

        dialog = PhysicsEditorDialog(
            "Support",
            entity=constraint,
            object_name=object_name,
            parent=self,
        )

        if not dialog.exec():
            return

        values = dialog.values()

        try:
            self.constraint_manager.update(
                constraint_id,
                name=values["name"],
                constraint_type=values[
                    "type"
                ],
                direction_x=values[
                    "direction_x"
                ],
                direction_y=values[
                    "direction_y"
                ],
                direction_z=values[
                    "direction_z"
                ],
                location_x=values[
                    "location_x"
                ],
                location_y=values[
                    "location_y"
                ],
                location_z=values[
                    "location_z"
                ],
            )

            self._refresh_physics_ui()

            self.status_bar.set_message(
                "Support modified."
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Invalid Support",
                str(error),
            )

    def _delete_constraint(
        self,
        constraint_id: str,
    ) -> None:
        constraint = (
            self.constraint_manager.get(
                constraint_id
            )
        )

        if constraint is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete Support",
            (
                f"Delete '{constraint.name}'?"
            ),
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.constraint_manager.remove(
            constraint_id
        )

        self._refresh_physics_ui()

        self.properties_dock.clear_properties()

        self.status_bar.set_message(
            "Support deleted."
        )

    def _refresh_physics_ui(
        self,
    ) -> None:
        self.project_dock.refresh_physics(
            self.load_manager.all(),
            self.constraint_manager.all(),
        )

    # =====================================================
    # MATERIALS
    # =====================================================

    def _material_selection_changed(
        self,
        material_ids: list[str],
    ) -> None:
        if not material_ids:
            self.material_manager.select(
                None
            )

            if not self.scene.selected_objects():
                self.properties_dock.clear_properties()

            return

        self.scene.select([])

        material_id = material_ids[0]

        self.material_manager.select(
            material_id
        )

        material = (
            self.material_manager.get_selected()
        )

        if material:
            self.properties_dock.set_material(
                material
            )

            self.status_bar.set_message(
                f"Selected Material: "
                f"{material.name}"
            )

    def _edit_material(
        self,
        material_id: str,
    ) -> None:
        material = (
            self.material_manager.get(
                material_id
            )
        )

        if material is None:
            return

        if material.is_readonly:
            QMessageBox.information(
                self,
                "Read-Only Material",
                (
                    f"{material.name} is a built-in "
                    "material and cannot be edited."
                ),
            )
            return

        dialog = MaterialEditorDialog(
            material,
            self,
        )

        if not dialog.exec():
            return

        try:
            self.material_manager.update(
                material_id,
                **dialog.get_values(),
            )

            self._refresh_materials_ui()

            self.status_bar.set_message(
                "Custom material modified. "
                "Use 'Save Material' to persist it."
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Invalid Material",
                str(error),
            )

    def _reset_material(
        self,
        material_id: str,
    ) -> None:
        material = (
            self.material_manager.get(
                material_id
            )
        )

        if material is None:
            return

        if material.is_readonly:
            QMessageBox.information(
                self,
                "Read-Only Material",
                "Built-in materials cannot be reset.",
            )
            return

        self.material_manager.reset_custom(
            material_id
        )

        self._refresh_materials_ui()

        self.status_bar.set_message(
            "Custom material reset."
        )

    def _save_material(
        self,
    ) -> None:
        try:
            self.material_manager.save()

            self._refresh_materials_ui()

            self.status_bar.set_message(
                "Material library saved."
            )

        except IOError as error:
            QMessageBox.critical(
                self,
                "Save Error",
                str(error),
            )

    def _refresh_materials_ui(
        self,
    ) -> None:
        self.project_dock.refresh_materials(
            self.material_manager.materials()
        )

        material = (
            self.material_manager.get_selected()
        )

        if material:
            self.properties_dock.set_material(
                material
            )

    # =====================================================
    # PROJECT / GEOMETRY
    # =====================================================

    def new_project(
        self,
    ) -> None:
        self.clear_generated_mesh()

        self.scene.clear()

        self.load_manager.clear()
        self.constraint_manager.clear()

        self.viewport.rebuild_scene()

        self.project_dock.set_project_name(
            "Atlas Project"
        )

        self.project_dock.refresh_physics(
            [],
            [],
        )

        self.properties_dock.clear_properties()

        self.material_manager.select(
            None
        )

        self.current_geometry_path = None
        self.current_project_path = None

        self.status_bar.clear_geometry()

        self.status_bar.set_project(
            "Untitled Project"
        )

        self.status_bar.set_message(
            "New Project"
        )

    def open_geometry(
        self,
    ) -> None:
        filename, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Import Geometry",
                "",
                self.GEOMETRY_FILTER,
            )
        )

        if filename:
            self.load_geometry_file(
                filename
            )

    def load_geometry_file(
        self,
        filename: str,
        metadata: dict | None = None,
    ) -> bool:
        try:
            if len(
                self.scene.objects
            ):
                self.new_project()

            path = (
                self.geometry_loader.load(
                    filename
                )
            )

            obj = (
                self.viewport.add_geometry(
                    path,
                    metadata,
                )
            )

            self.current_geometry_path = path

            self.project_manager.add_recent_file(
                path
            )

            logging.info(
                "Geometry imported: %s",
                path,
            )

            self._refresh_recent_files()

            self.status_bar.set_message(
                f"Imported: "
                f"{obj.display_name}"
            )

            return True

        except (
            FileNotFoundError,
            ValueError,
        ) as error:
            self.status_bar.set_error(
                str(error)
            )

            logging.warning(
                "Geometry import failed: %s",
                error,
            )

        except Exception as error:
            self.status_bar.set_error(
                f"Could not read geometry: "
                f"{error}"
            )

            logging.exception(
                "Geometry import failed"
            )

        return False

    # =====================================================
    # SELECTION
    # =====================================================

    def _selection_changed(
        self,
        ids: list[str],
    ) -> None:
        selected = (
            self.scene.selected_objects()
        )

        if selected:
            self.material_manager.select(
                None
            )

        if len(selected) == 1:
            self.properties_dock.set_scene_object(
                selected[0]
            )

        elif not selected:
            if not self.material_manager.get_selected():
                self.properties_dock.clear_properties()

        self._scene_changed()

    def _scene_changed(
        self,
    ) -> None:
        stats = (
            self.scene.statistics()
        )

        selected = (
            self.scene.selected_objects()
        )

        if len(selected) == 1:
            name = selected[0].display_name

        elif selected:
            name = (
                f"{len(selected)} objects"
            )

        else:
            name = "None"

        self.status_bar.set_scene_statistics(
            **stats,
            selected=name,
        )

    def rename_object(
        self,
        object_id: str,
        name: str | None = None,
    ) -> None:
        obj = (
            self.scene.objects.get(
                object_id
            )
        )

        if not obj:
            return

        if name is None:
            name, ok = (
                QInputDialog.getText(
                    self,
                    "Rename Geometry",
                    "Name:",
                    text=obj.display_name,
                )
            )

            name = (
                name
                if ok
                else ""
            )

        if name and name.strip():
            self.scene.update_object(
                object_id,
                display_name=name.strip(),
            )

    def delete_selected(
        self,
    ) -> None:
        self.delete_objects(
            self.scene.selection.selected_ids
        )

    def delete_objects(
        self,
        object_ids: list[str],
    ) -> None:
        if not object_ids:
            return

        for object_id in object_ids:
            self.load_manager.remove_for_object(
                object_id
            )

            self.constraint_manager.remove_for_object(
                object_id
            )

        removed = (
            self.scene.remove(
                object_ids
            )
        )

        self.viewport.remove_objects(
            removed
        )

        self._refresh_physics_ui()

        self.status_bar.set_message(
            f"Deleted {len(removed)} object(s)"
        )

    def _viewport_command(
        self,
        object_id: str,
        command: str,
    ) -> None:
        if command == "delete":
            self.delete_objects(
                [object_id]
            )

        elif command == "rename":
            self.rename_object(
                object_id
            )

    # =====================================================
    # RECENT FILES / SCREENSHOTS
    # =====================================================

    def _refresh_recent_files(
        self,
    ) -> None:
        files = (
            self.project_manager
            .recent_files()
        )

        self.menu_bar.set_recent_files(
            files
        )

        self.viewport.set_recent_files(
            files
        )

    def save_screenshot(
        self,
    ) -> None:
        filename, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Save Screenshot",
                "atlas_view.png",
                "PNG (*.png)",
            )
        )

        if filename:
            self.viewport.take_screenshot(
                filename
            )

            self.project_dock.add_screenshot(
                Path(filename).name
            )

            self.status_bar.set_message(
                f"Screenshot saved: "
                f"{Path(filename).name}"
            )

    # =====================================================
    # PROJECT PERSISTENCE
    # =====================================================

    def _project_data(
        self,
    ) -> dict:
        return {
            "format": "Atlas Project",
            "version": "0.0.9",

            "objects": [
                obj.to_project_dict()
                for obj in self.scene.objects
            ],

            "camera": (
                self.viewport.camera_state()
                if len(self.scene.objects)
                else None
            ),

            "selection": (
                self.scene.selection.selected_ids
            ),

            "materials": {},

            "mesh": {},

            "physics": {
                "loads": (
                    self.load_manager.to_list()
                ),
                "constraints": (
                    self.constraint_manager.to_list()
                ),
            },

            "results": {},
        }

    def save_project(
        self,
    ) -> None:
        filename, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Save Atlas Project",
                self.current_project_path
                or "untitled.atlas",
                self.PROJECT_FILTER,
            )
        )

        if not filename:
            return

        if not filename.lower().endswith(
            ".atlas"
        ):
            filename += ".atlas"

        try:
            self.project_manager.save_project(
                filename,
                self._project_data(),
            )

            self.current_project_path = (
                filename
            )

            self.project_manager.add_recent_project(
                filename
            )

            self.project_dock.set_project_name(
                Path(filename).stem
            )

            self.status_bar.set_project(
                Path(filename).stem
            )

            self.status_bar.set_message(
                f"Project saved: "
                f"{Path(filename).name}"
            )

            logging.info(
                "Project saved: %s",
                filename,
            )

        except OSError as error:
            self.status_bar.set_error(
                f"Could not save project: "
                f"{error}"
            )

    def open_project(
        self,
    ) -> None:
        filename, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Open Atlas Project",
                "",
                self.PROJECT_FILTER,
            )
        )

        if filename:
            self._load_project(
                filename
            )

    def _load_project(
        self,
        filename: str,
    ) -> bool:
        try:
            data = (
                self.project_manager
                .open_project(filename)
            )

            self.new_project()

            objects = data.get(
                "objects"
            )

            if (
                objects is None
                and data.get(
                    "geometry_path"
                )
            ):
                objects = [
                    {
                        "file_path": data[
                            "geometry_path"
                        ],
                        "wireframe": data.get(
                            "wireframe",
                            False,
                        ),
                    }
                ]

            for item in (
                objects or []
            ):
                if not self.load_geometry_file(
                    item["file_path"],
                    item,
                ):
                    raise ValueError(
                        f"Could not load "
                        f"{item['file_path']}"
                    )

            physics = data.get(
                "physics",
                {},
            )

            self.load_manager.from_list(
                physics.get(
                    "loads",
                    [],
                )
            )

            self.constraint_manager.from_list(
                physics.get(
                    "constraints",
                    [],
                )
            )

            self._refresh_physics_ui()

            if data.get(
                "camera"
            ):
                self.viewport.restore_camera(
                    data["camera"]
                )

            self.scene.select(
                data.get(
                    "selection",
                    [],
                )
            )

            self.current_project_path = (
                filename
            )

            self.project_manager.add_recent_project(
                filename
            )

            self.project_dock.set_project_name(
                Path(filename).stem
            )

            self.status_bar.set_project(
                Path(filename).stem
            )

            self.status_bar.set_message(
                f"Project opened: "
                f"{Path(filename).name}"
            )

            logging.info(
                "Project opened: %s",
                filename,
            )

            return True

        except (
            ValueError,
            KeyError,
        ) as error:
            self.status_bar.set_error(
                str(error)
            )

            logging.exception(
                "Project open failed"
            )

        return False

    # =====================================================
    # AUTOSAVE
    # =====================================================

    def _autosave(
        self,
    ) -> None:
        if len(
            self.scene.objects
        ):
            try:
                self.project_manager.save_project(
                    str(
                        Path.cwd()
                        / "autosave.atlas"
                    ),
                    self._project_data(),
                )

            except OSError:
                logging.exception(
                    "Autosave failed"
                )