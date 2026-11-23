"""Geometric metrics computed from (solved) hardpoint positions.

All functions take points in ISO 8855 (X fwd, Y left, Z up) for the LEFT wheel
and return angles in degrees.
"""

from __future__ import annotations

import numpy as np


def kingpin_axis(upper_ball_joint: np.ndarray, lower_ball_joint: np.ndarray) -> np.ndarray:
    """Unit vector of the steering axis, pointing from lower to upper ball joint."""
    v = upper_ball_joint - lower_ball_joint
    return v / np.linalg.norm(v)


def kingpin_inclination_deg(upper_ball_joint, lower_ball_joint) -> float:
    """KPI: steering axis angle from vertical, seen from the front (YZ plane).

    Positive when the top of the axis leans in towards the car centreline.
    For the left wheel 'inwards' is -Y.
    """
    a = kingpin_axis(upper_ball_joint, lower_ball_joint)
    return float(np.degrees(np.arctan2(-a[1], a[2])))


def caster_deg(upper_ball_joint, lower_ball_joint) -> float:
    """Caster: steering axis angle from vertical, seen from the side (XZ plane).

    Positive when the top of the axis is behind the bottom (top leans rearward, -X).
    """
    a = kingpin_axis(upper_ball_joint, lower_ball_joint)
    return float(np.degrees(np.arctan2(-a[0], a[2])))


def camber_deg(spin_axis: np.ndarray) -> float:
    """Camber from the wheel spin axis (unit vector pointing outboard, +Y on left).

    Negative camber = top of wheel leans inward. For the left wheel, an outboard
    axis tilted upward (+Z) means the top of the wheel leans inward -> negative.
    """
    s = spin_axis / np.linalg.norm(spin_axis)
    return float(-np.degrees(np.arcsin(s[2])))


def toe_deg(spin_axis: np.ndarray) -> float:
    """Toe from the wheel spin axis (outboard unit vector, left wheel).

    Toe-in positive: front of the wheel points toward the centreline.
    For the left wheel that means the outboard axis rotates toward -X... i.e.
    the spin axis gains a negative X component.
    """
    s = spin_axis / np.linalg.norm(spin_axis)
    return float(-np.degrees(np.arctan2(s[0], s[1])))


def instant_center_front_view(
    upper_inner, upper_outer, lower_inner, lower_outer
) -> np.ndarray | None:
    """Front-view instant centre (Y, Z) as the intersection of the two arm lines.

    Inner points should be the projection of the arm's pivot axis onto the
    plane of the wheel centre. Returns None if the arms are parallel.
    """
    p1, p2 = np.asarray(upper_inner)[1:], np.asarray(upper_outer)[1:]
    p3, p4 = np.asarray(lower_inner)[1:], np.asarray(lower_outer)[1:]
    d1, d2 = p2 - p1, p4 - p3
    denom = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(denom) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / denom
    return p1 + t * d1


def roll_center_height(instant_center_yz, contact_patch_yz) -> float | None:
    """Roll centre height: where the line from contact patch through IC crosses Y=0.

    Assumes a symmetric car (the other side gives the same line mirrored).
    """
    if instant_center_yz is None:
        return None
    (yi, zi), (yc, zc) = instant_center_yz, contact_patch_yz
    if abs(yi - yc) < 1e-9:
        return None
    return float(zc + (0.0 - yc) * (zi - zc) / (yi - yc))
