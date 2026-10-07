# TextualGraphics

Python-authored engineering models rendered with Blender. The first adapter
reads a detached `Sim3D.document(model)` from PracticalMechanicalSimulation
(PMS), retaining its qualified object names and local reference frames.

## Static WISTR installation

### Approved reactor baseline — 2026-10-07

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

### Isolated reactor review

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
service tubes.
Opening radius is approximately 2.667 m, allowing at least 100 mm radial clearance
around the raised core and 20 mm around the conservative raised tube envelope.
The spider outer band is narrowed to provide this continuous circular opening.
Peripheral/bottom reflectors and separators stay below
this opening. The cap plate radius is approximately 2.682 m, including its
15 mm overlap onto the spider band. Its outer arc is smooth.
Plate tops remain at Z=6.57 m.

Each absorber carries two pairs of tubes, each with one 25 mm and one 50 mm OD
tube (24 tubes total). Across the hot plenum, the four lines are stacked at
55 mm pitch, with the lowest centreline 250 mm above the plenum floor. Near the
wall they spread into four side-by-side risers at 60 mm pitch, with
individual passages through the enlarged spider. Provisional saddles provide
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
crossings. Only after meeting do the pairs fan into the existing cap opening.
The six cap risers lie at radius 1.95 m and terminate 100 mm above the cap.
The enlarged circular spider opening clears the raised radial tube row during
vertical core withdrawal, with a provisional 20 mm allowance around its
conservative envelope. Larger circular caps cover this opening; local spider
reliefs and matching cap extensions have been removed. The cap-edge tube
penetration notches and absorber tube passages through the ring remain.
`reactor-core-tubes.png` hides the core to expose the stacked edge runs and slot.
External connections and disconnections are not modeled.

Checks cover counts, diameters, open bores, closed pipe walls, reflector/cap
notches, tube separation and spider passages. The complete tube projection
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

### Overall installation

The installation is authored directly in Python and needs no PMS simulation.
`models/wistr_installation.py` holds its layout parameters and assumptions;
`scripts/build_wistr.py` constructs reusable, named visual assemblies with the
geometry helpers in `src/textual_graphics/static_scene.py`.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_wistr.py
```

Use `-- --draft` for half-resolution previews, or, for example,
`-- --views cutaway equipment` to render selected views. Default output is
`outputs/wistr/`:

- `wistr-installation.blend`: editable metric scene, opening in the cutaway view.
- `wistr-cutaway.png`: building shell, lower level and equipment overview.
- `wistr-plan.png`: top-view arrangement with shell and crane hidden.
- `wistr-equipment.png`: closer view with shell, crane and stacks hidden.
- `wistr-model-report.json`: named assemblies, counts, dimensions, source hash,
  geometric opening checks and presentation assumptions.

The source sketch is preserved unchanged at `references/reactor-building-v1.svg`.
Its 28.4 m building diameter and 34.2 m / 9.7 m height labels are used with the
interpretation recorded in the model. Steam-generator casings use the owner's
approximate 4 × 4 × 10 m dimensions. Other sizes and precise equipment positions
are illustrative and should be refined through review.

The scene contains three steam generators, six fuel-storage tanks in three
pairs, a closed reactor vessel, coolant and sector storage, three perimeter
stacks, and a circular overhead crane. Exterior details include panel joints,
inspection covers, ladders, catwalks, guard rails, flanges, lifting bars and
support plinths. Pipe and duct shapes indicate the supplied connection layout;
their routing and dimensions are editable presentation geometry.

The front half of the shell and dome, a front deck wedge and storage-bay floor
openings expose the lower level. The operating deck and perimeter walkway have
separate, non-overlapping meshes. Build-time ray checks confirm the central,
storage-bay and front openings remain open after Boolean operations.

Each major object is an empty coordinate frame with named child geometry,
`assembly_id` metadata, and a corresponding Blender collection. These frames
have no masses, joints, forces or motion. The reactor vessel and storage units
use closed exterior envelopes; internal process/core geometry is not included.

The saved cameras are `View.Cutaway`, `View.Plan` and `View.Equipment`. For manual
alternate views, hide the **Shell** and **Crane** collections (and **Stacks** for
the equipment view), and show the matching **Annotations** collection. The build
script applies these choices automatically for each exported image.

## First demonstration

The spatial double pendulum comes directly from PMS's existing Python example.
It is not rewritten here. Its two boxes are 1.00 and 0.80 metres long and
0.08 metres wide/deep. Their joint markers meet at x = 0 and x = 1 metre;
the free end is at x = 1.8 metres.

On this Mac, run from this project directory:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/render_pms.py -- \
  --pms-root ../PracticalMechanicalSimulation
```

