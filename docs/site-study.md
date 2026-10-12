# Fast Salt System site draft

Cleanup note — 12 October 2026: superseded generated drafts have been removed. Current site plans and the saved scene are together in `outputs/site-45-bends/`. The current site now imports the maintenance/utility installation and adds the D-043 process buildings. Historical output links below may require rebuilding.

The accepted site and service checkpoint is preserved in [the named baseline](../baselines/fast-salt-site-2026-10-12/), including the model, selected views, reports and file hashes. Routine outputs remain ignored.

## Generator air inlets and complete column layout — D-050

The composed site now includes all **18 wall-column positions at 20° intervals**, including the previously omitted front half. The wall remains a cutaway; columns have their own **Building columns** collection and remain visible in equipment views. The existing equipment doorway cut remains in the 20° column. This is an architectural envelope, not structural sizing.

Three short outdoor fresh-air intakes replace the single south intake. Their provisional locations are **190°, 70° and 310°**, between columns and near the three generators; their louver faces are at radius 23.5 m. They feed the common internal floor duct. Each generator has a butterfly-valve box centered on its local −X side, horizontally centered and **1.35 m above the floor**, near the bottom of the generator. The owner requested lowering these from the initial 8.5 m center height. Valve-box bottoms clear the floor by approximately **0.37 m**. Short, level branches connect the floor header directly to the boxes, replacing the tall risers. The west route clears the stair supports; the north-east branch and coolant supply drop are coordinated with the fuel/gas routes. The coolant drop is now at X = 3.8 m, Y = 16.5 m.

The requested **75% area ratio applies to clear duct bores**: the existing 1.800 m exhaust OD with a provisional 3 mm wall has a 1.794 m bore. Inlet bore = √0.75 × 1.794 = **1.55365 m**, with **1.55965 m OD** using the same wall allowance. The three outdoor intake envelopes use this inlet diameter too. Exhaust insulation is excluded from the area calculation. This ratio is a visual design instruction, not a heat-removal or airflow-capacity calculation.

Both air headers have sealed recesses around columns. The cold duct retains 6.25 m² nominal clear section between columns, but its inner face stays clear of the coolant-storage jacket at the 340° column: the resulting minimum clear section is **4.725 m²**, recorded in `site-report.json`. The hot header's outer edge and insulation layers also recess around the columns. Local losses, thermal performance and structural/support design remain open.

The builder checks branch counts, centered ports, the bore-area ratio, columns, doorway clearance and selected air/pipe/equipment/stair envelopes. The builder also checks inlet bend radii against the duct radius and valve-box clearance above the floor. The lowered-inlet screen passes all 15 selected nearby comparisons, with approximately 95 mm minimum pipe-envelope clearance and 1.0 m bend radii. Current results are recorded in `site-report.json`. The source installation and named baselines remain retained inputs.

- [Current Blender site](../outputs/site-45-bends/fast-salt-site.blend).
- [Fresh-air plan](../outputs/site-45-bends/site-fresh-air-draft.png) and [generator inlet detail](../outputs/site-45-bends/site-generator-air-detail.png).
- Rebuild with `scripts/build_site.py`; refresh the isolated views with `scripts/render_fresh_air.py` and `scripts/render_generator_air.py` in Blender.

## Internal fresh-air duct — D-049

Historical D-049 arrangement; D-050 above supersedes the single intake and generator ports. The composed site replaces the **exterior concrete fresh-air ring** with a floor-level steel duct inside the 42 m reactor building. The outdoor louver remains at the south side and connects through the wall; all ten equipment branches now enter the inner side of the internal duct. Their equipment ports are unchanged, and the former wall-side risers and building-wall holes are removed.

The nominal clear section is **2.45 × 2.551 m**, retaining the preceding **6.25 m² nominal area**. A provisional 6 mm steel skin and 60 mm bearing-strip height put the duct top 2.623 m above floor, below the existing feedwater header. Its outer radius is 20.30 m between columns, 50 mm inside the nominal inner wall. The entire closed section offsets inward around the retained wall columns; both its inner and outer walls follow those recesses. Local effective flow area, pressure loss, supports and capacity remain to analyze. Cold air has no added thermal insulation in this draft.

The C-shaped duct retains a **5.5 m level gap** aligned with the existing equipment doorway. Both duct ends are sealed. The reactor retains its direct low fresh-air run; the generator and fuel-tank branches are shortened to the new inside connections. Existing hot-air routes, fuel bundles, gas services and process equipment retain their positions. The coolant-storage supply drop shifts 0.5 m inward to clear a column recess.

