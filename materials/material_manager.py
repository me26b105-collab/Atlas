"""Atlas Material Manager."""

from __future__ import annotations

import json
from pathlib import Path

from .material import Material


class MaterialManager:
    """Handles material library IO, retrieval, state, and validation."""

    def __init__(self):
        self._materials: dict[str, Material] = {}
        self._selected_uuid: str | None = None
        self._json_path = Path(__file__).parent / "materials.json"

        self.load()

    def load(self) -> None:
        """Load materials from materials.json."""

        self._materials.clear()

        if not self._json_path.exists():
            return

        try:
            with open(self._json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            for item in data:
                material = Material.from_dict(item)
                self._materials[material.uuid] = material

        except Exception as error:
            print(f"Error loading materials.json: {error}")

    def save(self) -> None:
        """Save all materials."""

        data = [
            material.to_dict()
            for material in self._materials.values()
        ]

        try:
            with open(
                self._json_path,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(data, file, indent=4)

            for material in self._materials.values():
                material.is_dirty = False

        except Exception as error:
            raise IOError(
                f"Could not save materials: {error}"
            ) from error

    def get(self, uuid: str) -> Material | None:
        return self._materials.get(uuid)

    def get_selected(self) -> Material | None:
        if self._selected_uuid:
            return self._materials.get(self._selected_uuid)

        return None

    def select(self, uuid: str | None) -> None:
        self._selected_uuid = uuid

    def materials(self) -> list[Material]:
        return list(self._materials.values())

    def update(self, uuid: str, **kwargs) -> None:
        """Update a custom material."""

        material = self._materials.get(uuid)

        if not material or material.is_readonly:
            raise ValueError(
                "Material is read-only or not found."
            )

        # Only validate values that were actually supplied.
        for key, value in kwargs.items():

            if value is None:
                continue

            if key == "density" and value <= 0:
                raise ValueError(
                    "Density must be > 0."
                )

            if key == "youngs_modulus" and value <= 0:
                raise ValueError(
                    "Young's Modulus must be > 0."
                )

            if key == "poisson_ratio":
                if value < 0 or value >= 0.5:
                    raise ValueError(
                        "Poisson Ratio must be >= 0 and < 0.5."
                    )

            if key == "thermal_conductivity" and value < 0:
                raise ValueError(
                    "Thermal Conductivity must be >= 0."
                )

            if key == "coefficient_thermal_expansion" and value < 0:
                raise ValueError(
                    "Thermal Expansion must be >= 0."
                )

            if key == "yield_strength" and value <= 0:
                raise ValueError(
                    "Yield Strength must be > 0."
                )

            if key == "ultimate_strength" and value <= 0:
                raise ValueError(
                    "Ultimate Strength must be > 0."
                )

        # Apply the supplied values.
        for key, value in kwargs.items():
            if hasattr(material, key):
                setattr(material, key, value)

        material.is_dirty = True

    def reset_custom(self, uuid: str) -> None:
        """Clear all custom material values."""

        material = self.get(uuid)

        if material and not material.is_readonly:
            material.density = None
            material.youngs_modulus = None
            material.poisson_ratio = None
            material.thermal_conductivity = None
            material.coefficient_thermal_expansion = None
            material.yield_strength = None
            material.ultimate_strength = None

            material.is_dirty = True