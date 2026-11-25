# Suspension geometry & kinematics (working name)

An open-source, 3D-first tool for designing and analysing suspension geometry:
camber, toe / bump steer, caster, KPI, scrub, trail, roll centre, anti-dive /
anti-squat, motion ratio. It supports both analysing existing cars and designing
from targets ("lock & solve").

**Status:** Phase 1, a clickable prototype. The full TypeScript app is not built yet.

- Concept, research and roadmap: [docs/research-and-concept.md](docs/research-and-concept.md)
- Example target set (Toyota MR2 rallycross): [docs/mr2-rx-targets.md](docs/mr2-rx-targets.md)
- Conventions: ISO 8855 (X forward, Y left, Z up), millimetres and degrees.
  Hardpoint names like `FL · Lower arm · inner forward` (concept doc §5.7).

## Clickable prototype
Open [prototype/suspension-prototype.html](prototype/suspension-prototype.html) in
a browser (double-click it). It needs an internet connection to load three.js.

- Double wishbone or MacPherson, front or rear axle.
- Isometric, front and side views. Click a point, drag the arrows, or type values.
- Wheel-travel, body-roll and rack sliders; Play animates bump and droop.
- Charts in heave, roll (camber to ground, roll steer, roll-centre height and sideways
  movement) and steering.
- mm / inch switch for everything shown (the model and the CSV stay in mm).
- Live graphs with a baseline to compare against; IC, roll centre and side-view IC
  constructions; read-outs at ride height.
- Design targets ("lock & solve"): tick KPI, caster, trail, camber gain, roll centre,
  anti-dive, bump steer, steering angle, Ackermann and more. Type a value or a range
  such as `9..12`, lock the points (or single X/Y/Z coordinates) that must stay, and
  press Solve. The proposal is shown in amber in the views and the charts; Apply or
  Discard it.
- Steering layout: one button moves the rack (or toe link) between behind and in front
  of the axle, and shows arm angle, the arm angle for 100 % Ackermann, rack length and height.
- Springs and anti-roll bar: spring rate, sprung corner mass, tyre rate and bar size give wheel
  rate, ride rate, ride frequency (and the spring for a wanted frequency), and roll stiffness from
  springs and bar. Wheel rate and ride frequency can be charted through travel.
- 60 engine checks run on load and compare the solver with values worked out by hand.

- Room inside the wheel: rim width, offset (ET) and rim wall define the wheel. Ball joints,
  arms, tie rods and the strut are checked against rim, tyre and hub face at full bump and
  droop combined with full lock. Parts that are too close turn red, and Solve can clear them.

Your edits are saved in the browser you use (local storage). Under **Save, open and share**:

- **Save design** downloads a `.json` file with everything (both suspension types, wheel,
  vehicle, sweep, locks and targets). **Open design** loads it again.
- **Copy share link** copies a link that opens exactly this design. The design travels inside
  the link (after `#`), so nothing is stored on a server. The person opening it keeps their own
  design one Undo away.

## From the prototype into CAD
1. In the prototype, use **CAD exchange**. **Download CSV** saves the file (in the claude.ai
   preview: **Copy CSV**, paste into Notepad and save as `hardpoints.csv`).
2. **Fusion:** Utilities > Add-Ins > Scripts and Add-Ins, Scripts tab, green **+**, choose the
   folder `cad/fusion/ImportHardpoints`. Select **ImportHardpoints**, **Run**, pick the CSV.
   You get a sketch with points and link lines, and named construction points. Use a Z-up
   design.
3. **FreeCAD:** Macro > Macros..., set the macro location to `cad/freecad` (or copy the file
   to your macro folder), select **ImportHardpoints.FCMacro**, **Execute**, pick the CSV.
   You get named vertices and link lines that follow the vertices.

**Back from Fusion:** move the sketch points, then run **ExportHardpoints** (folder
`cad/fusion/ExportHardpoints`, installed the same way). In the prototype, **Import CSV** reads
the file. The design before the import becomes the baseline, so the charts show before and after.

The CSV columns are `name,id,corner,x_mm,y_mm,z_mm` (ISO 8855, mm, X from the front axle
line). Test the scripts' CSV handling with `py tests/test_cad_import.py`.

## Python prototype (older)
```
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m hjuloppheng examples/double_wishbone_front.yaml
```

## Licence
MIT – see [LICENSE](LICENSE).
