"""Atlas mesh controls and statistics dock."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QDockWidget,
)


class MeshDock(QDockWidget):
    """User interface for Atlas meshing operations."""

    surface_mesh_requested = Signal(float, int)
    volume_mesh_requested = Signal(float, int)
    clear_mesh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Mesh", parent)

        self.setObjectName("MeshDock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._setup_ui()

    def _setup_ui(self) -> None:
        container = QWidget(self)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # -------------------------------------------------
        # Mesh controls
        # -------------------------------------------------

        controls = QGroupBox("Mesh Controls")
        form = QFormLayout(controls)

        self.element_size = QDoubleSpinBox()
        self.element_size.setRange(0.001, 1e6)
        self.element_size.setDecimals(3)
        self.element_size.setValue(1.0)
        self.element_size.setSuffix(" units")

        self.refinement = QSpinBox()
        self.refinement.setRange(0, 3)
        self.refinement.setValue(0)

        form.addRow(
            "Element Size",
            self.element_size,
        )

        form.addRow(
            "Refinement",
            self.refinement,
        )

        layout.addWidget(controls)

        # -------------------------------------------------
        # Surface mesh
        # -------------------------------------------------

        surface_group = QGroupBox("Surface Mesh")
        surface_layout = QVBoxLayout(surface_group)

        self.surface_button = QPushButton(
            "Generate Surface Mesh"
        )

        self.surface_button.clicked.connect(
            self._generate_surface
        )

        surface_layout.addWidget(
            self.surface_button
        )

        layout.addWidget(surface_group)

        # -------------------------------------------------
        # Volume mesh
        # -------------------------------------------------

        volume_group = QGroupBox("Volume Mesh")
        volume_layout = QVBoxLayout(volume_group)

        self.volume_button = QPushButton(
            "Generate Volume Mesh"
        )

        self.volume_button.clicked.connect(
            self._generate_volume
        )

        volume_layout.addWidget(
            self.volume_button
        )

        layout.addWidget(volume_group)

        # -------------------------------------------------
        # Statistics
        # -------------------------------------------------

        statistics = QGroupBox("Mesh Statistics")
        stats_layout = QFormLayout(statistics)

        self.points_label = QLabel("—")
        self.cells_label = QLabel("—")
        self.surface_cells_label = QLabel("—")
        self.volume_cells_label = QLabel("—")
        self.memory_label = QLabel("—")

        stats_layout.addRow(
            "Nodes",
            self.points_label,
        )

        stats_layout.addRow(
            "Total Cells",
            self.cells_label,
        )

        stats_layout.addRow(
            "Surface Cells",
            self.surface_cells_label,
        )

        stats_layout.addRow(
            "Volume Cells",
            self.volume_cells_label,
        )

        stats_layout.addRow(
            "Memory",
            self.memory_label,
        )

        layout.addWidget(statistics)

        # -------------------------------------------------
        # Quality
        # -------------------------------------------------

        quality = QGroupBox("Mesh Quality")
        quality_layout = QFormLayout(quality)

        self.minimum_quality = QLabel("—")
        self.average_quality = QLabel("—")
        self.maximum_quality = QLabel("—")

        quality_layout.addRow(
            "Minimum",
            self.minimum_quality,
        )

        quality_layout.addRow(
            "Average",
            self.average_quality,
        )

        quality_layout.addRow(
            "Maximum",
            self.maximum_quality,
        )

        layout.addWidget(quality)

        # -------------------------------------------------
        # Clear
        # -------------------------------------------------

        self.clear_button = QPushButton(
            "Clear Generated Mesh"
        )

        self.clear_button.clicked.connect(
            self.clear_mesh_requested.emit
        )

        layout.addWidget(self.clear_button)

        layout.addStretch()

        self.setWidget(container)

    def _generate_surface(self) -> None:
        self.surface_mesh_requested.emit(
            self.element_size.value(),
            self.refinement.value(),
        )

    def _generate_volume(self) -> None:
        self.volume_mesh_requested.emit(
            self.element_size.value(),
            self.refinement.value(),
        )

    def set_statistics(
        self,
        points: int,
        cells: int,
        surface_cells: int,
        volume_cells: int,
        memory_mb: float,
    ) -> None:
        """Display mesh statistics."""

        self.points_label.setText(
            f"{points:,}"
        )

        self.cells_label.setText(
            f"{cells:,}"
        )

        self.surface_cells_label.setText(
            f"{surface_cells:,}"
        )

        self.volume_cells_label.setText(
            f"{volume_cells:,}"
        )

        self.memory_label.setText(
            f"{memory_mb:.2f} MB"
        )

    def set_quality(
        self,
        minimum: float | None,
        average: float | None,
        maximum: float | None,
    ) -> None:
        """Display quality values."""

        self.minimum_quality.setText(
            "—"
            if minimum is None
            else f"{minimum:.6g}"
        )

        self.average_quality.setText(
            "—"
            if average is None
            else f"{average:.6g}"
        )

        self.maximum_quality.setText(
            "—"
            if maximum is None
            else f"{maximum:.6g}"
        )

    def clear_statistics(self) -> None:
        """Reset the statistics display."""

        self.set_statistics(
            0,
            0,
            0,
            0,
            0.0,
        )

        self.set_quality(
            None,
            None,
            None,
        )