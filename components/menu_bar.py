"""Atlas Menu Bar Component."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar


class AtlasMenuBar(QMenuBar):
    """Main menu bar configured with core software categories."""

    # ---------- File ----------
    new_project_requested = Signal()
    open_geometry_requested = Signal()
    open_project_requested = Signal()
    save_project_requested = Signal()
    clear_project_requested = Signal()
    exit_requested = Signal()

    # ---------- View ----------
    reset_camera_requested = Signal()
    fit_to_screen_requested = Signal()
    shaded_view_requested = Signal()
    toggle_wireframe_requested = Signal()
    screenshot_requested = Signal()
    recent_file_requested = Signal(str)
    recent_project_requested = Signal(str)
    preferences_requested = Signal()

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
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(
            self.new_project_requested.emit
        )

        open_action = file_menu.addAction("Open Geometry...")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(
            self.open_geometry_requested.emit
        )

        open_project_action = file_menu.addAction("Open Atlas Project...")
        open_project_action.triggered.connect(self.open_project_requested.emit)

        save_project_action = file_menu.addAction("Save Project...")
        save_project_action.triggered.connect(self.save_project_requested.emit)

        self.recent_menu = file_menu.addMenu("Recent Geometry")
        self._set_recent_actions([])
        self.recent_projects_menu = file_menu.addMenu("Recent Projects")
        self._set_recent_project_actions([])

        clear_action = file_menu.addAction("Clear Project")
        clear_action.triggered.connect(self.clear_project_requested.emit)

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
        preferences = edit_menu.addAction("Preferences…")
        preferences.triggered.connect(self.preferences_requested.emit)

        # ==========================================================
        # View
        # ==========================================================
        view_menu = self.addMenu("&View")

        # Camera controls
        reset_camera = view_menu.addAction("Reset Camera")
        reset_camera.setShortcut(QKeySequence("R"))
        reset_camera.triggered.connect(
            self.reset_camera_requested.emit
        )

        fit_screen = view_menu.addAction("Fit To Screen")
        fit_screen.setShortcut(QKeySequence("F"))
        fit_screen.triggered.connect(
            self.fit_to_screen_requested.emit
        )

        view_menu.addSeparator()

        # Display modes
        shaded = view_menu.addAction("Shaded")
        shaded.setShortcut(QKeySequence("S"))
        shaded.triggered.connect(
            self.shaded_view_requested.emit
        )

        wireframe = view_menu.addAction("Wireframe")
        wireframe.setShortcut(QKeySequence("W"))
        wireframe.triggered.connect(
            self.toggle_wireframe_requested.emit
        )

        view_menu.addSeparator()

        # Export
        screenshot = view_menu.addAction("Save Screenshot...")
        screenshot.setShortcut(QKeySequence("Ctrl+Shift+S"))
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

    def set_recent_files(self, files: list[str]) -> None:
        """Refresh the recent-geometry submenu."""
        self._set_recent_actions(files)

    def _set_recent_actions(self, files: list[str]) -> None:
        self.recent_menu.clear()
        if not files:
            action = self.recent_menu.addAction("No recent geometry")
            action.setEnabled(False)
            return

        for filename in files:
            action = QAction(Path(filename).name, self)
            action.setToolTip(filename)
            action.triggered.connect(
                lambda checked=False, path=filename: self.recent_file_requested.emit(path)
            )
            self.recent_menu.addAction(action)

    def set_recent_projects(self, files: list[str]) -> None:
        """Refresh the independent recent-project submenu."""
        self._set_recent_project_actions(files)

    def _set_recent_project_actions(self, files: list[str]) -> None:
        self.recent_projects_menu.clear()
        if not files:
            action = self.recent_projects_menu.addAction("No recent projects")
            action.setEnabled(False)
            return
        for filename in files:
            action = QAction(Path(filename).name, self)
            action.setToolTip(filename)
            action.triggered.connect(lambda checked=False, path=filename: self.recent_project_requested.emit(path))
            self.recent_projects_menu.addAction(action)
