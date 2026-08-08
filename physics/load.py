"""Atlas physics load models and manager."""

from __future__ import annotations

import math
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class LoadType(str, Enum):
    FORCE = "Force"
    PRESSURE = "Pressure"
    GRAVITY = "Gravity"
    MOMENT = "Moment"


@dataclass
class Load:
    """Represents one applied engineering load."""

    name: str
    load_type: str

    magnitude: float = 0.0

    direction_x: float = 0.0
    direction_y: float = 0.0
    direction_z: float = 1.0

    location_x: float = 0.0
    location_y: float = 0.0
    location_z: float = 0.0

    object_id: str | None = None

    uuid: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    enabled: bool = True

    extra: dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "Load name cannot be empty."
            )

        if not math.isfinite(self.magnitude):
            raise ValueError(
                "Load magnitude must be finite."
            )

        if self.magnitude < 0:
            raise ValueError(
                "Load magnitude cannot be negative."
            )

    @property
    def direction(self) -> tuple[float, float, float]:
        return (
            self.direction_x,
            self.direction_y,
            self.direction_z,
        )

    @property
    def location(self) -> tuple[float, float, float]:
        return (
            self.location_x,
            self.location_y,
            self.location_z,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Load":
        return cls(
            name=str(
                data.get("name", "Load")
            ),
            load_type=str(
                data.get(
                    "load_type",
                    LoadType.FORCE.value,
                )
            ),
            magnitude=float(
                data.get("magnitude", 0.0)
            ),
            direction_x=float(
                data.get("direction_x", 0.0)
            ),
            direction_y=float(
                data.get("direction_y", 0.0)
            ),
            direction_z=float(
                data.get("direction_z", 1.0)
            ),
            location_x=float(
                data.get("location_x", 0.0)
            ),
            location_y=float(
                data.get("location_y", 0.0)
            ),
            location_z=float(
                data.get("location_z", 0.0)
            ),
            object_id=data.get("object_id"),
            uuid=str(
                data.get(
                    "uuid",
                    uuid.uuid4(),
                )
            ),
            enabled=bool(
                data.get("enabled", True)
            ),
            extra=dict(
                data.get("extra", {})
            ),
        )


class LoadManager:
    """Owns all loads in the current Atlas project."""

    def __init__(self) -> None:
        self._loads: dict[str, Load] = {}

    def add(
        self,
        load: Load,
    ) -> Load:
        load.validate()
        self._loads[load.uuid] = load
        return load

    def create(
        self,
        load_type: str,
        name: str | None = None,
        **kwargs: Any,
    ) -> Load:
        try:
            type_name = LoadType(
                load_type
            ).value
        except ValueError:
            type_name = str(load_type)

        if not name:
            name = self._next_name(
                type_name
            )

        return self.add(
            Load(
                name=name,
                load_type=type_name,
                **kwargs,
            )
        )

    def get(
        self,
        load_id: str,
    ) -> Load | None:
        return self._loads.get(load_id)

    def remove(
        self,
        load_id: str,
    ) -> Load | None:
        return self._loads.pop(
            load_id,
            None,
        )

    def clear(self) -> None:
        self._loads.clear()

    def all(self) -> list[Load]:
        return list(
            self._loads.values()
        )

    def by_object(
        self,
        object_id: str,
    ) -> list[Load]:
        return [
            load
            for load in self._loads.values()
            if load.object_id == object_id
        ]

    def by_type(
        self,
        load_type: str,
    ) -> list[Load]:
        return [
            load
            for load in self._loads.values()
            if load.load_type == str(load_type)
        ]

    def update(
        self,
        load_id: str,
        **changes: Any,
    ) -> Load:
        load = self.get(load_id)

        if load is None:
            raise ValueError(
                "Load was not found."
            )

        for key, value in changes.items():
            if hasattr(load, key):
                setattr(
                    load,
                    key,
                    value,
                )

        load.validate()

        return load

    def to_list(
        self,
    ) -> list[dict[str, Any]]:
        return [
            load.to_dict()
            for load in self._loads.values()
        ]

    def from_list(
        self,
        data: list[dict[str, Any]],
    ) -> None:
        self.clear()

        for item in data:
            self.add(
                Load.from_dict(item)
            )

    def remove_for_object(
        self,
        object_id: str,
    ) -> None:
        ids = [
            load.uuid
            for load in self.by_object(object_id)
        ]

        for load_id in ids:
            self.remove(load_id)

    def _next_name(
        self,
        load_type: str,
    ) -> str:
        existing = {
            load.name
            for load in self._loads.values()
        }

        index = 1

        while (
            f"{load_type} {index}"
            in existing
        ):
            index += 1

        return f"{load_type} {index}"