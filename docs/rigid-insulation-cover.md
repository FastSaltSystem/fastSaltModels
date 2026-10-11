# Rigid-block insulation cassette — preliminary alternative

11 October 2026. Owner requested comparison with the wool cassette after raising
concerns about apex sag and the number of intermediate supports. This is a separate
candidate; the existing wool model and installed reactor hood are unchanged.

## Review

- [Editable Blender model](../outputs/reactor-rigid-cover/wistr-rigid-cover.blend)
- [Complete enclosure](../outputs/reactor-rigid-cover/rigid-cover-assembly.png)
- [Upper frame and suspended tray](../outputs/reactor-rigid-cover/rigid-cover-frame.png)
- [Stepped block cutaway](../outputs/reactor-rigid-cover/rigid-cover-cutaway.png)
- [Mass, geometry and screening report](../outputs/reactor-rigid-cover/rigid-cover-report.json)
- [Hurmet worksheet](../../fastSalt/calculations/reactor/Rigid%20cover%20cassette%20-%20Hurmet.md)

The Blender file opens on the frame. Toggle **Calcium silicate blocks** and
**Exterior skins** in the Outliner to see the complete cassette. **Cutaway blocks**
contains display copies only. The common head is included in **Remote lifting tools**.
One cassette represents the repeated six-sector assembly; no reactor integration
or installation-envelope update is made by this script.

## Load path and construction

Keep the existing approximately 8.24 m cover footprint, five 100 mm insulation
layers and four sliding pickups with 40 mm take-up. Use rigid calcium-silicate
blocks instead of wool. The draft block pattern uses nominal 600 × 300 mm plan
pieces, staggered by 300/150 mm between layers, with trimmed perimeter pieces.
The 348 modeled pieces include small edge fragments; this is a visual
joint arrangement, not an optimized cutting or procurement schedule. Thin joints
need an insulating closure. Product form and 100 mm layer supply remain to confirm.

Blocks stack directly on one another. Their dead-weight pressure at the bottom
is only about 1.18 kPa at the 240 kg/m³ density allowance. No block tensile,
flexural, composite or joint shear strength is credited in the frame calculation.
A continuous 1.5 mm stainless liner retains fragments and spans short gaps between
100 mm-wide bottom channel tops at nominal 300 mm pitch. Each channel has two
60 × 2 mm webs below its 2 mm top. Longitudinal perimeter strips retain the edge.

Three 6 mm tension rods support each of the 14 bottom channel rows: one at the
centre and two near its ends. These 42 rods distribute pickup
across the footprint, including the apex and outer rim. The last row is at
4.02 m. Top brackets and lower bearing washers connect the rods to steel rather
than placing small washers directly against insulation. Thread roots, adjustment,
thermal expansion accommodation and lock arrangements need detail design.

The upper frame has two radial edge members and a centre spine joined by
transverse members at the hook rows and intermediate stations. The outer boundary
is faceted to follow the circular rim. Initial members are 160 × 60 × 3 mm steel
rectangular hollow sections; their joints are idealized as rigid. Pickup slots
are cut through the crossbeams and reinforced schematically by 12 mm bearing
plates. Actual local reinforcement, welds and net sections are not checked.

The frame is above the insulation, at Z=0.565–0.725 m. The enclosing top skin
is at Z=0.760–0.761 m, **240 mm higher** than the wool enclosure. Hook feet are
at Z=0.850 m before the 40 mm take-up. Hook profile and 750 mm bar pitch stay
compatible with the existing common head. Longer poles, envelope checks and
service penetrations remain to integrate at reactor level.

Four hollow posts below the upper frame give it a resting load path. Their feet
rest on the same provisional Ø50 × 75 mm zirconia breaks, placed beneath the
edge members at the hook-row radii. Fixed seats remain behind during lifting.
The four posts and their attachments are not structurally qualified. Rod/post
passages are cut through the block layers and liner; joint seals are not detailed.

## Comparison and first structural screening

