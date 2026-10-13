# Python authoring, resolved documents and Blender

13 October 2026. The first migrated assembly is the three main coolant legs: reactor connection interface, three steam generators, three pumps and nine pipe segments. This follows the PMS authoring pattern while using a separate static-graphics schema.

**Python assembly builder → detached resolved document → Blender**, with **TOML export/import** available between the last two steps. Writing a file is optional; the direct dictionary and TOML paths produce the same geometry.

## Sources and responsibilities

| Layer | File | Responsibility |
| --- | --- | --- |
| Geometry dimensions and layout choices | [wistr_installation.py](../models/wistr_installation.py) | Current geometry inputs and provisional assumptions |
| Assembly authoring | [coolant_assembly.py](../models/coolant_assembly.py) | Repetition, hierarchy, named ports, nozzle assignment and geometric route rules |
| General static assembly API | [assembly_model.py](../src/textual_graphics/assembly_model.py) | Compose local frames, resolve port positions, detach documents, validate and exchange TOML |
| Blender adapter | [coolant_scene.py](../src/textual_graphics/coolant_scene.py) | Create existing pump and pipe geometry from resolved data |
| Generator geometry | [build_wistr.py](../scripts/build_wistr.py) | Consume resolved generator placements and geometry parameters |
| Resolved working document | [coolant.resolved.toml](../outputs/coolant-assembly/coolant.resolved.toml) | Generated, inspectable snapshot; excluded from Git |

Edit Python to express the 3D design intent. Generated TOML is a delivery and inspection format, not a second source that must be edited in parallel. The [shared coolant engineering source](../../fastSalt/design/engineering/README.md) now supplies main-circulation topology, IDs, pipe dimensions and pump inputs to both this builder and the P&ID (D-053). The [P&ID view TOML](../../fastSalt/design/pids/coolant-system/coolant-system.toml) retains diagram-specific data and unmigrated systems.

The current builder takes visual generator/pump envelopes from the graphics definition, engineering dimensions and duties from the shared source, and reactor terminals from the manifest-verified reactor report. It records source hashes when called with the repository path. The optional P&ID check compares seven equipment tags, six main lines, dimensions and flow endpoints. It reports disagreement instead of silently choosing which repository is correct. No new sizing values are introduced.

## Authoring example

```python
from textual_graphics.assembly_model import Model, document, write

model = Model("Example assembly")
model.component("plant")
model.component("leg", parent="plant", rotation_deg=(0, 0, 120))
model.component("pump", "pump", parent="leg", position=(8, 0, 1))
model.port("pump", "discharge", (0.5, 0, 0), direction=(1, 0, 0))
model.component("receiver", parent="leg", position=(12, 0, 1))
model.port("receiver", "inlet", (0, 0, 0), direction=(-1, 0, 0))
model.connect("delivery", "pump.discharge", "receiver.inlet", frame="leg")

resolved = document(model)       # Detached copy; contains literal data only.
write(resolved, "outputs/example.resolved.toml")
```

The generic example demonstrates description and resolution. Rendering a new equipment kind requires a corresponding geometry builder; `kind="pump"` alone does not define its shape. The coolant model supplies the necessary equipment parameters.

Components have explicit parents. Local frames use metres, Z up and XYZ Euler angles in degrees, composed as `Rz @ Ry @ Rx`; the resolved document contains world positions and rotation matrices. Ports carry local positions and outward direction vectors. A connection resolves its endpoint positions from the named ports, with intermediate route controls expressed in the selected frame.

`place_port_at(owner, port, target)` translates one component to meet another port while retaining its orientation. It does not solve a rotational or dynamic constraint. Repetition and more complicated placement rules stay in Python. `document(model)` returns a deep, detached copy: editing that copy does not modify the authored model.

Pipe geometric point order and fluid direction are distinct. The existing cold-return curve is retained in reactor-to-pump order to preserve its geometry, but its `flow_from` is the pump discharge and its `flow_to` is the reactor cold port. The P&ID comparison checks actual fluid direction.

