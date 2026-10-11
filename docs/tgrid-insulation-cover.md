# Five-level T-grid insulation cover

11 October 2026. The current cassette gives **each insulation layer its own
suspended T-grid**, following the owner's bottom-up assembly proposal. The current revision retains grooves only in the bottom layer; the four upper
layers rest on flat T-bar flanges. Five grids are retained by owner direction. The installed reactor
has not yet been changed. The previous all-grooved five-grid files are preserved in
`outputs/reactor-tgrid-cover/five-grooved-grid-review/`. Single-grid files are preserved locally
under `outputs/reactor-tgrid-cover/single-grid-review/`; the earlier
[rigid tray](rigid-insulation-cover.md) and [wool](insulation-cover.md) studies remain.

## Review the model

- [Editable cassette](../outputs/reactor-tgrid-cover/wistr-tgrid-cover.blend)
- [Five-layer section: start here](../outputs/reactor-tgrid-cover/tgrid-detail-layers.png)
- [Complete cassette cutaway](../outputs/reactor-tgrid-cover/tgrid-cover-cutaway.png)
- [Groove and collar detail](../outputs/reactor-tgrid-cover/tgrid-detail-groove.png)
- [Upper ceramic connection](../outputs/reactor-tgrid-cover/tgrid-detail-ceramic.png)
- [Editable sections](../outputs/reactor-tgrid-cover/tgrid-connection-details.blend)
- [Complete enclosure](../outputs/reactor-tgrid-cover/tgrid-cover-assembly.png)
- [Frame and grids, blocks hidden](../outputs/reactor-tgrid-cover/tgrid-cover-frame.png)
- [Mass and screening report](../outputs/reactor-tgrid-cover/tgrid-cover-report.json)
- [Hurmet worksheet](../../fastSalt/calculations/reactor/T-grid%20cover%20-%20Hurmet.md)

The main Blender file now opens with **actual stepped-cut insulation blocks
visible**, rather than hiding all insulation. Tan objects are blocks; silver
members are the T-grids (recessed at the bottom, below each upper layer); teal members are shared rods; gold sleeves
are crimp stops. The larger brown members above the blocks are the upper lifting
frame, not T-bars. The gray wedge below is only a **sector-cap seating reference**.
The standalone section opens showing all five layers on one rod.

Original blocks, display-cut blocks, exterior skins, grids, ceramics, facing,
and cap reference occupy separate collections. Cap hooks, plugs, bolts and
service connections still require reliefs and seating checks before integration.
The coating is cured off the reactor and is not bonded to the cap.

## Bottom-up assembly and lifting load path

1. On a flat assembly fixture, assemble the bottom grooved blocks, segmented
   cross-tees, main runners and inward-facing edge rails together. Insert rods
   through the grid saddles, with stop collars already below the saddles.
2. Set and crimp the first collars. Slide the next collars and grid saddles down
   the same rods, then place plain-bottom blocks on the T-bar flanges. Upper
   runner webs fit between blocks; no side grooves are cut in these four layers.
3. Repeat for all five layers. Main runners stay at common stations; alternating
   cross-tees and block cross-joints shift 150 mm. Main-runner joints remain aligned.
4. Install the upper frame, ceramic sleeves/washers, spreaders and nuts. Set the
   upper attachments and check that each grid takes its own layer when lifted.
   Apply/cure the assumed underside facing with appropriate fixture access.

Each saddle bridges a local clearance notch in its runner web and rests on a
collar underneath it. The collar is a **provisional swaged/crimped stop**, not a
rated connection. Its modeled Ø12 × 10 mm envelope and Ø6 mm bore are layout
inputs. Saddles have Ø8 mm sliding holes; local grid clearance is Ø14 mm and
block clearance is Ø36 mm. Cross-tee clips, saddle welds and crimp tooling access
remain to detail. Final assembly needs controlled load transfer from the fixture.

When lifting, the bottom layer bears on its groove roofs; each upper layer
bears through its flat underside on a flange. Both paths continue through the
T-grid, saddles and collars into the rods. **Loads accumulate upward in each rod**;
the upper washer/frame sees all five supported levels. Lower grooves no longer
have to carry the entire stack in the intended load path. No strength is credited
to adhesion between layers or block/coating composite action.

There are 37 Ø6 mm shared rods and 185 collars/saddles.
Five 100 mm layers provide 500 mm of nominal block thickness. The four upper
3 mm flanges increase the stack envelope to **512 mm**. Upper block bottoms are
at 103, 206, 309 and 412 mm; their supporting flanges lie immediately below.
At rest, the intervening grid strips bear on the tops of the blocks below. Collar heights are set so each grid takes its own layer during
lifting. Contact, tolerances, rod stretch and thermal expansion may redistribute
load; the idealized calculation is not proof of uniform load sharing. No rigid
adhesive is specified across layer interfaces.

