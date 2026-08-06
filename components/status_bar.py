"""Atlas Status Bar Component."""

from PySide6.QtWidgets import QLabel, QStatusBar


class AtlasStatusBar(QStatusBar):
    """Bottom status bar displaying application state."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the status bar widgets."""

        self.setSizeGripEnabled(False)

        # Left: current application status
        self.status_label = QLabel("🟢 Ready")
        self.status_label.setStyleSheet(
            "padding-left: 8px; color: #a0a5b0;"
        )

        # Right: geometry information
        self.geometry_label = QLabel("No Geometry Loaded")
        self.geometry_label.setStyleSheet(
            "padding-right: 12px; color: #7f8794;"
        )

        self.addWidget(self.status_label, 1)
        self.addPermanentWidget(self.geometry_label)

    def set_message(self, message: str) -> None:
        """Display a normal status message."""

        self.status_label.setText(f"🟢 {message}")

    def set_warning(self, message: str) -> None:
        """Display a warning message."""

        self.status_label.setText(f"🟡 {message}")

    def set_error(self, message: str) -> None:
        """Display an error message."""

        self.status_label.setText(f"🔴 {message}")

    def set_geometry_info(
        self,
        filename: str,
        vertices: int,
        cells: int,
    ) -> None:
        """Display information about the currently loaded geometry."""

        self.geometry_label.setText(
            f"{filename} | {vertices:,} Vertices | {cells:,} Cells"
        )

    def clear_geometry(self) -> None:
        """Reset geometry information."""

        self.geometry_label.setText(
            "No Geometry Loaded"
        )