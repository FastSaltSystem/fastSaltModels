# Fast Salt System installation

[Repository overview](../README.md)

Current working model: [42 m insulated-piping Blender draft](../outputs/installation-insulated/wistr-installation.blend).
The isolated reactor is imported at full scale from the current working model,
with six insulation covers and side air plenums. The preserved 2026-10-08
handling-and-plug baseline remains unchanged. Equipment and supports remain conceptual.

## Build and view

Run from the `fastSaltModels` repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_wistr.py -- \
  --draft --output outputs/installation-insulated --views equipment plan cutaway
```

Draft mode saves the editable scene, geometry report and smaller preview images.
`--build-only` saves the model/report without rendering. Default output remains
`outputs/wistr/`; use a named output folder to retain previous review versions.

- [Equipment draft](../outputs/installation-insulated/wistr-equipment-draft.png): shell, crane and plenum roofs hidden; both hollow concrete rings shown.
- [Plan draft](../outputs/installation-insulated/wistr-plan-draft.png): plan with the upper plenum roof hidden; the lower ring lies directly beneath it.
- [Building draft](../outputs/installation-insulated/wistr-cutaway-draft.png): retained rear shell, dome, crane, stack, and sectioned upper plenum.
- [Geometry report](../outputs/installation-insulated/wistr-model-report.json): parameters, equipment frames, pipe routes, counts and checks.

`models/wistr_installation.py` owns layout parameters. `scripts/build_wistr.py`
builds the installation; `installation_reactor.py` handles verified reactor import
and coolant connections; `installation_services.py` handles steel frames,
absorber envelopes, secondary headers and component checks; `installation_air.py`
defines the two air networks and checks their connection topology. Distances are metres,
Z is up. Z=0 retains the old intermediate-floor datum for comparison.

## Insulated process piping — 11 October 2026

This draft supersedes the equipment positions and uninsulated pipe sizes in the
10 October descriptions below. It applies the project hub's four Hurmet piping
and insulation worksheets as **conditional visual dimensions**. Their pressure,
material, thermal and environmental assumptions remain provisional.

| Service | Bore | Nominal metal wall | Radial insulation | Bare OD | Insulated OD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Hot salt | 1.425 m | 25 mm | 400 mm | 1.475 m | 2.275 m |
| Return salt | 1.425 m | 25 mm | 350 mm | 1.475 m | 2.175 m |
| Steam branch | 425 mm | 115 mm | 350 mm | 655 mm | 1.355 m |
| Steam header | 725 mm | 195 mm | 350 mm | 1.115 m | 1.815 m |
| Feedwater branch | 375 mm | 75 mm | 175 mm | 525 mm | 875 mm |
| Feedwater header | 650 mm | 120 mm | 175 mm | 890 mm | 1.240 m |

All 19 external process routes have separate hollow **Pressure pipe metal** and
**Pipe insulation** meshes. Hide the *Pipe insulation* collection in Blender's
Outliner to inspect the metal pipes. The hidden *Pipe route guides* collection
stores centreline geometry for checks; it should stay hidden. End faces expose
the layer thicknesses at open connections. Service colors remain on the insulation.
Tee intersections and collectors are visual connection envelopes, not fabricated
pressure-boundary designs. Collector insulation uses the corresponding branch
allowance; collector pressure walls have not been sized.

### Layout changes

- Equipment shell diameter grows from **36 to 42 m**; the 3 m exterior rings
  give **48 m overall ring diameter**. This is a provisional fit adjustment,
  not a structurally sized building. The crane and dome span grow with the shell.
- Generator centres move to **radius 14 m**, fuel-storage pairs to **12.8 m**,
  secondary headers to **18.5 m**, coolant storage to **(14, −6.5) m**, and
  sector storage to **(17.3, 0) m**. All generator casings and storage remain floor-mounted.
- Cold salt collector/suction runs rise to **1.9 m above the floor** (Z=−7.2 m).
  Pump side-discharge centres are Z=−4.59 m, bottom-suction ports Z=−5.49 m.
  Open pump frames are 3.61 m high, accommodating the insulated bottom-entry bend.
  Motor bottoms rise to Z=−3.2 m; pump/motor duty remains unchanged.
- Water collectors/header rise to **3.5 m above the floor** (Z=−5.6 m).
  The reactor fresh-air riser moves inside the header at radius **16.5 m**, then
  passes beneath it at Z=−7.6 m to enter the fresh ring. This removes the
  interference introduced by the larger feedwater header. The feedwater wall
  crossing clears the fresh-ring roof by **1.7 m** beneath its insulation.
- The steam header's insulation clears the inside wall by **0.9425 m**. The
  low salt suction insulation clears the floor by **0.8125 m**.
- The stack moves to radius **27 m**, outdoor intake to **28 m**. The existing
  4.5 × 6.5 m doorway, 5.5 m fresh-ring gap and level lane are retained and
  repositioned for the larger shell. The lane extends from radius 16.5 to 27 m.
- Generators remain 17 m tall. Building height remains **32.505 m**; the valve-box
  tops still have **5 m clearance to the hoist body underside**. No circumferential
  railing or intermediate floor is added.

### Reactor and checks

The current working reactor is imported at full scale and its source hash is
verified. In the **installation copy only**, six coolant nozzle sleeves and their
flanges/opening tools are adjusted to 1.425 m bore / 25 mm wall. Source baselines
and the isolated reactor file are unchanged. External insulation starts at the
reactor connection terminals, outside the concrete well; in-well cooling surfaces
are unchanged.

The report includes worksheet paths/hashes, exact dimensions, minimum bend radii,
floor clearance, header/wall clearance and interference results. Circular elbow
centreline radii exceed the insulation outside radius. The interference screen
compares process-route capsules with other process/air routes and selected oriented
equipment boxes. Intended header junctions and own-equipment attachments are
excluded; three conservative spherical pump-end overlaps are recorded separately
from their disjoint exterior mouth geometry (0.3125 m clearance).

Existing checks also cover port tangents and diameters, pumps, storage, floor
contacts, doorway and ring gap, air-network connections and crane height. These
checks are selective. Full maintenance/crane swept paths, all supports and fitting
bodies, seismic displacement and fabrication details remain to be developed.

The generator casing collectors retain their previous bare envelope diameters:
2.1 m salt, 1.2 m steam, 0.75 m feedwater. Their connection lofts now meet the
correct insulated branch sizes. Pressure-wall sizing for these D-shaped collectors
is not inferred from the circular-pipe worksheets.

## Single-floor layout — 10 October 2026

The only equipment floor is the sub-floor at **Z = −9.1 m**. The intermediate
deck, circumferential walkway and former deck columns are removed.

| Component/interface | Current placement |
| --- | --- |
| Reactor concrete well bottom | Z = −9.1 m, directly on sub-floor |
| Reactor vessel top / seated cap tops | Z = −2.02 / −1.75 m |
| Generator casing bottoms | Z = −9.1 m, directly on the floor; raised frames removed |
| Generator casings | Three 4 × 4 × 17 m envelopes; centres at radius 12 m |
| Generator orientation | Each turned −90° from the preceding layout: salt inward, water and steam outward |
| Hot salt / steam manifolds | Z = +6.4 m |
| Cold salt / water manifolds | Z = −7.9 m |
| Pump discharge centres | Z = −5.8 m, discharging toward the reactor |
| Pump bottom suction | Z = −6.7 m, vertically upward into casing |
| Under-pump suction pipe run | Z = −7.9 m; 0.5 m clearance below the 1.4 m diameter pipe to floor |
| Pump support frames | From floor to casing bottom, 2.4 m high; open centre for suction |
| Absorber platform tops | Z = −2.02 m, even with vessel-top datum |
| Fuel storage tanks | All six rest on floor, tank tops Z = −3.7 m |
| Coolant storage tank | Bottom Z = −9.1 m, tank height 8 m |
| Sector storage | On floor; moved to (14.3, 0) m in the open end of the common secondary headers |

The latest revision lowers the generators 2.1 m onto the floor, superseding
the previous outlet/manifold elevation match. Coolant returns from each generator's lower manifold to **pump bottom suction**, then
leaves its side discharge toward the reactor. The suction line now has two bends
and a level run from the cold manifold, followed by an upward turn into the pump.
The building is widened from 28.4 to **36 m**, as approved by the owner.
Generator centres move from radius 10 to 12 m; fuel-tank pairs move from radius
8.1 to 10.8 m. Pumps move outward 2 m, coolant storage moves to (12, −5.5) m,
and the water/steam headers move to radius 15 m. The reactor stays at full scale
and in its existing position. These moves open the connection space around it. Pump frame member sizes and precise routes are
provisional geometry. The absorber instruction is interpreted as **support
platform** elevation matching the vessel top, rather than tank-top elevation.

Each pump retains the provisional 2 MW motor and 2.8 m diameter × 1.8 m casing
from the [Hurmet pump allowance](../../fastSalt/calculations/steam-generator/Coolant%20pump%20estimate%20-%20Hurmet.md).
The previous hydraulic power estimate is unchanged; this layout does not
recalculate piping losses or select supports, bearings, motors or salt-service
materials.

Steam and water manifolds feed separate shared C-shaped headers at their
respective elevations. Both terminate outside the building at azimuth 200°,
clear of the stacks. Visible diameters of 0.8 m steam and 0.5 m water remain
layout assumptions. Salt pipe visible diameter is 1.4 m; wall/insulation and
clear-bore reconciliation remain separate work.

Six external absorber supply/control envelopes remain in three pairs. Capacities,
internal arrangements and small-bore service routing are not yet defined.

## Generator collectors and top exhaust — 10 October 2026

Each generator now has four **half-pipe collectors** attached directly to its
casing: hot/cold salt on the inward face, steam/feedwater on the outward face.
The flat side of each D-shaped collector sits on the casing. Collector diameters
are increased 50% to 2.1 m for hot/cold salt, 1.2 m for steam, and 0.75 m for
feedwater. External pipe diameters remain 1.4, 0.8, and 0.5 m respectively.
A 1.2 m transition region blends each collector into its pipe, ending with a
straight round collar. Steam/feedwater transitions curve outward to match
the radial pipes; salt transitions remain axial. The previous three
right-angle branch stubs per manifold are removed. Collector envelopes retain
the existing service heights and pipe endpoints; internal distribution, section
areas, wall thickness and pressure losses are not calculated by this revision.

A provisional **1.2 × 1.2 × 0.6 m box** on each generator roof represents a
butterfly valve. The hot-air duct starts vertically from its top, then turns
outward toward the hot ring. No valve mechanism or actuator is modeled.
A [generator detail](../outputs/installation-concrete-rings/wistr-generator-detail-draft.png)
shows the new components; regenerate it with Blender and
`scripts/render_generator_detail.py` after building the installation. The
boxes raise the generator equipment tops by 0.6 m; the crane and roof also rise
0.6 m to preserve the existing 5 m clearance to the hoist body.

## Exterior concrete plenums — 10 October 2026

The owner requested air manifolds integrated into the building exterior. Two
full hollow concrete rings now join the outside of the 36 m shell. Each occupies
a provisional **3 m radial width × 3 m height**, with 0.25 m skins and a clear
2.5 × 2.5 m passage. These are visual section allowances, not structural sizing.
The rings extend the exterior diameter to 42 m; the equipment shell stays 36 m.
The slab and foundation envelopes extend beneath the lower ring.

- The **fresh-air ring** rests at floor elevation Z=−9.1 m and reaches Z=−6.1 m.
  An outdoor intake connects at azimuth 270°. Small equipment feeds enter
  through its inner wall, turn down inside the building, and pass beneath the
  water header. The reactor keeps its present cold-hood inlet and removable
  overhead connection at Z=3.5 m; its wall-side riser is now inside the building
  and crosses the wall horizontally at the fresh-ring centreline, Z=−7.6 m.
- The **hot-air ring** is lowered to Z=8.5–11.5 m, entirely below the crane
  runway underside at Z=12.305 m: 0.805 m visual clearance. Equipment exhaust
  risers run inside the wall and penetrate it only at the ring centreline,
  Z=10 m, directly through the ring's inner web. The reactor crossover also
  enters horizontally at Z=10 m. No equipment connections pass through the
  ring floors or roofs.
- The **single 3.6 m exhaust stack** moves to radius 24 m so its base clears both
  full rings. A 2.4 m connection joins the upper ring to the stack.
- The **feedwater wall crossing** rises inside at radius 16 m to centreline
  Z=−5.35 m. The pipe underside clears the fresh-ring roof by 0.5 m before it
  passes through the wall and continues outside. The low common feedwater
  header and generator inlets retain their existing elevations.
- Both networks retain all ten equipment connections. Existing reactor hood
  stubs are unchanged; their crossover spools remain removable for maintenance.
- Equipment and plan views hide the plenum roofs to reveal the hollow passages.
  The building cutaway removes the front half of the upper ring with the shell.
  Colored internal floor finishes are diagram keys: copper for hot air, cyan
  for fresh air. The full roof and front pieces are present in the Blender file.

Equipment air ports remain conceptual cooling-space interfaces. Concrete joints,
reinforcement, liners, insulation, supports and full maintenance paths have not
been designed. The concrete bands might contribute to building stiffness, but
openings, load paths and thermal effects must be assessed before claiming a
strength benefit. No airflow or heat-removal calculation is implied.

### Alternative under-floor fresh-air plenum

This remains an option for comparison, not the implemented draft. It could
replace visible low supply branches with equipment feeds from below. It would
also require accessible plenum spaces, drainage and spill separation, equipment
foundation coordination, and revised reactor inlet routing. A bottom-fed
reactor arrangement must reconsider cooling of the outer hood that currently
surrounds the insulated hot hood. The present flow arrangement is retained
while the exterior-ring concept is reviewed.

## Building and reactor provenance

Building diameter is 36 m. The crane and roof now follow the requested **5 m
clearance to the underside of the hoist body**, measured from the valve-box tops of
the floor-mounted generators. Top covers are Z=8.03 m, valve tops Z=8.63 m,
hoist body underside Z=13.63 m and crane runway Z=12.605 m. The wall springline
is Z=15.305 m and dome top Z=22.805 m: overall envelope 32.505 m including the
lower level. This lowers the crane and roof 8.695 m from the preceding raised-generator draft. The hook
is shown retracted; its clearance is not the 5 m reference.

The single stack base bottom is at floor elevation Z=−9.1 m. Its 1 m base
supports the retained 35 m tube; the tube top is Z=26.9 m (rim adds 0.05 m).

The saved Blender viewport has overlays hidden. To toggle them, hover over the
3D view and press **Shift–Option–Z** on Mac (Shift–Alt–Z elsewhere), or click
Show Overlays, the overlapping-circles icon. To hide only parent/child guides,
open that icon's dropdown and uncheck **Relationship Lines**.

The reactor is imported without scaling, with origin Z=−8.32 m and plan rotation
45°. Scene and report hashes are verified against the source manifest. Reactor
property drivers are redirected to the installation scene; the front section
is visible in equipment/cutaway views. Saved source drawings and approved
baselines are unchanged. Imported maintenance controls remain available, but
full building-wide lifting reach and extraction clearances are not validated.

Each generator fresh-air inlet is on its local −X face, perpendicular to the
salt and secondary collector faces and opposite the pump side. Its centre is
0.45 m above the floor. A normal approach clears the casing before turning
toward the low supply ring.

## Shared absorber platforms and equipment entrance — 10 October 2026

Each absorber-module pair now shares a **1.8 × 4.2 m steel deck** on one braced
frame. The three decks stay at vessel-top Z=−2.02 m. Four larger columns per
pair replace the individual module frames; deck and member dimensions are
provisional visual choices.

A **4.5 m clear width × 6.5 m clear height** equipment door is placed at plan
angle 18°, beside the sector-storage bins. It is shown open, with an overhead
door housing. The wall and intersecting pilaster have a real opening. The
fresh-air plenum has a **5.5 m minimum gap** aligned with the door, with sealed
end walls; the remaining C-shaped passage still connects every fresh-air
branch to the outdoor intake. The hot ring is unchanged.

The [entrance close-up](../outputs/installation-concrete-rings/wistr-access-detail-draft.png)
shows the opening and interrupted plenum; regenerate it with Blender and
`scripts/render_access_detail.py` after the installation build.

A level apron and marked lane extend from radius 13.5 m to 24 m. This location
clears the sector-storage envelope and the coolant tank, which remains at
(12, −5.5) m. Checks cover the wall aperture, equipment bounds, service routes,
plenum gap and level crossing. Full vehicle turning/extraction paths, external
site grading, door construction and structural capacity are not established.

## Checks and scope

The build checks equipment counts, finite metric transforms, absence of the
intermediate floor/walkway/columns, well bearing elevation, tank bottoms and
support feet at floor level, generator orientation, 50% collector enlargement, pipe-end diameters/tangents,
perpendicular fresh-air inlet locations and manifold connections,
pump inlet/outlet continuity and vertical suction approach, alignment of cold manifolds
with level, two-bend suction runs, suction-pipe floor clearance, absorber platform
elevation, common-header branches/outlets, and pump footprint clearance from
storage and generator envelopes. Actual mesh bounds verify generator floor
contact, stack base elevation and the 5 m hoist-body clearance. It also checks
source hashes and reactor drivers. Air checks verify ten connections on each
network, imported hood-stub alignment, the reactor hot crossover's vertical space, exterior plenum attachment, hollow section, sealed access gap and stack clearance, and small feeds below the water header.

These are selective geometry checks, not complete plant interference, structural,
pressure-loss or pressure-boundary validation. Steel frames are visual concepts.

## Earlier layout revisions

The [round-duct air layout](../outputs/installation-air-layout/wistr-installation.blend)
retains the previous high internal duct ring and low exterior C-header for comparison.


The [28.4 m single-floor draft](../outputs/installation-single-floor/wistr-installation.blend)
preserves the preceding floor-mounted-generator arrangement and three stacks.
The wider single-stack air layout above supersedes it for current review.


The preceding [installation-layout draft](../outputs/installation-layout/wistr-installation.blend)
retains the intermediate floor and the earlier right/left generator arrangement.
The still earlier `outputs/workshop-installation/` images predate the 17 m
casings and pump/module additions. They remain available for comparison and
should not be substituted for current draft views in the workshop deck.


## Reactor insulation and side-air integration — 11 October 2026

The current installation imports `outputs/reactor-study/` with a generated hash
manifest. The preserved handling baseline is retained in `baselines/`, but the
working scene now contains six fitted insulation covers and side supply/return
plenums in place of the enclosing hood. Side ducts leave at installed azimuths
135° hot and 255° cold, then rise outside the cassette footprint and connect to
the building's existing hot and fresh-air rings. Plenum airflow and complete
crane clearances remain provisional.

Absorber module pairs move to radius 9.5 m, at 0°, 105° and 225°; their shared
platform centres are radius 9.8 m. The platforms retain vessel-top elevation.
This clears the side plenums/riser region; absorber service tubing is still to
route. The building diameter and process-pipe specifications are unchanged.

Run the reactor build and its fitted-cover check first, then:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_wistr.py -- --draft \
  --output outputs/installation-insulated --views cutaway plan
```

