"""Atlas Material Library Manager Interface."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from geometry.material import Material, get_preset_materials


class MaterialDialog(QDialog):
    """UI for browsing, creating, and modifying application materials."""

    material_saved = Signal(object)

    def __init__(self, materials: list[Material], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Atlas Material Manager")
        self.resize(550, 420)

        self.materials: list[Material] = list(materials)
        if not self.materials:
            self.materials = get_preset_materials()

        self._init_ui()
        self._populate_list()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)

        # Left Column - Material Selection
        left_layout = QVBoxLayout()
        self.mat_list = QListWidget()
        self.mat_list.currentRowChanged.connect(self._on_material_selected)
        left_layout.addWidget(self.mat_list)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("New Custom")
        self.add_btn.clicked.connect(self._add_custom_material)
        self.del_btn = QPushButton("Delete")
        self.del_btn.clicked.connect(self._delete_material)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        left_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout, 1)

        # Right Column - Form Properties
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._update_current_material)

        self.density_box = self._create_spinbox(0.0, 1e6, " kg/m³", 1.0)
        self.youngs_box = self._create_spinbox(0.0, 1e14, " Pa", 1e9)
        self.poisson_box = self._create_spinbox(-0.99, 0.49, "", 0.01, decimals=3)
        self.shear_box = QLineEdit()
        self.shear_box.setReadOnly(True)

        self.thermal_cond_box = self._create_spinbox(0.0, 10000.0, " W/(m·K)", 1.0)
        self.thermal_exp_box = self._create_spinbox(0.0, 1.0, " 1/K", 1e-6, decimals=8)
        self.yield_box = self._create_spinbox(0.0, 1e14, " Pa", 1e6)
        self.ultimate_box = self._create_spinbox(0.0, 1e14, " Pa", 1e6)

        # Connect property edits
        for box in (
            self.density_box,
            self.youngs_box,
            self.poisson_box,
            self.thermal_cond_box,
            self.thermal_exp_box,
            self.yield_box,
            self.ultimate_box,
        ):
            box.valueChanged.connect(self._update_current_material)

        form_layout.addRow("Name", self.name_edit)
        form_layout.addRow("Density", self.density_box)
        form_layout.addRow("Young's Modulus (E)", self.youngs_box)
        form_layout.addRow("Poisson's Ratio (ν)", self.poisson_box)
        form_layout.addRow("Shear Modulus (G)", self.shear_box)
        form_layout.addRow("Thermal Conductivity", self.thermal_cond_box)
        form_layout.addRow("Coeff. Thermal Expansion", self.thermal_exp_box)
        form_layout.addRow("Yield Strength", self.yield_box)
        form_layout.addRow("Ultimate Strength", self.ultimate_box)

        right_container = QVBoxLayout()
        right_container.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        right_container.addWidget(buttons)

        main_layout.addLayout(right_container, 2)

    def _create_spinbox(self, min_val: float, max_val: float, suffix: str, step: float, decimals: int = 2) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(min_val, max_val)
        box.setSuffix(suffix)
        box.setSingleStep(step)
        box.setDecimals(decimals)
        return box

    def _populate_list(self) -> None:
        self.mat_list.clear()
        for mat in self.materials:
            item = QListWidgetItem(f"{mat.name} {'(Preset)' if mat.is_preset else ''}")
            self.mat_list.addItem(item)
        if self.materials:
            self.mat_list.setCurrentRow(0)

    def _on_material_selected(self, index: int) -> None:
        if index < 0 or index >= len(self.materials):
            return
        mat = self.materials[index]

        # Block signals temporarily to prevent infinite feedback loops during populating
        self.blockSignals(True)
        self.name_edit.setText(mat.name)
        self.density_box.setValue(mat.density)
        self.youngs_box.setValue(mat.youngs_modulus)
        self.poisson_box.setValue(mat.poisson_ratio)
        self.thermal_cond_box.setValue(mat.thermal_conductivity)
        self.thermal_exp_box.setValue(mat.coeff_thermal_expansion)
        self.yield_box.setValue(mat.yield_strength)
        self.ultimate_box.setValue(mat.ultimate_strength)

        # Update Shear Modulus Display
        self.shear_box.setText(f"{mat.shear_modulus:.3e} Pa")

        # Preset immutability
        editable = not mat.is_preset
        self.name_edit.setEnabled(editable)
        self.density_box.setEnabled(editable)
        self.youngs_box.setEnabled(editable)
        self.poisson_box.setEnabled(editable)
        self.thermal_cond_box.setEnabled(editable)
        self.thermal_exp_box.setEnabled(editable)
        self.yield_box.setEnabled(editable)
        self.ultimate_box.setEnabled(editable)
        self.del_btn.setEnabled(editable)
        self.blockSignals(False)

    def _update_current_material(self) -> None:
        idx = self.mat_list.currentRow()
        if idx < 0 or idx >= len(self.materials):
            return
        mat = self.materials[idx]
        if mat.is_preset:
            return

        mat.name = self.name_edit.text()
        mat.density = self.density_box.value()
        mat.youngs_modulus = self.youngs_box.value()
        mat.poisson_ratio = self.poisson_box.value()
        mat.thermal_conductivity = self.thermal_cond_box.value()
        mat.coeff_thermal_expansion = self.thermal_exp_box.value()
        mat.yield_strength = self.yield_box.value()
        mat.ultimate_strength = self.ultimate_box.value()

        self.shear_box.setText(f"{mat.shear_modulus:.3e} Pa")
        self.mat_list.item(idx).setText(mat.name)

    def _add_custom_material(self) -> None:
        mat = Material(name=f"Custom Material {len(self.materials) + 1}", is_preset=False)
        self.materials.append(mat)
        self._populate_list()
        self.mat_list.setCurrentRow(len(self.materials) - 1)

    def _delete_material(self) -> None:
        idx = self.mat_list.currentRow()
        if idx >= 0 and not self.materials[idx].is_preset:
            self.materials.pop(idx)
            self._populate_list()