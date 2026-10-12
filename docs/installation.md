# Fast Salt System installation

[Repository overview](../README.md)

Current working model: [under-cover service-bundle draft](../outputs/installation-under-cover-bundles/wistr-installation.blend).
The isolated reactor is imported at full scale from the current working model,
with six insulation covers and side air plenums. The preserved 2026-10-08
handling-and-plug baseline remains unchanged. Equipment and supports remain conceptual.

Accepted checkpoint: [12 October maintenance and utilities baseline](../baselines/wistr-maintenance-2026-10-12/).
The earlier [service-bundle baseline](../baselines/wistr-service-bundles-2026-10-12/) remains preserved.

## Maintenance laydown and mobile sector canister — 12 October 2026

D-042 removes the fixed sector-storage enclosure. A provisional upright canister
on a low-profile cart is parked outside the equipment door, aligned with a
straight approach to a loading position at radius 15.5 m and angle 18°.
The cart is 3.60 × 3.25 m; the illustrative canister has 2.95 m clear diameter,
6.00 m clear height and 3.05 m shell outside diameter. Overall height from the
floor is 6.33 m, leaving only **0.17 m** under the current 6.50 m doorway.
This tight margin is a geometric allowance, not a finalized transport design.
The envelope includes the modeled core's attached service tubes and plug.
Canister containment, shielding, cooling, restraints and cart load capacity
remain unselected; the thin displayed shell is not a shielding specification.

An **8.70 × 6.10 m platform at catwalk elevation Z=−0.60 m** has separate
4.35 × 4.30 m and 3.25 × 3.00 m receiving bays for one insulation cover and one
sector cap. The northern aisle is about 1.5 m wide. A short 1.30 m bridge joins
the catwalk at 15°, retaining its existing stair entrance at 195°. Four columns
stand outside the maintenance-tank footprints. Framing is provisional and
should be developed as demountable sections to retain tank replacement access;
no support is attached to the reactor pressure vessel. Receiving runners must
be matched to the removable items' load-carrying frames before detailing.

The normal scene shows empty receiving bays. The dedicated inspection render
places the actual installation cover and cap meshes in their respective bays
and omits those two installed items for that image only. It does not save that
maintenance state over the normal Blender scene.

- [Current scene](../outputs/installation-under-cover-bundles/wistr-installation.blend)
- [Laydown inspection](../outputs/installation-under-cover-bundles/wistr-maintenance-laydown-draft.png)
- [Plan](../outputs/installation-under-cover-bundles/wistr-plan-draft.png)
- Definition: `MAINTENANCE` in `models/wistr_installation.py`; geometry and selected
  checks: `src/textual_graphics/installation_maintenance.py`.
- Recreate the inspection image with Blender background execution of
  `scripts/render_maintenance_laydown.py` after building the current installation.

The report records component fit, the cart's straight swept envelope, selected
platform-solid/service clearances and the bridge/aisle headroom checks. These
checks do not qualify a loaded crane trajectory, structural capacity or a
complete maintenance sequence. Earlier baselines and the site snapshot remain
unchanged.

## Generator exhausts, coolant transfer and nitrogen supply — 12 October 2026

D-041 centres each steam-generator exhaust on its roof and doubles its nominal
metal outside diameter from **0.90 to 1.80 m**. The existing 100 mm insulation
and 1 mm jacket give **2.002 m jacket OD**. The illustrative butterfly housings
are enlarged to 2.2 × 2.2 × 0.6 m. Their top elevations are unchanged, retaining
the 5 m allowance to the underside of the hoist body. These changes do not
constitute an exhaust-flow or valve-sizing calculation.

A **50 mm OD coolant-transfer tube** now connects the reactor vessel bottom to
a small motor-pump envelope beside the coolant storage tank, then into that
tank's bottom. The owner confirmed heating and insulation: 50 mm radial
insulation is used provisionally, giving 150 mm jacket OD; 3 mm tube wall is
also provisional. The line runs below the reactor's cooling-air baffle and
through a new well sleeve. Local vessel-floor, baffle-floor and well openings
are applied only to the installation copy. Seals, local reinforcement and
thermal expansion remain to detail. Pump duty, drain time, NPSH and materials
are not sized by this model.

