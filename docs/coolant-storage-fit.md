# Coolant storage tank — provisional fit study

14 October 2026. Owner-selected size: **8.2 m bare diameter × 16 m bare height**, subject to future SG/inventory revisions (D-058). Current installation/site scenes retain the earlier 4 × 8 m tank. The [selected envelope](../../fastSalt/design/engineering/coolant-storage.toml) is separate from the unresolved location.

![Proposed tank at the existing location](../outputs/coolant-storage-fit/coolant-storage-fit.png)

## Finding

The tank fits inside the gross building envelope, but **does not fit the current equipment arrangement at its existing centre (14, −6.5) m**.

| Check at existing position | Result |
| --- | --- |
| Insulation/cladding outside diameter | 8.902 m |
| Clearance to nominal inside building wall | 0.463 m; excludes access and local columns/ducts |
| Tank insulation top above floor | 17.316 m, retaining 0.9 m support height |
| Ladder top allowance above floor | 17.60 m |
| Hoist body underside above floor | 22.73 m; about 5.13 m higher than ladder allowance |
| Maintenance platform overlap | 1.65 m into its south edge; both receiving trays affected |
| Fresh-air header | Tank overlaps the floor duct; about 2.05 m radial penetration into its nominal band |
| SG-3 fresh-air branch | Sampled pipe-envelope overlap about 0.60 m |
| Loop-3 insulated hot coolant pipe | Sampled pipe-envelope overlap about 0.12 m |
| Local transfer-pump motor | Enlarged tank insulation envelope overlaps its present location |

The two bottom tank connections are intentional interfaces, not clearance failures. Their routes would need coordination with any relocation. The small nominal wall clearance is not an adequate demonstration of inspection access. The height comparison is not a loaded-crane swept-path or removal-clearance assessment.

## Capacity of this draft size

Using the same provisional 25 mm radial wall, 100 mm end-height allowance, 20% freeboard and 5% heel gives **829.5 m³ internal** and **622.1 m³ working acceptance**. The D-063 inventory revision requires **526.5 m³ working acceptance**, including a 10% inventory allowance; this leaves about **95.6 m³ additional margin**. The earlier fit study used 588.9 m³ and 33.2 m³ margin; its geometric interference findings are unchanged. Tank geometry, wall, supports and thermal/pressure design remain unresolved.

## Basis and next step

Read the current saved `outputs/site-45-bends/fast-salt-site.blend` in Blender without changing or saving it. Compare the proposed cylindrical jacket envelope with existing platform boxes and sampled pipe jacket guide paths; use current Python configuration for nominal building, header and height dimensions. The [report](../outputs/coolant-storage-fit/fit-report.json) identifies the source scene by hash. This is a selected fit screen, not a complete intersection audit. The plan intentionally shows selected equipment only; duct column pockets are omitted.

The next layout study should test a relocated tank and coordinated changes to the laydown platform, air duct/branch, salt pipe and transfer pump before deciding whether the building must grow. No alternative location has yet been shown to clear all equipment and access routes. Existing scene geometry and historical baselines remain unchanged.
