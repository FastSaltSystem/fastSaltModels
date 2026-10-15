# WISTR reactor study

Current absorber update (15 October 2026): [chamber-bottom revision and capacity/P&ID review](absorber-system-review.md). Absorber bottoms now align with the active-core bottom; earlier dimensions below describe prior snapshots.

All shell commands and code paths below are relative to the `fastSaltModels` repository root.

[Repository overview](../README.md)

## Approved reactor baseline — 2026-10-07

Git tag `wistr-reactor-baseline-2026-10-07` marks the approved isolated reactor,
including the enclosing cold-air hood and short central hot/cold duct stubs,
before adding fuel/absorber tubing or integrating it into the installation.
That tagged snapshot retains the earlier 3.6 m core diameter. The working model
now uses the owner-confirmed 3.8 m from slide 6 of Fast Salt System 5.pptx.
`baselines/wistr-reactor-2026-10-07/` preserves the exact Blender model, its
geometry-check report, and a SHA-256 manifest. Open that saved `.blend` for the
baseline; use `outputs/reactor-study/` for ongoing work. Routine generated
outputs and working backups remain excluded from Git.

The subsequent approved tubing snapshot is preserved in
`baselines/wistr-reactor-tubing-2026-10-07/`, including its Blender file,
validation report and SHA-256 manifest. It incorporates the 3.8 m core,
three coolant legs, separator supports, absorber and core service tubing,
radial reflector slots, and larger caps over a smooth circular spider opening.
The original baseline remains unchanged.

The approved handling and tube-plug design is preserved separately in
`baselines/wistr-reactor-handling-2026-10-08/`. It includes the exact Blender
file, geometry report, lifting-head animation and SHA-256 manifest. This snapshot
adds the centered pivoting lifting head, opposed hooks, remote maintenance
catches, removable tube plugs and simplified routing. Both earlier baselines
remain unchanged; continue editing the working outputs rather than this snapshot.

## Isolated reactor review