The coolant tank keeps its 4 m bare diameter and 8 m body height. It is raised
on **0.9 m supports** to accommodate a true bottom entry and **350 mm insulation
on the sides, roof and underside**, with a 1 mm metal jacket. This allowance
is borrowed from the return-salt pipe draft, not a tank heat-loss calculation.
The resulting side jacket diameter is **4.702 m**. The ladder and top access
neck are moved beyond the insulation envelope. Supports penetrate the bottom
insulation; their heat bridges and loads remain unresolved.

A provisional outdoor **liquid-nitrogen tank** is placed at radius **28.5 m,
angle 330°**, with a **2.5 m diameter × 6.5 m vessel envelope** (vent higher).
An adjacent finned ambient vaporizer supplies gas through a regulator-panel
envelope to a common **50 mm OD gas header** just inside the building. Its wall
entry is above the fresh-air ring. Three capped takeoffs reserve future system
connections; no individual consumer is yet connected. Tank usable inventory,
vaporizer rating, gas pressure, demand, redundancy and final siting are not
established. The owner approved this provisional scope.

Current files: [Blender installation](../outputs/installation-under-cover-bundles/wistr-installation.blend),
[equipment view](../outputs/installation-under-cover-bundles/wistr-equipment-draft.png),
[plan](../outputs/installation-under-cover-bundles/wistr-plan-draft.png),
[coolant-transfer detail](../outputs/installation-under-cover-bundles/wistr-coolant-transfer-draft.png),
[nitrogen supply detail](../outputs/installation-under-cover-bundles/wistr-nitrogen-draft.png).
The nitrogen pad is extended down to the presentation ground datum; foundation
geometry is provisional. The complete installation passes its 34 existing checks
plus 448 auxiliary route/equipment and tank-envelope comparisons, with no selected
clashes. The stair walking/headroom screen also remains clear.
Generation and selected service/envelope checks are in
[`installation_utilities.py`](../src/textual_graphics/installation_utilities.py).
Named baselines, the isolated reactor asset and the site composition are preserved.

## Internal hot-air header and direct reactor exhaust — 12 October 2026

D-040 replaces the upper exterior concrete hot-air ring with a hollow insulated
sheet-metal duct just inside the 42 m building. Its centre radius is **18.75 m**
and centre elevation **Z=10 m**. The provisional clear section is **2.50 × 2.702 m**
(**6.755 m²**), preserving the previous ring's flow area in response to the owner's
identification of the steam generators as the largest maximum heat load. This
is a layout allowance, not a calculated airflow capacity. The envelope includes
3 mm sheet metal, 100 mm insulation and 1 mm cladding, with separate meshes.
The jacket is 246 mm from the inside wall and 850 mm below the crane runway.
The header bottom is 1.238 m above the insulated steam-header envelope.

The stack is rotated from 90° to **135°**, remaining at radius 27 m, aligned with
the reactor's existing hot-air outlet. A separate **2.0 m duct** runs straight
and level from that outlet to the stack at **Z=−2.77 m**. It bypasses the upper
header. The three steam-generator roof exhausts enter the header's inner side;
six fuel-maintenance-tank exhausts rise into its underside after short inward
turns above the steam header. The upper header has its own **2.4 m stack connector**.
Only the direct reactor exhaust and common upper connector pass through the hot
side of the building wall. The fresh-air concrete ring, doorway gap and low reactor
supply remain as before.

The current output remains
[the installation Blender scene](../outputs/installation-under-cover-bundles/wistr-installation.blend).
[Equipment view](../outputs/installation-under-cover-bundles/wistr-equipment-draft.png) ·
[Plan](../outputs/installation-under-cover-bundles/wistr-plan-draft.png).
Checks cover branch topology, direct reactor alignment, geometric insulation,
header/wall/runway/steam-header separation, selected process/air/equipment
interference and existing stair/access clearances. Complete crane and equipment
handling sweeps, brackets and expansion supports remain unresolved. Airflow,
peak duty, pressure loss, natural draft, thermal sizing and stack mixing still
require analysis. No hydraulic or thermal capacity is inferred from this graphic.
The preserved D-038 baseline and site composition are not automatically changed.

## Catwalk stairway — 12 October 2026

D-039 adds a provisional, independently supported three-flight switchback stair
in the clear bay at radius 14 m and 210° from the installation's +X axis,
between a steam generator and maintenance tanks. An approximately **8.2 m
bridge with two bends** reaches a 1.30 m outer-rail opening at 195°, avoiding
the hot-salt riser and leaving the equipment delivery lane open. The inner
catwalk railing and equipment positions remain unchanged. Steel open-grating treads,
landings, stringers, columns, bracing, handrails and landing guards are shown.

