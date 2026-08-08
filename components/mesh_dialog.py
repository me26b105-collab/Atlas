"""Atlas mesh controls dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QSpinBox,
)

from geometry.mesher import MeshSettings


class MeshDialog(QDialog):
    """Collect meshing settings from the user."""

    def __init__(
        self,
        settings: MeshSettings | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Atlas Mesh Controls")
        self.resize(420, 220)

        settings = settings or MeshSettings()

        layout = QFormLayout(self)

        self.mesh_type = QComboBox()
        self.mesh_type.addItems(
            [
                "Surface",
                "Volume",
            ]
        )

        self.mesh_type.setCurrentText(
            settings.mesh_type
        )

        self.target_size = QDoubleSpinBox()
        self.target_size.setRange(
            0.001,
            1e6,
        )
        self.target_size.setDecimals(4)
        self.target_size.setValue(
            settings.target_size
        )

        self.refinement = QSpinBox()
        self.refinement.setRange(
            0,
            5,
        )
        self.refinement.setValue(
            settings.refinement
        )

        self.quality = QComboBox()
        self.quality.addItems(
            [
                "scaled_jacobian",
            ]
        )

        self.quality.setCurrentText(
            settings.quality_measure
        )

        layout.addRow(
            "Mesh Type",
            self.mesh_type,
        )

        layout.addRow(
            "Target Element Size",
            self.target_size,
        )

        layout.addRow(
            "Refinement Level",
            self.refinement,
        )

        layout.addRow(
            "Quality Metric",
            self.quality,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addRow(buttons)

    def get_settings(self) -> MeshSettings:
        """Return the selected meshing settings."""

        return MeshSettings(
            mesh_type=self.mesh_type.currentText(),
            target_size=self.target_size.value(),
            refinement=self.refinement.value(),
            quality_measure=self.quality.currentText(),
        )