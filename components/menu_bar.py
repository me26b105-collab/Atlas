"""Atlas Menu Bar Component."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenuBar


class AtlasMenuBar(QMenuBar):
    """Main menu bar configured with core software categories."""

    new_project_requested = Signal()
    open_geometry_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_menus()

    def _build_menus(self) -> None:
        # File Menu
        file_menu = self.addMenu("&File")

        new_action = file_menu.addAction("New Project")
        new_action.triggered.connect(self.new_project_requested.emit)

        open_action = file_menu.addAction("Open Geometry...")
        open_action.triggered.connect(self.open_geometry_requested.emit)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_requested.emit)

        # Edit
        edit_menu = self.addMenu("&Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")

        # View
        view_menu = self.addMenu("&View")
        view_menu.addAction("Reset Layout")

        # Simulation
        sim_menu = self.addMenu("&Simulation")
        sim_menu.addAction("Model Setup")

        # AI
        ai_menu = self.addMenu("&AI")
        ai_menu.addAction("Mesh Optimization Assistant")

        # Help
        help_menu = self.addMenu("&Help")
        help_menu.addAction("Documentation")
        help_menu.addAction("About Atlas")