Requires Blender with Python 3.11+ and the PMS 0.3.0 source checkout. No pip
installation, Julia process, or third-party Python dependency is required.
The demo adds the chosen checkout's `python/src` to its process's import path.
It executes that checkout's trusted Python example to construct the model.
`--pms-root` defaults to the sibling checkout, or to the
`PRACTICAL_MECHANICAL_SIMULATION_ROOT` environment variable when set.

Outputs (regenerated on each run, excluded from source control):

- `outputs/double-pendulum.png`: presentation rendering.
- `outputs/double-pendulum.blend`: editable scene with **PMS Model** and
  **Presentation** collections; the latter contains lighting, camera, text,
  backdrop, and marker inspection dots.
- `outputs/double-pendulum.model.json`: expanded Python document snapshot for
  inspection, not an authoring format.
- `outputs/double-pendulum.report.json`: source path, PMS/Blender versions,
  model hash, world positions, graphics names, and omitted mechanical elements.

Use `--output-dir /path/to/output` to choose another destination. The rendering
script starts a new scene in its process; run it in background mode as above.
The reusable adapter itself adds a collection without deleting existing objects.

## Supported model subset

- Spatial, literal primitive documents; nested namespaces preserve qualified names.
- Rigid-body reference origins and ground/body markers, with body-local placement.
- Axis-angle rotations (radians, `deg`, or `°`) and proper 3x3 rotation matrices.
- Explicit boxes, including named graphics and graphics placed on an owner marker.
- Marker `xy_frame` graphics: three colored arrows and a translucent plane.
  Their label is preserved as Blender metadata; the demo supplies presentation text.
- Explicit visibility, box opacity, and a small color vocabulary: `steelblue`,
  `darkorange`, `white`, `black`, `red`, `green`, `blue`, `gray0`–`gray100`,
  `#RRGGBB`, or three sRGB values in [0, 1].

PMS coordinates are preserved directly in Blender (metres, no axis conversion).
The example uses Y as its vertical/gravity axis. Boxes remain centered on the
authored reference frame even when a separate center-of-mass marker exists.
Frames are Blender empties; visual objects carry `pms_name` and `pms_owner`
custom properties. Parent links retain marker/body relationships.

The first static demonstration shows the **authored initial pose**, not a solver-corrected pose or a simulated
trajectory. Joints, loads, and analysis settings do not generate geometry;
the report lists skipped mechanical elements. The adapter does not infer a
body's shape from its mass or inertia. Bodies without explicit shapes remain
frames only. Unsupported explicit shapes, flexible beams, and unexpanded
assemblies raise errors. PMS expression/assembly expansion and general loader
validation remain outside this adapter. The initial interface is intentionally
limited to documents like the checked example, not arbitrary PMS inputs.

