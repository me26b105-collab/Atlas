"""Atlas Main Application Window."""

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
    """Central container window assembling all docks, tools, and workspaces."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Atlas")
        self.resize(1400, 900)

        self.geometry_loader = GeometryLoader()

        self._init_layout()
        self._connect_signals()

    def _init_layout(self) -> None:
        # Central Workspace
        self.viewport = AtlasViewport(self)
        self.setCentralWidget(self.viewport)

        # Menu Bar
        self.menu_bar = AtlasMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Toolbar
        self.tool_bar = AtlasToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar)

        # Left Dock
        self.project_dock = ProjectDock(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)

        # Right Dock
        self.properties_dock = PropertiesDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        # Status Bar
        self.status_bar = AtlasStatusBar(self)
        self.setStatusBar(self.status_bar)

    def _connect_signals(self) -> None:
        self.menu_bar.new_project_requested.connect(self.new_project)
        self.menu_bar.open_geometry_requested.connect(self.open_geometry)
        self.menu_bar.exit_requested.connect(self.close)

    def new_project(self) -> None:
        self.project_dock.clear_tree()
        self.viewport.plotter.clear()
        self.status_bar.set_message("New Project")

    def open_geometry(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Geometry",
            "",
            "Geometry Files (*.stl *.obj)",
        )

        if not filename:
            return

        try:
            path = self.geometry_loader.load(filename)

            self.viewport.load_geometry(path)

            self.project_dock.set_geometry_file(Path(path).name)

            self.status_bar.set_message(
                f"Loaded: {Path(path).name}"
            )

        except Exception as e:
            self.status_bar.set_message(str(e))