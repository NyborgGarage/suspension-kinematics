# Suspension geometry app – research and concept

*Status: research / proposal, 2026-11-23, updated with the first decisions
(see the table below). Phase 1 is built: a clickable prototype in
`prototype/suspension-prototype.html` (see §11).*

---

## TL;DR

**Yes, this is very doable, and there is a real gap for it.** Several tools solve
suspension kinematics. In what I found, none of them combines all of these:

1. **3D-first direct manipulation.** You drag hardpoints in 3D (or type values
   in a table), and all curves update while you edit.
2. **"Lock & solve" (inverse design).** You lock what you want (KPI, scrub, roll
   centre height, zero bump steer…) and the app finds the hardpoints, making the
   smallest change possible.
3. **Round trip with Fusion**, so hardpoints go in and out as sketches and
   parameters.
4. **A shared, open library of real cars.** I found no public database of
   production hardpoints anywhere.

The key idea that makes the UI manageable is that analysing an existing car,
changing a few values, and designing from scratch differ only in **which values
are locked and which are free**. This works like a fully constrained sketch in
Fusion: black (locked) and blue (free). One engine and one UI handle all of
them.

### Decisions so far

| Topic | Decision |
|---|---|
| Audience | Everyone. Open source. |
| Licence | **MIT** for the code. Proposed: CC BY 4.0 for shared car data. |
| Platform | **Browser app (TypeScript + React + Three.js)**, engine in the browser. Python only for the Fusion add-in. |
| Language | App UI and documentation in English |
| Editing | Values are edited **directly in 3D and in tables, both kept in sync**. No typed "what if" questions. |
| CAD axes | Fusion model is **Z up**, the same as ISO 8855 |
| Scope | **A general tool.** Every variable that matters is adjustable, and nothing is tuned to one car. |
| Example data | The MR2 rallycross targets in [mr2-rx-targets.md](mr2-rx-targets.md) are one example dataset and a source of hand-checked tests. They do not drive the design of the app. |
| Suspension types | MacPherson and double wishbone both supported from the start, and comparable against the same targets. |
| Hardpoint names | Corner · part · point, e.g. `FL · Lower arm · inner forward` (§5.7) |

---

## 1. What is in the folder today

| File | State |
|---|---|
| `CLAUDE.md`, `README.md` | Plan and conventions (ISO 8855, mm/deg, left side, mirror to right). Good basis, and the conventions carry over unchanged. |
| `geometry.py` | Dataclasses + YAML loader for 9 double-wishbone hardpoints. Works. |
| `solver.py` | Only `rotate_about_axis` exists. `solve_position` / `sweep_travel` are `NotImplementedError`. |
| `metrics.py` | KPI, caster, camber, toe, 2D front-view IC and RC height. |
| `plotting.py` | Generic matplotlib curve plot. |
| `examples/double_wishbone_front.yaml` | Placeholder geometry (KPI ≈ 9.0°, caster ≈ 1.5°). |
| `tests/test_metrics.py` | 8 tests on the metrics above. |

So it is a clean skeleton with about 200 lines of real code. Not much is lost by
moving to TypeScript.

**Bug found: the toe sign is inverted.** For the left wheel, toe-in means the
heading vector points towards −Y. The outboard spin axis is perpendicular to the
heading, so it must then get a **positive** X component. `toe_deg()` returns a
positive value for a **negative** X component, and the test
`test_camber_and_toe` asserts the same wrong thing. Both agree with each other,
so the tests pass, but toe-out is reported as toe-in. Hand-checked tests must
catch this kind of error (see §10). Camber, KPI and caster signs are correct.

Smaller issue: `instant_center_front_view` projects the inner pivots by simply
dropping X. That is only correct when the arm axes are parallel to X. The 3D
method in §4.3 replaces it.

---

## 2. Existing tools – what is out there

| Tool | Platform | 3D | Drag points in view | Targets / inverse design | Notes |
|---|---|---|---|---|---|
| **OptimumKinematics** (OptimumG) | Desktop, commercial | Yes | – | Not confirmed | Motorsport/FSAE standard. Successor to OptimumK. |
| **Lotus Suspension Analysis (SHARK)** | Desktop, commercial | Yes | No (tables) | **Yes**: kinematic optimiser with target lines, weights and selectable "positional parameters" | Many templates. Tolerance and bushing compliance. Older UI. |
| **SusProg3D** | Windows, commercial | Yes | – | Partly: auto rack position for minimum bump steer | 40+ suspension types, roll and weight transfer. |
| **bellcrank.io** | Browser | Yes (view) | No (numeric entry) | Not mentioned (forward + overlay compare) | 20 templates, wide outputs incl. anti-dive/squat and 1 g loads. CSV/IGES export, team sharing. Free tier limited; Pro €129/month. |
| **Suspension Explorer** | Python core (AGPL) + browser app | – | – | No (forward only) | Uses `scipy.optimize.least_squares`. Experimental. |
| **Bremergy SuspensionKinematics** | C++/Qt desktop, GPL | Yes | **Yes** (axis arrows, typed values, Esc to cancel) | One-shot "Generate from Design" | STEP/STL import for packaging. FSAE team tool. |
| **GearheadCalc A-arm** | Browser | Front view only (3D just for display) | Yes | **Yes**: lock the package, set windows, Solve; result shown as a *ghost* you Apply/Discard | No side view, no anti-dive. |
| **PapaCAD calculator** | Browser | Front view exact, side view approximate | Yes | No | Includes anti-dive and roll steer approximations. |
| **Racing Aspirations** calculators | Browser | 2D | Yes | No | Free. ISO 8855 / SAE J670e input. |
| **open-kinematics** (Nick McCleery) | Python, open source, work in progress | Plots (matplotlib) | No | No (forward only) | Numerical solver: each joint is a residual equation (distance, point-on-line), solved with Newton's method. Double wishbone and MacPherson. "Derived points" (wheel centre, contact patch) computed in dependency order. Well-written blog series explaining the maths. |

**Takeaways**

- Forward kinematics (hardpoints → curves) is a solved, commodity problem. We
  must get it right, but it is not the differentiator.
- **Inverse design exists only in old desktop tools (Lotus), or in 2D only
  (GearheadCalc).** Research papers treat it as the hard part: target cascading
  and hardpoint synthesis are still active SAE and thesis topics in 2022–2026.
- **No Fusion integration** turned up, beyond generic CSV-to-sketch-points
  scripts.
- **No public hardpoint library** turned up, and none of the tools above is
  both free *and* complete. An MIT-licensed, community-driven tool fills a real
  hole.
- Good UX patterns worth copying: the **ghost preview with Apply/Discard**
  (GearheadCalc), **axis-constrained dragging with typed values and Esc**
  (Bremergy), and **overlaying several designs over a sweep** (bellcrank).
- McCleery's diagrams (an isometric view next to a front view, one colour per
  part, monospace labels, a moving marker on the curve) are the visual model for
  our 3D views. His numerical approach (residual equations + Newton) is also
  what the prototype engine uses (§4.1).

---

## 3. The core idea: one model, "lock & solve"

### 3.1 Every number has a state

Every quantity in the model is one of:

| State | Meaning | Fusion analogy |
|---|---|---|
| **Free** | Computed by the app (output) | Blue sketch geometry |
| **Locked** | You fixed it; the solver must not change it | Fixed / fully constrained |
| **Target** | You want this value or curve (exact or within a band) | A driving dimension |

