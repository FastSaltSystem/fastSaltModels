# Shared-wall process annex, coolant silo and preparation room

Superseded for current layout review by the [compact shared-wall enclosure draft](compact-services-draft.md), D-066. This earlier scene remains reproducible.

14 October 2026 — D-065. This revises the [attached tank-bay draft](tank-bay-draft.md) to the owner's requested arrangement. Equipment remains illustrative; this revision changes its placement and connecting geometry, not treatment or refining technology.

## Current review files

- [Blender scene](../outputs/site-attached-services/fast-salt-attached-services.blend)
- [Cutaway](../outputs/site-attached-services/cutaway-draft.png), [plan](../outputs/site-attached-services/plan-draft.png), [exterior](../outputs/site-attached-services/exterior-draft.png)
- [Geometry, source hashes and check report](../outputs/site-attached-services/attached-services-report.json)

## Combined off-gas and fuel building

One **5 m high** building now extends from X=−7 to +13 m, with its north wall at Y=31 m. Its curved southern boundary follows the **existing reactor building wall at R=21 m**. There is no separate southern facade or long exterior service bridge. The approximately **221 m²** footprint is divided by a wall at X=3.8 m: off-gas to the west, fuel refining/recycling to the east. Both areas have separate north-side service/receiving openings.

The retained process placeholders move 6 m toward the reactor. Existing fuel supply/return stays together in one insulated, heated bundle. The gas supply and collection routes are shortened and separated vertically. Their local reactor-wall opening is increased from 1.0 to 1.3 m height, with its bottom unchanged; the altered sleeve/opening remains a spatial reservation, not a qualified containment or structural detail. Nitrogen equipment moves beside the western area and continues to feed it. The separate release stack remains separate, with its connection rerouted.

The inspection view shows a 5 m high **display slice of the existing reactor wall**. The original full-height wall is retained in the hidden Shell collection. The display slice is not an additional construction layer; hide Shared wall inspection when displaying the full Shell collection.

## Cylindrical coolant enclosure

The rectangular tank bay is replaced by a **12.5 m outside-diameter, 19.5 m high silo** at the same tank centre, (20.5, 20.5) m. Its provisional wall thickness is 0.35 m and inside diameter is 11.8 m. This accommodates the existing P-401 envelope as well as the insulated tank. The existing tank remains 8.2 × 16 m bare, with 350 mm insulation and 1 mm cladding.

The closest checked equipment-to-wall gap is about 63 mm at the pump-base envelope; this does not establish pump maintenance access.

The round enclosure has about **39.27 m wall perimeter**, compared with 44 m for the preceding square bay: approximately **11% less external wall area at the same height**. This is geometry only. Total heat loss, enclosure insulation, temperature and ventilation have not been calculated or selected. Tank insulation is retained. A small east-side access door is a layout allowance; tank installation/removal is not established.

## Separate coolant preparation

A **5 m high**, approximately **120 m²** room attaches to the silo on its **+Y side**. It spans X=15.5–25.5 m and extends north to Y=38 m. Its southern boundary follows the silo wall. Coolant equipment placeholders move together into this room; their dimensions remain unchanged. A north receiving opening and apron are reserved.

The heated/insulated preparation line now runs south directly through the silo wall to the same low-point tee beneath TK-401. P-401 and the reactor transfer route remain in their preceding positions. The earlier high crossing over the internal headers still requires drainage/venting review.

## Air inlet and retained layout

Only the former **70° exterior fresh-air intake** moves, to **33°**, near but outside the reactor doorway approach. Its louver, connecting duct and wall/duct opening tools move together, restoring the old openings. The other two intakes and the generator connections are retained. The three-item laydown platform and its maintenance placement remain unchanged.

## Reproduce and inspect

[Parameters](../models/wistr_attached_services_draft.py) and [builder](../scripts/build_attached_services_draft.py) are a draft composition layer over the preceding tank-bay scene. Generate that scene first on a fresh checkout, using its guide. Existing accepted baselines and earlier scene builders are retained.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --python-exit-code 1 \
  --python scripts/build_attached_services_draft.py
```

Use `-- --build-only` to skip rendering. `-- --resume` rechecks/renders the generated geometry checkpoint; rebuild without it after changing geometry logic. A configuration hash guards parameter changes. Working outputs are excluded from Git.

Checks cover moved equipment against room boundaries, tank/pump envelopes against the silo wall, the relocated intake against the silo and doorway corridor, and changed routes against nearby evaluated solids and one another. Intentional component ports, unchanged internal gas tees and existing fuel-bundle bearing contacts are distinguished from clashes. A route fingerprint checks that main circulation paths are unchanged. These are selected geometric checks; they do not establish shielding, room segregation/ventilation, process capacity, structural adequacy, pipe stress or complete operational access.
