"""Atlas Properties Dock Panel (Right Dock)."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PropertiesDock(QDockWidget):
    """Displays properties of the currently loaded geometry."""

    def __init__(self, parent=None):
        super().__init__("Properties", parent)

        self.setObjectName("PropertiesDock")

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the property table."""

        container = QWidget(self)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        self.table = QTableWidget(0, 2)

        self.table.setHorizontalHeaderLabels(
            ["Property", "Value"]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        self.setWidget(container)

        self.clear_properties()

    def clear_properties(self) -> None:
        """Reset the panel."""

        self.table.setRowCount(0)

        self._add_property("Status", "No Geometry Loaded")

    def set_geometry(self, filename: str, mesh) -> None:
        """Display information about the currently loaded mesh."""

        self.table.setRowCount(0)

        bounds = mesh.bounds

        self._add_property(
            "File",
            Path(filename).name,
        )

        self._add_property(
            "Vertices",
            str(mesh.n_points),
        )

        self._add_property(
            "Cells",
            str(mesh.n_cells),
        )

        self._add_property(
            "X Range",
            f"{bounds[0]:.2f} → {bounds[1]:.2f}",
        )

        self._add_property(
            "Y Range",
            f"{bounds[2]:.2f} → {bounds[3]:.2f}",
        )

        self._add_property(
            "Z Range",
            f"{bounds[4]:.2f} → {bounds[5]:.2f}",
        )

        try:
            self._add_property(
                "Surface Area",
                f"{mesh.area:.2f}",
            )
        except Exception:
            self._add_property(
                "Surface Area",
                "N/A",
            )

        try:
            self._add_property(
                "Volume",
                f"{mesh.volume:.2f}",
            )
        except Exception:
            self._add_property(
                "Volume",
                "N/A",
            )

    def _add_property(self, name: str, value: str) -> None:
        """Insert a property row."""

        row = self.table.rowCount()

        self.table.insertRow(row)

        self.table.setItem(
            row,
            0,
            QTableWidgetItem(name),
        )

        self.table.setItem(
            row,
            1,
            QTableWidgetItem(value),
        )