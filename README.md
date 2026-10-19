# Fast Salt System models

Python and Blender models of the WISTR reactor, its maintenance equipment, and the surrounding power plant. This repository contains the editable geometry and selected visual checkpoints for the [Fast Salt System](https://github.com/FastSaltSystem/fastSalt).

**[Browse the model gallery](results/README.md)** · **[Open a saved Blender model](#open-a-model)** · **[Contribute](CONTRIBUTING.md)**

![Provisional plant layout with the reactor building, turbine hall and control annex](results/2026-10-15/control-annex/site.png)

*Control-annex site draft, 14 October 2026; published in the 15 October review snapshot. Roofs and walls are selectively hidden to show equipment. Building envelopes and equipment details are provisional.*

## Start here

| I want to… | Go to |
| --- | --- |
| See the plant, reactor, insulation and turbine equipment | [Model gallery with dated captions](results/README.md) |
| Understand the system and its P&IDs | [Project hub](https://github.com/FastSaltSystem/fastSalt) |
| Rotate and inspect a saved model | [Opening a Blender checkpoint](#open-a-model) |
| Modify a component or rebuild a scene | [Model source guides](#edit-and-build) |
| Suggest or contribute a change | [Contribution workflow](CONTRIBUTING.md) |

## Open a model

The gallery can be read without installing software. To rotate or inspect the geometry, install Blender and download a saved `.blend` file using **Download raw file** on its GitHub file page, then open it in Blender. These scenes were developed with Blender 5.2; other versions have not been verified here.

| Saved checkpoint | What it contains |
| --- | --- |
| [Complete site with turbine equipment — 12 October](baselines/turbine-equipment-2026-10-12/fast-salt-site.blend) | Reactor installation, turbine machinery and piping; approximately 65 MB. Predates the later tank bay and control annex. |
| [Reactor and insulation — 11 October](baselines/wistr-insulated-installation-2026-10-11/reactor/wistr-reactor-study.blend) | Isolated reactor with fitted insulation and side air connections. |
| [Maintenance installation — 12 October](baselines/wistr-maintenance-2026-10-12/wistr-installation.blend) | Maintenance and utility layout at that checkpoint. |
| [All preserved baselines](baselines/) | Earlier revisions, reports and hash manifests. |

Use the middle mouse button to orbit, the wheel to zoom, and Shift + middle mouse to pan. The Outliner controls which collections are visible. Cutaway views deliberately hide parts of the model.

The more recent control-annex **images** are published in the gallery. Its complete scene is generated locally at `outputs/site-control-annex/fast-salt-control-annex.blend`; it is not included in this review snapshot. The earlier downloadable model is labeled by its own date.

## Edit and build

Keep the two repositories beside each other when following workflows that consume shared inputs:

```sh
git clone https://github.com/FastSaltSystem/fastSalt.git
git clone https://github.com/FastSaltSystem/fastSaltModels.git
```

Run Blender scripts from the `fastSaltModels` root using Blender's Python. The static geometry does not require a PMS simulation. Some composed scenes read intermediate `.blend` files: follow the linked guide's prerequisite builds rather than assuming a fresh checkout contains `outputs/`.

| Work | Guide | Editable definition / builder |
| --- | --- | --- |
| WISTR reactor, sectors, handling and services | [Reactor study](docs/reactor-study.md) | [Parameters](models/wistr_reactor.py) / [builder](scripts/build_reactor.py) |
| Current five-level insulation cassette | [T-grid insulation](docs/tgrid-insulation-cover.md) | [Parameters](models/wistr_tgrid_cover.py) / [builder](scripts/build_tgrid_cover.py) |
| Reactor-building installation | [Installation](docs/installation.md) | [Parameters](models/wistr_installation.py) / [builder](scripts/build_wistr.py) |
| Site and turbine equipment | [Site study](docs/site-study.md), [turbine detail](docs/turbine-equipment.md) | [Site definition](models/wistr_site.py) / [builder](scripts/build_site.py) |
| Coolant P&ID tags and nitrogen routing | [Coolant coverage](docs/coolant-pid-3d.md) | [Parameters](models/wistr_coolant_pid_draft.py) / [builder](scripts/build_coolant_pid_draft.py) |
| Attached control annex | [Annex guide](docs/control-annex.md) | [Parameters](models/wistr_control_annex.py) / [builder](scripts/build_control_annex.py) |
| Python assemblies and TOML exchange | [Assembly models](docs/assembly-models.md) | [Coolant authoring](models/coolant_assembly.py) / [resolver](scripts/resolve_coolant.py) |
| PMS examples and motion | [PMS adapter](docs/pms-adapter.md) | [Python package](src/textual_graphics/) |

Other design variants remain in [docs](docs/) and the Git history. The former repository name was `TextualGraphics`; the Python package is still `textual_graphics`.

## Files and review status

- `models/`, `src/`, `scripts/`: editable geometry, builders and checks.
- `docs/`, `references/`: model explanations and preserved source drawings.
- `baselines/`: deliberately saved Blender checkpoints.
- `results/`: selected dated previews with provenance, viewable on GitHub.
- `outputs/`: local generated scenes and renders, ignored by Git.

The models describe visual geometry. Geometry checks do not establish structural, thermal, neutronics or equipment performance. Captions retain the date and scope of each view; the gallery is not one synchronized engineering release. Code and document licensing choices remain pending in the project hub.
