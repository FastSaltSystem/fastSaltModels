# Absorber system geometry review

15 October 2026. See the [P&ID and capacity assessment](../../fastSalt/design/pids/absorber-system/README.md) for D-070.

The [current review scene](../outputs/absorber-review/fast-salt-absorber-review.blend) raises all six absorber tank bottoms by 0.30 m to the active-core bottom, Z = -7.27 m. Their upper boundary stays at -3.62 m. The active core remains 3.4 m high. No bottom-reflector volume is included in the absorber liquid chamber.

The canonical generator in `reactor_geometry.py` now uses `core_z` for the absorber bottom. [The overlay builder](../scripts/build_absorber_review.py) applies that change to the saved complete site while preserving the earlier control-annex scene. [Checks](../outputs/absorber-review/checks.json) verify all six new bottoms and unchanged tops.

External salt lines are to enter at the chamber bottoms, per owner instruction. Those lines, separate primary/secondary internals, and the absorber support arrangement remain to model. Existing top tube terminations remain placeholders. The module's two gas vessels and compressor also need an internal layout before resizing its external envelope.

[Read-only audit](../scripts/audit_absorber_system.py) measures the preceding scene. Its source hash and reduced geometry evidence are retained with the hub calculation. The original scene has 3.95 m absorber tanks; the current bottom revision reduces the visual absorber tank height to 3.65 m, including the provisional upper gas region.

Build from repository root with Blender: `--background --python-exit-code 1 --python scripts/build_absorber_review.py`. No commit or binary baseline is created automatically.

## Separate presentation illustration

The [stacked module illustration](absorber-stack-illustration.md) places a pressure-tank shape above a surge-tank shape, with a control box on top. This unscaled prop has symbolic exterior stubs only and does not replace any equipment in the site model.
