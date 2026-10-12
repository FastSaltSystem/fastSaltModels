# Fast Salt System site draft

Cleanup note — 12 October 2026: superseded generated drafts have been removed. Current site plans and the saved scene are together in `outputs/site-45-bends/`. The saved site still represents the last accepted site arrangement; the next build imports the current under-cover-bundle installation. Historical output links below may require rebuilding.

## Current motor-BFP equipment draft — revised arrangement

The [main internal piping draft](turbine-piping.md) now adds 59 route sections
and a color-coded plan to this layout. It retains the 60 m hall and flags the
east feedwater aisle height, crossover lengths and overhead maintenance access.

D-031 reduces the D-029/D-030 hall from 66 × 40 × 28 m to **60 × 40 × 28 m**.
The current D-032 alignment places its centre at (−66, 0) m. Its east wall remains at X=−36 m. A **20 × 10 × 7 m BFP electrical
annex** sits to the south; north/south extraction aprons reserve 7/12 m beyond
selected wall segments. Fuel preparation stays at its earlier dimensions/location.
The common pad expands to 190 × 110 m, centred at (−14, −5), still at Z=−9.1 m.
This is a first arrangement, not a minimum-building or complete-plant-fit claim.

- [Dimensioned two-level plan](../outputs/site-45-bends/turbine-equipment-plan.png)
- [Editable SVG plan](../outputs/site-45-bends/turbine-equipment-plan.svg)
- [Draft Blender scene](../outputs/site-45-bends/fast-salt-site.blend)
- [Aligned site view](../outputs/site-45-bends/site-alignment-draft.png)
- [Layout definition](../models/turbine_layout.py) and [checked handoff JSON](../models/turbine-layout.json)
- [Equipment worksheet](../../fastSalt/calculations/power-cycle/Motor-BFP%20equipment%20sizing%20-%20Hurmet.md)

D-032 aligns the reactor and turbine-building centres on world Y=0 by translating
the turbine hall, annex, machinery and aprons 10 m north. The reactor installation
stays at its established origin. D-033 replaces the sharp external dogleg with
**two 45° bends per pipe**, joining parallel westward runs. A separate shallow
**20° turn** is added to each reactor-side connection just outside the reactor,
retaining the original upstream routing and wall penetration. This adaptation is
made only in the site copy; the source installation file is preserved.

The two offset corners lie at approximately (−27.2, −8.89252) and
(−31.89768, −4.19484) m. Both pipes enter the turbine's east wall at X=−36 m
perpendicularly and terminate at X=−39 m. Rack frames move to X=−33.5 and −35 m.
The build checks the 45° deflections, joined tangents and endpoints, reactor-ring
clearance, wall bay and retained internal routing. The steam pipe overlays the
feedwater pipe in plan because the two share an XY route at different elevations.

The wall-to-reactor-ring separation remains 11.798 m. Pipe wall/insulation sizes,
elevations, building dimensions, and the HP → reheaters → IP → LP sequence remain
unchanged. Bends, nozzle loads, flexibility and supports remain provisional. The
4.70 m feedwater underside clearance remains flagged. The saved model opens on
the alignment camera; other cameras remain available. The earlier site and piping
snapshots preserve the previous 10 m offset arrangement.

The current arrangement retains D-030’s grouping around the east/right steam entry:

- Four reheaters are grouped on the right, with the HP/IP turbine above that side.
- Three condensers and their LP casings move left. The condensate pumps sit along the west wall, south of the condensers and
  before the LP heaters. The LP heater bank shifts 2.25 m east to reserve a
  1.2 m pump-side access strip. The 3 m cross aisle and heater pulls stay clear.
- LP heaters occupy the front left; HP heaters the front right; all three BFPs sit
  between the banks. DA storage is above this central pump area.
- The HP/IP train reverses: its turbine is east of the 550 MVA generator. Both
  generators align at local X=30–42 m, alongside one another with a 3 m gap.
  This reserves a common electrical connection area; bus ducts are not routed.
- The BFP electrical annex moves to the central south frontage (local X=20–40 m).
  Separate southwest and southeast aprons leave the heater withdrawals clear.

Condenser outlet/hotwell locations are provisional; suction routing is a draft;
the west-wall location does not establish suction head or quantify piping savings.

The east/right arrow on the plan indicates the steam-entry side, not a routed
internal steam line. Equipment sizes, elevations and cycle calculations are unchanged. Local coordinates start at the southwest hall corner.

D-031 turns each BFP/motor envelope from 10 × 4 m to 4 × 10 m and places
the three side by side with 2 m gaps. A 2 m front-access strip meets the retained
3 m cross aisle. The full 4 × 10 m laydown reservation remains next to the pumps.
HP heaters and reheaters move 6 m west in local coordinates. The east wall and
steam/feedwater terminals stayed fixed in world coordinates in D-031; the west wall moved
6 m east. The main-hall footprint falls from 2,640 to 2,400 m² (9.1%); the annex,
height and common site pad stay unchanged. This remains a candidate layout,
not a minimum-building claim. Turbine envelopes limit further narrowing without
further rearrangement.