The first Blender adapter preserves existing world-space assembly roots and object names because existing installation checks and service builders refer to them. Parent relationships from the semantic model are retained as metadata (`model_parent`), while geometry children keep their Blender parents. The generic model resolves full 3D frame rotations; the existing pump/generator renderer explicitly supports Z-axis placement rotations only and rejects tilted placements.

## Build without Blender

Python 3.11+; no additional package installation:

```sh
python3 scripts/resolve_coolant.py
python3 scripts/resolve_coolant.py \
  --pid-model ../fastSalt/design/pids/coolant-system/coolant-system.toml
python3 -m unittest discover -s tests -p test_assembly_model.py -v
```

The output is `outputs/coolant-assembly/coolant.resolved.toml`. It contains 11 components, 18 ports and nine route segments. The schema rejects inconsistent world/local data, disconnected endpoints, zero-length segments, cyclic parents and unsupported literal values. TOML import reads data only; it does not evaluate Python or expressions. This graphics exchange contains no unresolved values. The P&ID's `unresolved_fields` convention belongs to that separate document schema.

## Use the resolved document in the installation

The normal installation build now resolves the Python coolant model once, supplies that document to the coolant and generator renderers, and saves `coolant.resolved.toml` beside its outputs. To reuse an already generated document:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_wistr.py -- --build-only \
  --coolant-model outputs/coolant-assembly/coolant.resolved.toml \
  --output outputs/coolant-architecture-installation
```

Other installation systems still use the existing Python layout, so changed coolant placements must also satisfy their interface and clearance checks. A resolved file is not an automatic whole-plant redesign mechanism.

Blender integration check:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python tests/test_coolant_scene.py
```

It compares direct-document and TOML-imported meshes, verifies named ports against pipe endpoints and actual generator manifold mouths, and saves an equipment-only inspection scene to `outputs/coolant-assembly/coolant-equipment.blend`. That scene contains the three generators, pumps and main pipes; the reactor is represented by its connection interface in the document. The full installation scene retains the detailed reactor.

## Verification and migration scope

Eight plain-Python checks cover detached copies, nested rotations, geometric mating, missing/duplicate references, hierarchy cycles, real-model TOML round trips, reconnection after placement changes and tampered routes. Blender checks confirm identical direct/TOML geometry and endpoint agreement within 0.00001 m.

A one-time comparison against the pre-refactor coolant and generator functions retained all 117 mesh names and topology counts, with maximum world-bound difference 0.000002282 m and route controls agreeing within 0.00001 m. The [comparison report](../outputs/coolant-assembly/legacy-comparison.json) and [integration report](../outputs/coolant-assembly/assembly-check.json) are working outputs. The full installation also builds from the exported TOML and passes its existing equipment, piping, integration and selected clearance checks; its separate working output is `outputs/coolant-architecture-installation/`. These are document/geometry checks, not pressure, thermal, load or flow validation.

This is the first migration, not a conversion of the entire plant. Storage/transfer piping, reactor internals, fuel/absorber services, air systems and the turbine hall remain in their existing builders. Existing baselines are preserved. PMS itself is unchanged; its simulation schema is not replaced by this visual assembly schema. Future Lua or Julia authors could emit the same resolved TOML, but no such authoring bindings are implemented here.


## Shared engineering dependency — D-053

Keep `fastSalt` beside this repository, or set `FAST_SALT_HUB` to its path. The adapter fails clearly if the shared package is missing or a referenced worksheet has changed. Review and explicitly adopt new worksheet results before updating hashes. Geometry placement tags are explicit, so reordering shared TOML tables cannot exchange equipment locations. The graphics author reads flow connections from the shared model; unsupported new topologies require adapter/layout changes. Existing port aliases and object names remain stable.

Six additional checks in `tests/test_shared_coolant.py` exercise an actual source-file edit through both consumers, ordering stability, units, references, overrides and stale sources. The migrated resolved components, ports and routes match the preceding version exactly. Working full-installation verification output is `outputs/shared-coolant-installation/`. See the hub guide for editing responsibilities and the remaining Hurmet/simulation adapter work.
