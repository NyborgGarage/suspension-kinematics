"""Hardpoint definitions and loading.

Coordinate system: ISO 8855 (X forward, Y left, Z up), millimetres.
Hardpoints are given for the LEFT side; use `mirror_to_right` for the right side.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

DOUBLE_WISHBONE_POINTS = (
    "upper_front_inner",
    "upper_rear_inner",
    "upper_ball_joint",
    "lower_front_inner",
    "lower_rear_inner",
    "lower_ball_joint",
    "tie_rod_inner",
    "tie_rod_outer",
    "wheel_center",
)


@dataclass
class Wheel:
    radius: float
    static_camber_deg: float = 0.0
    static_toe_deg: float = 0.0


@dataclass
class Suspension:
    name: str
    type: str
    hardpoints: dict[str, np.ndarray]
    wheel: Wheel
    extra: dict = field(default_factory=dict)

    def point(self, key: str) -> np.ndarray:
        return self.hardpoints[key]

    def validate(self) -> None:
        if self.type == "double_wishbone":
            missing = [p for p in DOUBLE_WISHBONE_POINTS if p not in self.hardpoints]
            if missing:
                raise ValueError(f"Missing hardpoints: {missing}")


def load_suspension(path: str | Path) -> Suspension:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    hardpoints = {k: np.asarray(v, dtype=float) for k, v in data["hardpoints"].items()}
    susp = Suspension(
        name=data.get("name", Path(path).stem),
        type=data["type"],
        hardpoints=hardpoints,
        wheel=Wheel(**data["wheel"]),
    )
    susp.validate()
    return susp


def mirror_to_right(points: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Mirror left-side points about the XZ plane (Y -> -Y)."""
    m = np.array([1.0, -1.0, 1.0])
    return {k: v * m for k, v in points.items()}
