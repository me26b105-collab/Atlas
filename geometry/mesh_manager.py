"""Atlas mesh generation and mesh statistics service."""

from __future__ import annotations

from dataclasses import dataclass

import pyvista as pv


@dataclass
class MeshStatistics:
    """Basic statistics for a generated mesh."""

    points: int = 0
    cells: int = 0
    surface_cells: int = 0
    volume_cells: int = 0
    bounds: tuple[float, ...] | None = None

    @property
    def memory_mb(self) -> float:
        """Return an approximate memory usage."""
        return (
            self.points * 3 * 8
            + self.cells * 16
        ) / (1024 * 1024)


class MeshManager:
    """Creates and analyzes surface and volume meshes."""

    def __init__(self):
        self.surface_mesh: pv.DataSet | None = None
        self.volume_mesh: pv.DataSet | None = None

        self.surface_statistics = MeshStatistics()
        self.volume_statistics = MeshStatistics()

    def clear(self) -> None:
        """Clear all generated meshes."""
        self.surface_mesh = None
        self.volume_mesh = None

        self.surface_statistics = MeshStatistics()
        self.volume_statistics = MeshStatistics()

    def generate_surface_mesh(
        self,
        geometry: pv.DataSet,
        refinement: int = 0,
    ) -> pv.PolyData:
        """Generate a triangulated/refined surface mesh."""

        if geometry is None or geometry.n_points == 0:
            raise ValueError("No valid geometry is available.")

        mesh = geometry.extract_surface().triangulate()

        if refinement > 0:
            mesh = mesh.subdivide(
                int(refinement),
                subfilter="linear",
            )

        self.surface_mesh = mesh

        self.surface_statistics = self._statistics(
            mesh,
            volume=False,
        )

        return mesh

    def generate_volume_mesh(
        self,
        geometry: pv.DataSet,
        refinement: int = 0,
    ) -> pv.UnstructuredGrid:
        """Generate a tetrahedral volume mesh."""

        if geometry is None or geometry.n_points == 0:
            raise ValueError("No valid geometry is available.")

        surface = geometry.extract_surface().triangulate()

        if surface.n_cells == 0:
            raise ValueError(
                "The geometry has no surface cells."
            )

        volume = surface.delaunay_3d()

        if volume.n_cells == 0:
            raise ValueError(
                "Could not generate a volume mesh."
            )

        if refinement > 0:
            # Refinement is intentionally conservative.
            # Subdivision of the generated volume mesh is
            # avoided because it can produce invalid cells.
            for _ in range(int(refinement)):
                volume = volume.subdivide_tetra()

        self.volume_mesh = volume

        self.volume_statistics = self._statistics(
            volume,
            volume=True,
        )

        return volume

    def _statistics(
        self,
        mesh: pv.DataSet,
        volume: bool,
    ) -> MeshStatistics:
        """Calculate basic mesh statistics."""

        surface_cells = 0
        volume_cells = 0

        if isinstance(mesh, pv.PolyData):
            surface_cells = mesh.n_cells
        else:
            try:
                cell_types = mesh.celltypes

                volume_types = {
                    pv.CellType.TETRA,
                    pv.CellType.HEXAHEDRON,
                    pv.CellType.VOXEL,
                    pv.CellType.WEDGE,
                    pv.CellType.PYRAMID,
                }

                volume_cells = sum(
                    1
                    for cell_type in cell_types
                    if cell_type in volume_types
                )
            except Exception:
                volume_cells = mesh.n_cells

        return MeshStatistics(
            points=int(mesh.n_points),
            cells=int(mesh.n_cells),
            surface_cells=surface_cells,
            volume_cells=volume_cells,
            bounds=tuple(float(v) for v in mesh.bounds),
        )

    def surface_quality(self) -> dict[str, float]:
        """Return basic surface quality measurements."""

        mesh = self.surface_mesh

        if mesh is None or mesh.n_cells == 0:
            return {}

        try:
            areas = mesh.compute_cell_sizes(
                length=False,
                area=True,
                volume=False,
            )["Area"]

            if len(areas) == 0:
                return {}

            return {
                "minimum_area": float(areas.min()),
                "maximum_area": float(areas.max()),
                "average_area": float(areas.mean()),
            }
        except Exception:
            return {}

    def volume_quality(self) -> dict[str, float]:
        """Return basic volume quality measurements."""

        mesh = self.volume_mesh

        if mesh is None or mesh.n_cells == 0:
            return {}

        try:
            volumes = mesh.compute_cell_sizes(
                length=False,
                area=False,
                volume=True,
            )["Volume"]

            if len(volumes) == 0:
                return {}

            return {
                "minimum_volume": float(volumes.min()),
                "maximum_volume": float(volumes.max()),
                "average_volume": float(volumes.mean()),
            }
        except Exception:
            return {}