This applies to **hardpoint coordinates** (e.g. `upper_ball_joint.z`) and to
**derived values** (e.g. scrub radius, RC height, the bump-steer curve).
Hardpoint coordinates can also be partly locked: for example, lock Y and Z of
an inner pivot because it sits on a chassis tube, but leave X free.

There are two ways to change things:

- **Direct editing** (most of the time). You change a value in 3D or in the
  table, and everything updates instantly. No solver is involved; the app just
  recomputes.
- **Solve.** You set targets, and the app changes the *free* hardpoints as
  little as possible so that all targets are met, without touching anything
  locked.

### 3.2 Typical tasks – all done by editing values

There is no question box. Every task is done by changing a value, in 3D or in
a table, and watching the numbers and curves change.

| Task | What you do |
|---|---|
| **Analyse your car** | Enter or import the measured hardpoints. Read the curves. |
| **Lower the car 30 mm on the springs** | Change *ride height* by −30 mm. The hardpoints stay the same relative to the body; the static position moves along the existing travel curves. |
| **Lower it with a drop spindle** | Move the wheel-centre point on the upright up 30 mm. Different geometry, different result. Both cases are worth showing to students. |
| **Change camber and see what happens to scrub** | Change the camber *adjuster* value (shim thickness, eccentric angle, top-mount slot). The app moves the right point, and KPI, scrub and everything else follow. |
| **Fix bump steer** | Either drag `tie_rod_outer.z` and watch the toe curve flatten, or set *toe change = 0 ± 0.05° over ±50 mm* as a target, leave only `tie_rod_outer.z` free, and press Solve. The answer appears as e.g. "−7.4 mm". |
| **Design from scratch** | Lock the wheel, hub, track and chassis mounting planes. Set targets for KPI, caster/trail, scrub, camber curve, RC height, anti-dive, bump steer, motion ratio… Use the guided cascade (§6), then Solve. |

**Adjusters are modelled as real mechanisms** (shim stack, rod-end turns,
eccentric bolt, slotted top mount), because *how* camber is changed decides
what else changes:

- Shims at a double-wishbone upper ball joint move the UBJ outward. KPI changes,
  so scrub changes.
- A camber bolt at a MacPherson strut-to-knuckle joint rotates the knuckle. KPI
  stays the same, but the included angle and scrub change.
- A slotted top mount moves the top of the steering axis, so KPI and caster
  change.

### 3.3 Under- and over-constrained designs (the "DOF budget")

A double wishbone has 8 hardpoints × 3 = 24 coordinates, plus wheel and hub
parameters. Typical targets fix fewer than that, so designs are usually
**under-constrained**, and many designs meet the targets. Sometimes targets
**conflict**, for example a high roll centre combined with very low RC
migration and a given camber curve.

The app handles this the same way a CAD sketch solver does, and shows it:

- **Under-constrained:** the solver picks the *smallest change* from the current
  design, which is predictable and intuitive. The app also shows the **remaining
  free directions** as arrows on the hardpoints: "you can still slide this inner
  pivot along this line without changing any of your targets". Mathematically
  these are the null-space directions of the target Jacobian (SVD). For the
  front view this reproduces the classic textbook insight that an inner pivot
  can move along the line to the IC without changing static RC or camber gain.
- **Over-constrained:** the solver finds the best compromise (weighted least
  squares). It shows which targets are missed and by how much, and **which
  targets fight each other**.
- **Status indicator:** like Fusion's sketch, the app shows "Fully defined /
  N free directions / Conflicting".

### 3.4 Sensitivity view: "which knob moves this curve?"

For any selected metric (e.g. bump steer at +50 mm), the app can draw an arrow
on **every hardpoint**. Its direction shows which way to move the point to
increase the metric, and its length shows how strong the effect is (per mm).
Usually it is immediately obvious that, for example, outer tie-rod Z dominates
bump steer while the upper inner pivots barely matter. This uses the same
Jacobian as the solver, so it costs almost nothing to compute. The same
machinery also finds suspicious measurements (§8.5).

---

## 4. The kinematics engine

### 4.1 Solving positions: closed form where possible

For a **double wishbone** the position can be solved almost entirely in closed
form, without a general optimiser:

1. Each ball joint moves on a **circle** around its arm's inner pivot axis.
2. Given the lower arm angle, the LBJ is known. The UBJ is then the intersection
   of its circle with a **sphere** of radius |UBJ–LBJ| around the LBJ, which
   reduces to a trig equation `A·cos φ + B·sin φ = C` with a closed-form solution.
3. The upright can still rotate about the UBJ–LBJ line (the steering axis). The
   outer tie-rod joint fixes that rotation, giving one more equation of the same
   `A·cos ψ + B·sin ψ = C` form.
4. The input is usually wheel-centre Z rather than arm angle, so a 1-D Newton
   iteration (2–4 steps) wraps the steps above.

Each pose takes microseconds. A 101-point bump sweep takes well under a
millisecond, even in a browser. That is fast enough to **re-solve every curve on
every mouse-move while dragging**, and to let the optimiser try thousands of
designs per second.

**Assembly branches.** Each circle/sphere intersection has two solutions. One
is the real one; the other is the arm "flipped through". The app picks the one
closest to the previous pose (continuity) and flags the design if the branches
merge, which means the linkage is at a dead point.

| Suspension | Method |
|---|---|
| Double wishbone | Closed form as above |
| **MacPherson** | Strut = sliding joint (cylinder) + lower-arm circle. Small Newton solve (2–3 unknowns). Needs templates for the common lower-link variants: a one-piece A-arm, or a transverse link plus a separate tension/compression rod. For the rear: strut + lateral link(s) + trailing rod. |
| Multilink (5-link) | 5 distance constraints on a rigid upright with 6 DOF → Newton / Levenberg–Marquardt with 6 unknowns, warm-started. Still ~ms. |
| Anything else | The same general rigid-body + distance-constraint solver (this is what bellcrank and Suspension Explorer do for everything). |

**MacPherson detail that matters for teaching and for correct numbers:** the
**steering axis** runs from the *top-mount pivot* to the *lower ball joint*. It
is **not** the strut (damper) axis, which is usually offset from it. KPI,
caster, scrub and trail use the steering axis. The front-view IC is where the
lower-arm line meets the line through the top mount *perpendicular to the strut
axis*. The velocity method in §4.3 handles this automatically.

**What the prototype does today.** The prototype treats the upright as one rigid
body with 6 unknowns (3 rotations, 3 translations) and writes every joint as a
residual equation that is zero when the joint is satisfied:

- Double wishbone: each ball joint keeps its distance to both inner pivots (4),
  tie-rod length (1), wheel-centre height = requested travel (1).
- MacPherson: the lower ball joint keeps its distance to both inner pivots (2),
  the top-mount pivot stays on the strut axis, which is fixed to the upright (2),
  tie-rod length (1), wheel-centre height (1).

Newton's method with a numerical Jacobian solves the 6×6 system. Each sweep step
starts from the previous pose, so the solver stays on the same assembly branch.
A full bump sweep plus a steering sweep takes about 20 ms in the browser. That
is fast enough to recompute while dragging. The closed form above can replace
it later if speed is ever needed.

### 4.2 Inputs that drive a pose