Selected checks cover all ten branch endpoints, column and wall clearance, the clear doorway lane, and the new air-volume envelope against equipment and process/service piping. The slab/apron and outdoor intake remain. This updates the current composed site; the source installation and named historical baselines are retained as build inputs.

- [Current Blender site](../outputs/site-45-bends/fast-salt-site.blend), collection **Internal fresh-air duct**.
- [Fresh-air routing plan](../outputs/site-45-bends/site-fresh-air-draft.png).
- [Builder/checks](../src/textual_graphics/site_fresh_air.py); refresh the inspection with `scripts/render_fresh_air.py` using Blender.

## Common heated fuel bundles — D-048

The fuel supply and return now stay together inside **one continuous clad insulation jacket** from the fuel-refining building, through the shared service duct, to the distributor. Six more paired jackets connect the distributor to the six maintenance fuel tanks. This replaces the separate colored outer envelopes in D-045/D-046. Gold and rose identify the individual tubes inside the jacket; the outside is silver cladding with retaining bands.

Each bundle contains two modeled **50 mm OD tubes at 80 mm centre spacing**, with electrical resistance tracing on both. The inherited 50 mm minimum insulation allowance and new 1 mm cladding allowance give a **236 mm overall bundle diameter**. These remain provisional visual allowances; heater power and thermal performance have not been calculated. The common jacket contains a cavity for both tubes and their tracing.

The long fuel runs are now centred **0.18 m above floor** to clear the existing coolant crossings without moving the coolant run from 0.40 m. The refiner end is a paired interface at its supply-station envelope; the return remains a reserved connection, with internal refining circuitry unspecified. The shared duct still clears the exterior fresh-air ring. The distributor has seven paired interfaces: one building connection and six tank connections.

The selected model checks cover seven common jackets, fourteen continuous heated member tubes, tube spacing, minimum insulation envelope, duct fit, tank assignments, floor clearance and interference with existing gas, air, salt, equipment and supports. These are geometry checks, not a qualified thermal, pressure, support or operating design.

- [Fuel routing plan](../outputs/site-45-bends/site-salt-distribution-draft.png)
- [Bundle cutaway](../outputs/site-45-bends/site-fuel-bundle-detail.png) — inspection sample generated with the same geometry helper; the installed jackets remain closed.
- [Current Blender site](../outputs/site-45-bends/fast-salt-site.blend), collection **Salt storage distribution**.
- Refresh the cutaway with `scripts/render_fuel_bundle_detail.py` using Blender; the existing site and floor-plan renderers show the new jackets.

## Fuel pressure servers and nitrogen relocation — D-047

Three pressure-server envelopes now stand beside the three pairs of maintenance fuel tanks: P1 serves F1/F2, P2 serves F3/F4, and P3 serves F5/F6. Each has a cylindrical buffer tank below a control box, using the existing absorber-module proportions (about 0.81 m tank diameter, 1.26 m cylindrical height and a 1.5 m-high control enclosure). These are visual allowances, not pressure-rated equipment selections.

Each maintenance tank has its own **pair of 25 mm OD gas tubes** from its server, terminating in the tank's upper inner wall below the roof. There are twelve tank tubes in total. Their provisional 25 mm radial insulation gives a 75 mm visible envelope; gas tubes are unheated. Existing roof fuel bundles and the low liquid supply/return lines are retained.

A blue supply-gas line is paired with the purple off-gas line through the shared duct. Each header has three explicit branch tees feeding the three servers. Long supply/return branch centrelines are 0.65/0.85 m above the floor, with risers to the tank headspace connections. The existing 150 mm off-gas trunk envelope is retained; new gas tubing uses 25 mm OD. The former reserved off-gas pickup above the reactor is replaced by this server collection network. The off-gas building contains a small supply-interface enclosure separate from its treatment train; internal controls and valves are not designed.

The nitrogen tank **and vaporizer skid** are now at (−10, 30) m beside the west side of the off-gas building. Its inherited 50 mm gas outlet feeds that building through a new wall sleeve. The old direct reactor gas feed, capped header takeoffs and reactor-wall sleeve are removed from this site copy. The isolated installation and named baselines remain unchanged.

Selected checks confirm three servers, six tank connection pairs, six header tees, duct fit, server/equipment separation and tubing clearance from existing gas, air, salt and process routes. The relocated nitrogen skid clears the neighboring building, cooling-air ring and release-stack foundation envelope. These checks do not establish gas capacity, pressure control, containment, treatment performance, remote operating logic or complete maintenance access.

