import pyvista as pv
from pyvistaqt import QtInteractor

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMenu,
    QStackedLayout,
    QVBoxLayout,
)



class AtlasViewport(QFrame):
    """Primary 3D workspace."""

    geometry_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Currently loaded mesh
        self.current_mesh = None

        # Currently displayed actor
        self.mesh_actor = None

        # Rendering state
        self.wireframe_enabled = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the Atlas viewport."""

        self.setFrameShape(QFrame.Shape.NoFrame)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # --------------------------------------------------
        # Stacked Layout
        # --------------------------------------------------

        self.stack = QStackedLayout()

        # =========================
        # Welcome Screen
        # =========================

        welcome = QFrame()

        welcome_layout = QVBoxLayout(welcome)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("ATLAS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size:42px;
            font-weight:700;
            color:#ECEFF4;
            letter-spacing:3px;
        """)

        subtitle = QLabel(
            "Drag & Drop STL / OBJ Files\n\nor\n\nFile → Open Geometry"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size:16px;
            color:#7D8794;
        """)

        welcome_layout.addStretch()
        welcome_layout.addWidget(title)
        welcome_layout.addSpacing(12)
        welcome_layout.addWidget(subtitle)
        welcome_layout.addStretch()

        # =========================
        # Viewport
        # =========================

        viewport_widget = QFrame()

        viewport_layout = QVBoxLayout(viewport_widget)
        viewport_layout.setContentsMargins(0, 0, 0, 0)

        self.plotter = QtInteractor(viewport_widget)

        self.plotter.set_background(
            "#101214",
            top="#38404B",
        )

        self.plotter.show_axes()
        self.plotter.add_axes()

        self.plotter.show_grid(
            color="#3F4652",
            font_size=8,
        )

        viewport_layout.addWidget(self.plotter)

        # =========================
        # Stack
        # =========================

        self.stack.addWidget(welcome)
        self.stack.addWidget(viewport_widget)

        outer_layout.addLayout(self.stack)

        self.stack.setCurrentIndex(0)

        # Enable drag & drop
        self.setAcceptDrops(True)

        # Double click = reset camera
        self.plotter.interactor.mouseDoubleClickEvent = (
            lambda event: self.reset_camera()
        )

        # Right click menu
        self.plotter.interactor.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.plotter.interactor.customContextMenuRequested.connect(
            self._show_context_menu
        )

    # ==========================================================
    # Geometry
    # ==========================================================

    def load_geometry(self, filename: str) -> None:
        """Load and display a geometry file."""

        # Switch from welcome page to viewport
        self.stack.setCurrentIndex(1)

        # Clear previous scene
        self.plotter.clear()

        # Restore helpers
        self.plotter.show_axes()
        self.plotter.add_axes()

        self.plotter.show_grid(
            color="#3F4652",
            font_size=8,
        )

        # Read mesh
        mesh = pv.read(filename)
        self.current_mesh = mesh

        # Display mesh
        self.mesh_actor = self.plotter.add_mesh(
            mesh,
            color="#D8DDE6",
            smooth_shading=True,
            show_edges=True,
            edge_color="#505865",
            line_width=0.6,
            specular=0.55,
            ambient=0.28,
            diffuse=0.82,
        )

        # Camera
        self.plotter.view_isometric()
        self.plotter.reset_camera()

        self.wireframe_enabled = False

        self.plotter.render()

    # ==========================================================
    # Camera
    # ==========================================================

    def reset_camera(self) -> None:
        """Reset the camera."""

        self.plotter.reset_camera()
        self.plotter.render()

    def fit_to_screen(self) -> None:
        """Fit the model to the viewport."""

        self.plotter.reset_camera()
        self.plotter.render()

    def view_front(self) -> None:
        """Front view."""

        self.plotter.view_yz()
        self.plotter.render()

    def view_top(self) -> None:
        """Top view."""

        self.plotter.view_xy()
        self.plotter.render()

    def view_right(self) -> None:
        """Right view."""

        self.plotter.view_xz()
        self.plotter.render()

    def view_isometric(self) -> None:
        """Isometric view."""

        self.plotter.view_isometric()
        self.plotter.render()

    # ==========================================================
    # Rendering
    # ==========================================================

    def toggle_wireframe(self) -> None:
        """Toggle between shaded and wireframe."""

        if self.mesh_actor is None:
            return

        prop = self.mesh_actor.GetProperty()

        if self.wireframe_enabled:
            prop.SetRepresentationToSurface()
        else:
            prop.SetRepresentationToWireframe()

        self.wireframe_enabled = not self.wireframe_enabled

        self.plotter.render()

    def set_shaded(self) -> None:
        """Switch back to shaded rendering."""

        if self.mesh_actor is None:
            return

        self.mesh_actor.GetProperty().SetRepresentationToSurface()

        self.wireframe_enabled = False

        self.plotter.render()

    # ==========================================================
    # Screenshot
    # ==========================================================

    def take_screenshot(self, filename: str) -> None:
        """Save the current viewport as an image."""

        self.plotter.screenshot(filename)

    # ==========================================================
    # Context Menu
    # ==========================================================

    def _show_context_menu(self, position) -> None:
        """Display the viewport context menu."""

        menu = QMenu(self)

        front_action = QAction("Front View", self)
        top_action = QAction("Top View", self)
        right_action = QAction("Right View", self)
        iso_action = QAction("Isometric View", self)

        front_action.triggered.connect(self.view_front)
        top_action.triggered.connect(self.view_top)
        right_action.triggered.connect(self.view_right)
        iso_action.triggered.connect(self.view_isometric)

        menu.addAction(front_action)
        menu.addAction(top_action)
        menu.addAction(right_action)

        menu.addSeparator()

        menu.addAction(iso_action)

        menu.exec(
            self.plotter.interactor.mapToGlobal(position)
        )

    # ==========================================================
    # Drag & Drop
    # ==========================================================

    def dragEnterEvent(self, event) -> None:
        """Accept supported geometry files."""

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        """Handle dropped geometry files."""

        urls = event.mimeData().urls()

        if not urls:
            return

        filename = urls[0].toLocalFile()

        if filename.lower().endswith((".stl", ".obj")):
            self.geometry_dropped.emit(filename)