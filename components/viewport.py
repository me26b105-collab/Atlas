"""Atlas Viewport (Central Workspace Panel)."""

import pyvista as pv
from pyvistaqt import QtInteractor

from PySide6.QtWidgets import QFrame, QVBoxLayout


class AtlasViewport(QFrame):
    """Primary 3D workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plotter = QtInteractor(self)
        self.plotter.set_background("#121315")

        layout.addWidget(self.plotter)

    def load_geometry(self, filename: str) -> None:
        """Load and display a geometry file."""

        self.plotter.clear()

        mesh = pv.read(filename)

        self.plotter.add_mesh(
            mesh,
            color="#d8d8d8",
            smooth_shading=True,
            show_edges=True,
            edge_color="#404040",
            line_width=0.8,
            specular=0.25,
        )

        self.plotter.reset_camera()