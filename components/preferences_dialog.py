"""Persisted application preferences kept separate from the workspace."""

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox


class PreferencesDialog(QDialog):
    """Small, extensible preferences surface for scene-engine defaults."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent); self.setWindowTitle("Atlas Preferences")
        settings = QSettings(); layout = QFormLayout(self)
        self.theme = QComboBox(); self.theme.addItems(["Dark", "System"]); self.theme.setCurrentText(settings.value("preferences/theme", "Dark"))
        self.units = QComboBox(); self.units.addItems(["Model Units", "Millimetres", "Metres", "Inches"]); self.units.setCurrentText(settings.value("preferences/units", "Model Units"))
        self.autosave = QSpinBox(); self.autosave.setRange(1, 120); self.autosave.setSuffix(" min"); self.autosave.setValue(int(settings.value("preferences/autosave_minutes", 3)))
        self.recent_limit = QSpinBox(); self.recent_limit.setRange(1, 50); self.recent_limit.setValue(int(settings.value("preferences/recent_limit", 10)))
        layout.addRow("Theme", self.theme); layout.addRow("Units", self.units); layout.addRow("Autosave interval", self.autosave); layout.addRow("Recent file limit", self.recent_limit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(self._save); buttons.rejected.connect(self.reject); layout.addRow(buttons)

    def _save(self) -> None:
        settings = QSettings(); settings.setValue("preferences/theme", self.theme.currentText()); settings.setValue("preferences/units", self.units.currentText()); settings.setValue("preferences/autosave_minutes", self.autosave.value()); settings.setValue("preferences/recent_limit", self.recent_limit.value()); self.accept()
