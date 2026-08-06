"""
Atlas Geometry Loader.
Loads supported geometry files.
"""

from pathlib import Path


class GeometryLoader:
    """Handles geometry file loading."""

    SUPPORTED_EXTENSIONS = {".stl", ".obj"}

    def load(self, filename: str) -> str:
        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(filename)

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError("Unsupported file format.")

        return str(path)