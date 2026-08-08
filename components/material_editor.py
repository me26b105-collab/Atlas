"""Atlas Material Editor Dialog."""

from __future__ import annotations

from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
)


class MaterialEditorDialog(QDialog):
    """Dialog used to edit the custom material."""

    def __init__(self, material, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Edit {material.name}")
        self.resize(420, 320)

        layout = QFormLayout(self)

        self.density = self._create_spinbox(
            0.001,
            1e12,
            3,
            material.density,
        )

        self.youngs = self._create_spinbox(
            0.001,
            1e15,
            2,
            material.youngs_modulus,
        )

        self.poisson = self._create_spinbox(
            0.0,
            0.4999,
            4,
            material.poisson_ratio,
        )

        self.thermal_cond = self._create_spinbox(
            0.0,
            1e6,
            3,
            material.thermal_conductivity,
        )

        self.thermal_exp = self._create_spinbox(
            0.0,
            1.0,
            10,
            material.coefficient_thermal_expansion,
        )

        self.yield_str = self._create_spinbox(
            0.001,
            1e12,
            2,
            material.yield_strength,
        )

        self.ult_str = self._create_spinbox(
            0.001,
            1e12,
            2,
            material.ultimate_strength,
        )

        layout.addRow("Density (kg/m³)", self.density)
        layout.addRow("Young's Modulus (Pa)", self.youngs)
        layout.addRow("Poisson Ratio", self.poisson)
        layout.addRow(
            "Thermal Conductivity (W/(m·K))",
            self.thermal_cond,
        )
        layout.addRow(
            "Thermal Expansion (1/K)",
            self.thermal_exp,
        )
        layout.addRow("Yield Strength (Pa)", self.yield_str)
        layout.addRow(
            "Ultimate Strength (Pa)",
            self.ult_str,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def _create_spinbox(
        self,
        minimum: float,
        maximum: float,
        decimals: int,
        value: float,
    ) -> QDoubleSpinBox:
        """Create a numeric field that accepts scientific notation."""

        spinbox = QDoubleSpinBox()

        spinbox.setRange(minimum, maximum)
        spinbox.setDecimals(decimals)
        if value is not None:
            spinbox.setValue(float(value))
        validator = QDoubleValidator(
            minimum,
            maximum,
            decimals,
            spinbox,
        )

        # Allow inputs such as:
        # 210000000000
        # 2.1e11
        # 2.1E11
        validator.setNotation(
            QDoubleValidator.Notation.ScientificNotation
        )

        spinbox.lineEdit().setValidator(validator)

        return spinbox

    def get_values(self) -> dict:
        return {
            "density": self.density.value(),
            "youngs_modulus": self.youngs.value(),
            "poisson_ratio": self.poisson.value(),
            "thermal_conductivity": self.thermal_cond.value(),
            "coefficient_thermal_expansion": self.thermal_exp.value(),
            "yield_strength": self.yield_str.value(),
            "ultimate_strength": self.ult_str.value(),
        }