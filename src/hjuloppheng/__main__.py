"""CLI: python -m hjuloppheng <geometry.yaml>  - prints static geometry."""

import sys

from .geometry import load_suspension
from .metrics import caster_deg, kingpin_inclination_deg


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: python -m hjuloppheng <geometry.yaml>")
        return 1
    s = load_suspension(argv[0])
    ubj, lbj = s.point("upper_ball_joint"), s.point("lower_ball_joint")
    print(f"{s.name} ({s.type})")
    print(f"  KPI:    {kingpin_inclination_deg(ubj, lbj):6.2f} deg")
    print(f"  Caster: {caster_deg(ubj, lbj):6.2f} deg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
