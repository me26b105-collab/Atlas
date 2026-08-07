"""Atlas Status Bar Component."""

from PySide6.QtWidgets import QLabel, QStatusBar


class AtlasStatusBar(QStatusBar):
    """Three-part status bar for application, project, and geometry state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setSizeGripEnabled(False)
        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet("padding-left: 8px; color: #a0a5b0;")
        self.project_label = QLabel("Untitled Project")
        self.project_label.setStyleSheet("padding: 0 18px; color: #C3CBD6;")
        self.geometry_label = QLabel("Objects: 0 | Vertices: 0 | Cells: 0")
        self.geometry_label.setStyleSheet("padding-right: 12px; color: #7f8794;")
        self.addWidget(self.status_label, 1)
        self.addWidget(self.project_label, 1)
        self.addPermanentWidget(self.geometry_label)

    def set_message(self, message: str) -> None:
        self.status_label.setText(f"● {message}")

    def set_warning(self, message: str) -> None:
        self.status_label.setText(f"▲ {message}")

    def set_error(self, message: str) -> None:
        self.status_label.setText(f"● {message}")

    def set_geometry_info(self, filename: str, vertices: int, cells: int) -> None:
        self.geometry_label.setText(f"{filename} | {vertices:,} Vertices | {cells:,} Cells")

    def clear_geometry(self) -> None:
        self.geometry_label.setText("Objects: 0 | Vertices: 0 | Cells: 0")

    def set_scene_statistics(self, objects: int, vertices: int, cells: int, selected: str = "None") -> None:
        """Display scene-wide figures instead of a misleading single mesh value."""
        self.geometry_label.setText(f"Objects: {objects} | Vertices: {vertices:,} | Cells: {cells:,} | Selected: {selected}")

    def set_project(self, name: str) -> None:
        self.project_label.setText(name or "Untitled Project")
