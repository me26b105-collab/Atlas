"""Atlas Properties Dock Panel (Right Dock)."""

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
    """Right dock panel displaying attributes of selected items."""

    def __init__(self, parent=None):
        super().__init__("Properties", parent)
        self.setObjectName("PropertiesDock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self._setup_ui()

    def _setup_ui(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        # Property grid representation
        self.table = QTableWidget(0, 2, container)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)

        # Default structural placeholder properties
        self._add_property("Name", "Simulation_01")
        self._add_property("Solver", "Implicit Dynamic")
        self._add_property("Status", "Unconfigured")

        layout.addWidget(self.table)
        self.setWidget(container)

    def _add_property(self, prop: str, val: str) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(prop))
        self.table.setItem(row, 1, QTableWidgetItem(val))