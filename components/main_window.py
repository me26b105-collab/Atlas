"""
Atlas Main Application Window.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMainWindow

from components.menu_bar import AtlasMenuBar
from components.project_dock import ProjectDock
from components.properties_dock import PropertiesDock
from components.status_bar import AtlasStatusBar
from components.tool_bar import AtlasToolBar
from components.viewport import AtlasViewport

from geometry.geometry_loader import GeometryLoader


class AtlasMainWindow(QMainWindow):
    """Main Atlas window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Atlas")
        self.resize(1400, 900)

        self.geometry_loader = GeometryLoader()

        self._init_layout()
        self._connect_signals()

    # ==========================================================
    # UI
    # ==========================================================

    def _init_layout(self) -> None:

        self.viewport = AtlasViewport(self)
        self.setCentralWidget(self.viewport)

        self.menu_bar = AtlasMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.tool_bar = AtlasToolBar(self)
        self.addToolBar(
            Qt.ToolBarArea.TopToolBarArea,
            self.tool_bar,
        )

        self.project_dock = ProjectDock(self)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.project_dock,
        )

        self.properties_dock = PropertiesDock(self)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.properties_dock,
        )

        self.status_bar = AtlasStatusBar(self)
        self.setStatusBar(self.status_bar)

    # ==========================================================
    # Signals
    # ==========================================================

    def _connect_signals(self) -> None:

        # ---------- Menu ----------

        self.menu_bar.new_project_requested.connect(
            self.new_project
        )

        self.menu_bar.open_geometry_requested.connect(
            self.open_geometry
        )

        self.menu_bar.exit_requested.connect(
            self.close
        )

        self.menu_bar.reset_camera_requested.connect(
            self.viewport.reset_camera
        )

        self.menu_bar.fit_to_screen_requested.connect(
            self.viewport.fit_to_screen
        )

        self.menu_bar.shaded_view_requested.connect(
            self.viewport.set_shaded
        )

        self.menu_bar.toggle_wireframe_requested.connect(
            self.viewport.toggle_wireframe
        )

        self.menu_bar.screenshot_requested.connect(
            self.save_screenshot
        )

        # ---------- Toolbar ----------

        self.tool_bar.new_project_requested.connect(
            self.new_project
        )

        self.tool_bar.open_geometry_requested.connect(
            self.open_geometry
        )

        self.tool_bar.reset_camera_requested.connect(
            self.viewport.reset_camera
        )

        self.tool_bar.fit_to_screen_requested.connect(
            self.viewport.fit_to_screen
        )

        self.tool_bar.shaded_requested.connect(
            self.viewport.set_shaded
        )

        self.tool_bar.wireframe_requested.connect(
            self.viewport.toggle_wireframe
        )

        self.tool_bar.screenshot_requested.connect(
            self.save_screenshot
        )

        # ---------- Drag & Drop ----------

        self.viewport.geometry_dropped.connect(
            self.load_geometry_file
        )

    # ==========================================================
    # Project
    # ==========================================================

    def new_project(self) -> None:
        """Create a fresh empty project."""

        # Clear the project tree
        self.project_dock.clear_tree()

        # Clear the properties panel
        self.properties_dock.clear_properties()

        # Clear the viewport
        self.viewport.plotter.clear()

        # Reset viewport state
        self.viewport.mesh_actor = None
        self.viewport.current_mesh = None
        self.viewport.wireframe_enabled = False

        # Show the welcome screen again
        self.viewport.stack.setCurrentIndex(0)

        # Reset the status bar
        self.status_bar.clear_geometry()
        self.status_bar.set_message("New Project")

    # ==========================================================
    # Geometry
    # ==========================================================

    def open_geometry(self) -> None:
        """Open a geometry file."""

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Geometry",
            "",
            "Geometry Files (*.stl *.obj)",
        )

        if filename:
            self.load_geometry_file(filename)

    def load_geometry_file(self, filename: str) -> None:
        """
        Central geometry loading function.

        BOTH File->Open and Drag&Drop use this.
        """

        try:

            path = self.geometry_loader.load(filename)

            self.viewport.load_geometry(path)

            mesh = self.viewport.current_mesh

            self.project_dock.set_geometry_file(
                Path(path).name
            )

            self.properties_dock.set_geometry(
                path,
                mesh,
            )

            self.status_bar.set_geometry_info(
                Path(path).name,
                mesh.n_points,
                mesh.n_cells,
            )

            self.status_bar.set_message(
                f"Loaded: {Path(path).name}"
            )

        except Exception as error:

            self.status_bar.set_message(
                str(error)
            )

    # ==========================================================
    # Screenshot
    # ==========================================================

    def save_screenshot(self) -> None:

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "atlas_view.png",
            "PNG (*.png)",
        )

        if not filename:
            return

        self.viewport.take_screenshot(filename)

        self.status_bar.set_message(
            f"Screenshot saved: {Path(filename).name}"
        )