- [One server and its tank pair](../outputs/site-45-bends/site-fuel-pressure-detail.png)
- [Complete gas-routing plan](../outputs/site-45-bends/site-gas-distribution-draft.png)
- [Current Blender model](../outputs/site-45-bends/fast-salt-site.blend), collections **Fuel pressure servers**, **Fuel pressure gas piping**, and **Nitrogen supply**.
- [Builder/checks](../src/textual_graphics/site_fuel_pressure.py); run `scripts/render_fuel_pressure.py` with Blender to refresh the two inspection images after building the site.

## Low insulated salt distribution — D-046

The shared duct now connects to storage in the composed site scene:

- Gold supply and rose return enter an insulated **fuel valve-box reservation** north of the reactor. Six separate supply/return pairs run from that box to low ports on the inner ends of the six maintenance fuel tanks. Existing sector-to-tank roof bundles stay connected.
- The teal coolant line drops inside the building, follows the east side, and turns upward beneath the coolant tank to a separate bottom nozzle, 0.60 m from the existing reactor-transfer nozzle. The tank's bottom insulation and jacket have a corresponding opening.
- Long fuel runs have their centrelines **0.20 m above floor**; the coolant floor run is **0.40 m above floor**, allowing it to cross above fuel lines. The elevated duct remains above the exterior fresh-air ring. Short local transitions clear the existing feedwater header before descending.
- All new routes use the inherited **50 mm tube / 50 mm radial insulation / 150 mm outside envelope** as visual allowances, with heat tracing recorded. They are not new hydraulic, thermal or pressure calculations. The insulated valve box is a 1.6 × 3.0 × 1.14 m envelope, with no internal valve circuit or operating sequence specified.

The builder checks 15 new routes: two valve-box mains, twelve tank branches and one coolant line. It verifies terminal continuity, two connections per fuel tank, floor clearance and selected interference with existing pipe/air routes, equipment, columns and stairs. The equipment-door approach is kept clear. These are selected geometric screens; complete walking access, guarded crossings, supports and process qualification remain open.

- [Floor-routing preview](../outputs/site-45-bends/site-salt-distribution-draft.png) shows equipment footprints and hides overhead equipment so all routes can be followed.
- [Current Blender site](../outputs/site-45-bends/fast-salt-site.blend) contains the complete equipment and new lines in **Salt storage distribution**.
- Source: [routing and checks](../src/textual_graphics/site_salt_distribution.py), [parameters](../models/wistr_site.py).
- Rebuild with `scripts/build_site.py -- --output outputs/site-45-bends --with-piping --build-only`; refresh normal views with `scripts/render_process_site.py`, then the routing inspection with `scripts/render_salt_distribution.py` (all run using Blender from the repository root).

## Current rectangular reservations and fuel in/out — D-045

The site now uses a 20 × 15 × 8 m empty converter envelope at (11.5, 55) m,
beyond the existing receiving apron; the 15 × 12 × 5 m building beside the
reactor is labelled **Fuel refining / recycling**. Off-gas remains 10 × 11 × 5 m.
These are owner-accepted visual space allowances, easily resized, without an
internal building or processing design. Camera observation is the working
concept; no central post or leaded-glass windows are modeled.

Two distinct fuel lines pass through the existing shared duct: gold supply
(refiner to reactor) and rose return (reactor to refiner), with opposite-direction
arrows. Both use a 150 mm visible insulated envelope; this is a visual allowance,
not a qualified tube, insulation or shielding design. The return runs at X=4.95 m,
Z=−4.75 m through the duct; supply remains X=4.6 m, Z=−5.1 m. Their reactor-side
terminals are at Y=18.5 m. The return ends inside the refiner at (6.6, 28.4, −4.75) m.
D-046 now connects these former reactor-side tie-ins to the valve box and storage; the refiner-side return remains reserved.
Coolant and off-gas keep separate lines. Existing coolant equipment placeholders
remain pending later space allocation. No converter equipment train is added.

The build screens duct containment and the new return against existing annex
routes and selected installation equipment/routes. Full process engineering and
all building/maintenance clashes are outside these checks.

- [Fuel duct close-up](../outputs/site-45-bends/site-fuel-duct-draft.png)
- [Updated process-building view](../outputs/site-45-bends/site-process-draft.png)
- [Updated site model](../outputs/site-45-bends/fast-salt-site.blend)

## Fuel return and horseshoe study — D-044

A reference-only [dimensioned fuel-handling floor plan](fuel-handling-study.md) explores a
28 m horseshoe with central observation room, outer operating gallery and a
separate radioactive fuel-return interface. Its 8 m height and 12 × 12 × 5 m
coolant annex are provisional alternatives. This plan has not yet replaced
the D-043 rectangular buildings in the Blender scene below. Subsequent
[presentation review](../../fastSalt/design/conversion-refining-review.md)
withdraws the EBR-II-derived dimensions as the sizing basis: conversion and
liquid-salt refining/recycling require separate building studies.