The 8.50 m climb from floor Z=−9.10 m to catwalk Z=−0.60 m uses 48 equal risers
of **177.1 mm**, arranged as three flights of 16 risers. Each flight has 15 treads
at **280 mm going**, a 4.20 m run, and approximately **32.3°** pitch. The 1.30 m
tread envelopes provide at least **1.20 m clear width**. Reversing landings are
1.20 m deep at Z=−6.267 and −3.433 m. The stair tower occupies roughly 3.1 × 6.8 m, plus its lower approach and
connecting bridge. Side trusses indicate the bridge load path to the stair
and catwalk frames; end reactions and members require structural sizing. Handrail/guard height allowances
are 0.90/1.10 m. Frame sections are visual allowances, not load-rated members.

Actual stair members and 52 tread/landing/entry/approach walking volumes
are screened against equipment and insulated process/service tubing with every
collection evaluated, reserving **2.10 m headroom**. The stair's own upper
structure is included in the headroom screen. Intended floor and catwalk
attachment contacts are excluded. The selected screen found no intersections, and the existing equipment-door
access check also passes; complete building egress, stair/frame strength, foundations,
handrail details and personnel access during operation remain to assess.
[OSHA's standard-stair dimensions](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.25)
were used as a preliminary geometry reference, not as a compliance determination.

[Full-height stair view](../outputs/installation-under-cover-bundles/wistr-stairs-draft.png) ·
[Equipment context](../outputs/installation-under-cover-bundles/wistr-equipment-draft.png) ·
[Current Blender scene](../outputs/installation-under-cover-bundles/wistr-installation.blend).
Build with `--draft --output outputs/installation-under-cover-bundles --views stairs catwalk fuel-services equipment`.
The stair view is saved as View.Stairs; the committed D-038 baseline remains unchanged.

## Under-cover service bundles and lower catwalk — 12 October 2026

D-038 supersedes D-037's raised service boxes and routing elevations. Twelve
reservoirs and twelve independent modules remain. Only the 50 mm absorber salt
drains are heat traced; their paired 25 mm gas lines share compact insulation.
Tank-top gas connections are insulated without separate heat tracing. Six heated,
insulated maintenance bundles each contain three independent 25/50 mm pairs.
Heater tape adds no separate bulky enclosure. Bundle insulation is a provisional
50 mm allowance; reservoir insulation remains 100 mm with 1 mm cladding.

The catwalk is **1.10 m lower**, at **Z=−0.60 m**. Reservoir bottoms are at
Z=−0.05 m, giving **1.60 m fall** to the spider stubs. External salt drains have
no uphill sections; inherited internal paths retain their horizontal portions.
This checks geometry, not drain time or a qualified operating procedure.

Connected bundles run beneath the six insulation cassettes in **open-bottom
channels**. The covers can lift before cap-side tubing is disconnected. Local
raised insulation strips restore the nominal 512 mm insulation depth above the
channels: the channel roof is 480 mm above the cover base, leaving 32 mm of the
original blocks, with 480 mm added above locally. Header members and channel-edge
webs provide a conceptual load path around interrupted lower grids. Cover pickup
stems and guides extend upward 550 mm to clear those strips. These changes need
new mass, structural and thermal assessments; earlier standalone cover results
do not qualify this revision. Pressure caps, vessel and tube plugs are unchanged.

Checks cover all 72 individual external service tubes, continuous drain geometry,
selected bundle/frame/process/air surface intersections, and five sampled vertical
positions of a representative cover against connected tubing and jackets. They
are selective geometric checks, not a continuous crane sweep or maintenance
procedure validation. Remote connectors, tube supports, expansion accommodation,
heater duty and controls remain to develop.

This revision is applied to the installation's imported cassette copies. The
isolated reactor, standalone cover study and site composition remain earlier
snapshots until explicitly refreshed.

[Blender scene](../outputs/installation-under-cover-bundles/wistr-installation.blend) ·
[Catwalk draft](../outputs/installation-under-cover-bundles/wistr-catwalk-draft.png) ·
[Maintenance bundles](../outputs/installation-under-cover-bundles/wistr-fuel-services-draft.png) ·
[Covers hidden for inspection](../outputs/installation-under-cover-bundles/wistr-under-cover-detail.png) ·
[Geometry report](../outputs/installation-under-cover-bundles/wistr-model-report.json).
Build with `--draft --output outputs/installation-under-cover-bundles --views catwalk fuel-services`.
Render the inspection view with `blender --background --python scripts/render_under_cover_bundles.py`.

## Paired absorber reservoirs and raised catwalk — 12 October 2026

D-037 provides two independent reservoir/module stations for each absorber:
12 new heated salt-reservoir envelopes and 12 existing-style control modules.
The centre and outer spider pairs remain separate. Each 50 mm spider tube now
connects to its own reservoir bottom. Each 25 mm spider tube connects directly
to its own module, which also receives a new 25 mm line from the reservoir top.
There are 24 spider connections and 12 additional tank-top connections.

The catwalk rises **1.70 m**, from Z=−1.20 to **+0.50 m**, and its outer radius
increases from 7.15 to **7.35 m**. The inner radius remains 4.95 m. Tanks and
modules sit at radius 6.60 m: reservoirs at ±5° and modules at ±15° from each
absorber direction. The seats retain a **1.09 m inner walking band**. Access
stairs, structural sizes and handling sweeps remain to design.

Reservoir bottoms sit 0.55 m above the deck, at Z=1.05 m. External drain tubes
fall continuously to actual spider stubs at Z≈−1.65 m: **2.70 m total fall**.
The sloping under-deck runs connect approximate control elevations −0.45 m
outboard and −0.75 m inboard, before turning down. Small control lines fan out
farther outward to avoid the existing fuel-service routes. The existing internal
50 mm tube centrelines are checked for no upward step toward the absorber;
their horizontal portions remain horizontal. This is a geometric drainage
check, not a drain-time or pressure/gas-management calculation.

New reservoir sizing is deliberately provisional: the draft reuses the module's
**0.80635 m diameter × 1.25992 m height** (0.64340 m³ gross envelope). It does not
establish the necessary absorber inventory or usable tank capacity. Existing
module tanks retain those dimensions as well. New reservoirs show electric
heater bands beneath **100 mm insulation and 1 mm cladding**, with heater
terminal boxes. These are visualization allowances, not thermal sizing results.
Separate service-line insulation uses a provisional **50 mm radial allowance**;
the close-pitch spider bundle uses a common removable insulated enclosure.
That enclosure sits over the spider service insert; the main sector insulation
cassettes and pressure parts are unchanged. Remove the enclosure and jumpers
before lifting covers or the spider. Heating duty, controls, final connections,
pipe supports and thermal expansion remain to develop.

The updated checks cover independent station connectivity, actual spider
endpoints, sampled rounded drain paths, separated pipe-jacket clearance,
selected catwalk frame/equipment/process/air envelopes, and the existing 36
fuel-service lines against the new insulated routes. They do not establish a
complete maintenance sweep or engineering qualification.

[Installation Blender scene](../outputs/installation-absorber-reservoirs/wistr-installation.blend) ·
[Catwalk draft](../outputs/installation-absorber-reservoirs/wistr-catwalk-draft.png) ·
[Fuel-service context](../outputs/installation-absorber-reservoirs/wistr-fuel-services-draft.png) ·
[Geometry report](../outputs/installation-absorber-reservoirs/wistr-model-report.json).
Build with `--draft --output outputs/installation-absorber-reservoirs --views catwalk fuel-services`.
[Paired-station cutaway](../outputs/installation-absorber-reservoirs/wistr-absorber-detail.png)
shows the drain routes with the walkway and common covers removed, and one tank
jacket removed to expose its heater bands. Reproduce with
`blender --background --python scripts/render_absorber_detail.py`; this also sets
the complete installation scene to open on the catwalk overview.

Earlier installation and site snapshots are preserved; the site composition is
not refreshed automatically.

## Doubled absorber-tank volume — 12 October 2026

D-036 doubles the geometric volume of all six cylindrical tanks on the absorber
modules. Uniform linear scaling by **2^(1/3) = 1.259921** preserves their aspect
ratio: diameter **0.640 → 0.80635 m**, cylinder height **1.000 → 1.25992 m**.
Nominal cylindrical envelope volume is **0.32170 → 0.64340 m³ per tank**. Usable
salt capacity still depends on the eventual wall, internals and fill allowance.
The edge bevel scales by the same factor.

The tanks retain their bottom elevation and pipe connections. Control boxes and
front panels rise **259.9 mm**, keeping their previous dimensions. The wider
tanks fit the existing module footprint and bearing pads, so catwalk dimensions
and routing are retained. The outer guardrail has about **122 mm** radial
clearance from each tank envelope; module loads/support ratings remain to size.

[Revised close-up](../outputs/installation-absorber-tanks-v2/wistr-catwalk-draft.png) ·
[Fuel-service context](../outputs/installation-absorber-tanks-v2/wistr-fuel-services-draft.png) ·
[Dimensions and checks](../outputs/installation-absorber-tanks-v2/wistr-model-report.json).
Build with `--draft --output outputs/installation-absorber-tanks-v2 --views catwalk fuel-services`.
Earlier catwalk and fuel-service snapshots are preserved.

## Sector-to-maintenance-tank connections — 12 October 2026

D-035 adds **36 external tubes**, keeping all three 25/50 mm pairs on each sector
separate and assigning one maintenance tank to each sector. This is a provisional
layout assignment, not a transfer procedure or tank-internal design:

| Sector | Maintenance tank |
| --- | --- |
| 1 | 6 |
| 2 | 1 |
| 3 | 2 |
| 4 | 3 |
| 5 | 4 |
| 6 | 5 |

Each route starts at the actual imported sector plug stub. The tubes rise through
six-hole passages in the existing core-service insulation inserts, turn outward,
drop inside the catwalk and sweep beneath the deck before approaching six separate
roof nozzles on the corresponding tank's reactor-facing end. The two tube sizes
run at separate elevations to avoid crossings; their 2 mm walls remain inherited
visual assumptions. Magenta identifies 25 mm tubes, copper 50 mm tubes; colors do
not establish flow direction. No common fuel manifold is introduced.

Visible union allowances mark disconnects at the plug, outside the insulation
cover and at the tank. Remove the cap-side jumpers before handling insulation,
sector caps or core sectors. The core-service inserts have six bores and the tank
lids have matching six-port passages; the tank bodies remain closed envelopes.
Valve selection, remote connector details, tube heating/insulation, supports,
drainability and maintenance sweeps remain to develop.

- [Service-routing view](../outputs/installation-fuel-services/wistr-fuel-services-draft.png)
- [Full installation](../outputs/installation-fuel-services/wistr-equipment-draft.png)
- [Blender model](../outputs/installation-fuel-services/wistr-installation.blend)
- [Route coordinates, assignments and checks](../outputs/installation-fuel-services/wistr-model-report.json)

The saved model opens on the service-routing camera with the reactor, catwalk,
six tanks and connecting tubes visible. Remote equipment is hidden for clarity.
The full installation render retains that surrounding equipment. The previous
catwalk-only model and all site snapshots remain preserved; the site composition
has not yet been refreshed with this installation revision.

Verification: 36 unique source ports, six distinct tank assignments and retained
25/50 mm ODs pass. Static checks found no intersections with the other new fuel
lines, absorber routes, existing process/air pipes, catwalk rails, selected frame
members and equipment boxes. The closest screened bare-tube gap is about 20 mm;
this is not an insulation or thermal-movement allowance. Full cover/sector
removal sweeps and pipe-support design remain open.

Implementation: `src/textual_graphics/installation_fuel_services.py`; parameters:
`FUEL_SERVICES` in `models/wistr_installation.py`. Build using `--draft --output
outputs/installation-fuel-services --views fuel-services equipment`.

## Reactor catwalk and absorber connections — 12 October 2026

The owner requested expanded-metal access around the vessel top and approved
one absorber module opposite each absorber, replacing the three paired stands.
The new shared annular frame is independent of the vessel pressure boundary.

- Deck radii **4.95–7.15 m**, nominal width **2.20 m**, walking surface Z=**−1.20 m**.
  This sits 0.82 m above the vessel rim, clearing the large hot coolant pipes and
  side air collector boxes. Inner/outer guardrails are local to this catwalk;
  building-circumference railings remain absent.
- Six modules at radius **6.60 m**, angles **45°, 105°, 165°, 225°, 285°, 345°**,
  numbered to match absorbers 1–6. Dedicated bearing pads and beams carry the
  modules, leaving approximately **1.16 m** clear inside the seat plates.
- Open diamond-lattice panels represent expanded metal. Ring beams, radial
  joists, twelve columns and knee braces are provisional visual sections.
  Equipment weight, deck rating, structural loads and connections are not sized.
- Each absorber retains **two 25 mm and two 50 mm OD tubes**, with the existing
  illustrative 2 mm wall. All **24** external lines start at the imported stubs'
  exact coordinates. Each bundle rises through its insulation insert, turns
  outward, drops just inside the catwalk, runs below the deck and enters the base
  of its corresponding module. Walking surfaces remain free of cross-piping.
- Visible union envelopes identify removable spider-side jumpers. Disconnect
  these before lifting the inserts/covers or spider. The absorber thermal inserts
  receive bored service passages; core-service inserts remain as before. Detailed
  remote connectors, tube supports, heat tracing and insulation remain to design.
- Access stair/egress, complete crane sweeps and structural qualification remain
  open. This draft establishes arrangement and connectivity, not operating approval.

[Close-up](../outputs/installation-catwalk/wistr-catwalk-draft.png) ·
[Installation view](../outputs/installation-catwalk/wistr-equipment-draft.png) ·
[Model/check report](../outputs/installation-catwalk/wistr-model-report.json).
The saved model opens on the close-up; surrounding installation equipment is
hidden in that view. The equipment camera/build view shows the complete arrangement.
The earlier `installation-insulated` and `site-45-bends` snapshots are preserved;
the site snapshot has not yet been regenerated with this reactor-building revision.

Verification: all 24 stub endpoints and tube sizes match; selected tube/column
checks against existing process and air routes pass. Same-bundle tubes retain at
least 22.5 mm nominal surface separation (before coupling allowances). The
installation equipment counts and existing selected interference checks also pass.

Builder module: `src/textual_graphics/installation_catwalk.py`. Build with
`--draft --output outputs/installation-catwalk --views catwalk equipment`.

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
  the then-current sector storage to **(17.3, 0) m**. D-042 subsequently removes
  that fixed enclosure; D-041 raises coolant storage for its insulated bottom connection.
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

| Component/interface | Placement in the 10 October draft |
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


## Hot-air insulation allowance — 11 October 2026

The working model adds a **provisional 100 mm insulation layer and 1 mm metal
cladding** to all ten equipment hot-air branches, the stack connector and stack
barrel. The reactor's hot side collector, wall crossover and stub use the same
allowance in the isolated reactor and imported installation. The lower fresh-air
route is retained. The shared values live in `models/wistr_air_insulation.py`.

The duct branches have separate hollow metal, insulation and cladding meshes;
the illustrative branch sheet wall is 3 mm. Existing reactor-stub dimensions
remain unchanged. The insulation sits outside the nominal duct dimensions, and
hidden route guides use the complete jacket diameter for interference checks.
The stack retains its schematic internal representation. Valve mechanisms,
removable insulation blankets at actuators, support thermal bridges, expansion
joints and detailed jacket seams remain to design.

The upper concrete manifold has a liner on all four internal faces. It grows
202 mm radially outward and 404 mm in total height, providing a 2.500 m clear
radial width and 2.702 m clear height after lining. Its 2.602 m jacketed stack
connection fits within that height. Hot risers are adjusted for the larger
jackets; the two exhaust branches beside the sector-storage enclosure first rise
above it before reaching the wall. The earlier accepted checkpoint is unchanged.

This is an envelope allowance, **not a calculated insulation requirement**. Hot-air
normal/transient temperatures, ambient conditions, allowable surface temperature,
insulation material properties, heat loss and natural-draft performance are still
needed before selecting a thickness. No new thermal result is claimed.

Build the reactor with `scripts/build_reactor.py` and the installation with
`scripts/build_wistr.py`. To add this allowance once to a pre-existing working
reactor, `scripts/refresh_reactor_air_insulation.py` preserves its other geometry,
checks the air system and refreshes the source manifest. Subsequent allowance
changes require a full reactor rebuild.

Validation of this draft: eleven insulated route guides (ten equipment branches plus the stack connector), all three branch layers and bend envelopes passed checks. Expanded process/hot-air route and selected equipment-envelope checks found no unresolved clashes. The reactor insulation meshes passed closed-mesh and selected coolant-nozzle clearance checks. Junction blankets and cladding around flanges/actuators still need detailing.


## External site context — 11 October 2026

The separate [site study](site-study.md) places provisional turbine and fuel-preparation
buildings around this installation, retaining its current geometry and secondary
pipe interfaces. The installation source remains the detailed component-level view.