The newer reactor study is separate from the installation. Its sources are
`references/wistr-reactor-1.svg`, `references/fourbar-retract.svg`, and
`references/sectors-with-regions.jpg`, copied unchanged from the supplied drawings.
Run:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_reactor.py
```

Outputs in `outputs/reactor-study/` include `wistr-reactor-study.blend` and
`reactor-cutaway.png`, `reactor-section.png`, `reactor-plan.png`, and
`reactor-cap.png`, `reactor-linkage.png`, `reactor-supports.png`, and
`reactor-maintenance.png`. Detail views are `reactor-support-detail.png`,
`reactor-spider.png` (underside), and `reactor-pattern.png` (exploded bore layout).
`reactor-separator-supports.png` exposes the wall ledge and three levels of
absorber-to-vessel braces, with sector cores and separators hidden.
`reactor-absorber-tubes.png` shows all six absorber tube sets and the spider;
`reactor-absorber-tube-detail.png` isolates one set with a cropped tank top and
spider segment to expose both attachment pairs and the terminations.
`reactor-air-system.png` shows the complete air collectors and ductwork;
`reactor-air-section.png` opens them to show the separate inlet and return paths.
Use `-- --draft` for previews or `-- --views section plan`
for selected renders. Building the study does not change the installation scene.

`models/wistr_reactor.py` holds the supplied and provisional dimensions separately.
The core is 3.8 m diameter and 3.4 m high, excluding the reflectors and plenums.
The radial reflector adds 0.3 m and the downcomer adds 1.0 m radially, giving a
6.4 m lower vessel internal diameter. The upper vessel now fits around the raised
separator envelope, retaining the previous vessel allowance, giving
about 7.663 m hot-plenum inside diameter. The well and air baffle follow this
stepped profile. Bottom reflector, top reflector, and bottom plenum heights
are 0.3 m, 0.25 m, and 0.75 m respectively. The bottom plenum was reduced by 25%.
The hot plenum remains 1.6 m high to fit the 1.4 m side outlet, giving 6.30 m
total internal stack height. Cold-inlet centres are at Z=3.73 m, lowered
0.17 m to clear the new top absorber braces by 30 mm.
There are three hot outlets and three cold inlets for three coolant legs,
spaced every 120 degrees within each set and staggered by 30 degrees between
the sets. Hot outlets are at 30, 150 and 270 degrees, shifted 30 degrees
toward the cold inlets to clear the absorber tubing routes at 60-degree intervals.
The shared hot plenum and cold downcomer distribute coolant among
the six sectors; there are no external branch manifolds. All side pipes retain
their 1.4 m outside diameter and illustrative 35 mm wall (1.33 m clear bore).
The cold stubs extend 0.35 m farther outward for presentation; stub lengths
do not define the installation routing.

A fixed annular ledge projects 89.3 mm inward from the lower vessel wall.
Its height is twice its radial width (178.6 mm); its top at Z=4.66 m seats
the underside of the 40 mm separator below the Z=4.70 m hot-plenum floor.
The ledge width derives from the outer envelope of the upright four-bar links
plus 30 mm provisional running clearance, allowing for the faceted ring mesh.
At each of the six absorber positions, three fixed radial braces join the
absorber outer end to the vessel wall (18 total). They are 200 mm tall and
160 mm thick, twice the current illustrative 80 mm absorber thickness.
The top braces share the separator bearing elevation and support both
adjacent separator edges. Bottom braces start at the absorber bottom,
Z=0.75 m; middle braces are equally spaced between the top and bottom levels.
Braces extend 10 mm into the vessel wall to connect their flat ends to its
curved surface. Checks verify separator contact, inlet clearance, fixed support
positions, and clearance from the selected sector's links and moving mounts
in seated and raised poses. Leakage reduction is a geometric design intent;
leakage, load capacity, and a continuous motion sweep are not calculated.

The removable caps cover openings for the core, top reflector and attached
service tubes and the core-owned tube plug.
Opening radius is approximately 2.975 m, allowing at least 100 mm radial clearance
around the raised core and 20 mm around the conservative raised tube-and-plug envelope.
The spider outer band is narrowed to provide this continuous circular opening.
Peripheral/bottom reflectors and separators stay below
this opening. The cap plate radius is approximately 2.990 m, including its
15 mm overlap onto the spider band. Its outer arc is smooth.
Plate tops remain at Z=6.57 m.

Caps, top reflectors and cores each have two opposed pairs of parallel lifting
hooks, 25 mm thick and 255 mm high. The outer pair is reversed so the mouths
face away from the centre of the pickup head. Two 40 mm bars engage from outside,
then sit beneath the crowns behind the retaining lips.

The common head has two pivoting arms on parallel hinge axes. Their bars remain
parallel as they spread. A split release cable pulls offset horns on the arms;
releasing it permits gravity-closing motion in principle. The closed bars are
750 mm apart and 500 / 1370 mm long. Pin centres are 80 mm inward and 480 mm
above their respective closed bars; the open arm angle is 30 degrees from vertical.
The mast top remains 1.30 m above the bars. Its upright, mounting block and
hoist connection are centered between the two pivot axes on all three pickup
types; the former offset suspension settings are removed. Actual load sharing
depends on the lifted assembly’s centre of mass. The cap hook pattern is displaced outward
1250 mm to retain space around its tube plug.

The checked approach keeps the bars together while descending past the service
tubes, spreads them 170 mm above their carrying position, then lowers the head
88 mm below that position before closing. Hoisting seats the bars behind the
lips. After setting down the item, lower the unloaded head 88 mm, pull the release
cable to spread the bars, and withdraw along the reverse path. Setting the load
down alone is not modeled as opening the bars. The plug-support upright was
narrowed and shifted within its existing reflector relief to clear the bar ends;
no new reflector slot was added.

`lifting_bars_open` varies from 0 (together) to 1 (spread), and
`lifting_head_lowered` varies from 0 (carrying height) to 1 (lowered 88 mm).
These are presentation controls, not a release interlock. The `cap-handling` and
`cap-handling-open` views show the engaged and spread positions.
`outputs/reactor-study/reactor-lifting-head-motion.gif` illustrates closing,
seating, lowering after set-down, and cable-operated spreading. Repeated heads
in inspection views depict the same tool. Checks cover engagement, withdrawal,
bar parallelism, arm/body clearance, cable geometry and obstruction by all four
hook lips at carrying height. Gravity return, friction, load capacity, balance,
load sharing, welds and release-under-load prevention remain unqualified.

The remote-handling concept adds two dedicated pickup eyes and two separate
U-bar keepers to each peripheral reflector. The pickup eyes are 0.70 m apart;
the keeper bars are 1.30 m apart. In the raised position, paired wall-mounted
rotary catches capture the keepers. Outward stops define the maintenance endpoint.
Braced brackets reach inward from mounting plates beside the hot nozzles.
A curved plate crossbar, 10 mm thick and 50 mm high, links each pair of catches
through 10 mm rod uprights. Bent rod ends pass
through 16 mm holes in the hooks and have captive end retainers. Two small U-shaped
guides stand off from brackets attached to the spider's inner edge. Their loose
openings let the rod slide and rock as the hook holes move through their arcs.
Fixed rests define the hooks’ closed position. The crossbar follows the spider curve. A temporary secondary crane hook or robot
pulls its centre upward through the removed cap opening. The model constrains
both lower connections to the hook holes throughout the release stroke.

The previous catch locking pins, powered drive housings, release rockers and
secondary cable yoke are removed. This is now a gravity-return catch concept;
there is no independent positive locking pin. Gravity return, resistance to
load-induced opening, friction, wear and release force require engineering checks.
All 24 former catch-release shaft holes in the spider remain closed. There are
no permanent catch-release penetrations; other pressure boundaries are not
qualified by this geometry.

The peripheral-reflector pickup head retains guided forks and captive powered-pin
envelopes as the second tool type. Both heads have a top stud for a remote
crane tool-changing coupling. The reflector
head fits through the spider opening in the maintenance position. The tool heads
are in **Remote lifting tools**, hidden in the normal assembled scene. New views:
`remote-handling` shows the raised sector and attached head; `latch-detail` shows
the closed catches; `latch-released` shows the common bar raised and catches open;
`cap-handling` shows the cap pickup head; `release-tool` shows the temporary
secondary hook and cable together with the primary reflector lifting head. All attachment and release interfaces
assume remote equipment, with no hands-on work at the vessel.

Scene Properties **maintenance_release** varies the selected pair continuously
from 0 (down/closed) to 1 (fully raised/open). **maintenance_locks_engaged** is
retained as a display shortcut: disabling it fully opens that pair. Other pairs
stay closed. **maintenance_position** controls the sector pose independently;
**remote_grapple_engaged** still controls powered pins in the removable lifting
head for the peripheral reflector only. These are visual controls, not dynamic simulations or safety interlocks.

The intended sequence is to support the sector with the main crane, hold the
catches open while raising the sector, then lower the release bar and verify
both catches have engaged before transferring support. To lower the sector,
re-engage the main lifting head and take the load before pulling the release bar.
Position confirmation, load retention, welds, remote handling equipment,
temperature/radiation qualification, service disconnections and jam recovery
remain engineering work. The report distinguishes geometric checks from these
unverified functions.

Each core has four parallel hooks anchored to its two radial side edges (two
per edge), with short inward tabs carried by straps into the side structure.
Each top reflector has four independent parallel hooks farther inward. Edge-open
reliefs clear the core hooks during independent top-reflector removal; a narrow
continuous opening clears the service-tube edge. The shortened bar ends clear
the core tubes during reflector withdrawal. Local top-reflector hook reinforcement
still needs design; the contact-area check only confirms partial bearing on
remaining steel between illustrative cooling holes.

`top-reflector-removal` shows the reflector lifted away; `core-lifting` exposes
the core-edge attachments; `core-removal` shows the core and its attached tubes
above the retained peripheral and bottom reflectors. The latter stay in the
latched maintenance position. **Extraction tools** and **Remote release tools**
are hidden in the normal assembled scene. These inspection views use exploded
poses; they do not add a programmed removal cycle. The checks cover the top
reflector body's vertical swept volume, sampled pickup-head clearance from the
service tubes, sampled core-tube withdrawal past the fixed catches, and the
core/reflector/tool envelopes through the spider opening. The temporary release
hook and common bar are checked against the primary lifting head, tubes and
spider at 2-degree hook-angle intervals over the 60-degree release stroke. The
bent rod ends stay aligned with the hook holes, and the rods fit inside the
U-guides throughout those samples.
Lifting capacity, crane stability, remote engagement verification and service
disconnections require further design.

Each absorber carries two pairs of tubes, each with one 25 mm and one 50 mm OD
tube (24 tubes total). Across the hot plenum, the four lines are stacked at
55 mm pitch, with the lowest centreline 250 mm above the plenum floor. Near the
wall they spread into four side-by-side risers at 60 mm pitch, with
a shared removable plug through the spider. Provisional saddles provide
wall attachment locations. Tube ends are at Z=6.67 m, 100 mm above cap plates.
The 2 mm tube walls, bends, offsets, saddles and hole allowances are provisional.

Each core sector carries three service pairs (36 tubes total). Each 25 mm
blue tube starts at the core top; each 50 mm copper tube starts at the core
bottom. All six tubes stay in one radial plane 75 mm from the sector boundary
until the top runs reach their bottom partners. Three vertically stacked bottom
runs share one edge-open groove, and their risers occupy one radial slot in the
peripheral reflector. The slot reaches 110 mm from the boundary (62 mm beyond
the reflector edge), limiting its footprint to the first illustrative bore row.
The bottom groove intersects 19 illustrative bore footprints per sector, versus 49 with the
previous three L-shaped routes. This is a geometric comparison, not a coolant
flow-loss calculation.
Bottom risers at radial coordinates 2.11, 2.04 and 1.97 m are nested in the same
plane. Top runs retain the extra 300 mm rise; staggered meeting heights avoid
crossings. A single rising diagonal now takes each tube to its plug terminal, replacing
the intermediate riser and upper doglegs. Each 50 mm bottom tube has four bends;
each 25 mm top tube has three. The tubes form three pairs in a circular plug centred at sector-local (2.16, 0.50) m. The plug is outboard of
the core outline, so the top reflector can lift past it. Tube ends remain 100 mm
above the seated cap. A 300 mm enclosed circular cap opening replaces the
rectangular edge notch. The larger circular spider opening clears the raised
plug flange with a provisional 20 mm allowance; fixed bridges reconnect the
release-guide brackets to the remaining outer ring.

The four cap hooks have moved 200 mm outward, retaining the common two-bar
crane head. The `cap-service` view shows the seated cap and connection space. A 700 mm diameter workspace around the plug axis is checked clear
of the hooks; external fittings still need their own layout. The support frame
passes outside the simplified sloping tubes and stays attached to the core.

Each absorber's four tubes now pass through one removable plug beneath the
spider: six plugs in all, each with a provisional 400 mm flange, 260 mm pilot,
270 mm spider opening, circular face-seal placeholder and six captive screws.
The risers sit farther inward, at radius 3.53 m. Extended wall saddles hold the
risers; two separate wall shelves carry each plug independently of the tubes.
The screws and seals remain with the spider; tubes and plugs remain below it.
`absorber_plug_bolts_retracted` controls screw withdrawal. The
`absorber-plug-detail` view raises the locally cropped spider 300 mm to show the
interface. Both inspection properties reset in the assembled view.

Spider removal also requires disconnecting external services and detaching the
separate release-guide bridges and other roof attachments. Those attachment
removal operations are not modeled. The tube-interface check withdraws all
screws and samples a 1 m vertical spider lift in 25 mm steps against stationary
plugs, shelves and tubes; it is not a complete spider-handling procedure.

Each plug has a provisional 470 mm flange, 290 mm pilot and 120 mm body height.
The six tubes pass through bores and have illustrative seal-weld rings. Six M16
socket-head screws enter 60 mm blind holes; their 75 mm withdrawal leaves the
plug free while retaining the screws inside cages on the cap. Threads are
represented by smooth shafts and bores. An annular metallic-seal placeholder
sits in the cap's underside groove outside the bolt circle. Its actual seal
section and retention detail require design. A separate core-owned support
frame carries the unbolted plug through an existing core-hook relief and the
existing reflector edge opening. No additional reflector cutouts are needed.

Tubes, plug and frame are parented to the core in Blender, so moving the core
keeps the complete assembly together.

The maintenance sequence assumes depressurization and external service
isolation/disconnection: retract screws, lift cap over tube ends, raise and
latch sector, remove top reflector, then withdraw core, tubes, frame and plug.
The `plug-detail` view shows the cap lifted 350 mm and the seal exploded 100 mm
below its groove for visibility; cap and tubes are locally cropped and the
support frame is hidden. `sector_plug_bolts_retracted` controls the screw display
pose. `sector_plug_detail_view` controls the inspection crop. Both are off in
the saved assembled scene. `Sector tube plugs` is a separate Blender collection.

The model checks screw withdrawal, cap lift, the sector's maintenance arc,
top-reflector passage, and core/plug extraction. These are geometric checks;
pressure and leak tightness, seal selection, welds, bolt preload, differential
thermal movement, support capacity and remote failure recovery remain unverified.
`reactor-core-tubes.png` hides the core to expose the stacked edge runs and slot.
External connections and disconnections are not modeled.

Checks cover counts, diameters, open bores, closed pipe walls, reflector slots and circular cap openings, tube separation and spider passages. The complete tube projection
fits through the spider in the raised pose; sampled vertical lifts check
that the bottom tubes can leave their open reflector slots. Fixed absorber
tubes are checked against the moving sector and links; moving core tubes are checked against
fixed tubing, mounts and the spider at 31 positions on the actual four-bar arc.
These sampled checks do not constitute a continuous collision proof or a
thermal-expansion or structural analysis.

The file opens in the air-system section view, with all sectors seated and
all six vessel cap pieces installed beneath the new air hood.
In Blender **Scene Properties → Custom
Properties**, turn off **section_cutaway** to restore the complete geometry;
one scene property drives all presentation-cut modifiers. Turn off
**maintenance_position** to reseat sector 3, return its links to horizontal and
restore its cap. For maintenance access, hide the **Air collectors**, **Air ducts**,
and **Air path arrows** collections before enabling **maintenance_position**.
Cap pieces, spider,
core sectors, absorber tanks, four-bar hardware, well, baffle, and radial supports
are separate named assemblies/collections. Hide **Labels.air-section** for an
unannotated viewport. The saved **View.ReactorSection**, **View.ReactorPlan**,
**View.CapAndSpider**, **View.SectorAndLinks**, **View.RadialSupports**, and
**View.MaintenanceSector**, **View.SupportDetail**, **View.SpiderUnderside**, and
**View.TriangularBores** cameras are also available; the build script applies
the corresponding collection visibility and cap offsets for each exported view.
The new **View.AirCollectors** and **View.AirCircuit** cameras show the assembled
exterior and the operating air-circuit section. The earlier cutaway and
maintenance renders retain the raised sector with the air collectors hidden.

### Historical hood arrangement — superseded by the side-air revision

The insulated hot-air hood collects air rising between the vessel and baffle,
including air over the segmented vessel cap. A larger cold-air hood encloses
its roof and sides, so incoming air flows over and around the hot collector
before entering the downflow annulus between the baffle and concrete well.
The cold ring extends across 85% of the 0.40 m concrete wall width; its clear
radial width increases from 0.22 m to 0.56 m. Its outer skin leaves about 52 mm
to the outer edge of the concrete wall. The added width is above the wall;
the existing downflow passage below remains 0.22 m wide.

Two open vertical stubs, centred at X=−1.15 m (cold) and X=+1.15 m (hot), are
left for later connection. Both are provisionally 2 m outside diameter with
20 mm walls and extend 0.80 m above the outer hood. The cold stub opens only
into the outer hood. The hot stub passes through that cold-air space in a
separate sealed tube, connecting directly to the hot collector. The earlier
long exhaust duct, stack, and side supply duct are removed from this study.

The hot roof underside remains 1.40 m above the vessel top, with 120 mm
insulation and 8 mm skins. Its upper surface is Z=7.836 m. The cold hood has
0.60 m clear space over that roof, an 8 mm roof at Z=8.444 m, and stub ends at
Z=9.244 m. The hot wall insulation tapers above the spider-ring overhang to
keep the return-air entrance open. These dimensions are provisional. Hood
removal and duct disconnection are conceptual; detailed lifting hardware and
seals are not modeled. Reduced heat release to the room is the intent of the
cold-air enclosure; heat transfer and pressure losses have not been calculated.
Geometry checks verify closed wall meshes, open duct mouths, isolation of the
hot duct from the cold-air space, and the inlet path into the well-side annulus.

The two absorber tanks on the section plane are removed by the viewing cut,
which is offset 0.06 m behind the centre to expose the core. The complete model
still has six tanks and six sectors. The cap render shows the five remaining
caps lifted for inspection; sector 3's cap is hidden. Each sector owns its neutron reflectors and
one separator segment spanning the downcomer; these parts move together when
the sector parent is moved. The separator is not part of the vessel assembly.
The top reflector has the same 1.9 m outer radius as the core and rests directly
on it, inside the peripheral reflector. The peripheral reflector extends up
alongside the top reflector and carries the separator at its upper outer edge.
Each sector has two upper bars
and two lower bars. The bars lie in parallel planes aligned with the sector
bisector, rather than diverging along different radial directions. Their pair
spacing is provisionally 1.5 m. Each bar is now 0.26 m wide and 0.30 m deep,
four times both previous transverse dimensions. Rounded ends extend 0.15 m past
each pin centre, with actual through-holes for the pins (3 mm provisional radial
clearance). Wall-pin centres are 0.30 m
inward from the lower vessel inner surface. Larger clevis cheeks and curved
backplates join those pins to the wall. Moving lugs are also extended enough to
clear the upright bars from the curved reflector, with 0.02 m nominal clearance.
The moving lugs belong to the sector. Sector 3's maintenance pose rotates all
four links upright about their fixed wall pins. Its outward translation and
lift each equal the revised 0.521 m pivot-to-pivot link length. Scene drivers
switch between the seated and raised endpoints; there is no dynamic simulation
or full collision sweep. Section and linkage renders remain seated references;
the maintenance close-up isolates the raised sector and its hardware.
Seals and detailed hardware clearances remain to be specified.

The core and both reflectors now contain actual aligned through-bores in a
triangular lattice, with row families parallel to both radial sector edges.
The previous illustrative 85 mm pitch and 48 mm bore diameter are retained.
There are 257 lattice positions per sector, giving 1,542 aligned passage
positions. Top-reflector service notches open into a few edge bores. The count
and dimensions do not specify a tube design. The pattern render offsets the
two reflectors for inspection and resets them before saving the assembled scene.

Spider legs are widened to approximately 0.465 m, derived from the raised
separator's edge offsets. A matching hexagonal hub joins their inner ends.
The circular opening clears the raised core and top reflector, with at least
100 mm radial clearance, and also accommodates their attached service tubes.
The larger peripheral reflector,
bottom reflector and separator remain below the opening; they are not part of
the vertical extraction envelope. A vertical sheet 15 mm thick and 50 mm high
is welded along the underside centre line of each radial leg. This projected
passage check does not constitute a full mechanism collision sweep or structural
analysis.
The reactor report records dimensions, source hashes, assumptions, assembly
counts, checks that all six pipes pass through the vessel, baffle, and well,
checks sector/reflector/separator parenting, and verifies four equal-length
parallel bars per sector (24 link bars total). It also checks the wall-pin
setback, fixed wall mounts, bar-to-pin coincidence in both poses, upright links,
reflector clearance, cap visibility and repeatable pose toggling. Further checks
verify through-bores, closed perforated meshes, pin overhang and the spider's
vertical passage envelope.

Twelve cylindrical pedestals now support the peripheral reflector, two in each
sector at 15° and 45°, centred at radius 2.05 m. Their owner-specified 0.30 m
diameter matches the peripheral reflector's radial thickness. Six 20 mm radial
sheets, one beneath each absorber, extend from radius 0.15 m to 2.2 m. Provisional
200 mm wide, 20 mm thick lips support each absorber and both adjoining bottom
reflectors. Each sheet has eighteen 100 mm through-holes in two rows. Hollow
half-tube stiffeners (20 mm outside diameter, provisional 2 mm tube wall) are
welded vertically on both faces, at 200 mm centres between the holes.
The same pedestals, sheets, lips, openings and stiffeners are used beneath the
vessel, retaining the previous provisional 0.40 m external support height.
The central 0.30 m diameter remains clear. The air baffle has twelve pedestal
openings and six slots around the stiffened sheets.
The supports view hides the vessel plate, baffle, reflector and well to expose
both levels without moving them. Geometry checks verify seated contact, alignment,
the central clearance and open radial channel centre lines; these are not
structural capacity or coolant/air pressure-loss calculations.


## Refresh preserved-baseline views

Use `scripts/render_reactor_baseline.py` to render the preserved 2026-10-08 scene without rebuilding or overwriting it. This refreshes views whose older working PNGs may predate the current cap hooks and tube plugs.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/render_reactor_baseline.py -- \
  --views cutaway air-section core-removal
```

