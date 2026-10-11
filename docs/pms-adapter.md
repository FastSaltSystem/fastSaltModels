# PMS adapter and playback

All shell commands and code paths below are relative to the `fastSaltModels` repository root.

[Repository overview](../README.md)

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