[Working installation](../outputs/installation-insulated/wistr-installation.blend),
[cutaway](../outputs/installation-insulated/wistr-cutaway-draft.png),
[plan](../outputs/installation-insulated/wistr-plan-draft.png).

The supplementary `scripts/check_installation_side_air.py` check confirms the new reactor branches clear the relocated absorber decks/enclosures by at least 1.65 m, and finds no intersecting side-plenum surfaces with those envelopes. This is a selected clearance check, not full crane or plant interference qualification.


### Reactor fresh-air floor route — 11 October 2026

At the owner's request, the reactor fresh-air branch now runs directly from the
lower exterior ring along the floor, rising only at the reactor side manifold.
It retains the 255° radial alignment and 2 m diameter. The horizontal centreline
is 1.5 m above the floor, leaving 0.5 m beneath the duct envelope; the former
high crossover and outer downleg are removed. Duct supports remain to design.

The builder checks floor clearance, the absence of an intermediate high point,
and the route against oriented equipment envelopes (including support members)
and other air branches. Existing process-route checks also screen its clearance
to insulated process piping. This is geometry verification, not airflow sizing.

The revised-route check found 0.500 m floor clearance and a minimum 0.266 m clearance to the fourth fuel-storage tank envelope. No clashes were found in the selected equipment, air-route and process-route checks.