## Verification

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python tests/test_blender_adapter.py
```

The Blender integration tests check composed rotations, body/marker placement,
reference-origin versus CM semantics, named/hidden graphics, and explicit error
cases. The demo separately checks its actual box dimensions and joint-marker
coincidence before writing the scene and rendering.

The Codex sandbox on this Mac prevents Blender's graphics-device detection;
these Blender commands need to run outside that sandbox, including CPU renders.

## Simulation playback and detailed geometry

The motion demonstration runs the unchanged spatial Python double-pendulum
example in PMS, then shows its basic geometry beside a detailed visual assembly.
Each link's rails, braces, end bosses, bearings, rings, bolts, and badge attach
to that link's animated body-reference frame. These 54 visual objects contribute
no solver mass, inertia, constraints, or forces. Decorative link assemblies
are separated in depth to avoid overlapping bearing faces at the elbow.

From this project directory, prepare the result with a Python 3.11+ interpreter
and Julia on PATH:

```sh
python3 scripts/prepare_motion.py --pms-root ../PracticalMechanicalSimulation
```

The preparation command writes all generated files beneath `outputs/motion`.
It uses PMS's own Julia result reader and viewer exporter to reconstruct
**body-reference** pose tracks from the `.simp` file, including the stored CM
offsets. It also extracts the model embedded in that same result, avoiding a
mismatch with subsequently edited source models. Blender needs no HDF5 Python
package or Julia interpreter loaded into its process. Use `--reuse-result` to
repeat the export without running the simulation again.

Render and save the comparison:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/animate_pms.py -- --animation
```

Omit `--animation` to generate only the still preview and editable scene.
`--input-dir` selects another prepared output directory; `--fps` defaults to 30.
The rendering example itself is specific to the double pendulum. The reusable
motion sampler and baker live in `src/textual_graphics/playback.py`.

Outputs:

- `double-pendulum.simp`: completed four-second simulation, with 241 output samples.
- `double-pendulum.motion.json`: PMS's versioned SimpView 4 export.
- `double-pendulum.model.json`: the exact input model embedded in the result.
- `double-pendulum-motion.mp4`: original and detailed geometry animated together.
- `double-pendulum-motion.blend`: editable, keyframed Blender scene. Press Space
  over the 3D viewport to play; **Render → Render Animation** regenerates the movie.
- `comparison.png`: still at half a second of simulated motion.
- `playback.report.json`: per-frame verification maxima and result provenance.
- `provenance.json`: source example, PMS version, and SHA-256 of the result file.

The movie covers timestamps 0–4 seconds at 30 fps, including both endpoints
(121 frames). Named `body_frame:` tracks contain reference-frame origins and
orientations, rather than inertia-ellipsoid axes. The sampler converts PMS's
`[x,y,z,w]` quaternions to Blender's `[w,x,y,z]`, handles equivalent quaternion
signs, linearly interpolates positions, and uses spherical interpolation for
rotations. Each movie frame is baked explicitly. Blender's between-frame curves
are linear in quaternion components; regenerate at a new fps for accurate
sampling at that frame rate. Ground and marker attachment offsets remain fixed.

Both views have separate presentation offsets. Validation removes those offsets
and compares their animated body frames, all attached detailed objects, and
joint-marker coincidence at every movie frame. This verifies the graphics
connection, not the physical accuracy of the mechanical model. The asset shapes
are illustrative and do not update the model's physical properties.

Run the additional tests with:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python tests/test_playback.py
```

These check known 90-degree midpoint rotation, quaternion sign continuity,
constant packed tracks, local marker/mesh inheritance, missing body bindings,
multiple result choices, and invalid data. A real-result integration check runs
when the exported example is present. Multiple PMS result choices require
explicit selection through `Motion(document, choice="Dynamic")`.

The Julia viewer export is an internal PMS facility, so this bridge is tested
against PMS 0.3.0 and SimpView document version 4. Other SimpView format versions
are rejected by the playback reader rather than silently interpreted.

`scripts/inspect_movie.py`, run through Blender in the same way as the test
scripts, decodes the finished MP4 and writes six sample frames plus a movie
verification report. This checks the encoded deliverable separately from the
scene's animation data.

## Next extensions

Add cylinders, indexed surfaces, and imported visual assets as actual
presentation models need them. Generalize the example's visual attachments into
reusable equipment assemblies. Flexible deformation needs a separate adapter;
the current playback applies rigid-body reference poses only.
