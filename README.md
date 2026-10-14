# fastSaltModels

Python-authored WISTR reactor and Fast Salt System installation models rendered with Blender. This repository was formerly named `TextualGraphics`; its Git history and baseline files are retained. The internal Python package remains `textual_graphics`.

The sibling [fastSalt project hub](../fastSalt/README.md) owns shared design documentation, calculations, publications, and decisions. Start with its [project status](../fastSalt/STATUS.md) for current priorities.

## Choose the work

| Work | Instructions | Definition and builder |
| --- | --- | --- |
| Detailed WISTR reactor | [Reactor study, handling, controls, and checks](docs/reactor-study.md) | [Parameters](models/wistr_reactor.py), [builder](scripts/build_reactor.py) |
| Removable reactor insulation cover | [Six-sector cassette and sliding-hook study](docs/insulation-cover.md) | [Parameters](models/wistr_insulation_cover.py), [builder](scripts/build_insulation_cover.py) |
| Five-level T-grid cover — current draft | [Design and sections](docs/tgrid-insulation-cover.md) | [Parameters](models/wistr_tgrid_cover.py), [builder](scripts/build_tgrid_cover.py) |
| Rigid-block cover alternative | [Comparison and structural screening](docs/rigid-insulation-cover.md) | [Parameters](models/wistr_rigid_cover.py), [builder](scripts/build_rigid_cover.py) |
| Overall installation | [Layout, cameras, and assumptions](docs/installation.md) | [Parameters](models/wistr_installation.py), [builder](scripts/build_wistr.py) |
| Attached control annex — latest site draft | [Placement, views and checks](docs/control-annex.md) | [Parameters](models/wistr_control_annex.py), [builder](scripts/build_control_annex.py) |
| Coolant P&ID, exterior nitrogen and lowered transfer piping — source draft | [Coverage and checks](docs/coolant-pid-3d.md) | [Parameters](models/wistr_coolant_pid_draft.py), [builder](scripts/build_coolant_pid_draft.py) |
| Compact shared-wall tank enclosure — preceding draft | [Layout and checks](docs/compact-services-draft.md) | [Parameters](models/wistr_compact_services_draft.py), [builder](scripts/build_compact_services_draft.py) |
| Shared-wall service annex and coolant silo — preceding draft | [Layout and checks](docs/attached-services-draft.md) | [Parameters](models/wistr_attached_services_draft.py), [builder](scripts/build_attached_services_draft.py) |
| Attached coolant tank bay and three-item laydown — preceding draft | [Layout and checks](docs/tank-bay-draft.md) | [Parameters](models/wistr_tank_bay_draft.py), [builder](scripts/build_tank_bay_draft.py) |
| Site with turbine and fuel preparation | [Site envelopes and interfaces](docs/site-study.md) | [Parameters](models/wistr_site.py), [builder](scripts/build_site.py) |
| Horseshoe fuel-handling study | [Dimensioned plan and reference basis](docs/fuel-handling-study.md) | [Parameters](models/fuel_handling_layout.py), [drawing generator](scripts/draw_fuel_handling_plan.py) |
| Python assembly authoring and TOML exchange | [Model structure, examples and checks](docs/assembly-models.md) | [Coolant authoring](models/coolant_assembly.py), [resolver](scripts/resolve_coolant.py) |
| PMS examples and motion | [Adapter, playback, supported objects, and tests](docs/pms-adapter.md) | [Python package](src/textual_graphics/) |

The isolated reactor includes the developed sector handling and removable tube plugs. The workshop installation imports the current working reactor with six fitted insulation covers and side air plenums at full scale, with three insulated coolant pairs routed to the illustrative steam-generator envelopes. The current 42 m draft uses conditional Hurmet pipe bore/wall/insulation dimensions; the installation copy of its nozzle sleeves is adapted to match. The current installation adds catwalk-level laydown bays for one insulation cover and sector cap, with a mobile sector canister/cart replacing fixed sector storage. It uses an internal insulated hot-air header for generators and fuel tanks, a direct reactor exhaust to an aligned stack, and, in the current composed site, an internal floor-level steel fresh-air duct with three outdoor intakes, centered generator-side valve boxes, and a complete wall-column layout. The [site draft](docs/site-study.md) now includes [illustrative motor-BFP machinery detail](docs/turbine-equipment.md) in a provisional 60 × 40 × 28 m turbine hall with electrical annex and withdrawal aprons; adjacent off-gas and fuel refining/recycling buildings are 5 m tall, with a separate 20 × 15 × 8 m converter envelope beyond them. The shared reactor duct carries fuel supply and return together in a common heated, insulated jacket alongside coolant and gas lines. Six low, commonly insulated and heat-traced fuel pairs now link a fuel valve-box reservation to all six maintenance tanks, with a separate coolant line to the storage-tank bottom. Three pressure servers now service the maintenance-tank pairs via 25 mm gas tubes; paired gas headers use the shared duct, and the nitrogen skid feeds the off-gas building from its new position beside it. A [main internal piping draft](docs/turbine-piping.md) adds steam, reheat, condensate and feedwater routes with explicit clearance and maintenance limitations. Airflow sizing and external plant equipment remain to develop.

