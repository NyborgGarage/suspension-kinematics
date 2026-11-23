import numpy as np
import pytest

from hjuloppheng.geometry import load_suspension, mirror_to_right
from hjuloppheng.metrics import (
    camber_deg,
    caster_deg,
    instant_center_front_view,
    kingpin_inclination_deg,
    roll_center_height,
    toe_deg,
)
from hjuloppheng.solver import rotate_about_axis


def test_vertical_kingpin_has_zero_kpi_and_caster():
    lbj, ubj = np.array([0, 700, 150.0]), np.array([0, 700, 450.0])
    assert kingpin_inclination_deg(ubj, lbj) == pytest.approx(0)
    assert caster_deg(ubj, lbj) == pytest.approx(0)


def test_kpi_inward_lean_positive():
    # top 100 mm inboard over 100 mm height -> 45 deg
    lbj, ubj = np.array([0, 700, 100.0]), np.array([0, 600, 200.0])
    assert kingpin_inclination_deg(ubj, lbj) == pytest.approx(45)


def test_caster_rearward_top_positive():
    lbj, ubj = np.array([0, 700, 100.0]), np.array([-100, 700, 200.0])
    assert caster_deg(ubj, lbj) == pytest.approx(45)


def test_camber_and_toe():
    assert camber_deg(np.array([0, 1.0, 0])) == pytest.approx(0)
    a = np.radians(2)
    # outboard axis tilted up -> top of wheel leans in -> negative camber
    assert camber_deg(np.array([0, np.cos(a), np.sin(a)])) == pytest.approx(-2)
    # spin axis rotated toward -X -> front of wheel points in -> toe-in
    assert toe_deg(np.array([-np.sin(a), np.cos(a), 0])) == pytest.approx(2)


def test_parallel_equal_arms_give_no_ic():
    assert instant_center_front_view([0, 300, 500], [0, 650, 500],
                                     [0, 300, 200], [0, 650, 200]) is None


def test_roll_center_on_ground_for_ic_on_ground_line():
    ic = instant_center_front_view([0, 0, 400], [0, 600, 500],
                                   [0, 0, 100], [0, 600, 150])
    rc = roll_center_height(ic, (750.0, 0.0))
    assert rc is not None and np.isfinite(rc)


def test_rotate_about_axis_quarter_turn():
    p = rotate_about_axis(np.array([0, 1.0, 0]), np.zeros(3),
                          np.array([1.0, 0, 0]), np.pi / 2)
    assert p == pytest.approx([0, 0, 1])


def test_example_loads_and_mirrors():
    s = load_suspension("examples/double_wishbone_front.yaml")
    right = mirror_to_right(s.hardpoints)
    assert right["wheel_center"][1] == pytest.approx(-s.point("wheel_center")[1])