Images and a source/image hash manifest go to `outputs/workshop-reactor/`. Optional `--draft` halves resolution; `--output` selects a different destination. The view-selection code is shared with `build_reactor.py`; the manifest records that script's hash as well as the preserved scene hash. Source geometry remains the pinned baseline.


## Insulation covers and side air connections — 11 October 2026

The current working reactor replaces the former enclosing hot/cold hoods with
six removable rigid insulation cassettes. Five suspended T-grids are retained:
the bottom layer is grooved; four upper layers rest on flat flanges. The pressure
caps remain separate below the insulation. Preserved 2026-10-07/08 baselines are
unchanged. The installation now imports this working reactor through its generated
SHA-256 manifest rather than importing the older hooded geometry.

- [Complete working reactor](../outputs/reactor-study/wistr-reactor-study.blend)
- [Insulated reactor and side plenums](../outputs/reactor-study/reactor-air-system-draft.png)
- [Air-path section](../outputs/reactor-study/reactor-air-section-draft.png)
- [Fitted-cover checks](../outputs/reactor-study/reactor-cover-fit-report.json)
- [Independent cover development](tgrid-insulation-cover.md)

The cassettes seat at the cap elevation, with blind pockets around the existing
cap hooks. Twelve circular service access wells align with six core-tube plugs
and six absorber-tube plugs. Lift-out thermal inserts cover the disconnected
terminals. Remove these inserts before cassette removal. External service-line
extensions, sealing around operating lines, insert handling and thermal bridges
remain to design; this is not a completed operating-service arrangement.