## Attached off-gas and salt-preparation buildings — 12 October 2026

D-043 adds adjacent process buildings north of the reactor. They share one enclosed pipe-and-tube duct into the reactor shell above the
existing fresh-air ring. The owner halved both plan dimensions (one-quarter
the original area) and set both buildings to 5 m tall. This keeps the ring, main equipment doorway, canister-cart approach,
outdoor nitrogen supply and turbine pipe connection in place.

| Draft component | Envelope / location |
| --- | --- |
| Off-gas treatment | 10 × 11 × 5 m; centre (−1, 31.5) m; floor area 110 m² |
| Fuel and coolant salt preparation | 15 × 12 × 5 m; centre (11.5, 32) m; floor area 180 m² |
| Separate off-gas release stack | 0.8 m outside diameter, 22 m tall; centre (−7.5, 35.5) m; owner selected a separate stack |
| Shared service duct | 4 m wide, 1 m internal envelope height; floor Z=−5.6 m, 3.5 m above building floors; underside clears fresh-air ring by 0.3 m; top 4.66 m above floor |
| Salt receiving | 6 × 4.2 m north-wall opening and 15 × 8 m level apron |
| Common site pad | 190 × 140 m, centre (−14, 5) m; floor datum remains Z=−9.1 m |

The purple gas line starts at a **reserved collection interface above the
reactor**, passes to an inlet-treatment/filtering envelope, a further-treatment
reservation and a release-monitoring envelope, then to the separate stack.
These are functional reservations, not a selected treatment train or a claim
that filtration alone handles every gas constituent. Actual collection points,
gas inventory, equipment duties, monitoring and release requirements remain open.
The 150 mm gas line and stack dimensions are visual allowances, not flow or
release-dispersion calculations. The cooling-air stack is independent.

Salt preparation shows incoming canisters, separate fuel and coolant purification
reservations, melting/holding vessels and supply-pump envelopes. Gold and teal
liquid-supply lines share the duct with the separate off-gas line and enter the reactor
building. Both use a provisional 50 mm OD tube / 50 mm radial insulation envelope
(150 mm overall), with heat tracing represented by the insulated jacket.
The capped **reactor-side supply tie-ins** are reserved interfaces: distribution
to the reactor and storage tanks is not yet routed. Equipment arrangement does
not select purification chemistry, operating sequence, temperature, capacity,
material, shielding or pressure design.

Unsized equipment placeholders are compacted in plan to fit the reduced envelopes;
heights and service-line diameters are retained. They remain space reservations.

The site imports the current maintenance/utility reactor installation, including
the laydown platform and mobile canister. The isolated installation scene and
committed baselines are unchanged. Existing turbine equipment and its 59 main
pipe routes remain in the composed model.

- [Attached-building close-up](../outputs/site-45-bends/site-process-draft.png)
- [Process-building plan](../outputs/site-45-bends/site-process-plan-draft.png)
- [Whole-site plan](../outputs/site-45-bends/site-plan-draft.png)
- [Site Blender model](../outputs/site-45-bends/fast-salt-site.blend)
- [Site report](../outputs/site-45-bends/site-report.json)

Selected checks cover building spacing, the unchanged door approach, service-link
height, line fit through the shared duct, and new routes versus existing process/air/
utility routes and selected equipment boxes. No screened clashes remain. Full
vehicle/crane access, pipe supports, building structure, process hazards and
performance are outside this geometry screen.

Build with `scripts/build_site.py -- --output outputs/site-45-bends --with-piping`.
To refresh the focused images from the saved scene, run
`scripts/render_process_site.py` through Blender in background mode.
Parameters are in `models/wistr_site.py`; process geometry and selected checks
are in `src/textual_graphics/site_process_buildings.py`.

## Current motor-BFP equipment draft — revised arrangement

The [main internal piping draft](turbine-piping.md) now adds 59 route sections
and a color-coded plan to this layout. It retains the 60 m hall and flags the
east feedwater aisle height, crossover lengths and overhead maintenance access.

D-031 reduces the D-029/D-030 hall from 66 × 40 × 28 m to **60 × 40 × 28 m**.
The current D-032 alignment places its centre at (−66, 0) m. Its east wall remains at X=−36 m. A **20 × 10 × 7 m BFP electrical
annex** sits to the south; north/south extraction aprons reserve 7/12 m beyond
selected wall segments. D-043 above supersedes the earlier fuel-preparation location and 190 × 110 m pad; turbine dimensions and interfaces are unchanged.
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