- **Wheel travel** (bump +), defined as wheel-centre Z relative to the body
  (current convention).
- **Rack travel** (steering).
- **Ride height** (static operating point, §3.2).
- Later, at axle level: **roll angle** and **heave** of the body, solving left
  and right corners together. This is needed for camber-in-roll, roll steer and
  the anti-roll bar.
- Vehicle data needed for some metrics: wheelbase, CG height, brake bias,
  drive split, inboard or outboard brakes, corner weights (ride frequency).

### 4.3 Metrics – definitions that work in 3D

Most textbook definitions are 2D projections, for example "extend the arm lines
in front view to find the IC". That breaks down when arms are inclined in plan
view, when the arms are parallel (IC at infinity), or for multilink. The robust
general method is based on **velocities**: the derivative of positions with
respect to travel, which the solver gives almost for free.

**Instant screw axis (ISA).** From the velocities of three upright points, the
app computes the instantaneous screw axis of the upright relative to the body.
This is *the* 3D concept you were missing:

- **FVIC** = where the ISA pierces the transverse plane through the wheel
  (front view).
- **SVIC** = where the ISA pierces the longitudinal plane through the contact
  patch (side view).
- For a double wishbone with no bump steer, the ISA is the intersection line of
  the two arm planes. With bump steer it is a true screw, not a pure rotation, so
  the plane-intersection shortcut is no longer exact (Racecar Engineering makes
  this point).

In the 3D view the ISA is drawn as a line, with its front and side piercing
points marked. This links the 3D picture directly to the familiar 2D diagrams.

**Velocity-based formulas** have no singularities when arms are parallel:

| Metric | Formula (left wheel, symmetric axle) |
|---|---|
| Kinematic **roll centre height** | `z_RC = (t/2) · d(y_cp)/dz`, i.e. half-track × lateral contact-patch movement per mm of bump. This gives the same result as the IC line construction, but stays finite when the IC is at infinity. |
| **Anti-dive** (outboard brakes) | `% = (dx_cp/dz) · (L/h) · front_brake_fraction · 100` |
| **Anti-dive** (inboard brakes) / **anti-lift** (front drive) | Same, but using the **wheel-centre** path `dx_wc/dz`, because the torque is reacted by the chassis, not the upright |
| **Anti-squat** (independent rear, chassis-mounted diff, as on the MR2) | Wheel-centre path `dx_wc/dz`, L/h, rear drive fraction |
| **Motion ratio** | `MR = d(spring length)/d(wheel travel)` (virtual work). Wheel rate = `k · MR²`. |
| **Camber, toe** | From the wheel spin axis, relative to the body (and to the ground in roll) |
| **KPI, caster** | Steering axis projected onto the YZ and XZ planes (SAE definitions) |
| **Scrub radius, mechanical trail** | Steering-axis ground intercept relative to the contact patch, in the wheel's own frame (scrub along the wheel axis, trail along the heading). This matters with camber and steer. |
| **Spindle length / kingpin offset at hub height** | Steering axis to wheel centre, horizontal |
| **FVSA / SVSA length** | Distance from the contact patch (or wheel centre) to FVIC / SVIC |
| **Roll camber compensation** | `(t/2) / FVSA` (share of body roll recovered) |
| **Ackermann %, steering ratio, roll steer** | Axle-level sweeps |

The app should also offer the **force-based roll centre** next to the
kinematic one. The SAE definition is the point where a lateral force produces no
suspension movement. It needs the left/right lateral-force split as an input,
which is why it is a separate option and not the default.

**Contact patch.** It is treated as the lowest point of the (rigid) tyre in the
wheel plane, accounting for camber. Tyre vertical stiffness and loaded radius
can come later.

---

## 5. UI / UX concept: 3D-first, but not 3D-only

The 3D model should be the centre of the app. The risk is clutter. The answer
is **progressive disclosure** combined with **one-click orthographic views**,
which give you the classic 2D diagrams for free.

### 5.1 Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ File  Edit  View   Car: "MR2 RX v3" ▾      Variant: [A] [B] (+)   ↶ ↷   [Solve]│
├─────────────────┬──────────────────────────────────────────┬──────────────────┤
│ MODEL TREE      │                                          │ PROPERTIES       │
│ ▸ Vehicle       │                                          │ (selected item)  │
│ ▾ Front axle    │            3D VIEWPORT                   │                  │
│   ▸ Wheel & hub │      orbit / pan / zoom + view cube      │ Outer tie-rod L  │
│   ▸ Strut       │                                          │  X  -134.6 [ ]   │
│   ▸ Lower arm   │  [3D] [Front] [Side] [Top]   lenses ▾    │  Y   668.5 [L]   │
│   ▾ Steering    │                                          │  Z   221.3 [ ]   │
│     • Rack      │  selected point: gizmo + X/Y/Z fields    │ ──────────────── │
│     • Inner TR  │  ghost = previous / variant B            │ METRICS (static) │
│     • Outer TR  │                                          │ Camber -1.75 [T] │
│   ▸ Spring      │                                          │ KPI     10.0 [T] │
│ ▸ Rear axle     │                                          │ Scrub  +10 mm[T] │
│ ▸ Targets       │                                          │ Bump st. 0.02°/25│
├─────────────────┴──────────────────────────────────────────┴──────────────────┤
│ GRAPHS  [Bump] [Roll] [Steer]     travel ◀━━━━━━━━━●━━━━━━━▶ +32 mm  ▶ play     │
│  camber | toe (bump steer) | RC height | caster | scrub | anti-dive | MR       │
│  A = solid, B = dashed, target band = shaded, cursor synced with 3D pose       │
└──────────────────────────────────────────────────────────────────────────────┘
[L] = locked, [T] = target, empty = free. Click to toggle.
```

### 5.2 How the 3D view avoids clutter

- **Lenses (overlays) per topic, not everything at once.**
  - *Front-view lens:* arm lines extended to the FVIC, line from the contact patch
    to the RC, FVSA length, camber.
  - *Side-view lens:* SVIC, anti-dive line, caster, trail, SVSA.
  - *Steering lens:* tie-rod lines, Ackermann construction, rack.
  - *Packaging lens:* rim barrel, brake disc and caliper envelopes, clearances
    through full bump and steer.
  - *Spring lens:* spring/damper line, motion ratio.
- **Snap to Front / Side / Top** (orthographic, animated). In those views the
  matching lens turns on automatically, and you get the classic 2D construction
  drawings that teachers and textbooks use. 3D and 2D thinking are linked by
  just rotating the camera.
- **Labels only where they matter:** for the selected point and for pinned
  dimensions. Everything else shows on hover. Labels scale and fade with
  distance, so small numbers are fine as long as orbit, pan and zoom are good.
- **Click a metric to see its construction.** Clicking "Scrub radius" highlights
  the steering axis, its ground intercept, the contact patch, and a dimension
  line between them. That is great for teaching.

**Realistic view (2026-11-25).** A second drawing style for teaching, next to the diagram: the same solved points drawn as real parts (tubular arms, rubber bushings or uniballs, cast upright, hub, brake disc and caliper, coilover, tyre on a rim). It is a button in the 3D view, not a separate app, so variants, Solve and share links all work in it. Double wishbone first; the other types and guided lessons follow.

### 5.3 Editing directly in 3D

- Click a hardpoint to get a gizmo with X/Y/Z arrows. Drag along one axis, or
  type an exact value in the small field next to the point. Arrow keys nudge it
  ±1 mm (Shift ±10 mm). Esc cancels the drag.
- **While dragging**, all curves update live, and the old state stays visible as
  a faint ghost in both the 3D view and the graphs.
- **Constraint-aware dragging:** if a coordinate is locked, the gizmo only offers
  the free directions. Optionally it shows the "free directions" from §3.3, so
  you can drag *along* a direction that keeps your targets.
- **Sensitivity arrows** (§3.4) can be toggled for the selected metric.

### 5.4 Graphs

- Curves against bump, roll or steer, with variants overlaid.
- **Bidirectional link:** scrubbing the cursor in a graph moves the 3D pose, and
  dragging the wheel in 3D moves the cursor.
- **Targets drawn in the graph:** you drag a shaded band, for example "camber
  between −0.6 and −0.9°/deg roll" or "toe within ±0.05° over ±50 mm". That band
  *is* the target the solver uses. This is far more intuitive than typing
  numbers into tables.

### 5.5 Solve workflow

1. Mark targets ([T]) and locks ([L]).
2. Press **Solve**. The proposed design appears as a **ghost** with a table of
   hardpoint changes, e.g. "tie_rod_outer.z −7.4 mm", and a report of which
   targets are met.
3. **Apply** or **Discard**, or save as variant B to compare.

Undo/redo and named variants are essential from day one, because people
experiment a lot in this kind of tool.

### 5.6 Input: menus, tables and 3D – always in sync

You are right that the input needs a menu system: steering alone is a lot of
numbers. The structure is:

**1. Model tree (left)** = the menu. It is grouped by axle and subsystem, and
the suspension template decides which groups appear:

- Vehicle
- Front axle
  - Wheel & hub
  - Strut *or* Upper arm (depends on the suspension type)
  - Lower arm
  - Steering
  - Spring & damper
  - Anti-roll bar
- Rear axle
  - The same groups
- Targets

**2. Properties panel (right)** = a table for the selected group or point.
Every value has its lock/target toggle.

**3. 3D view and graphs.** Selecting something in one place selects it
everywhere. Editing a value in the table moves the point in 3D, and dragging in
3D updates the table. There is only one model underneath, so they can never
disagree.

**Two input modes per subsystem.** This solves the "too many numbers" problem:

| Mode | You enter | Used for |
|---|---|---|
| **Points** | Raw X/Y/Z of every hardpoint (what you measure, or import from Fusion) | Existing cars, fine-tuning |
| **Parameters** | Engineering values that *generate* the points | Design from scratch, quick concept work |

You can switch at any time, and the app converts between them. Example for
**Steering** (illustrative numbers):

```
STEERING (front)                         mode: (•) Parameters  ( ) Points
  Rack position         [behind ▾] the axle    X = -120 mm
  Rack height           Z = 210 mm
  Rack length           740 mm   (distance between inner joints)
  Rack travel           ±72 mm,  c-factor 48 mm/rev
  Steering arm length   135 mm
  Ackermann             60 %       (0–130 % range planned on the upright)
  ── derived (read only) ──────────────────────────────────────────────
  Inner TR joint L      X -120.0  Y  370.0  Z 210.0
  Outer TR joint L      X -134.6  Y  668.5  Z 221.3
  Tie-rod length        299.1 mm
  Max steer, inner      41.2°   ✓ ≥ 38°
  Bump steer ±50 mm     +0.02° / 25 mm   ✓ target ±0.05°