The imported frame has local hollow box-section collars around service openings.
These change its structural load path. The standalone cover's grillage estimate
and approximate 2.16 t mass must not be treated as fitted-cover capacity or mass.
The integration report gives a separate additive geometric estimate, with no
lifting rating. Local bearing, frame/grid cuts, collar welds and the revised heat
balance require renewed analysis.

### Vessel cooling-air circuit

Two separate side plenums connect to the existing annular cooling passages:

- Fresh air enters the outer passage between the well and steel baffle, descends
  to the bottom, turns beneath the vessel, and rises next to the vessel.
- Hot return air enters its side collector from the inner vessel-to-baffle space.
  A sealed rectangular sleeve crosses the cold passage and concrete well wall.
  It does not open the reactor pressure vessel.
- A fixed annular closure seals the air passages at the top. There is no forced
  cooling-air space above the pressure caps; the six cassettes provide insulation.

The provisional side stubs retain 2 m outside diameter and 20 mm wall. Local
azimuths are 90° hot and 210° cold; installation rotation makes these 135° and
255°. The side plenums are 1.4 m radially × 3.6 m tangentially × 2.3 m high.
Clear wall mouths are 3.20 × 1.05 m at Z=5.55 m. Their geometry is illustrative:
transition losses, circumferential flow distribution, natural draft, structural
well openings and heat-removal performance have not been sized or qualified.