The seated geometry establishes bottom-face contact with the cap reference.
At rest, load passes through blocks and intervening flange strips, with broad
upper-frame shoes bearing on the top blocks. Local compression under the strips
requires checking; gross average pressure is not the local bearing pressure. The rods take tension during lifting. Local resting contact
pressures and thermal movement still require assessment; the old four-post
solution does not apply. There is still no full bottom tray or floor-standing support post.

## Dimensions and thermal breaks

Main runner stations are X=0.30, 0.60, 1.20, 1.80, 2.40, 3.00, 3.60 and 4.02 m.
Main flanges are 50 × 3 mm, webs 45 × 2 mm; cross webs are 30 × 2 mm.
Flange elevations are 40–43, 100–103, 203–206, 306–309 and 409–412 mm.
Only the lowest flange uses the 38–43 mm groove with nominal 27 mm half-recess
width. Upper block bottoms are flat; their side joints clear the webs. A small
perimeter allowance clears the upper edge webs. No upper groove lip is used to
carry the block. Block spanning, bearing and edge integrity remain unqualified.

The upper 160 × 60 × 3 mm RHS frame begins at Z=0.515 m. Every rod crosses it
through a Ø16 mm steel bore with Ø14/8 mm zirconia sleeve, then a Ø40/14 × 10 mm
ceramic washer, Ø32 mm steel spreader and nut. There is no rod/frame steel contact
in the checked geometry. Exterior top skin is now at 0.710–0.711 m. Four sliding
hooks retain 40 mm travel and the common tool's 750 mm bar pitch.

Retain the owner-authorized assumption that the **2 mm refractory underside
facing** and bottom joint cement adhere and survive handling. Density is
provisionally 1,500 kg/m³; no product or structural composite capacity is selected.
The facing is not a pressure seal. Added embedded steel, aligned runner joints,
rod penetrations and ceramic connections need a full thermal reassessment; the
older unbridged 500 mm thermal result cannot qualify this cassette.

## Updated estimates

| Quantity | Preliminary value |
|---|---:|
| Total cassette | 2161 kg |
| Blocks | 1029 kg |
| Steel and hardware | 1088 kg |
| Ceramics | 6.4 kg |
| Facing and joint cement | 37.0 kg |
| Change from single-grid estimate | +362 kg |
| CM along bisector | 2.607 m |
| CM offset inward of tool axis | 17 mm |
| Lifted upper-frame apex displacement | 6.46 mm |
| Gross upper-frame bending stress | 55.5 MPa |
| Local main runner deflection | 0.043 mm |
| Heaviest-level collar force estimate | 125 N |
| Accumulated upper rod force estimate | 576 N |
| Gross rod stress | 20.4 MPa |
| Upper ceramic bearing estimate | 0.89 MPa |

Mass sums evaluated volumes with provisional densities; intersections are counted
additively and unfinished attachments are omitted. The added four grids increase
weight even though each grid carries its own layer. Local screening
uses each layer's actual block/grid mass, plus bottom facing on level 1, smeared
over the gross area and a 600 mm tributary width. Rod screening sums all levels
plus shared hanger/ceramic hardware. It does not determine actual reaction
redistribution, groove breakout, notched runner strength, crimp slip or weld capacity.

The upper-frame grillage uses E=140 GPa, rigid joints, area-distributed total
mass and four equal-height hooks. It is a lifted-only gross-section estimate;
local and global deflections are separate calculations. No lifting rating, hot
strength allowable, buckling, thermal distortion or fatigue qualification is given.

## Reproduce and checks

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_tgrid_cover.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/render_tgrid_detail.py
```

[Parameters](../models/wistr_tgrid_cover.py), [builder](../scripts/build_tgrid_cover.py),
[sections](../scripts/render_tgrid_detail.py), [solver](../scripts/rigid_cover_screening.py).
Checks cover 1979 closed meshes, five collars/saddles per rod,
ceramic washer count, rod/frame separation, bottom groove clearances, upper
flange/block bearing elevations, CM inside the
four-hook footprint, and common-tool engagement at both hook positions.
The solver checks cantilever reference solutions, force balance and residuals.
Report source hashes support reproduction; these checks are not a load rating.


## Fitted reactor integration

The [working reactor](reactor-study.md#insulation-covers-and-side-air-connections--11-october-2026)
now imports six fitted copies of this cassette. Hook pockets, service access wells,
thermal inserts and local frame collars are integration changes. This standalone
model and worksheet remain the unperforated-frame development reference; their
mass and grillage do not qualify the fitted assembly. See the separate fitted
geometry report in the reactor guide.