```

In **Points** mode the same panel shows the two joints as editable X/Y/Z, and
"rack behind the axle", Ackermann % and arm length become read-only derived
values. "Rack in front of or behind the axle" is then simply the sign of the
inner joint's X (origin under the axle).

**Moving the rack to the other side of the axle (built in the prototype).** One
button switches between "rack behind the axle" and "rack in front of the axle".
It does more than move the points forward:

- **What the button does.** It mirrors the outer tie-rod joint through the
  steering axis in plan view. The arm keeps its length and its line: angled
  inwards behind the axle becomes angled outwards in front.
- **Why.** That is what Ackermann needs. If the points were only moved forward
  with the arm still angled inwards, the result would be anti-Ackermann.
- **Tie rod and rack.** The tie rod keeps its length, height and front-view
  angle, so bump steer stays close. The rack becomes longer or shorter by twice
  the sideways move of the outer joint.
- **Ackermann at full lock still changes.** The arm-line rule only holds for
  small steer angles. At full lock the tie rod's own fore/aft swing works the
  other way in front of the axle. On the double wishbone example, Ackermann at
  70 mm rack went from 35 % to 16 %, and on the MacPherson from 23 % to 10 %.
  The app shows the change and makes the old layout the baseline, and the
  Ackermann and bump steer targets re-tune it.
- **Steering direction.** A given rack movement now steers the other way, so the
  pinion side changes in the real car.
- **Practical side, not modelled.** Packaging (sump, subframe, luggage area) and
  exposure of the tie rods to impacts. Tie rods in front of the axle are hit
  more easily, which matters in rallycross.

Other details that matter:

- **Left/right.** Designs are mirrored by default. A measured car can have
  **both sides entered separately**, because old cars are rarely symmetric, and
  the app then shows left/right differences.
- **Defaults from the template.** A new model is always complete and solvable,
  using typical values. Points you have not measured or set yet are shown
  greyed out as "estimated" until you replace them.
- **Paste from a spreadsheet**, and CSV import/export of the points table.

### 5.7 Hardpoint names

Every point has a readable name built from three parts: **corner · part · point**.

| Part | Points |
|---|---|
| Upper arm | inner forward, inner rearward, outer (ball joint) |
| Lower arm | inner forward, inner rearward, outer (ball joint) |
| Tie rod (front) / Toe link (rear) | inner, outer |
| Strut (MacPherson, strut + links) | top mount (pivot), axis point on upright |
| Damper | upper mount, lower mount (on arm / on upright / on the arm) |
| Wheel | centre |
| Upper forward link, Upper rearward link, Lower forward link, Lower rearward link (multilink) | inner, outer |
| Forward lateral link, Rearward lateral link (strut + links) | inner, outer |
| Trailing rod (strut + links) | forward (on the body), rearward (on the upright) |
| Trailing arm | pivot, inboard; pivot, outboard |

Code ids follow the same pattern, e.g. `upperForwardLinkOuter`, `forwardLinkInner`,
`trailingRodRearward`, `trailingArmPivotInboard`.

Examples: `FL · Lower arm · inner forward`, `RR · Upper arm · outer (ball joint)`,
`RL · Toe link · inner`.

- **Corner** is FL, FR, RL or RR. Points are entered for the left side; the right
  side is the mirror image unless both sides are measured.
- **"forward / rearward"** is used for the two inner pivots instead of
  "front / rear", so that "RL · Lower arm · inner forward" can't be confused
  with the front axle.
- In code the same point is a stable camelCase id, e.g. `lowerArmInnerForward`.
  The corner is not part of the id, because every corner has the same set of
  points. Fusion sketch points and CSV columns will use the display name.

---

## 6. Design from scratch: the guided cascade

The general optimiser can design from scratch in principle. In practice, a
**guided step-by-step cascade** works better. It follows the classic order of
the textbooks (Milliken *RCVD* ch. 17, Staniforth, Dixon), with each step
placing a few points analytically:

| Step | You give | The app places / computes |
|---|---|---|
| 1. Vehicle | Wheelbase, track, CG height, weight split, drive layout (FWD/RWD/AWD), brake bias, inboard/outboard brakes, ride height, travel range | Reference frame, contact patches |
| 2. Wheel & hub | Tyre size (→ radius), rim diameter/width/**ET offset**, hub face, bearing width, brake disc/caliper size | Wheel-centre plane, hub face, **keep-out envelope** (rim barrel, brake) |
| 3. Steering axis | KPI, caster, scrub radius, trail (or spindle length) | The steering axis as a line in 3D. Double wishbone: ball-joint heights on that line, inside the keep-out. MacPherson: lower ball joint and top-mount pivot on that line (the top mount is limited by the strut tower). |
| 4. Front view | Static RC height, camber gain (or FVSA length), chassis mounting width or plane | FVIC location, then the inner pivots. Double wishbone: both arm lines go through the FVIC. MacPherson: the lower-arm line goes through the FVIC, and the strut angle follows from the perpendicular at the top mount. |
| 5. Side view | Anti-dive % (front) / anti-squat % (rear), SVSA length | SVIC, then the tilt of each arm's pivot axis in side view (and the strut's side-view angle for MacPherson) |
| 6. Steering | Rack fore/aft position and height, Ackermann %, steering arm length | Outer tie-rod point; **inner tie-rod point solved for zero (or target) bump steer** with the classic three-position method or least squares; rack length |
| 7. Spring/damper | Motion ratio target, packaging | Spring mounts |
| 8. Refine | Curves over full travel, keep-outs, weights | General optimiser (lock & solve), minimum change |

Each step shows its construction live in 3D, with a short explanation of the
physics. Steps 1–7 are deterministic and explainable, and the optimiser then
polishes the result in step 8. A student sees *why* each point ends up where it
does.

**Comparing suspension types against the same targets.** Because the targets
are stored separately from the geometry, the *same* target set can be run
through the cascade for a MacPherson and for a double wishbone, and the two
results shown side by side. For example: "MR2 front, all targets met? Packaging?
RC migration? Camber in full bump?" This directly answers the open question
about the MR2 build.

---

## 7. Technology (decided: browser app)

### 7.1 Why a browser app

| Option | Live 3D drag | Easy to install and share | Community | Fusion palette later |
|---|---|---|---|---|
| Python desktop (old plan) | Medium | Poor | Hard | No |
| Python server + web front end | Medium (network round trip per drag) | OK | OK | Yes |
| **Browser app, engine in TypeScript (chosen)** | **Excellent** | **Excellent (just a link)** | **Easy** | **Yes** |
| Browser app, Python engine via Pyodide | OK | OK (~10–20 MB download at start) | Easy | Yes |
| C++/Qt desktop (like Bremergy) | Excellent | Poor | Hard | No |

The whole idea depends on solving on every mouse move, and that is easiest when
the engine runs in the same place as the 3D view. The problems are small (at
most ~30 unknowns), so SciPy is not needed. Levenberg–Marquardt and Newton
solvers for this size are a few hundred lines of well-tested code.

### 7.2 Stack

| Part | Choice | Why |
|---|---|---|
| Language | TypeScript | Type safety catches many mistakes; runs everywhere |
| App framework | React + Vite | Most widely used; huge ecosystem |
| 3D | three.js via **@react-three/fiber** + **drei** | Orbit controls, view cube, pivot/transform gizmos, HTML labels in 3D are ready-made |
| Charts | uPlot (fast for live updates) or Plotly (more built-in features) | Decided in the prototype |
| State + undo | Zustand (+ undo middleware) | Simple; undo/redo for free |
| Heavy solving | Web Worker | Keeps the UI smooth while the optimiser runs |
| Tests | Vitest | Same idea as pytest: hand-checkable geometries |
| Files | JSON (plus YAML/CSV import) | Easy to share and version |
| Hosting | GitHub Pages / Cloudflare Pages | Free. Works offline as a PWA. |

The **engine is a separate package** with no UI code. It can be tested on its
own, reused by the Fusion add-in or a command-line tool, and checked by
contributors.

### 7.3 Fusion bridge (Python add-in)

Fusion's API is Python (or C++), so the Fusion part stays Python.

**First step, built (2026-11-23).**

- **CSV export in the prototype.** "Export for CAD" writes a CSV with the columns
  `name,id,corner,x_mm,y_mm,z_mm`. It holds both corners, plus the steering-axis
  ground point and the contact patch centre. Coordinates are global ISO 8855 in mm.
- **Fusion script** (`cad/fusion/ImportHardpoints`). It reads the CSV and makes a
  sketch on the XY plane with one sketch point per hardpoint and lines for the
  links. It also adds one named construction point per hardpoint (mm ÷ 10, using
  `modelToSketchSpace`).
- **FreeCAD macro** (`cad/freecad/ImportHardpoints.FCMacro`). It creates labelled
  `Part::Vertex` objects and `Part::Line` links whose ends are bound to the
  vertices by expressions, so moving a vertex moves its lines. FreeCAD works in
  mm with Z up, so no conversion is needed.
- **Tests.** `tests/test_cad_import.py` runs without Fusion or FreeCAD and checks
  the parsing, the mirroring, the links and the unit conversion against an
  exported example.
- **Back from Fusion (2026-11-25).** `cad/fusion/ExportHardpoints` writes the named
  construction points (cm × 10) to the same CSV columns, with an empty id. The
  prototype's **Import CSV** (under CAD exchange, `hardpointsFromCsv`) finds points by
  id or by full name, mirrors a right-only file, undoes the wheelbase shift of rear
  files, reads ";" files with decimal commas, and makes the design before the import
  the baseline. Points not in the file are kept and listed.
- **Not yet tested inside Fusion or FreeCAD.**

**Design files and share links (2026-11-25).** *Save design* writes the whole model
(both types, wheel, vehicle, sweep, locks, targets) as JSON with a small header
(`format: "suspension-kinematics-design"`, `version: 1`). *Open design* reads it back
and makes it the baseline. *Copy share link* puts the same model, rounded to 0.001,
deflate-compressed and base64url-encoded, after `#design=` in the site URL (about
650 characters for the example). The part after `#` is never sent to the server. Opening
such a link replaces the design shown, keeps the old one one Undo away, and removes the
code from the address bar.

