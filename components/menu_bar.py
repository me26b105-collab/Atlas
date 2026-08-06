"""Atlas Menu Bar Component."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenuBar


class AtlasMenuBar(QMenuBar):
    """Main menu bar configured with core software categories."""

    # ---------- File ----------
    new_project_requested = Signal()
    open_geometry_requested = Signal()
    exit_requested = Signal()

    # ---------- View ----------
    reset_camera_requested = Signal()
    fit_to_screen_requested = Signal()
    shaded_view_requested = Signal()
    toggle_wireframe_requested = Signal()
    screenshot_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_menus()

    def _build_menus(self) -> None:
        """Construct the Atlas menu bar."""

        # ==========================================================
        # File
        # ==========================================================
        file_menu = self.addMenu("&File")

        new_action = file_menu.addAction("New Project")
        new_action.triggered.connect(
            self.new_project_requested.emit
        )

        open_action = file_menu.addAction("Open Geometry...")
        open_action.triggered.connect(
            self.open_geometry_requested.emit
        )

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(
            self.exit_requested.emit
        )

        # ==========================================================
        # Edit
        # ==========================================================
        edit_menu = self.addMenu("&Edit")

        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")

        # ==========================================================
        # View
        # ==========================================================
        view_menu = self.addMenu("&View")

        # Camera controls
        reset_camera = view_menu.addAction("Reset Camera")
        reset_camera.triggered.connect(
            self.reset_camera_requested.emit
        )

        fit_screen = view_menu.addAction("Fit To Screen")
        fit_screen.triggered.connect(
            self.fit_to_screen_requested.emit
        )

        view_menu.addSeparator()

        # Display modes
        shaded = view_menu.addAction("Shaded")
        shaded.triggered.connect(
            self.shaded_view_requested.emit
        )

        wireframe = view_menu.addAction("Wireframe")
        wireframe.triggered.connect(
            self.toggle_wireframe_requested.emit
        )

        view_menu.addSeparator()

        # Export
        screenshot = view_menu.addAction("Save Screenshot...")
        screenshot.triggered.connect(
            self.screenshot_requested.emit
        )

        # ==========================================================
        # Simulation
        # ==========================================================
        sim_menu = self.addMenu("&Simulation")

        sim_menu.addAction("Model Setup")
        sim_menu.addAction("Materials")
        sim_menu.addAction("Mesh")
        sim_menu.addAction("Boundary Conditions")

        # ==========================================================
        # AI
        # ==========================================================
        ai_menu = self.addMenu("&AI")

        ai_menu.addAction("Mesh Optimization Assistant")
        ai_menu.addAction("Topology Optimization")
        ai_menu.addAction("Design Space Exploration")

        # ==========================================================
        # Help
        # ==========================================================
        help_menu = self.addMenu("&Help")

        help_menu.addAction("Documentation")
        help_menu.addAction("About Atlas")