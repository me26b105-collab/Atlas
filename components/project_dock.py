"""Project explorer for the Atlas multi-body scene."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QInputDialog,
    QMenu,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from geometry.scene import SceneManager


class ProjectDock(QDockWidget):
    """Presentation-only project tree."""

    selection_requested = Signal(list)
    rename_requested = Signal(str, str)
    delete_requested = Signal(list)
    visibility_requested = Signal(str, bool)
    properties_requested = Signal(str)

    material_selection_requested = Signal(list)
    edit_material_requested = Signal(str)
    reset_material_requested = Signal(str)
    save_material_requested = Signal()

    # NEW: v0.0.8
    mesh_requested = Signal()

    OBJECT_ID_ROLE = Qt.ItemDataRole.UserRole
    MATERIAL_ID_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(
        self,
        scene: SceneManager,
        parent=None,
    ):
        super().__init__("Project", parent)

        self.scene = scene

        self.setObjectName("ProjectDock")

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._setup_ui()

        scene.scene_changed.connect(
            self.refresh
        )

        scene.selection.selection_changed.connect(
            self._sync_selection
        )

        scene.object_changed.connect(
            lambda _: self.refresh()
        )

    def _setup_ui(self) -> None:
        container = QWidget(self)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        self.tree = QTreeWidget(container)

        self.tree.setHeaderHidden(True)

        self.tree.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )

        self.tree.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove
        )

        self.tree.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.tree.itemSelectionChanged.connect(
            self._tree_selection_changed
        )

        self.tree.itemDoubleClicked.connect(
            self._item_double_clicked
        )

        self.tree.customContextMenuRequested.connect(
            self._context_menu
        )

        self.tree.model().rowsMoved.connect(
            lambda *_: self._store_order()
        )

        layout.addWidget(self.tree)

        self.setWidget(container)

        self._create_nodes()

    def _create_nodes(self) -> None:
        self.tree.clear()

        style = self.style()

        self.root_item = QTreeWidgetItem(
            self.tree,
            ["Atlas Project"],
        )

        self.root_item.setIcon(
            0,
            style.standardIcon(
                QStyle.StandardPixmap.SP_DirHomeIcon
            ),
        )

        self.geometry_node = QTreeWidgetItem(
            self.root_item,
            ["Geometry"],
        )

        self.geometry_node.setIcon(
            0,
            style.standardIcon(
                QStyle.StandardPixmap.SP_DirIcon
            ),
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
            ["Physics"],
        )

        self.results_node = QTreeWidgetItem(
            self.root_item,
            ["Results"],
        )

        self.screenshots_node = QTreeWidgetItem(
            self.root_item,
            ["Screenshots"],
        )

        self.root_item.setExpanded(True)
        self.geometry_node.setExpanded(True)
        self.materials_node.setExpanded(True)

    def refresh_materials(
        self,
        materials: list,
    ) -> None:
        """Populate the Materials library."""

        self.materials_node.takeChildren()

        for material in materials:
            name = material.name

            if material.is_dirty:
                name += " *"

            item = QTreeWidgetItem(
                self.materials_node,
                [name],
            )

            item.setData(
                0,
                self.MATERIAL_ID_ROLE,
                material.uuid,
            )

        self.materials_node.setExpanded(True)

    def refresh(self) -> None:
        blocked = self.tree.blockSignals(True)

        self.geometry_node.takeChildren()

        style = self.style()

        for obj in self.scene.objects:
            item = QTreeWidgetItem(
                self.geometry_node,
                [obj.display_name],
            )

            item.setData(
                0,
                self.OBJECT_ID_ROLE,
                obj.uuid,
            )

            item.setIcon(
                0,
                style.standardIcon(
                    QStyle.StandardPixmap.SP_FileIcon
                ),
            )

            item.setToolTip(
                0,
                obj.file_path,
            )

        self.geometry_node.setExpanded(True)

        self.tree.blockSignals(blocked)

        self._sync_selection(
            self.scene.selection.selected_ids
        )

    def _tree_selection_changed(self) -> None:
        """Handle tree selection without clearing geometry selection for action nodes."""

        selected_items = self.tree.selectedItems()

        # Mesh, Materials, Physics, Results, Screenshots, etc.
        # are action/category nodes and should not change the
        # currently selected geometry objects.
        action_nodes = {
            self.root_item,
            self.geometry_node,
            self.materials_node,
            self.mesh_node,
            self.physics_node,
            self.results_node,
            self.screenshots_node,
        }

        # If the user clicked an action/category node, preserve
        # the existing scene selection.
        if any(item in action_nodes for item in selected_items):
            return

        object_ids = []
        material_ids = []

        for item in selected_items:
            object_id = item.data(
                0,
                self.OBJECT_ID_ROLE,
            )

            material_id = item.data(
                0,
                self.MATERIAL_ID_ROLE,
            )

            if object_id:
                object_ids.append(object_id)

            if material_id:
                material_ids.append(material_id)

        self.selection_requested.emit(object_ids)
        self.material_selection_requested.emit(material_ids)

    def _item_double_clicked(
        self,
        item: QTreeWidgetItem,
        column: int,
    ) -> None:
        """Handle double-click actions."""

        if item is self.mesh_node:
            self.mesh_requested.emit()

    def _sync_selection(
        self,
        ids: list[str],
    ) -> None:
        blocked = self.tree.blockSignals(True)

        self.tree.clearSelection()

        for index in range(
            self.geometry_node.childCount()
        ):
            item = self.geometry_node.child(index)

            item.setSelected(
                item.data(
                    0,
                    self.OBJECT_ID_ROLE,
                ) in ids
            )

        self.tree.blockSignals(blocked)

    def _store_order(self) -> None:
        ordered = [
            self.geometry_node.child(i).data(
                0,
                self.OBJECT_ID_ROLE,
            )
            for i in range(
                self.geometry_node.childCount()
            )
        ]

        self.scene.objects.reorder(
            ordered
        )

        self.scene.scene_changed.emit()

    def _context_menu(
        self,
        position,
    ) -> None:
        item = self.tree.itemAt(position)

        if not item:
            return

        # Mesh node
        if item is self.mesh_node:
            menu = QMenu(self)

            action = menu.addAction(
                "Open Mesh Controls"
            )

            action.triggered.connect(
                self.mesh_requested.emit
            )

            menu.exec(
                self.tree.viewport().mapToGlobal(
                    position
                )
            )

            return

        # Material node
        material_id = item.data(
            0,
            self.MATERIAL_ID_ROLE,
        )

        if material_id:
            menu = QMenu(self)

            edit = menu.addAction(
                "Edit Material"
            )

            reset = menu.addAction(
                "Reset Custom Material"
            )

            menu.addSeparator()

            save = menu.addAction(
                "Save Material"
            )

            edit.triggered.connect(
                lambda: self.edit_material_requested.emit(
                    material_id
                )
            )

            reset.triggered.connect(
                lambda: self.reset_material_requested.emit(
                    material_id
                )
            )

            save.triggered.connect(
                self.save_material_requested.emit
            )

            menu.exec(
                self.tree.viewport().mapToGlobal(
                    position
                )
            )

            return

        # Geometry node
        object_id = item.data(
            0,
            self.OBJECT_ID_ROLE,
        )

        if not object_id:
            return

        obj = self.scene.objects.get(
            object_id
        )

        if not obj:
            return

        menu = QMenu(self)

        rename = menu.addAction(
            "Rename"
        )

        rename.triggered.connect(
            lambda: self._rename(
                object_id,
                obj.display_name,
            )
        )

        delete = menu.addAction(
            "Delete"
        )

        delete.triggered.connect(
            lambda: self.delete_requested.emit(
                [object_id]
            )
        )

        visibility = menu.addAction(
            "Hide"
            if obj.visible
            else "Show"
        )

        visibility.triggered.connect(
            lambda: self.visibility_requested.emit(
                object_id,
                not obj.visible,
            )
        )

        menu.addAction(
            "Duplicate (Coming Soon)"
        ).setEnabled(False)

        properties = menu.addAction(
            "Properties"
        )

        properties.triggered.connect(
            lambda: self.properties_requested.emit(
                object_id
            )
        )

        menu.exec(
            self.tree.viewport().mapToGlobal(
                position
            )
        )

    def _rename(
        self,
        object_id: str,
        current: str,
    ) -> None:
        name, accepted = QInputDialog.getText(
            self,
            "Rename Geometry",
            "Name:",
            text=current,
        )

        if accepted and name.strip():
            self.rename_requested.emit(
                object_id,
                name.strip(),
            )

    def set_geometry_file(
        self,
        filename: str,
    ) -> None:
        self.refresh()

    def clear_tree(self) -> None:
        self.refresh()
        self.screenshots_node.takeChildren()

    def set_project_name(
        self,
        name: str,
    ) -> None:
        self.root_item.setText(
            0,
            name or "Atlas Project",
        )

    def add_screenshot(
        self,
        filename: str,
    ) -> None:
        QTreeWidgetItem(
            self.screenshots_node,
            [filename],
        )

        self.screenshots_node.setExpanded(
            True
        )