"""Atlas material data model."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class Material:
    """Represents a material and its engineering properties."""

    name: str
    density: float | None
    youngs_modulus: float | None
    poisson_ratio: float | None
    thermal_conductivity: float | None
    coefficient_thermal_expansion: float | None
    yield_strength: float | None
    ultimate_strength: float | None

    is_readonly: bool = False
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_dirty: bool = False

    @property
    def shear_modulus(self) -> float | None:
        """Calculate shear modulus from E and Poisson's ratio."""

        if self.youngs_modulus is None or self.poisson_ratio is None:
            return None

        denominator = 2.0 * (1.0 + self.poisson_ratio)

        if denominator == 0:
            return None

        return self.youngs_modulus / denominator

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "uuid": self.uuid,
            "density": self.density,
            "youngs_modulus": self.youngs_modulus,
            "poisson_ratio": self.poisson_ratio,
            "thermal_conductivity": self.thermal_conductivity,
            "coefficient_thermal_expansion": self.coefficient_thermal_expansion,
            "yield_strength": self.yield_strength,
            "ultimate_strength": self.ultimate_strength,
            "is_readonly": self.is_readonly,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Material:
        return cls(
            name=data.get("name", "Unknown"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            density=_optional_float(data.get("density")),
            youngs_modulus=_optional_float(data.get("youngs_modulus")),
            poisson_ratio=_optional_float(data.get("poisson_ratio")),
            thermal_conductivity=_optional_float(
                data.get("thermal_conductivity")
            ),
            coefficient_thermal_expansion=_optional_float(
                data.get("coefficient_thermal_expansion")
            ),
            yield_strength=_optional_float(
                data.get("yield_strength")
            ),
            ultimate_strength=_optional_float(
                data.get("ultimate_strength")
            ),
            is_readonly=bool(data.get("is_readonly", False)),
        )


def _optional_float(value) -> float | None:
    """Convert a value to float while preserving blank/null values."""

    if value is None or value == "":
        return None

    return float(value)