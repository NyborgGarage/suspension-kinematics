# Toyota MR2 (1986, AW11) rallycross – geometry targets

Source: the user's earlier design discussion, pasted on 2026-11-23 and
translated from Norwegian. The values are copied unchanged.

Car: 1986 Toyota MR2, mid-engine, rear-wheel drive. Stock suspension is
MacPherson front and rear. Class: Nasjonal (rallycross). Rear diff: Torsen,
chassis-mounted.

These targets are the **first real test case** for the app. Every row should
end up as a target, a locked value or a derived check in the app.

## Front

| Parameter | Start value | Range | Comment |
|---|---|---|---|
| SAI / KPI | 10° | 9–12° | Follows from spindle length and scrub radius |
| Caster | 6.5° | 5.5–7°, adjustable ±1.5° | Gives negative camber on the outer wheel when steering in, positive when countersteering |
| Mechanical trail | 28 mm | 25–35 mm | Hub approx. 6 mm ahead of the steering axis at 6.5°; gives steering feel when sliding |
| Scrub radius | +10 mm | 0 to +20 mm | Low steering torque with uneven braking force |
| Spindle length at wheel-centre height | 63 mm | As short as rim and hub allow | Moment arm for impacts from edges and holes |
| Static camber | −1.75° | −1.5 to −2.0°, adjustable 0 to −4° | Moderate, because of braking and countersteer |
| Camber gain at static | 0.65°/25 mm | 0.55–0.8°/25 mm | FVSA approx. 2200 mm, slightly progressive in bump |
| Roll camber compensation | approx. 36 % | 30–45 % | Share of body roll that is recovered |
| Roll centre height | 50 mm | 40–70 mm | Small migration in heave and roll |
| Anti-dive | 30 % | 25–35 % | Side-view IC behind the wheel, below wheel-centre height |
| Caster change over travel | ≤ 0.55°/25 mm | approx. +2.3° at full bump, −1.8° at full droop | Follows from anti-dive |
| Wheel-centre path in bump | Slightly rearward | 0–2 mm per 25 mm | Absorbs impacts from edges and holes |
| Bump steer | 0 | ±0.05°/25 mm within ±50 mm, max ±0.3° total | Most important under braking |
| Static toe | 0 | 0 to 1 mm out per wheel | A little toe-out gives quicker turn-in |
| Ackermann | To be decided later | Upright prepared for approx. 0–130 % | Outer tie-rod joint movable, all positions at the same height |
| Steering angle, inner wheel | 40° | At least 38° | Hairpins, handbrake turns, countersteer |
| Total travel | 190 mm | 180–200 mm | 105 mm bump, 85 mm droop from static |
| Ride frequency | 1.4 Hz | 1.3–1.5 Hz | Geometry must tolerate 1.2–1.8 Hz |
| Motion ratio | 0.8 | 0.75–0.9 | Requires approx. 150 mm damper stroke |
| Bump stop | Progressive rubber/PU | Last 25–35 mm | Hydraulic bump stops are not allowed in Nasjonal |
| Anti-roll bar | Required | Adjustable, can be disconnected | Front takes 45–52 % of the lateral load transfer |
| Track width | approx. 1590 mm | Limited by 75 mm fender flares | More grip and stability at the front |
| Rim | 16×7J ET40 | 6.5–7.5J | See "Rim and tyre" (not included in the paste) |
| Lower arm | Inner mount high, arm near horizontal at static | – | The tube can be bent upward between the mounts |

## Rear

| Parameter | Start value | Range | Comment |
|---|---|---|---|
| Static camber | −1.2° | −1.0 to −1.5° | Traction at launch and out of corners |
| Camber gain | 0.5°/25 mm | 0.4–0.6°/25 mm | Calm under power |
| Roll centre height | 65 mm | 50–80 mm | Lower than previously suggested; keeps the inner wheel down |
| Anti-squat | 50 % | 40–65 % | Calculated from wheel centre to side-view IC, since the diff is chassis-mounted |
| Toe | 1.5 mm in per wheel | 1–2 mm in | Stability under power and braking |
| Bump steer | Slight toe-in in bump | 0 to +0.05°/25 mm | Stable in roll |
| Ride frequency | 1.4 Hz | 1.3–1.5 Hz | Softer than front |
| Total travel | 190 mm | 180–200 mm | More droop than front, approx. 95 mm |
| Track width | Not narrow, for traction | Front 0–50 mm wider | Torsen wants the inner wheel on the ground |

## Consistency checks (hand calculations → first unit tests)

The targets agree with each other. These checks become automated tests later.

| Check | Calculation | Result |
|---|---|---|
| Trail vs. caster | `R·tan(6.5°) − 6 mm = 28 mm` | Implies loaded tyre radius **R ≈ 298 mm** |
| Spindle length vs. KPI and scrub | `10 + 300·tan(10°) = 62.9 mm` | ✓ matches 63 mm (camber ignored) |
| Camber gain vs. FVSA | `25 / tan(0.65°) = 2204 mm` | ✓ matches FVSA ≈ 2200 mm |
| Roll camber compensation | `(1590/2) / 2200 = 36.1 %` | ✓ matches ≈ 36 % |
| Caster change at full bump / droop | `0.55 × 105/25 = 2.31°`, `0.55 × 85/25 = 1.87°` | ✓ matches +2.3° / −1.8° |
| Caster change vs. SVSA | `25 / tan(0.55°) ≈ 2600 mm` | Side-view swing arm ≈ 2.6 m |
| Damper stroke | `190 × 0.8 = 152 mm` | ✓ matches ≈ 150 mm |
| Rear camber gain vs. FVSA | `25 / tan(0.5°) = 2864 mm` | Rear FVSA ≈ 2.9 m |
| SVIC behind the wheel, between ground and wheel-centre height | Contact patch moves forward in bump → anti-dive (outboard brakes); wheel centre moves rearward | ✓ "slightly rearward wheel-centre path" and anti-dive are compatible |

**Inputs still missing** for anti-dive and anti-squat percentages and ride
frequencies:
- CG height
- wheelbase as built
- brake balance
- corner weights
- tyre size or loaded radius (implied ≈ 300 mm)
- rear track as built
