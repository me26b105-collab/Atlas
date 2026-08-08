"""Atlas Physics Editor Dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)


class PhysicsEditorDialog(QDialog):
    """Create or edit a load/support."""

    def __init__(
        self,
        entity_type: str,
        entity=None,
        object_name: str = "",
        parent=None,
    ):
        super().__init__(parent)

        self.entity_type = entity_type
        self.entity = entity

        title = (
            f"Edit {entity_type}"
            if entity is not None
            else f"Add {entity_type}"
        )

        self.setWindowTitle(title)
        self.resize(440, 420)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name = QLineEdit()

        self.type_box = QComboBox()

        if entity_type == "Load":
            self.type_box.addItems(
                [
                    "Force",
                    "Pressure",
                    "Gravity",
                    "Moment",
                ]
            )
        else:
            self.type_box.addItems(
                [
                    "Fixed",
                    "Pin",
                    "Roller",
                ]
            )

        self.magnitude = QDoubleSpinBox()
        self.magnitude.setRange(
            0.0,
            1e30,
        )
        self.magnitude.setDecimals(6)
        self.magnitude.setSingleStep(1.0)

        self.direction_x = QDoubleSpinBox()
        self.direction_y = QDoubleSpinBox()
        self.direction_z = QDoubleSpinBox()

        self.location_x = QDoubleSpinBox()
        self.location_y = QDoubleSpinBox()
        self.location_z = QDoubleSpinBox()

        for box in (
            self.direction_x,
            self.direction_y,
            self.direction_z,
            self.location_x,
            self.location_y,
            self.location_z,
        ):
            box.setRange(
                -1e12,
                1e12,
            )
            box.setDecimals(6)

        self.geometry = QLineEdit(
            object_name
        )
        self.geometry.setReadOnly(True)

        form.addRow(
            "Name",
            self.name,
        )

        form.addRow(
            "Type",
            self.type_box,
        )

        if entity_type == "Load":
            form.addRow(
                "Magnitude",
                self.magnitude,
            )

        form.addRow(
            "Direction X",
            self.direction_x,
        )

        form.addRow(
            "Direction Y",
            self.direction_y,
        )

        form.addRow(
            "Direction Z",
            self.direction_z,
        )

        form.addRow(
            "Location X",
            self.location_x,
        )

        form.addRow(
            "Location Y",
            self.location_y,
        )

        form.addRow(
            "Location Z",
            self.location_z,
        )

        form.addRow(
            "Geometry",
            self.geometry,
        )

        layout.addLayout(form)

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

        layout.addWidget(buttons)

        self.type_box.currentTextChanged.connect(
            self._update_magnitude_label
        )

        self._load_entity()

    def _load_entity(self) -> None:
        if self.entity is None:
            self.name.setText(
                ""
            )

            self.direction_z.setValue(
                1.0
            )

            return

        self.name.setText(
            self.entity.name
        )

        current_type = (
            self.entity.load_type
            if hasattr(
                self.entity,
                "load_type",
            )
            else self.entity.constraint_type
        )

        index = self.type_box.findText(
            current_type
        )

        if index >= 0:
            self.type_box.setCurrentIndex(
                index
            )

        if hasattr(
            self.entity,
            "magnitude",
        ):
            self.magnitude.setValue(
                float(
                    self.entity.magnitude
                )
            )

        self.direction_x.setValue(
            float(
                self.entity.direction_x
            )
        )

        self.direction_y.setValue(
            float(
                self.entity.direction_y
            )
        )

        self.direction_z.setValue(
            float(
                self.entity.direction_z
            )
        )

        self.location_x.setValue(
            float(
                self.entity.location_x
            )
        )

        self.location_y.setValue(
            float(
                self.entity.location_y
            )
        )

        self.location_z.setValue(
            float(
                self.entity.location_z
            )
        )

    def _update_magnitude_label(
        self,
        value: str,
    ) -> None:
        # Kept intentionally simple in v0.0.9.
        # Units are shown in the properties panel.
        return

    def values(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "type": self.type_box.currentText(),
            "magnitude": self.magnitude.value(),
            "direction_x": self.direction_x.value(),
            "direction_y": self.direction_y.value(),
            "direction_z": self.direction_z.value(),
            "location_x": self.location_x.value(),
            "location_y": self.location_y.value(),
            "location_z": self.location_z.value(),
        }