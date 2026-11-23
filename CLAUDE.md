# Suspension geometry & kinematics app (working name: hjuloppheng-kinematikk)

Open-source app for designing and analysing suspension geometry and kinematics.
The full concept, research and roadmap are in `docs/research-and-concept.md`.
Read it before starting larger work.

The maintainer (Nyborg Garage) knows suspension deeply and designs in Fusion,
but has little programming experience. Explain technical choices plainly and
give a recommendation. Chat replies may be in Norwegian (bokmål) or English. The app UI,
documentation, code, identifiers and comments are in English.

## Decisions (2026-11-23)
- Audience: everyone. Open source, **MIT** licence (proposed CC BY 4.0 for shared car data).
- Platform: **browser app in TypeScript** (React + Vite, three.js via
  @react-three/fiber + drei, Zustand, Vitest). The kinematics engine runs in the
  browser and lives in its own UI-free package.
- Python is used only for the Fusion add-in (import/export of hardpoints).
- Values are edited directly in 3D **and** in tables, always in sync. There are no
  typed "what if" questions.
- The core concept is "lock & solve": every value is free, locked or a target.
- Both MacPherson and double wishbone must be supported early, and the two must
  be comparable against the same target set.
- The app is general: every relevant variable is adjustable and nothing is tuned
  to one car. Don't design features around the user's MR2. The MR2 targets in
  `docs/mr2-rx-targets.md` are one example dataset and a source of hand-checked tests.
- The visual style follows Nick McCleery's suspension diagrams: isometric + front
  view, one colour per part, monospace labels, a moving marker on the curves.

## Goals
1. Define a suspension by hardpoints in 3D (or by engineering parameters that generate them).
2. Solve kinematics through bump/droop, steering, and later roll/heave.
3. Compute and plot through travel:
   - camber, toe (bump steer), caster, KPI, scrub radius, trail, spindle length
   - instant screw axis, FVIC/SVIC, roll centre height (kinematic, later force-based)
   - anti-dive / anti-squat / anti-lift
   - motion ratio
4. Compare variants (before/after hardpoint changes, MacPherson vs. double wishbone).
5. Lock & solve: find hardpoints that meet targets with minimum change.
6. Fusion bridge, measuring helpers, community library (see roadmap in the concept doc).

## Conventions (IMPORTANT)
- Coordinate system: ISO 8855. X forward, Y left, Z up.
  Global origin: on the ground, on the car centreline, under the front axle.
  Rear points may be *measured* from the rear axle line; the app converts using the wheelbase.
- Units: mm for lengths, degrees for angles in input/output. Radians internally.
- Signs:
  - Negative camber = top of the wheel leans in towards the car.
  - Toe-in is positive. For the LEFT wheel, toe-in means the outboard spin axis gets a **positive** X component.
  - Bump = positive Z displacement of the wheel centre.
- Hardpoints are defined for the LEFT side. The right side is mirrored about the XZ plane,
  unless both sides are entered separately (measured cars).
- MacPherson: the steering axis runs from the top-mount pivot to the lower ball joint, not along the strut axis.
- Fusion: model is Z up (matches ISO 8855). The Fusion API works in centimetres, so convert mm ÷ 10.
- Hardpoint names: **corner · part · point**, e.g. `FL · Lower arm · inner forward`,
  `RR · Upper arm · outer (ball joint)`, `RL · Toe link · inner`. Inner pivots are
  "inner forward / inner rearward" (never "front / rear", which would clash with the axle).
  The tie rod is called "toe link" on the rear axle. Code ids are camelCase without the
  corner, e.g. `lowerArmInnerForward`. Full list: concept doc §5.7.

