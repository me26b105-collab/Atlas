"""Atlas meshing service.

Provides surface/volume meshing, mesh statistics, quality metrics,
and refinement without coupling the meshing logic to Qt widgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyvista as pv


@dataclass
class MeshSettings:
    """Settings used to generate a computational mesh."""

    mesh_type: str = "Surface"
    target_size: float = 1.0
    refinement: int = 0
    quality_measure: str = "scaled_jacobian"


@dataclass
class MeshResult:
    """Result returned by the meshing service."""

    mesh: pv.DataSet
    mesh_type: str
    target_size: float
    refinement: int
    statistics: dict[str, Any]
    quality: dict[str, Any]


class MeshManager:
    """Creates and analyzes meshes using PyVista."""

    def __init__(self) -> None:
        self.settings = MeshSettings()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def generate(
        self,
        geometry: pv.DataSet,
        settings: MeshSettings | None = None,
    ) -> MeshResult:
        """Generate a surface or volume mesh."""

        settings = settings or self.settings
        self._validate_settings(settings)

        if geometry is None or geometry.n_points == 0:
            raise ValueError("No valid geometry is available for meshing.")

        if settings.mesh_type == "Surface":
            mesh = self._surface_mesh(
                geometry,
                settings,
            )
        elif settings.mesh_type == "Volume":
            mesh = self._volume_mesh(
                geometry,
                settings,
            )
        else:
            raise ValueError(
                f"Unsupported mesh type: {settings.mesh_type}"
            )

        if settings.refinement > 0:
            mesh = self.refine(
                mesh,
                settings.refinement,
            )

        statistics = self.statistics(mesh)
        quality = self.quality(mesh)

        return MeshResult(
            mesh=mesh,
            mesh_type=settings.mesh_type,
            target_size=settings.target_size,
            refinement=settings.refinement,
            statistics=statistics,
            quality=quality,
        )

    def refine(
        self,
        mesh: pv.DataSet,
        levels: int = 1,
    ) -> pv.DataSet:
        """Refine a mesh by subdividing its cells."""

        levels = max(0, int(levels))

        result = mesh

        for _ in range(levels):
            if isinstance(result, pv.PolyData):
                result = result.subdivide(1, subfilter="linear")
            else:
                try:
                    result = result.subdivide(1)
                except AttributeError:
                    result = result.extract_surface().subdivide(
                        1,
                        subfilter="linear",
                    )

        return result

    def statistics(
        self,
        mesh: pv.DataSet,
    ) -> dict[str, Any]:
        """Return useful mesh statistics."""

        if mesh is None:
            return {
                "points": 0,
                "cells": 0,
                "vertices": 0,
                "faces": 0,
                "volume": 0.0,
                "area": 0.0,
            }

        area = 0.0
        volume = 0.0

        try:
            area = float(mesh.area)
        except Exception:
            pass

        try:
            volume = float(mesh.volume)
        except Exception:
            pass

        return {
            "points": int(mesh.n_points),
            "cells": int(mesh.n_cells),
            "vertices": int(mesh.n_points),
            "faces": int(mesh.n_cells),
            "volume": volume,
            "area": area,
        }

    def quality(
        self,
        mesh: pv.DataSet,
    ) -> dict[str, Any]:
        """Calculate basic mesh-quality statistics."""

        if mesh is None or mesh.n_cells == 0:
            return {
                "minimum": None,
                "maximum": None,
                "average": None,
                "poor_cells": 0,
            }

        try:
            quality_mesh = mesh.compute_cell_quality(
                quality_measure="scaled_jacobian"
            )

            values = quality_mesh.cell_data[
                "CellQuality"
            ]

            if len(values) == 0:
                raise ValueError("No quality values were produced.")

            minimum = float(values.min())
            maximum = float(values.max())
            average = float(values.mean())

            poor_cells = int(
                sum(float(value) < 0.2 for value in values)
            )

            return {
                "minimum": minimum,
                "maximum": maximum,
                "average": average,
                "poor_cells": poor_cells,
            }

        except Exception:
            # Some surface meshes do not support every quality metric.
            # Fall back to a topology-based report instead of crashing.
            return {
                "minimum": None,
                "maximum": None,
                "average": None,
                "poor_cells": 0,
            }

    # ------------------------------------------------------------------
    # INTERNAL GENERATORS
    # ------------------------------------------------------------------

    def _surface_mesh(
        self,
        geometry: pv.DataSet,
        settings: MeshSettings,
    ) -> pv.PolyData:
        """Create a surface mesh."""

        surface = geometry.extract_surface()

        if settings.target_size <= 0:
            return surface

        # PyVista's triangulate gives us a predictable surface mesh.
        surface = surface.triangulate()

        # Optional subdivision gives smaller elements for refinement.
        refinement = self._size_to_refinement(
            settings.target_size
        )

        for _ in range(refinement):
            surface = surface.subdivide(
                1,
                subfilter="linear",
            )

        return surface

    def _volume_mesh(
        self,
        geometry: pv.DataSet,
        settings: MeshSettings,
    ) -> pv.DataSet:
        """Create an approximate volume mesh."""

        surface = geometry.extract_surface().triangulate()

        # PyVista does not provide a universal tetrahedral mesher for
        # every installed VTK build.  Delaunay 3D is the most portable
        # option for closed surfaces.
        try:
            volume = surface.delaunay_3d(
                alpha=0.0,
                tol=0.001,
            )

            if volume.n_cells == 0:
                raise ValueError(
                    "Volume meshing produced no cells."
                )

            return volume

        except Exception as error:
            raise ValueError(
                "Volume meshing failed. "
                "Make sure the geometry is closed/watertight."
            ) from error

    # ------------------------------------------------------------------
    # VALIDATION / HELPERS
    # ------------------------------------------------------------------

    def _validate_settings(
        self,
        settings: MeshSettings,
    ) -> None:
        if settings.target_size <= 0:
            raise ValueError(
                "Target element size must be greater than zero."
            )

        if settings.refinement < 0:
            raise ValueError(
                "Refinement level cannot be negative."
            )

        if settings.mesh_type not in (
            "Surface",
            "Volume",
        ):
            raise ValueError(
                "Mesh type must be Surface or Volume."
            )

    def _size_to_refinement(
        self,
        target_size: float,
    ) -> int:
        """Convert a small target size into a modest subdivision level."""

        if target_size >= 5.0:
            return 0

        if target_size >= 2.0:
            return 1

        if target_size >= 1.0:
            return 2

        if target_size >= 0.5:
            return 3

        return 4