**Variants (2026-11-25).** Up to four whole designs (A–D) side by side, each with its own
baseline and undo history. With more than one, the design file adds `variants: [{ name, model }]`
and `active` (the `model` field stays the active variant, so a one-model reader still opens it),
and the share link carries all of them (about 900 characters for three). Opening a file or link
with several variants replaces the set, and *Bring back my variants* undoes that; a one-model
file or link opens into the variant being edited, as before.

The plan below (JSON, User Parameters, export back to the app) is still the goal.

- **Import into Fusion:** read the app's JSON and create, per corner, a component
  with named sketch points for every hardpoint, lines for arms and links,
  construction lines for the steering axis and ISA, and optionally **User
  Parameters** for every coordinate. With parameters, re-importing updates the
  model instead of rebuilding it.
- **Export from Fusion:** select named sketch points, then write JSON that the
  app opens.
- **Axes:** your Fusion model is Z up, the same as ISO 8855, so only the
  forward direction and the origin need to be agreed. Recommended: model with
  +X forward, +Y left, and the origin on the ground under the centre of the
  front axle. The add-in will also let you pick another forward axis.
- **Pitfalls to handle:**
  - The Fusion API works internally in **centimetres**, so every mm value is ÷10.
  - Sketch coordinates are relative to the sketch's own plane, so convert with
    `modelToSketchSpace` / `sketchToModelSpace`.
