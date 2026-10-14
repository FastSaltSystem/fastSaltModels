# Compact shared-wall tank enclosure

14 October 2026 — D-066. Current architectural draft, superseding the [separate cylindrical enclosure](attached-services-draft.md). The owner confirmed that the straight enclosure wall is radial to the reactor building and parallel to a tangent of the tank.

## Review

- [Blender scene](../outputs/site-compact-services/fast-salt-compact-services.blend)
- [Plan](../outputs/site-compact-services/plan-draft.png), [cutaway](../outputs/site-compact-services/cutaway-draft.png), [enclosed annex view](../outputs/site-compact-services/exterior-draft.png)
- [Geometry and selected checks](../outputs/site-compact-services/compact-services-report.json)

The tank centre moves from (20.5, 20.5) to **(18.5, 18.5) m**, approximately 2.83 m toward the reactor. The 8.2 × 16 m bare tank and 350 mm insulation are retained. The nominal jacket-to-reactor-wall gap is **0.712 m**; support bands project slightly farther.

The enclosure uses the reactor's **R=21 m wall as its inner boundary**. A straight radial wall at approximately **31.18°** meets the curved outer wall tangentially. The curved wall retains 5.9 m inside radius, 0.35 m wall thickness and 19.5 m height; the enclosure is now a joined shape, not a freestanding cylinder. Its west boundary joins the fuel building at X=13 m. The existing fuel wall supplies the lower 5 m, with an upper extension beside the tank. No second wall is placed against the existing reactor wall.

Coolant preparation remains north of the tank, **5 m high**, extending to Y=36.5 m. Its west boundary shares the fuel-recycling building's existing east wall from approximately **Y=21.47 to 31 m**, a 9.53 m shared length; above Y=31 m it continues as an exterior wall. Coolant equipment moves together by (−2, −1.5) m from the prior draft. The receiving opening and apron remain on the north side. Off-gas/fuel partitions and process placeholders remain unchanged.

P-401 moves to **(20.5, 13.8) m**, on the tank's southeast side, with its reversible positive-displacement metadata retained. The heated, insulated 50 mm transfer piping is rerouted to the common bottom tee. The internal header crossing remains raised; its external drop is shortened to R=21.4 m. The preparation line still reaches the bottom tee directly at low level. Drainability and high-point gas handling remain unresolved from the earlier draft.

Fresh-air intake 2 moves from 33° to **125°**, between the main hot-air stack and nitrogen equipment. Its connecting duct, louver and both penetration tools move together. The former opening is closed by moving the Boolean tools. This is a requested layout placement; intake/exhaust recirculation has not been assessed.

## Checks and presentation

The builder checks tank/pump vertices against the reactor wall, radial wall, curved wall and west boundary; coolant equipment against its room; changed transfer routes against nearby evaluated geometry and one another, excluding deliberate terminals and the common tee; and intake housing envelopes against the stack, nitrogen skid and adjacent building. The main-circulation route fingerprint is unchanged. The first enclosure check gives approximately 0.226 m minimum clearance at the pump envelope. This does not establish maintenance access.

The cutaway hides the tall shared-wall display slice and near outer walls to expose the tank. Plan and exterior views show the attachment. The original reactor Shell collection is retained but hidden; Shared wall inspection displays slices of that same wall, not additional construction. Hide that display collection when showing the original full wall. Earlier source scenes and the maintenance laydown preview are retained.

Geometry checks are not structural, thermal, shielding, process or operational qualification. No hydraulic calculation inputs or source geometry hashes are changed.

## Rebuild

[Parameters](../models/wistr_compact_services_draft.py) and [builder](../scripts/build_compact_services_draft.py) form an overlay on the preceding attached-services scene. Build that scene first using its guide.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --python-exit-code 1 \
  --python scripts/build_compact_services_draft.py
```

Use `-- --build-only` to skip renders. `-- --resume --build-only` rechecks the generated checkpoint without rebuilding geometry; do not use resume after changing geometry or parameters. Outputs are ignored by Git. The owner accepted this draft for versioning on 14 October 2026. Generated models and renders remain local outputs; no new binary baseline is included.
