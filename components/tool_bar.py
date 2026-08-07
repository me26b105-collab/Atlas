"""Atlas Toolbar Component."""

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QApplication, QStyle, QToolBar


class AtlasToolBar(QToolBar):
    """Main toolbar arranged into project, camera, view, and export groups."""

    new_project_requested = Signal()
    open_geometry_requested = Signal()
    reset_camera_requested = Signal()
    fit_to_screen_requested = Signal()
    shaded_requested = Signal()
    wireframe_requested = Signal()
    screenshot_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setObjectName("MainToolBar")
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(22, 22))
        self._build_toolbar()

    def _add_standard_action(self, icon, text: str, tooltip: str, status: str, signal) -> None:
        action = self.addAction(icon, text)
        action.setToolTip(tooltip)
        action.setStatusTip(status)
        action.triggered.connect(signal.emit)

    def _build_toolbar(self) -> None:
        style = QApplication.style()
        # Project
        self._add_standard_action(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "New", "New Project (Ctrl+N)", "Clear the current workspace", self.new_project_requested)
        self._add_standard_action(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "Open", "Open Geometry (Ctrl+O)", "Import an STL or OBJ geometry file", self.open_geometry_requested)
        self.addSeparator()
        # Camera
        self._add_standard_action(style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp), "Fit", "Fit to Screen (F)", "Fit geometry within the viewport", self.fit_to_screen_requested)
        self._add_standard_action(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Reset", "Reset Camera (R)", "Restore the default camera view", self.reset_camera_requested)
        self.addSeparator()
        # View
        self._add_standard_action(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton), "Wireframe", "Wireframe View (W)", "Toggle wireframe rendering", self.wireframe_requested)
        self._add_standard_action(style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Shaded", "Shaded View (S)", "Display a solid shaded surface", self.shaded_requested)
        self.addSeparator()
        # Export
        self._add_standard_action(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Screenshot", "Save Screenshot (Ctrl+Shift+S)", "Export the current viewport as PNG", self.screenshot_requested)
