"""Atlas Toolbar Component."""

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QToolBar,
)


class AtlasToolBar(QToolBar):
    """Main application toolbar."""

    # ---------- File ----------
    new_project_requested = Signal()
    open_geometry_requested = Signal()

    # ---------- View ----------
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

    def _build_toolbar(self):
        """Create toolbar buttons."""

        style = QApplication.style()

        # ==========================================================
        # File
        # ==========================================================

        new_action = self.addAction(
            style.standardIcon(QStyle.StandardPixmap.SP_FileIcon),
            "New",
        )
        new_action.triggered.connect(
            self.new_project_requested.emit
        )

        open_action = self.addAction(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton),
            "Open",
        )
        open_action.triggered.connect(
            self.open_geometry_requested.emit
        )

        self.addSeparator()

        # ==========================================================
        # Camera
        # ==========================================================

        reset_action = self.addAction(
            style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload),
            "Reset Camera",
        )
        reset_action.triggered.connect(
            self.reset_camera_requested.emit
        )

        fit_action = self.addAction(
            style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp),
            "Fit",
        )
        fit_action.triggered.connect(
            self.fit_to_screen_requested.emit
        )

        self.addSeparator()

        # ==========================================================
        # Display
        # ==========================================================

        shaded_action = self.addAction(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Shaded",
        )
        shaded_action.triggered.connect(
            self.shaded_requested.emit
        )

        wireframe_action = self.addAction(
            style.standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton),
            "Wireframe",
        )
        wireframe_action.triggered.connect(
            self.wireframe_requested.emit
        )

        self.addSeparator()

        # ==========================================================
        # Screenshot
        # ==========================================================

        screenshot_action = self.addAction(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            "Screenshot",
        )
        screenshot_action.triggered.connect(
            self.screenshot_requested.emit
        )