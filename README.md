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
| PMS examples and motion | [Adapter, playback, supported objects, and tests](docs/pms-adapter.md) | [Python package](src/textual_graphics/) |

The isolated reactor includes the developed sector handling and removable tube plugs. The workshop installation imports the current working reactor with six fitted insulation covers and side air plenums at full scale, with three insulated coolant pairs routed to the illustrative steam-generator envelopes. The current 42 m draft uses conditional Hurmet pipe bore/wall/insulation dimensions; the installation copy of its nozzle sleeves is adapted to match. The wider installation draft connects both reactor side ducts to conceptual exterior concrete fresh- and hot-air plenums and one stack. Airflow sizing and the external steam power plant layout remain to develop.

## Open existing models

For ongoing work, open [the reactor scene](outputs/reactor-study/wistr-reactor-study.blend) or [the current installation draft](outputs/installation-insulated/wistr-installation.blend) in Blender. These links refer to locally generated outputs, which are excluded from Git and must be generated on a fresh checkout.

For a reproducible review snapshot, use the preserved baselines below. The latest visual checkpoint is the 2026-10-11 insulated installation below. Commit `0d981f2` preserves the earlier reactor handling and tube-plug baseline.

| Baseline | Contents |
| --- | --- |
| [2026-10-11 insulated installation](baselines/wistr-insulated-installation-2026-10-11/) | Reactor, installation and standalone cover scenes, draft views, reports and hash manifest |
| [2026-10-08 handling and plugs](baselines/wistr-reactor-handling-2026-10-08/) | Latest preserved reactor scene, geometry report, lifting animation, and hash manifest |
| [2026-10-07 tubing](baselines/wistr-reactor-tubing-2026-10-07/) | Earlier tubing and service-routing snapshot |
| [2026-10-07 initial reactor](baselines/wistr-reactor-2026-10-07/) | Initial snapshot with the historical 3.6 m core; tag `wistr-reactor-baseline-2026-10-07` |

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
