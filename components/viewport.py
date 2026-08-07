"""Atlas viewport: a presentation adapter for the scene model."""

from pathlib import Path
from typing import Callable

import pyvista as pv
from pyvistaqt import QtInteractor
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QApplication, QColorDialog, QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QStackedLayout, QVBoxLayout

from geometry.scene import SceneManager, SceneObject


class AtlasViewport(QFrame):
    """Renders every body managed by :class:`SceneManager`."""

    geometry_dropped = Signal(str)
    new_project_requested = Signal()
    open_geometry_requested = Signal()
    recent_file_requested = Signal(str)
    loading_status_changed = Signal(str)
    object_picked = Signal(str)
    object_context_requested = Signal(str, str)

    def __init__(self, scene: SceneManager, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.current_mesh = None  # v0.0.5 compatibility: selected mesh
        self.mesh_actor = None
        self.wireframe_enabled = False
        self._recent_files: list[str] = []
        self._setup_ui()
        self.scene.selection.selection_changed.connect(self._selection_changed)
        self.scene.object_changed.connect(self._object_changed)

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedLayout(); self.stack.addWidget(self._build_welcome_page()); self.stack.addWidget(self._build_render_page())
        outer.addLayout(self.stack); self.setAcceptDrops(True)
        self.plotter.interactor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.plotter.interactor.customContextMenuRequested.connect(self._show_context_menu)
        #self.plotter.enable_mesh_picking(callback=self._mesh_picked, show=False, left_clicking=False, use_actor=True)

    def _build_welcome_page(self) -> QFrame:
        welcome = QFrame(); welcome.setObjectName("WelcomePage")
        layout = QVBoxLayout(welcome); layout.setContentsMargins(40, 40, 40, 28); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("ATLAS"); title.setObjectName("WelcomeTitle"); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version = QLabel("VERSION 0.0.6  •  SCENE ENGINE"); version.setObjectName("WelcomeVersion"); version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("A multi-body workspace for inspecting engineering geometry."); subtitle.setObjectName("WelcomeSubtitle"); subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions = QHBoxLayout(); actions.setSpacing(10)
        new_button = QPushButton("New Project"); new_button.setObjectName("WelcomePrimaryButton"); new_button.clicked.connect(self.new_project_requested.emit)
        open_button = QPushButton("Import Geometry"); open_button.setObjectName("WelcomeSecondaryButton"); open_button.clicked.connect(self.open_geometry_requested.emit)
        actions.addWidget(new_button); actions.addWidget(open_button)
        self.recent_files_label = QLabel(); self.recent_files_label.setObjectName("WelcomeRecents"); self.recent_files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recent_files_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction); self.recent_files_label.linkActivated.connect(self._open_recent_link)
        layout.addStretch(); layout.addWidget(title); layout.addWidget(version); layout.addSpacing(14); layout.addWidget(subtitle); layout.addSpacing(28); layout.addLayout(actions); layout.addSpacing(24); layout.addWidget(self.recent_files_label); layout.addStretch()
        return welcome

    def _build_render_page(self) -> QFrame:
        page = QFrame(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 0, 0, 0)
        self.plotter = QtInteractor(page); self.plotter.set_background("#2b2b2b"); self._add_scene_helpers(); layout.addWidget(self.plotter)
        return page

    def _add_scene_helpers(self) -> None:
        self.plotter.show_axes(); self.plotter.show_grid(color="#3F4652", font_size=8, location="outer")

    def set_recent_files(self, files: list[str]) -> None:
        self._recent_files = files
        if not files: self.recent_files_label.setText("RECENT GEOMETRY\nNo recent geometry"); return
        self.recent_files_label.setText("RECENT GEOMETRY\n" + "   •   ".join(f'<a href="{i}">{Path(p).name}</a>' for i, p in enumerate(files[:5])))

    def _open_recent_link(self, index: str) -> None:
        try: self.recent_file_requested.emit(self._recent_files[int(index)])
        except (ValueError, IndexError): pass

    def add_geometry(self, filename: str, metadata: dict | None = None) -> SceneObject:
        """Read a geometry file and add it without clearing the current scene."""
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            for stage in ("Reading Geometry", "Parsing", "Building Mesh"):
                self._report_loading(stage)
            mesh = pv.read(filename)
            if mesh.n_points == 0 or mesh.n_cells == 0: raise ValueError("The selected file contains no valid geometry.")
            self._report_loading("Creating Actor")
            obj = self.scene.add_mesh(filename, mesh, metadata)
            self._add_actor(obj)
            self._report_loading("Building Scene"); self.stack.setCurrentIndex(1)
            self.scene.select([obj.uuid]); self._report_loading("Updating UI")
            self.plotter.view_isometric(); self.plotter.reset_camera(); self._report_loading("Rendering"); self.plotter.render(); self._report_loading("Finished")
            return obj
        finally: QApplication.restoreOverrideCursor()

    def load_geometry(self, filename: str) -> None:
        """Compatibility entry point; v0.0.6 now imports additionally."""
        self.add_geometry(filename)

    def rebuild_scene(self) -> None:
        self.plotter.clear(); self._add_scene_helpers()
        for obj in self.scene.objects: self._add_actor(obj)
        if len(self.scene.objects): self.stack.setCurrentIndex(1)
        else: self.stack.setCurrentIndex(0)
        self.plotter.render()

    def _add_actor(self, obj: SceneObject) -> None:
        obj.actor = self.plotter.add_mesh(obj.mesh, color=obj.color, opacity=obj.opacity, show_edges=obj.edge_visibility,
        )
        self._apply_object_style(obj)

    def remove_objects(self, objects: list[SceneObject]) -> None:
        for obj in objects:
            if obj.actor: self.plotter.remove_actor(obj.actor, render=False)
        self.plotter.render()
        if not len(self.scene.objects): self.stack.setCurrentIndex(0)

    def _mesh_picked(self, mesh, actor) -> None:
        obj = next((item for item in self.scene.objects if item.actor == actor), None)
        if obj: self.scene.select([obj.uuid]); self.object_picked.emit(obj.uuid)

    def _selection_changed(self, ids: list[str]) -> None:
        selected = self.scene.selected_objects()
        self.current_mesh = selected[0].mesh if selected else None
        self.mesh_actor = selected[0].actor if selected else None
        self.wireframe_enabled = bool(selected and selected[0].wireframe)
        for obj in self.scene.objects: self._apply_object_style(obj)
        self.plotter.render()

    def _object_changed(self, object_id: str) -> None:
        obj = self.scene.objects.get(object_id)
        if obj: self._apply_object_style(obj)
        self.plotter.render()

    def _apply_object_style(self, obj: SceneObject) -> None:
        if not obj.actor: return
        obj.actor.SetVisibility(obj.visible)
        prop = obj.actor.GetProperty(); prop.SetOpacity(obj.opacity); prop.SetColor(*pv.Color(obj.color).float_rgb)
        prop.SetEdgeVisibility(obj.edge_visibility)
        if obj.wireframe: prop.SetRepresentationToWireframe()
        else: prop.SetRepresentationToSurface()
        prop.SetLineWidth(2.0 if obj.selected else 0.6)
        prop.SetEdgeColor(*(pv.Color("#FFD166" if obj.selected else "#505865").float_rgb))

    def _report_loading(self, message: str) -> None:
        self.loading_status_changed.emit(message); QApplication.processEvents()

    def reset_camera(self) -> None: self.plotter.reset_camera(); self.plotter.render()
    def fit_to_screen(self) -> None: self.reset_camera()
    def fit_selected(self) -> None:
        selected = self.scene.selected_objects()
        if selected and selected[0].actor: self.plotter.reset_camera(bounds=selected[0].bounds); self.plotter.render()
    def center_selected(self) -> None: self.fit_selected()
    def _set_view(self, callback: Callable) -> None: callback(); self.plotter.render()
    def view_front(self) -> None: self._set_view(self.plotter.view_yz)
    def view_back(self) -> None: self._set_view(lambda: self.plotter.view_yz(negative=True))
    def view_left(self) -> None: self._set_view(lambda: self.plotter.view_xz(negative=True))
    def view_right(self) -> None: self._set_view(self.plotter.view_xz)
    def view_top(self) -> None: self._set_view(self.plotter.view_xy)
    def view_bottom(self) -> None: self._set_view(lambda: self.plotter.view_xy(negative=True))
    def view_isometric(self) -> None: self._set_view(self.plotter.view_isometric)
    def toggle_wireframe(self) -> None:
        for obj in self.scene.selected_objects(): self.scene.update_object(obj.uuid, wireframe=not obj.wireframe)
    def set_shaded(self) -> None:
        for obj in self.scene.selected_objects(): self.scene.update_object(obj.uuid, wireframe=False)
    def take_screenshot(self, filename: str) -> None:
        self.plotter.set_background("white")
        self.plotter.render()

        self.plotter.screenshot(filename)

        self.plotter.set_background("#2b2b2b")
        self.plotter.render()
    def camera_state(self) -> list: return [list(point) for point in self.plotter.camera_position]
    def restore_camera(self, camera: list) -> None:
        if camera and len(camera) == 3: self.plotter.camera_position = camera; self.plotter.render()

    def _show_context_menu(self, position) -> None:
        menu = QMenu(self); selected = self.scene.selected_objects()
        if selected:
            obj = selected[0]
            for title, command in (("Rename", "rename"), ("Delete", "delete"), ("Hide" if obj.visible else "Show", "visibility"), ("Wireframe", "wireframe"), ("Shaded", "shaded"), ("Fit Object", "fit"), ("Center on Object", "center"), ("Color…", "color")):
                action = menu.addAction(title); action.triggered.connect(lambda checked=False, c=command, item=obj: self._context_command(c, item))
            menu.addSeparator()
        for name, callback in (("Front", self.view_front), ("Back", self.view_back), ("Left", self.view_left), ("Right", self.view_right), ("Top", self.view_top), ("Bottom", self.view_bottom), ("Isometric", self.view_isometric)):
            menu.addAction(name, callback)
        menu.exec(self.plotter.interactor.mapToGlobal(position))

    def _context_command(self, command: str, obj: SceneObject) -> None:
        if command == "visibility": self.scene.update_object(obj.uuid, visible=not obj.visible)
        elif command == "wireframe": self.scene.update_object(obj.uuid, wireframe=True)
        elif command == "shaded": self.scene.update_object(obj.uuid, wireframe=False)
        elif command == "fit": self.fit_selected()
        elif command == "center": self.center_selected()
        elif command == "color":
            color = QColorDialog.getColor(parent=self)
            if color.isValid(): self.scene.update_object(obj.uuid, color=color.name())
        else: self.object_context_requested.emit(obj.uuid, command)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls(): event.acceptProposedAction()
    def dropEvent(self, event) -> None:
        urls = event.mimeData().urls()

        if len(urls) != 1:
            return

        path = urls[0].toLocalFile()

        if path.lower().endswith((".stl", ".obj")):
            self.geometry_dropped.emit(path)