| Item | Wool draft | Rigid-block candidate |
|---|---:|---:|
| Insulation and filler | 561 kg | 1056 kg |
| Steel and hardware | 899 kg | 783 kg |
| Additive mass estimate | 1460 kg | 1839 kg |
| Insulation depth | 500 mm | 500 mm |
| Intermediate framed grids | Four | None |
| Top skin elevation above liner | 521 mm | 761 mm |

The candidate is approximately 379 kg heavier per
cassette. Eliminating four intermediate trays saves some steel, but this first
version is not yet a lightweight solution. Its 42 repeated rod connections also
remain a fabrication tradeoff. The CM is at radius 2.620 m,
inside the four-hook footprint and about 3.7 mm inward
of the head axis. The head and fixed ceramic seats are excluded from mass.

A NumPy linear grillage model screens the **upper frame only**. Each node has
vertical displacement and two rotations. Members use Euler bending and thin-wall
closed-box torsion, with E=140 GPa and Poisson ratio 0.30 as provisional inputs.
Total modeled mass is distributed by plan tributary area, then 25/50/25% to the
two edge rails and centre rail. This approximates bottom-channel reactions and
smears actual steel masses. Four equal-elevation vertical constraints represent
either hooks or seats. Rotations remain free; joints within the frame are rigid.

| Dead-weight result | Lifted | Seated |
|---|---:|---:|
| Upper-frame apex deflection | 5.65 mm | 4.72 mm |
| Maximum gross-section bending stress | 48.9 MPa | 32.3 MPa |

The apex is the largest downward nodal displacement in both cases. These values
exclude local pickup weakening, connection flexibility and thermal distortion.
They do not establish allowable strength or stiffness. A two-times-gravity
sensitivity doubles these linear results; it is not a prescribed code factor.
The prior wool draft has no comparable structural solution, so this is not a
quantified stiffness comparison against it.

Separate simply supported strip estimates give approximately
2.34 mm bottom-channel sag at the widest half-span,
0.62 mm liner-strip sag between channels and
0.11 mm maximum rod stretch. These occur at different
locations and should not be presented as a solved total apex displacement.
All load paths need a coupled model for further design. Hanger-root stress,
channel lateral stability, posts, welds, impact, fatigue, lifting dynamics,
seat-height errors and the compliant crane suspension are not solved.

## Material and thermal basis

[Johns Manville Thermo-1200 data](https://www.jm.com/content/dam/jm/global/en/industrial-insulation/calcium-silicate/thermo-1200/JM_IND_Thermo-1200_DS.pdf)
reports a typical dry-density average below 240 kg/m³, service to 650°C and
compression above 690 kPa **at 5% compression**. That compression-test value is
not a permissible working stress or a hot creep limit. The 240 kg/m³ density is
used as an allowance, not a guaranteed maximum delivered mass. Grade, wet mass,
cycling and allowable deformation remain open.

The previous 500 mm flat-wall insulation allowance is retained for comparison.
No new whole-cassette thermal result is claimed. Hangers, posts, seams and the
upper airspace introduce heat paths; the zirconia blocks only address their
specific axial support path. The upper frame must not be assumed to be cold.

## Reproduce and checks

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_rigid_cover.py
```

Inputs: [parameters](../models/wistr_rigid_cover.py),
[builder](../scripts/build_rigid_cover.py),
[screening solver](../scripts/rigid_cover_screening.py).
The solver runs with Blender's bundled NumPy. The report records source hashes.

Checks: 751 closed meshes; sampled common-tool docking, capture
and release at both slider endpoints; CM inside hook polygon; cantilever tip
solutions in two orientations; force equilibrium, positive support reactions and
small free-DOF residuals in both support cases. Mass uses evaluated mesh volumes
with provisional densities and double-counts overlapping metal at member joints.
Display-cut copies and fixed supports are excluded. These are screening and
geometry checks, not fabrication approval.

## Subsequent revision

The [recessed T-grid cassette](tgrid-insulation-cover.md) supersedes this tray/post
arrangement as the current development direction. This page preserves the earlier
comparison; its four-post seated result does not apply to the new design.
