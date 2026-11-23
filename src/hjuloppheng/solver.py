"""Kinematic solver (to be implemented).

Plan (see CLAUDE.md):
- Each wishbone rotates about its inner pivot axis (two chassis points).
- The upright is a rigid body carrying the ball joints, outer tie-rod joint
  and wheel centre.
- For a given wheel travel (dz) and rack displacement, solve for the arm
  angles and upright orientation so that all link lengths are preserved,
  using scipy.optimize.least_squares. Warm-start from the previous step.
"""

from __future__ import annotations

import numpy as np

from .geometry import Suspension


def rotate_about_axis(point, axis_a, axis_b, angle_rad) -> np.ndarray:
    """Rotate `point` about the line through axis_a -> axis_b (Rodrigues)."""
    k = axis_b - axis_a
    k = k / np.linalg.norm(k)
    v = point - axis_a
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return axis_a + v * c + np.cross(k, v) * s + k * np.dot(k, v) * (1 - c)


def solve_position(susp: Suspension, wheel_travel: float, rack_travel: float = 0.0):
    """Return solved hardpoints for a given wheel travel [mm] and rack travel [mm]."""
    raise NotImplementedError("Kinematic solver not implemented yet")


def sweep_travel(susp: Suspension, travels):
    """Solve over a range of wheel travel values, warm-starting each step."""
    raise NotImplementedError