## Open existing models

Latest complete site: [attached control annex](outputs/site-control-annex/fast-salt-control-annex.blend), with [exterior, interior and site views](docs/control-annex.md).

Preceding layout variant: [coolant P&ID and lowered transfer piping](outputs/site-coolant-pid/fast-salt-coolant-pid.blend), with a [coverage and review guide](docs/coolant-pid-3d.md).

Preceding layout variant: [attached coolant tank bay](outputs/site-tank-bay-draft/fast-salt-tank-bay.blend), with a separate [three-item maintenance placement](outputs/site-tank-bay-draft/maintenance-laydown.blend). See [the draft guide](docs/tank-bay-draft.md) for the composition workflow and remaining access/handling checks.

For ongoing work, open [the reactor scene](outputs/reactor-study/wistr-reactor-study.blend) or [the current installation draft](outputs/installation-under-cover-bundles/wistr-installation.blend) in Blender. These links refer to locally generated outputs, which are excluded from Git and must be generated on a fresh checkout.

For a reproducible review snapshot, use the preserved baselines below. The latest visual checkpoint is the 2026-10-12 turbine equipment snapshot below. Commit `0d981f2` preserves the earlier reactor handling and tube-plug baseline.

| Baseline | Contents |
| --- | --- |
| [2026-10-12 turbine equipment](baselines/turbine-equipment-2026-10-12/) | Accepted machinery detail, complete site, three equipment views, checked reports and hash manifest |
| [2026-10-12 site and services](baselines/fast-salt-site-2026-10-12/) | Accepted complete site, process connections, internal fresh-air duct, low generator inlets, checked report and hash manifest |
| [2026-10-12 maintenance and utilities](baselines/wistr-maintenance-2026-10-12/) | Accepted installation, maintenance/utility views, geometry report and hash manifest |
| [2026-10-12 service bundles](baselines/wistr-service-bundles-2026-10-12/) | Accepted installation scene, normal/inspection views, geometry report and hash manifest |
| [2026-10-11 insulated installation](baselines/wistr-insulated-installation-2026-10-11/) | Reactor, installation and standalone cover scenes, draft views, reports and hash manifest |
| [2026-10-08 handling and plugs](baselines/wistr-reactor-handling-2026-10-08/) | Latest preserved reactor scene, geometry report, lifting animation, and hash manifest |
| [2026-10-07 tubing](baselines/wistr-reactor-tubing-2026-10-07/) | Earlier tubing and service-routing snapshot |
| [2026-10-07 initial reactor](baselines/wistr-reactor-2026-10-07/) | Initial snapshot with the historical 3.6 m core; tag `wistr-reactor-baseline-2026-10-07` |

Routine outputs were cleaned on 12 October 2026: only the latest installation, reactor, T-grid cover and site outputs, plus the PMS examples, remain. Earlier working-output links in historical design notes may no longer resolve; committed baselines remain intact.

## Build and verify

Run commands from this repository root. Blender's Python supplies the required Blender modules; the static models do not require a PMS simulation. Build the standalone cassette and prepare its fitted asset first, as described in the [reactor integration guide](docs/reactor-study.md#build-the-current-revision).

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_reactor.py
```

For the installation, substitute `scripts/build_wistr.py`. The detailed guides describe selected views and draft rendering. Builders produce scenes, images, and geometry-check reports in `outputs/`.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python tests/test_blender_adapter.py
```

## File ownership

- `models/`: editable Python definitions and assumptions.
- `scripts/` and `src/`: scene generation, checks, and PMS adapters.
- `references/`: preserved source drawings.
- `baselines/`: preserved review snapshots and manifests; create a new snapshot for a new baseline.
- `outputs/`: generated working files and renders, excluded from Git.
- `docs/`: detailed usage and model notes.

These models provide geometry and visualization. Mass properties, load capacity, and agreement with university analysis models remain separate engineering work. Source assumptions and the scope of existing geometry checks are documented in the guides and reports.
