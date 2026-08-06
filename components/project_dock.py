"""Atlas Project Dock Panel (Left Dock)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ProjectDock(QDockWidget):
    """Left dock panel managing the simulation study tree."""

    def __init__(self, parent=None):
        super().__init__("Project", parent)

        self.setObjectName("ProjectDock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._setup_ui()

    def _setup_ui(self) -> None:
        container = QWidget(self)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        self.tree = QTreeWidget(container)
        self.tree.setHeaderHidden(True)

        self.root_item = QTreeWidgetItem(self.tree, ["Model Tree"])

        self.geometry_node = QTreeWidgetItem(
            self.root_item,
            ["Geometry"],
        )

        self.materials_node = QTreeWidgetItem(
            self.root_item,
            ["Materials"],
        )

        self.mesh_node = QTreeWidgetItem(
            self.root_item,
            ["Mesh"],
        )

        self.physics_node = QTreeWidgetItem(
            self.root_item,
            ["Physics / Boundary Conditions"],
        )

        self.results_node = QTreeWidgetItem(
            self.root_item,
            ["Results"],
        )

        self.tree.expandAll()

        layout.addWidget(self.tree)

        self.setWidget(container)

    def set_geometry_file(self, filename: str) -> None:
        """Display imported geometry."""

        self.geometry_node.takeChildren()

        QTreeWidgetItem(
            self.geometry_node,
            [filename],
        )

        self.geometry_node.setExpanded(True)

    def clear_tree(self) -> None:
        """Reset project tree."""

        self.geometry_node.takeChildren()