- **Later:** Fusion supports **HTML palettes** that talk to the add-in in both
  directions (`sendInfoToHTML` / `incomingFromHTML`). In principle the whole web
  app could run docked inside Fusion. There are reports of messaging problems
  on Mac, so this is a "later" item.

### 7.4 What happens to the existing Python code

The metric definitions and tests are ported to TypeScript, and the toe sign is
fixed at the same time. The Python folder is reused for the Fusion add-in.

---

## 8. Measuring a real car

### 8.1 Which reference (datum) to measure from

**Short answer:** use **ground (Z = 0)** and the **car centreline (Y = 0)**.
For X, do **not** use the midpoint between the axles; use the **axle line of the
axle you are measuring** (X = 0 at the front wheel centres for front points, at
the rear wheel centres for rear points). The app then converts everything to one
global system using the wheelbase.

Why:

- The **axle line** can be found precisely: drop a plumb bob from both hub
  centres and join the two marks. The midpoint of the wheelbase is a
  calculated point, not a physical one, and finding it adds error to every
  measurement.
- Each corner's geometry is naturally relative to its own wheel, so the numbers
  are short and easy to sanity-check. The wheel centre is at X ≈ 0.
- **Ground** is the right Z reference, because roll centre, anti-dive and scrub
  are all defined relative to the ground.
- The **centreline** makes left/right comparison easy and is what the track
  width is measured from.

Inside the app everything is stored in **one global system**: origin on the
ground, on the centreline, under the front axle (as in `CLAUDE.md` today), X
forward, Y left, Z up. Rear points measured from the rear axle line are shifted
by the wheelbase automatically. You choose the datum per measuring session, so
you never have to do this arithmetic yourself.

### 8.2 Ride height: measured points are only valid at a known body height

Z from the floor only means something if the body sits at its real ride height,
with driver and fuel, or with the ballast you choose. A practical way:

1. With the car on its wheels at ride height, mark **four body reference
   points** (for example the jacking points or the sills) and write down their
   heights.
2. Put the car on stands with the wheels off, and adjust the stands until those
   four heights are the same again. Now the floor represents the ground, and
   the hubs and pivots are easy to reach.
3. Optionally remove the springs, or replace them with a solid link, so the
   suspension can be moved through its travel by hand. This lets you check bump
   steer on the real car and compare it with the app.

**The floor is rarely flat or level.** You have two options:

- Measure the floor height under the four contact patches and let the app
  correct for it.
- Use a **horizontal laser plane** as the Z reference instead, and enter
  "Z measured down from the laser line at height H". The app converts.

### 8.3 Step by step

1. Car at ride height (§8.2), on a floor or laser plane you have checked.
2. **Centreline:** plumb down from two symmetric chassis points at each end,
   then snap a chalk line. **Check the chassis is square** by comparing
   diagonals. A 40-year-old shell can be off by several mm.
3. **Axle line:** plumb down from both hub centres, and draw a line square to
   the centreline.
4. **Each hardpoint:** plumb down (or use a cross-line laser) to the floor and
   mark it. Measure X along the centreline from the axle line, and Y square to
   the centreline. Measure Z from the floor (or the laser plane) to the point.
5. Enter the values in the app, preferably for **both sides**. The app shows
   the checks in §8.5 immediately.

### 8.4 Where exactly is "the point"?

The app shows a small picture and a definition for every point type, because
this is where most measuring errors come from:

| Joint | The point is… | Tip |
|---|---|---|
| Rubber/PU bushing | On the bolt axis, at the middle of the bushing length | Measure both ends of the bolt; the app computes the centre |
| Ball joint / rod end | The centre of the ball | It is inside the housing. Measure the housing and add the known offset, or measure along the stud taper. |
| Strut top mount | The pivot centre of the top bearing (spherical bearing centre on camber plates) | Not the top of the piston rod |
| Strut axis | A second point on the strut's sliding axis | For example the tube centre at the lower clamp |
| Tie-rod inner / outer | Ball centres | Inner: on the rack axis at the inner ball |
| Wheel centre | On the hub axis, in the wheel centre plane | Hub face + ET offset, or the middle of the mounted rim |

### 8.5 Help built into the app

- **Measure what you can.** XYZ is not the only input:
  - **Tape triangulation.** Measure 3–4 straight distances from known floor
    marks (or chassis points) to a hardpoint. The app solves XYZ by least
    squares and reports the error. This is often easier and more accurate than
    plumb bobs for points hidden above other parts.
  - **Bolt axis from its two ends** gives the bushing centre.
- **Plausibility checks:**
  - Left vs. right side.
  - Link lengths vs. the known part length (e.g. a tie rod you can measure on
    the bench).
  - **Alignment cross-check.** Enter the static camber, caster and toe measured
    on an alignment rig (or with a digital angle gauge). The app compares them
    with the values computed from the points, and uses the sensitivity
    machinery to name the most likely culprit, for example: "computed caster
    6.3° vs. measured 5.1°; most likely the strut top-mount X is off".
- **Measurement uncertainty (later):** each point gets a ± tolerance, and the
  app shows the curves as bands. You can then see whether a measured bump steer
  is real or within measuring noise.
- **3D scan / photogrammetry import (later):** pick points directly on a phone
  or LiDAR scan mesh (STL).

---

## 9. Community library

| Phase | Feature | Backend needed |
|---|---|---|
| 1 | **Share by link:** the whole geometry is compressed into the URL. Plus JSON files and an example library in the repo. | None |
| 2 | **Public library**, submitted via the app or GitHub pull requests | GitHub, or a small hosted database with login (e.g. Supabase, free tier) |
| 3 | Search by make/model/year/axle, "forked from" history, comments, ratings | Same |

**Metadata per car:** make, model, year, axle (front/rear), suspension type,
**data source** (measured / OEM drawing / estimated / designed), datum and ride
height used (§8), estimated accuracy, author, licence (proposed CC BY 4.0). A
"verified" flag matters, because wrong data spreads fast.

**Licence:** code under **MIT**. Car data under **CC BY 4.0** (free to use,
credit the author) is proposed.

---

## 10. Correctness and validation

- **Hand-checkable unit tests for every metric**, as `CLAUDE.md` already
  requires. The toe bug shows why tests must come from physical reasoning
  ("front of wheel points to centreline → toe-in → spin axis gets +X"), not from
  the code under test.
- **Invariant tests:** link lengths are preserved to <1e-9 mm at every pose;
  mirror symmetry holds; zero travel reproduces the static geometry.
- **Classic cases:**
  - Equal, parallel arms: no camber change relative to the body, RC at ground
    level.
  - Swing axle: RC at the pivot height.
  - Velocity-based RC equals the line-construction RC wherever both exist.
- **The MR2 targets as a test set.** The hand calculations in
  [mr2-rx-targets.md](mr2-rx-targets.md) (trail vs. caster, spindle length vs.
  KPI and scrub, camber gain vs. FVSA, roll camber compensation) become
  automated tests.