The layout contains 30 equipment reservation boxes: three condensers, four
reheaters, seven heaters, three BFP/motor trains, three condensate pumps, separate HP/IP sections within the original train reservation
and three LP casing envelopes, two generators, two DA-storage envelopes and
the electrical annex. Turbines sit at +12 m; DA-storage shell bottoms +13.5 m,
with a minimum water-level allowance +14 m. No load-carrying structure is implied
by the floating boxes. The upper equipment can be hidden using `turbine_upper`
object properties; the site plan view does so automatically.

`models/turbine_layout.py` checks selected 3D box/service overlaps and writes
JSON plus SVG. `scripts/turbine_equipment.py` adds these same boxes to the site
scene. Inputs are from the motor-cycle equipment revision. Reheaters are now
16 × 3.25 × 3.25 m; condensers remain 16 × 7 × 9 m. BFP/motor boxes are 10 × 4 ×
4 m analyst allowances. Heater/turbine/generator outlines are provisional.
Two storage boxes are 25 × 4.5 × 4.5 m, including a 3 m heads allowance beyond
the 22 m straight shell. The 550/350 MVA tags identify capacity reservations.

The new rectangle contains these boxes and 18 selected service reservations,
whereas this arrangement does not fit the former 45 × 24 × 20 m shell. Tube
withdrawal volumes cross the wall and require removable panels; the closed wall
meshes do not represent a designed panel-removal mechanism. Pipe corridors,
columns, deck/slab openings, stairs/egress, cooling-water plant, other auxiliary
systems, transport, motor/rotor lifting and crane reach remain to resolve.
The electrical annex reserves space, not a qualified transformer-room design.

Reproduce (from the models repository):

```sh
python models/turbine_layout.py outputs/site-45-bends
# This regenerates the SVG and layout JSON; PNG is a raster view of that SVG.
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_site.py -- \
  --output outputs/site-45-bends --view alignment --with-piping
```

Copy a reviewed generated JSON into `models/turbine-layout.json` before the Blender
build. The Blender scene imports that versioned handoff, retaining its hash.
Earlier `outputs/site-study` files are preserved as the empty-envelope draft;
`outputs/site-study-motor` preserves the first equipment arrangement and
`outputs/site-study-motor-v2` preserves the arrangement before moving the condensate pumps;
`outputs/site-study-motor-v3` retains the 66 m hall with west-wall condensate pumps. The revised
30 boxes and 18 service volumes pass the overlap, containment and vertical
clearance screens, plus arrangement-intent and external apron-coverage checks.

## Earlier empty-envelope study (preserved description)


11 October 2026. The owner requested turbine and fuel-preparation buildings and
approved provisional sizes and locations. This separate scene copies the current
installation; it does not replace the detailed reactor or installation models.

| Envelope | Footprint | Height above pad | Centre X, Y |
| --- | --- | --- | --- |
| Turbine building | 45 × 24 m | 20 m | −58.5, −10 m |
| Fuel preparation | 30 × 24 m | 14 m | 51, 12 m |

These are space reservations, not sizes derived from machinery, processing
throughput, shielding or construction design. Wall and roof thicknesses are
illustrative. The turbine building lies west/southwest of the reactor, beside the
existing secondary-system outlets. Fuel preparation lies east/northeast across a
service yard from the existing equipment door. Each building wall is at least
11.798 m from the 24.202 m outer hot-air-ring envelope. The common presentation pad
is at the existing equipment sub-floor, Z = −9.1 m; actual site grade, excavation,
drainage and access slopes remain to establish.

Steam and feedwater run straight and coaxially from the source installation
terminals through an open turbine pipe bay, retaining the source report's bore,
wall and insulation. Jacket diameters are 1.815 m for steam and 1.240 m for
feedwater. Both stop inside the building as unconnected interface terminals.
Illustrative pipe-rack frames show support locations only. Turbine machinery,
condenser, feedwater equipment, heat rejection and pipe expansion provisions are
not yet modeled. Fuel preparation is an empty envelope with a receiving opening;
no fuel-processing equipment or material-transfer system is inferred.

## Build and view

Parameters: `models/wistr_site.py`. Builder: `scripts/build_site.py`.
First build the current insulated installation using `scripts/build_wistr.py` with
`--output outputs/installation-insulated`. Then, from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_site.py
```

The builder opens a copy of the source installation and replaces its presentation
stage, lights and cameras. It preserves model objects, Boolean cutters and
section controls. Source and baseline files are not overwritten. Outputs:

- [Blender site model](../outputs/site-study/fast-salt-site.blend)
- [Overview](../outputs/site-study/site-overview-draft.png)
- [Plan with new roofs hidden](../outputs/site-study/site-plan-draft.png)
- [Dimensions, source hashes and checks](../outputs/site-study/site-report.json)

The overview shows closed new building envelopes alongside the existing reactor
cutaway. The plan hides the new roofs to show the reserved interior space. Change
visibility of objects carrying the `site_roof` property to inspect either state.
The saved Blender file opens on the overview camera.

## Verification scope

The builder checks building-to-ring separation, the existing doorway approach,
stack/intake clearance to the new footprints, coaxial pipe terminal alignment,
pipe dimensions, jacket separation, floor clearance and clearance through the
turbine wall opening. It records SHA-256 hashes of its installation and report
inputs. These selected envelope checks do not establish vehicle swept paths,
full plant interference clearance, crane access, structural adequacy or process
performance. Review the building footprints before developing their internals.
