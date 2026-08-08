"""Atlas physics support and constraint models."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ConstraintType(str, Enum):
    FIXED = "Fixed"
    PIN = "Pin"
    ROLLER = "Roller"


@dataclass
class Constraint:
    """Represents one engineering support."""

    name: str
    constraint_type: str

    location_x: float = 0.0
    location_y: float = 0.0
    location_z: float = 0.0

    direction_x: float = 0.0
    direction_y: float = 0.0
    direction_z: float = 1.0

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
                "Constraint name cannot be empty."
            )

        valid_types = {
            item.value
            for item in ConstraintType
        }

        if self.constraint_type not in valid_types:
            raise ValueError(
                "Invalid constraint type."
            )

    @property
    def location(self) -> tuple[float, float, float]:
        return (
            self.location_x,
            self.location_y,
            self.location_z,
        )

    @property
    def direction(self) -> tuple[float, float, float]:
        return (
            self.direction_x,
            self.direction_y,
            self.direction_z,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Constraint":
        return cls(
            name=str(
                data.get(
                    "name",
                    "Constraint",
                )
            ),
            constraint_type=str(
                data.get(
                    "constraint_type",
                    ConstraintType.FIXED.value,
                )
            ),
            location_x=float(
                data.get(
                    "location_x",
                    0.0,
                )
            ),
            location_y=float(
                data.get(
                    "location_y",
                    0.0,
                )
            ),
            location_z=float(
                data.get(
                    "location_z",
                    0.0,
                )
            ),
            direction_x=float(
                data.get(
                    "direction_x",
                    0.0,
                )
            ),
            direction_y=float(
                data.get(
                    "direction_y",
                    0.0,
                )
            ),
            direction_z=float(
                data.get(
                    "direction_z",
                    1.0,
                )
            ),
            object_id=data.get(
                "object_id"
            ),
            uuid=str(
                data.get(
                    "uuid",
                    uuid.uuid4(),
                )
            ),
            enabled=bool(
                data.get(
                    "enabled",
                    True,
                )
            ),
            extra=dict(
                data.get(
                    "extra",
                    {},
                )
            ),
        )


class ConstraintManager:
    """Owns all supports in the current Atlas project."""

    def __init__(self) -> None:
        self._constraints: dict[
            str,
            Constraint,
        ] = {}

    def add(
        self,
        constraint: Constraint,
    ) -> Constraint:
        constraint.validate()

        self._constraints[
            constraint.uuid
        ] = constraint

        return constraint

    def create(
        self,
        constraint_type: str,
        name: str | None = None,
        **kwargs: Any,
    ) -> Constraint:
        try:
            type_name = ConstraintType(
                constraint_type
            ).value
        except ValueError:
            type_name = str(
                constraint_type
            )

        if not name:
            name = self._next_name(
                type_name
            )

        return self.add(
            Constraint(
                name=name,
                constraint_type=type_name,
                **kwargs,
            )
        )

    def get(
        self,
        constraint_id: str,
    ) -> Constraint | None:
        return self._constraints.get(
            constraint_id
        )

    def remove(
        self,
        constraint_id: str,
    ) -> Constraint | None:
        return self._constraints.pop(
            constraint_id,
            None,
        )

    def clear(self) -> None:
        self._constraints.clear()

    def all(self) -> list[Constraint]:
        return list(
            self._constraints.values()
        )

    def by_object(
        self,
        object_id: str,
    ) -> list[Constraint]:
        return [
            item
            for item in self._constraints.values()
            if item.object_id == object_id
        ]

    def by_type(
        self,
        constraint_type: str,
    ) -> list[Constraint]:
        return [
            item
            for item in self._constraints.values()
            if item.constraint_type
            == str(constraint_type)
        ]

    def update(
        self,
        constraint_id: str,
        **changes: Any,
    ) -> Constraint:
        constraint = self.get(
            constraint_id
        )

        if constraint is None:
            raise ValueError(
                "Constraint was not found."
            )

        for key, value in changes.items():
            if hasattr(
                constraint,
                key,
            ):
                setattr(
                    constraint,
                    key,
                    value,
                )

        constraint.validate()

        return constraint

    def to_list(
        self,
    ) -> list[dict[str, Any]]:
        return [
            item.to_dict()
            for item in self._constraints.values()
        ]

    def from_list(
        self,
        data: list[dict[str, Any]],
    ) -> None:
        self.clear()

        for item in data:
            self.add(
                Constraint.from_dict(item)
            )

    def remove_for_object(
        self,
        object_id: str,
    ) -> None:
        ids = [
            item.uuid
            for item in self.by_object(
                object_id
            )
        ]

        for constraint_id in ids:
            self.remove(
                constraint_id
            )

    def _next_name(
        self,
        constraint_type: str,
    ) -> str:
        existing = {
            item.name
            for item in self._constraints.values()
        }

        index = 1

        while (
            f"{constraint_type} {index}"
            in existing
        ):
            index += 1

        return (
            f"{constraint_type} {index}"
        )