## Current state of the code
- `prototype/suspension-prototype.html` is the Phase 1 clickable prototype: one HTML
  file, plain JavaScript + three.js 0.170 from jsDelivr (no build step). The engine part
  (a classic `<script>`, no DOM) is a generic 6-unknown Newton solver for the upright
  pose, for double wishbone and MacPherson, with 48 hand-checked "engine checks" that
  run on page load. Charts sweep heave, body roll (`rollAt`/`sweepRoll`: wheels at ∓h·tan φ,
  camber to ground, roll steer, roll centre from both contact-patch lines) and steering.
  Anti values come from the 3D path of the contact patch / wheel centre (virtual work); the
  textbook 2D pivot-axis-line SVIC (`svic2d`, `antiDive2d` …) is shown beside them for comparison.
  They differ when ball joints sit off the pivot lines in side view (example DW: 36 % vs 51 %).
  A mm/inch switch converts display only (`disp`, `Lv`, `toMm` in the UI); the model stays in mm.
  Styling: original calm dark palette (IBM Plex) with the Nyborg Garage logo and black
  background; the user found the full brand palette too intense. A "Steering layout" panel switches the rack between behind and in
  front of the axle (`flipSteering`: mirrors the arm through the steering axis in plan view).
  "Room inside the wheel" checks joints and links against rim, tyre and hub face over full
  travel × full lock (`packagingCheck`), and is also a Solve target. "Export for CAD" writes
  a CSV (`hardpointsCsv`) that `cad/fusion/ImportHardpoints` (Fusion script) and
  `cad/freecad/ImportHardpoints.FCMacro` read; both are tested only outside Fusion/FreeCAD. It also has a first lock & solve: design targets (value or range,
  incl. Ackermann and inner lock angle), padlocks per point and per coordinate, a
  Levenberg–Marquardt minimum-change solver (`createTargetSolver`), and an amber proposal
  in 3D and in the charts with Apply/Discard (details in the concept doc under the roadmap). Published privately at https://claude.ai/artifact/TsPcmyuc426vhA9SsudaEa
  (republish from the same file path to update it).
- `src/hjuloppheng/` is an early Python prototype (geometry loader, a few metrics, tests).
  It will be ported to the TypeScript engine. The Python folder will then hold the Fusion add-in.
- Known bug in the Python prototype: `toe_deg()` and its test have the toe sign inverted.
  The HTML prototype already has the correct sign.
- The TypeScript project is not scaffolded yet. **Node.js and git are not installed**
  on the user's PC (Windows 10, PowerShell). Microsoft Edge is installed and can run the
  prototype headless for checks.

## Way of working
- Write tests for every calculation using simple, hand-checkable geometries.
  Derive expected values from physical reasoning, never from the code under test.
- Run the test suite before a task counts as done.
- Keep functions small and pure: geometry in, numbers out, no global state.
- Explain the physics briefly in doc comments. The user teaches this subject, so
  correct terminology matters.

## Publishing
- Repo: https://github.com/NyborgGarage/suspension-kinematics (public, branch `main`).
- Site (GitHub Pages from `main`, root): https://nyborggarage.github.io/suspension-kinematics/
  It serves `index.html`, which is generated from the prototype. After changing the
  prototype, regenerate it and push:
  ```
  powershell -ExecutionPolicy Bypass -File tools\build-index.ps1
  git add -A; git commit -m "..."; git push
  ```
- git and gh are installed (`C:\Program Files\Git\cmd`, `C:\Program Files\GitHub CLI`); gh is
  logged in as NyborgGarage. Commits use the GitHub noreply address, never a personal email.
- `3d view example 1.png` (Nick McCleery's image) is git-ignored and must not be published.

## Commands
HTML prototype: open `prototype/suspension-prototype.html` in a browser (needs internet
for three.js). The engine checks run on load; the "engine checks" chip in the top bar
shows the result. Headless check from PowerShell (prints the DOM, including the checks):
```
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --virtual-time-budget=15000 --dump-dom "file:///<full path to prototype/suspension-prototype.html>"
```

CAD import scripts (Python 3.13 via the `py` launcher; `python` is only the Store stub):
```
py tests/test_cad_import.py
```
The fixture `tests/data/example-hardpoints.csv` is the prototype's export of the example
double-wishbone front corner; regenerate it if the example geometry changes.

Python prototype (until it is replaced):
```
pip install -e ".[dev]"
pytest
python -m hjuloppheng examples/double_wishbone_front.yaml
```
TypeScript app: to be added when the project is scaffolded.
