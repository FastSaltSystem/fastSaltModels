# Turbine equipment detail draft

12 October 2026. The turbine hall now has illustrative machinery exteriors in place of opaque equipment boxes. The existing 60 × 40 × 28 m hall, equipment reservations, cycle sizing and pipe terminal coordinates are retained. This is a visual definition for review and presentation, not supplier or fabrication geometry.

Accepted checkpoint: [12 October turbine equipment baseline](../baselines/turbine-equipment-2026-10-12/), preserved separately from working outputs.

## Current views

- [Machinery and main piping](../outputs/site-45-bends/site-turbine-machinery.png)
- [Turbine and generator trains](../outputs/site-45-bends/turbine-trains-detail.png)
- [Ground-level equipment](../outputs/site-45-bends/turbine-ground-equipment.png)
- [Complete site in Blender](../outputs/site-45-bends/fast-salt-site.blend)
- [Equipment detail report](../outputs/site-45-bends/turbine-equipment-detail.json)

The train and ground-equipment views omit external piping to expose the casings. The train inspection view uses a display plane at the machine-base elevation; this does not add an upper deck to the site model. The combined view retains the complete modeled main circuits. The site file is saved with the turbine camera selected and upper machinery visible.

## What is represented

| Equipment | Exterior detail |
| --- | --- |
| HP, IP and three LP turbine casings | Split casing flanges and bolts, casing ribs, bearing pedestals, shafts, bedplates; LP exhaust skirts |
| Two generators | Main housings, end bearings, top cooler enclosures/grilles and terminal housings |
| Three motor-driven boiler feed pumps | Pump barrels, motors, coupling guards, base skids and mounting feet |
| Three condensate pumps | Vertical pump/motor bodies, guards and motor cooling fins |
| Four reheaters and seven feedwater heaters | Horizontal shells, end covers/flanges, jacket bands, saddles and nozzle connections |
| Three condensers | Shells, water boxes, access covers, hotwells, stiffeners and feet |
| Two deaerator/storage reservations | Horizontal drums, end covers, jacket bands and saddles; deaerator internals remain unspecified |

The electrical annex remains a building reservation. Each equipment item has a hidden wireframe reservation in the **Turbine equipment reservations** collection. Show this collection to compare exterior detail with the original space allowance.

Both turbine-generator shaft trains share a provisional shaft elevation of 15.2 m above the hall floor. Five guarded couplings bridge the existing gaps between adjacent machines. This elevation and the modeled coupling dimensions are visual allowances, not a rotor-dynamics or alignment design.

## Checks and limits

The builder checks all detail mesh vertices against the original equipment reservations, including 61 local connections to the unchanged external pipe terminals. The 29 mechanical equipment items plus electrical annex contain 697 component meshes; five coupling assemblies add ten meshes in the existing shaft gaps. Coupling checks verify two intended neighboring machines, clearance from other equipment reservations and conservative clearance to pipe centerline capsules. Existing routing checks still apply to the main circuits.

All upper machinery, coupling guards and labels carry the upper-level visibility flag, so the existing plan and turbine views remain consistent. The original bounding boxes are hidden independently and do not reappear when upper machinery is enabled.

The generic bolts, bearings, support saddles, shell profiles and nozzle bodies are illustrative. They do not establish masses, pressure ratings, insulation requirements, actual motor sizes or vendor service clearances. Upper-level structural support, LP exhaust transitions to condensers, cooling-water circuits, heater extraction/drain circuits and detailed auxiliaries remain to develop. The existing 4.70 m feedwater-pipe clearance over the nominal 5 m cross-aisle reservation remains an open routing issue, as recorded in [the piping guide](turbine-piping.md).

## Rebuild

Run from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python scripts/build_site.py -- --output outputs/site-45-bends --with-piping --build-only --view turbine
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python scripts/render_turbine_detail.py
```

The first command rebuilds and checks the complete site. The second independently regenerates the same machinery and main piping for three inspection PNGs and a detail report; it does not overwrite the site Blender file. Inputs are [the existing layout](../models/turbine-layout.json), [pipe routes](../models/turbine_piping.py) and [the equipment builder](../scripts/turbine_equipment.py).