Air checks verify open central supply/return rays, a closed cold-side baffle,
and a hot-side baffle opening with a sleeved crossover. Cover checks verify the
six copies, representative cap-hook clearances during a vertical lift, and
side-air/coolant nozzle surface separation. These are selected geometric checks,
not a complete extraction or thermal qualification.

### Build the current revision

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/prepare_reactor_cover.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_reactor.py -- --draft --views air-system air-section
/Applications/Blender.app/Contents/MacOS/Blender --background \
  outputs/reactor-study/wistr-reactor-study.blend --python-exit-code 1 \
  --python scripts/check_reactor_cover.py
```

Build `scripts/build_tgrid_cover.py` first if its generated source is absent.
`prepare_reactor_cover.py` exports a compact, driver-free asset with outward
normals. The standalone editable cassette is preserved. `refresh_reactor_cover.py`
can refresh only the fitted covers in an already-built current reactor and updates
the working manifest; use a full reactor build after changing air or vessel geometry.

Current fitted mesh estimate: **2099 kg per cassette**, plus **298 kg** for all twelve thermal inserts. Additive volumes and provisional densities; unfinished details omitted.

For section views, individual closed frame members remain separate instead of cutting an overlapping aggregate. Evaluated fitted-cover bounds were checked in the isolated and installed orientations to guard against Boolean artefacts.


### Hot-air collector insulation allowance

The working reactor now wraps the hot side plenum, sealed crossover and stub in
100 mm provisional insulation with 1 mm metal cladding, coordinated with the
[installation hot-air insulation](installation.md#hot-air-insulation-allowance--11-october-2026).
The well/baffle openings accommodate the wrap while retaining the duct's flow
opening. This is a visual allowance; cold-annulus obstruction, thermal bridges,
heat loss and flow distribution require analysis. The committed 11 October
checkpoint remains unchanged.
