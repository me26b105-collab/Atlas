"""Atlas Properties Dock Panel (Right Dock)."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PropertiesDock(QDockWidget):
    """Displays grouped details for the currently loaded geometry."""

    def __init__(self, parent=None):
        super().__init__("Properties", parent)
        self.setObjectName("PropertiesDock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self._setup_ui()

    def _setup_ui(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        self.setWidget(container)
        self.clear_properties()

    def clear_properties(self) -> None:
        self.table.setRowCount(0)
        self._add_section("Geometry")
        self._add_property("Status", "No Geometry Loaded")

    def set_geometry(self, filename: str, mesh, mode: str = "Shaded") -> None:
        """Display professionally formatted mesh and rendering information."""
        self.table.setRowCount(0)
        bounds = mesh.bounds
        self._add_section("Geometry")
        self._add_property("File", Path(filename).name)
        self._add_property("Format", Path(filename).suffix.upper().lstrip("."))
        self._add_property("Vertices", f"{mesh.n_points:,}")
        self._add_property("Cells", f"{mesh.n_cells:,}")
        self._add_property("Area", self._mesh_value(mesh, "area", "units²"))
        self._add_property("Volume", self._mesh_value(mesh, "volume", "units³"))
        self._add_property(
            "Bounds",
            "X {0:.2f}–{1:.2f}\nY {2:.2f}–{3:.2f}\nZ {4:.2f}–{5:.2f}".format(*bounds),
        )
        self._add_section("Rendering")
        self._add_property("Current Mode", mode)
        self._add_property("Memory Estimate", self._memory_estimate(mesh))

    def set_scene_object(self, obj) -> None:
        """Display identity, geometry and per-object display settings."""
        self.table.setRowCount(0)
        mesh, bounds = obj.mesh, obj.bounds
        dimensions = (bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
        self._add_section("Object")
        self._add_property("Name", obj.display_name)
        self._add_property("UUID", obj.uuid)
        self._add_property("File", obj.original_filename)
        try:
            self._add_property("File Size", f"{Path(obj.file_path).stat().st_size / 1024:.1f} KB")
        except OSError:
            self._add_property("File Size", "Not available")
        self._add_property("Geometry Type", Path(obj.file_path).suffix.upper().lstrip("."))
        self._add_property("Vertices", f"{mesh.n_points:,}")
        self._add_property("Cells", f"{mesh.n_cells:,}")
        self._add_property("Bounds", "X {:.2f}–{:.2f}\nY {:.2f}–{:.2f}\nZ {:.2f}–{:.2f}".format(*bounds))
        self._add_property("Dimensions", "{:.2f} × {:.2f} × {:.2f}".format(*dimensions))
        self._add_property("Center", "{:.2f}, {:.2f}, {:.2f}".format(*obj.center))
        self._add_property("Surface Area", self._mesh_value(mesh, "area", "units²"))
        self._add_property("Volume", self._mesh_value(mesh, "volume", "units³"))
        self._add_property("Estimated Memory", self._memory_estimate(mesh))
        self._add_section("Rendering")
        self._add_property("Visible", "Yes" if obj.visible else "No")
        self._add_property("Opacity", f"{obj.opacity * 100:.0f}%")
        self._add_property("Color", obj.color)
        self._add_property("Wireframe", "On" if obj.wireframe else "Off")
        self._add_property("Rendering Mode", "Wireframe" if obj.wireframe else "Surface")
        self._add_section("Lifecycle")
        self._add_property("Created", obj.creation_time)
        self._add_property("Modified", obj.last_modified)

    def _mesh_value(self, mesh, attribute: str, units: str) -> str:
        try:
            return f"{getattr(mesh, attribute):,.2f} {units}"
        except Exception:
            return "Not available"

    def _memory_estimate(self, mesh) -> str:
        # A conservative estimate for point coordinates and cell connectivity.
        byte_count = mesh.n_points * 3 * 8 + mesh.n_cells * 16
        return f"{byte_count / (1024 * 1024):.2f} MB"

    def _add_section(self, title: str) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QTableWidgetItem(title.upper())
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setForeground(QColor("#8D99A8"))
        self.table.setItem(row, 0, item)
        self.table.setSpan(row, 0, 1, 2)

    def _add_property(self, name: str, value: str) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(value))
