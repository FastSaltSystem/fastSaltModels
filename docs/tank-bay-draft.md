# Attached coolant tank bay and three-item laydown draft

The [shared-wall annex and cylindrical silo draft](attached-services-draft.md) supersedes this square-bay arrangement while retaining its three-item laydown.

14 October 2026 — D-064. The owner requested moving TK-401 toward coolant preparation and selected an attached bay for this draft. The laydown must accommodate one insulation cover, one sector cap and one top reflector at the same time.

## Review files

- [Complete site with tank bay](../outputs/site-tank-bay-draft/fast-salt-tank-bay.blend)
- [Maintenance placement scene](../outputs/site-tank-bay-draft/maintenance-laydown.blend)
- [Tank-bay view](../outputs/site-tank-bay-draft/bay-draft.png), [plan](../outputs/site-tank-bay-draft/plan-draft.png), [three-item laydown](../outputs/site-tank-bay-draft/laydown-draft.png)
- [Dimensions, route coordinates and checks](../outputs/site-tank-bay-draft/tank-bay-report.json)

## Layout

The bay is **11 × 11 m**, with a provisional **19.5 m wall height**, attached to the south side of coolant preparation. Its centre is **(20.5, 20.5) m** on the common floor datum. The reactor building remains 42 m in diameter. A chamfered service corner receives the reactor transfer pipe; an east-side door is reserved for access. The bay roof and two nearer walls are hidden in the review cutaway, but remain in the model.

TK-401 uses the selected **8.2 m bare diameter × 16 m height**, with **350 mm insulation and 1 mm cladding**. The 8.902 m jacket leaves approximately **0.70 m** to the inside faces of the bay walls. The ladder allowance leaves **1.90 m** below roof level. These are spatial allowances, not a qualification of inspection access, tank construction, ventilation or structural capacity. Supports are provisional visual envelopes scaled with the tank.

The reversible P-401 envelope sits beside the tank bottom. The preparation liquid line now runs directly through the adjoining wall to the **common tee underneath TK-401**. The reactor-side discharge approaches that tee from the opposite direction, and a single vertical branch connects the tank bottom. The old separate preparation nozzle and long in-building preparation route are removed from this draft.

All these liquid lines retain **50 mm bare OD and 50 mm radial insulation**, representing heat-traced service. Most of the reactor transfer route is 0.40 m above the floor. A short crossing rises to **4.90 m above the floor** to clear the internal fresh-air and feedwater headers before descending beside P-401. The crossing creates a high point: gas handling, drainage of both legs, heating and operating procedures still require review. This geometry does not establish complete drainability. The previously defined coolant gas system is still a separate P&ID interface; its physical routing is not added here.

## Laydown

The platform grows by **0.40 m**, to **9.10 × 6.10 m**, retaining its catwalk elevation and northern aisle. The insulation cover keeps its own 4.35 × 4.30 m bay. A **3.60 × 3.20 m** shared tray holds the cap and top reflector, with the reflector rotated **180° in plan**. Both remain upright, with hooks above. Separate provisional seating pads carry each item on the common tray.

The inspection scene uses the actual evaluated component meshes, including their lifting hooks. Their projected outlines have approximately **0.139 m** separation. This demonstrates item fit, not clearance for the lifting tool, sling movement or a loaded crane path. The original narrow canister-door height margin is unchanged and remains provisional.

## Rebuild and review workflow

Parameters are in [wistr_tank_bay_draft.py](../models/wistr_tank_bay_draft.py). This is a composition layer over the current saved site: the earlier installation, site and accepted baselines are retained. The base builders continue to reproduce those earlier arrangements. Use this draft builder for the new bay and three-item laydown:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --python-exit-code 1 \
  --python scripts/build_tank_bay_draft.py
```

`-- --build-only` skips rendering. `-- --resume` reuses the generated geometry checkpoint for check/presentation edits only; rebuild without it after changing geometric parameters. `--source` can select the preserved 12 October turbine-equipment site snapshot when the working source is unavailable. Source-scene and parameter hashes are written to the report. Outputs are ignored by Git.

The generator checks the enlarged platform, aisle/bridge and straight canister approach; new route envelopes against nearby evaluated geometry; tank-envelope interference; bay dimensions; and actual projected component fit. Explicit tank/pump terminals and modeled vessel/well penetrations are treated as intended interfaces. The report contains individual near-clearance findings. Checks do not qualify pipe supports/stress, full plant interference, thermal performance, loaded handling or pressure protection. Main circulation-pipe geometry and hydraulic calculations are unchanged by this storage-layout variant.