- **Cross-checks:**
  - Against an independent tool. Suspension Explorer's open-source core is ideal:
    same hardpoints, compare the curves.
  - Against your own Fusion assembly: move a joint, measure camber in Fusion.
- **Assembly branch / dead point detection**, so the app never silently jumps to
  a "flipped" solution.

---

## 11. Roadmap

Each phase ends with something you can use and test yourself.

| Phase | Content | Done when |
|---|---|---|
| 0 | ✅ Decisions (platform, licence, audience). `CLAUDE.md` updated. | Done |
| 1 | ✅ **Clickable prototype** (`prototype/suspension-prototype.html`). Double wishbone and MacPherson, front or rear axle. Isometric + front + side views; drag any hardpoint or type values; travel and rack sliders. Live graphs with a baseline to compare against. Read-outs at ride height, IC/RC/SVIC constructions, 25 built-in engine checks. Single HTML file (plain JavaScript + three.js from a CDN), no install. | Done, 2026-11-23. Now: try it and tell us what to change in the UX. |
| 2 | **Engine** (separate TypeScript package): port the prototype engine, add closed-form double wishbone, all §4.3 metrics, Vitest tests (the prototype's engine checks and the MR2 consistency checks) | Tests pass. Curves cross-checked with one other tool. Needs Node.js installed. |
| 3 | **Analysis app:** model tree + properties tables + 3D editing in sync (§5.6), live graphs, ghost, variants A/B, orthographic views with lenses, JSON/CSV import/export, share-by-link | You can enter any measured car and see bump steer change live while dragging the outer tie-rod |
| 4 | **Lock & solve:** locks and targets, minimum-change solver, ghost Apply/Discard, DOF status, sensitivity arrows | "How far must the outer tie-rod move for zero bump steer?" is answered with one click. **First version in the prototype (2026-11-23):** see "Lock & solve in the prototype" below this table. |
| 5 | **Design cascade** (§6) and **MacPherson vs. double wishbone comparison** against the same targets | One target set (for example the MR2 example) solved for both types, compared side by side. **Started in the prototype (2026-11-25):** variants A–D are compared in one table, each checked against the active variant's targets, with dashed curves and a grey 3D ghost for the variant compared with. *Solve every type* (2026-11-25) solves the active variant's targets for every type that fits the axle (front: DW and MacPherson; rear: all five), each from its own points and locks, and shows targets met, largest move and full travel side by side; each result opens as a variant. The step-by-step design cascade (§6) is still to do. |
| 6 | **Fusion bridge** (import/export add-in) | A round trip Fusion → app → Fusion gives identical points |
| 7 | **Measuring helpers** (§8.5): datum choice, triangulation, alignment cross-check | – |
| 8 | Axle level (roll, both sides, ARB), then multilink | **Started in the prototype (2026-11-25):** body roll sweep, and per-axle springs and bar: wheel rate k·MR², ride rate with the tyre in series, ride frequency, spring for a wanted frequency, bar torsion G·πD⁴/32/L (arms taken as stiff), roll stiffness Kw·t²/2 + Kθ·MRbar²·t²/arm². **Rear layouts (2026-11-25):** multilink (five two-ball links, virtual steering axis through the crossings of the lower and upper link lines), strut with two lateral links and a trailing rod (toe set by the lateral links, no steering axis), and trailing arm (one arm turning about its pivot axis; square to the car = trailing arm, swept = semi-trailing; sweep, slope and arm length shown). All solve with the same 6-unknown Newton solver. Whole car from a front and a rear variant: roll axis under the CG, roll gradient m·g·d/(K_f + K_r) in °/g, front share of roll stiffness and of lateral load transfer (elastic + geometric, sprung mass only). |
| 9 | **Community library** | – |

### Lock & solve in the prototype

**Targets.** The Design targets panel lists these quantities. You tick one and type
either a value or a range such as `9..12`. Each has a fixed tolerance, so "within
tolerance" counts as met. With a range the error is zero inside it, so Solve stops
at the nearest edge (smallest change).

- KPI, caster, mechanical trail, scrub radius, spindle length, track width.
- Camber gain, caster change and wheel-centre fore/aft per 25 mm of bump.
- Roll centre height.
- Anti-dive on the front axle; anti-squat and anti-lift on the rear axle.
- Bump steer: the toe curve is held flat at ±25 and ±50 mm, not only its slope.
- Inner-wheel angle and Ackermann % at full rack (front axle). Ackermann uses the
  kingpin track and the wheelbase.
- Motion ratio.

**Locks.** A padlock per hardpoint locks the whole point. Small padlocks lock X,
Y or Z alone, for example a chassis rail that fixes Y. The wheel centre starts
locked. Damper mounts only move when motion ratio is a target.

**Proposal curves.** The proposal's curves are drawn in amber in the charts, next
to the current design and the baseline, before you apply it.

**Solver.** Levenberg–Marquardt on Σ(error/tolerance)² + μ²·Σ(Δ/100 mm)², with
μ = 0.05. The small second term means that, when there is more freedom than
targets, Solve picks the smallest change. When there is less freedom, it finds
the best compromise and names the targets it missed. The proposal is then checked
for full bump, full droop and full rack.

Checking full travel on *every* step trapped the solver at the edge of the
feasible region: the double wishbone example met only 5 of 7 targets. That check
is therefore done on the final proposal only.

**Result.** The proposal is drawn in amber in the 3D views. A list shows how far
each point moved. Apply makes the old design the baseline, so the charts show
before and after. Discard and Undo also work.

**Engine checks.** All three start from equal parallel arms, where the upper
ball joint sits straight above the lower one, and only the upper ball joint is
free:

- KPI target atan(30/300): Solve must move the joint to the nearest point on the
  new axis. It matches the hand-derived position to within 0.001 mm.
- KPI range 3..4°: Solve must stop at the 3° edge.
- Only Y free: Solve must land on y = 700 − 300·tan θ = 670 mm.

**Example runs** on both example corners:

- Targets KPI 8°, caster 6°, trail 25 mm, camber gain −0.65°/25 mm, RC 60 mm,
  anti-dive 30 % and zero bump steer: all 7 met. The largest move is 16 mm on
  the double wishbone and 51 mm on the MacPherson.
- With ranges (KPI 9..12, trail 25..32, camber gain −0.8..−0.55, RC 40..70,
  anti-dive 25..35, inner lock 40..45°, Ackermann 40..80 %), the inner pivots'
  Y locked, caster 6° and zero bump steer: all 9 met. The largest move is
  37 mm on the double wishbone and 34 mm on the MacPherson.

**Room inside the wheel (packaging).**

- **Wheel inputs.** Rim width (J), offset (ET) and rim wall (bead seat to the
  inside of the barrel) describe the wheel.
- **Envelope.** The wheel is three solid zones in its own frame: the rim shell
  with its flange, the tyre, and the wheel disc outboard of the hub face.
- **What is checked.** Ball joints count as 30 mm spheres, arms as 20 mm tubes,
  tie rods as 16 mm tubes and the strut tube as 50 mm. The check covers full
  bump, ride height and full droop, each straight ahead and at full rack both
  ways. Parts closer than the required clearance (default 5 mm) turn red in 3D.
- **In Solve.** The same check is the target "Room in the wheel (at least)", so
  Solve can move points until everything clears. It is one-sided: only parts
  that are too close count.
- **Engine checks.** Three hand-calculated points against a 15×7 ET35 wheel.
- **Example geometries.** They were re-tuned with Solve for zero bump steer,
  Ackermann 25–60 %, inner lock ≈ 36° and at least 5 mm clearance everywhere.

**Not yet included:**

- Brake disc and caliper in the wheel envelope.
- Bent or shaped arms (arms are straight lines between their joints).
- Weights per target (all count equally relative to their tolerance).
- The guided cascade from §6.

---

## 12. Risks and pitfalls

- **Definitions and signs.** Camber relative to body or ground, KPI as a
  projection or a true angle, scrub at ground in the wheel frame, the MacPherson
  steering axis vs. the strut axis. Every definition gets written down once, in
  the code docs, with a sketch.
- **Kinematics ≠ reality.** There is no bushing compliance, tyre deflection or
  frame flex. With rallycross travel (190 mm total) the full curves matter more
  than static values. Compliance could be a later add-on.
- **Scope creep.** The list of possible features is enormous. The phases above
  keep each step small and usable.
- **UI overload.** Lenses, progressive disclosure and the points/parameters
  modes are mandatory, not optional.
- **Measurement quality** in the community library. Datum, ride height and
  source must be recorded with every submission.

---

## 13. Open questions

**Answered**

| Question | Answer |
|---|---|
| Platform | Browser app (TypeScript) |
| Audience and licence | Everyone, open source, MIT |
| Editing | Directly in 3D and in tables, both |
| Fusion axes | Z up |
| Car | The app is general. The user's 1986 MR2 AW11 (MacPherson front and rear) is only one example dataset. |
| Hardpoint names | Corner · part · point (§5.7) |

**Still open (not urgent)**

1. **App name.** "hjuloppheng-kinematikk" works for the folder, but a public
   English app needs a name.
2. **Node.js** is not installed on the development PC (git isn't either). Phase 2
   (the TypeScript project) needs Node.js LTS. git is recommended for version
   history.
3. **Rear MacPherson templates.** Which link layouts should the rear strut
   template cover first (one A-arm, two lateral links + trailing rod, …)?
4. **Fusion:** are your current hardpoints named sketch points?

---

## Sources

- Lotus Suspension Analysis – kinematic optimisation (targets, weights, positional parameters): [Getting started with Lotus Suspension Analysis](https://www.slideshare.net/slideshow/getting-startedwithlotussuspensionanalysis/66385030), [Lotus Suspension Analysis manual (Scribd)](https://www.scribd.com/doc/299402235/Lotus-Suspension-Analysis)
- SusProg3D: [SusProg3D review (AutoSpeed)](https://autospeed.com.au/a_1515/page1), [SusProg3D tutorial](https://www.bevenyoung.com.au/tutorial02.htm)
- OptimumKinematics: [OptimumKinematics help file](https://www.scribd.com/document/111202422/OptimumKinematics-Help-File), [OptimumG – suspension kinematics and its effect on performance](https://optimumg.com/suspension-kinematics-and-its-effect-on-performance/)
- bellcrank: [bellcrank.io](https://bellcrank.io/), [pricing](https://bellcrank.io/pricing), [results](https://bellcrank.io/feature/results), [topologies](https://bellcrank.io/feature/topologies)
- Suspension Explorer: [GitHub org](https://github.com/suspension-explorer), [core repo](https://github.com/suspension-explorer/suspension-explorer-core)
- Bremergy SuspensionKinematics: [GitHub](https://github.com/Bremergy-e-V/SuspensionKinematics)
- open-kinematics and the diagrams the prototype's views are modelled on: [Nick McCleery – Building a suspension kinematics tool, part I](https://nickmccleery.com/posts/11-suspension-kinematic-simulation/)
- GearheadCalc A-arm calculator: [gearheadcalc.com/a-arm-calculator](https://gearheadcalc.com/a-arm-calculator)
- PapaCAD: [Suspension kinematics calculator](https://www.papacad.com/suspension-kinematics-calculator/)
- Racing Aspirations: [Free geometry calculator (750MC)](https://750mc.co.uk/free-geometry-calculator-from-racingaspirationscom-223)
- Inverse design / hardpoint synthesis research: [Target Cascading K&C Tables to Suspension Design (SAE 2026)](https://saemobilus.sae.org/papers/target-cascading-kinematics-compliance-tables-suspension-design-2026-01-0584), [Cotugno – Python kinematic optimisation thesis (Unimore)](https://unitesi.unimore.it/retrieve/6068804e-283f-4cb5-abe5-0150df11c9ec/Cotugno.FrancescoPio.pdf), [Huang, Brandin et al. (SAE)](https://saemobilus.sae.org/downloads/articles/15-16-02-0007/Full%20Text%20PDF), [Camber gain optimisation (UT Austin)](https://cloud.wikis.utexas.edu/wiki/display/RMD/Camber+Gain+Optimization+for+Double+Wishbone+Suspension+-+Parker+Randall)
- Roll centre definitions: [Force-Based Roll Centers and an Improved Kinematic Roll Center (SAE 2006-01-3617)](https://saemobilus.sae.org/content/2006-01-3617/), [Roll center (Wikipedia)](https://www.wikipedia.org/wiki/Roll_center), [Lee & Shim – screw-axis roll axis (Springer)](https://link.springer.com/article/10.1007/s12239-011-0089-6)
- Instant axis with bump steer: [Racecar Engineering, April 2022](https://issuu.com/chelseamagazines/docs/rcra22/53)
- Measuring pickup points (centreline, plumb bobs, floor marks, laser): [MotoIQ – Project SC300, measure all the things](https://motoiq.com/project-sc300-road-racer-part-31-ecmeasure-all-the-things/3), [HP Academy – alignment on hand-built cars](https://www.hpacademy.com/forum/motorsport-wheel-alignment-fundamentals/show/alignment-on-hand-builtclassicnon-mass-production-cars), [BodyShop Business – reference points](https://www.bodyshopbusiness.com/start-with-a-good-foundation/)
- Toyota MR2 (AW11) layout: [Toyota MR2 (Wikipedia)](https://wikipedia.com/wiki/AW11)
- Fusion API: [Palette introduction](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Palettes_UM.htm), [Palette.sendInfoToHTML](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Palette_sendInfoToHTML.htm), [Understanding units in Fusion](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Units_UM.htm), [Mac palette messaging issue](https://forums.autodesk.com/t5/fusion-support-forum/palette-communication-failure-python-gt-js-sendinfotohtml/m-p/13421602), [Import CSV points add-in](https://forums.autodesk.com/t5/fusion-api-and-scripts/import-csv-points-add-in/td-p/6415411)
- 3D UI: [drei (gizmos, PivotControls, Html)](https://cdn.jsdelivr.net/gh/pmndrs/drei@master/README.md), [three.js TransformControls](https://threejs.org/docs/#examples/en/controls/TransformControls)
- Pyodide performance: [Pyodide roadmap](https://pyodide-ryanking13.readthedocs.io/en/stable/project/roadmap.html), [Pyodide in a web worker](https://pyodide.readthedocs.io/en/latest/usage/webworker.html)
- Textbooks behind §4 and §6: Milliken & Milliken, *Race Car Vehicle Dynamics* (ch. 17); J. C. Dixon, *Suspension Geometry and Computation*; A. Staniforth, *Competition Car Suspension*.
