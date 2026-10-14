# Coolant P&ID coverage in the 3D model

The [control-annex draft](control-annex.md) composes this model into the latest complete site without changing coolant or nitrogen topology.

14 October 2026 — D-067 and D-068, draft. This continues the [compact service layout](compact-services-draft.md). It reads the current P&ID TOML and shared engineering model rather than the preserved Revision A PDF or CSVs.

## Review files

- [Complete Blender scene](../outputs/site-coolant-pid/fast-salt-coolant-pid.blend)
- [Exterior nitrogen header](../outputs/site-coolant-pid/nitrogen-exterior.png) and [room-entry cutaway](../outputs/site-coolant-pid/nitrogen-cutaway.png)
- [Overview](../outputs/site-coolant-pid/overview.png)
- [SG gas vessel and valve detail](../outputs/site-coolant-pid/sg-detail.png)
- [Tank gas connection](../outputs/site-coolant-pid/tank-detail.png)
- [Lowered transfer piping, plan with equipment hidden](../outputs/site-coolant-pid/drain-plan.png)
- [Tag-by-tag CSV](../outputs/site-coolant-pid/coolant-pid-coverage.csv) and [coverage, routes, provenance and checks](../outputs/site-coolant-pid/coolant-pid-coverage.json)

## Coverage

| P&ID group | Tags represented |
| --- | ---: |
| Equipment, including junction/header | 15 |
| Process boundaries | 5 |
| Lines | 25 |
| Valves | 16 |
| Instruments | 26 |
| Rupture-disc concepts | 3 |
| **Total** | **90** |

Every item is associated with named Blender objects. Representation is explicit: 21 existing/new modeled items, 36 spatial reservations, 26 measurement locations, three relief-interface stubs, three functional station envelopes and one unresolved receiving-system interface. “Represented” does not mean selected, sized or qualified equipment. Proposed valves and instruments remain proposed, colored amber. Accepted coolant-gas concepts are teal; unresolved relief interfaces are mauve.

| Added or reconciled element | Physical representation |
| --- | --- |
| AC-101/102/103 and L-101G/102G/103G | Three SG-top gas collection vessels, continuously connected to the hot coolant collectors; no intervening isolation valve |
| G-101/102/103 and V-101G/102G/103G | Separate gas branches and isolation-valve reservations above the collection vessels |
| H-401 | Common coolant-gas header above the hot-air header, with a riser and low-level connection toward coolant preparation |
| G-402 / V-402G | Separate tank-top nozzle and gas branch with an isolation-valve reservation; joins H-401 beside the tank |
| G-400 / B-401 | Connection to a coolant-only pressure-control station envelope in coolant preparation |
| J-401 / L-401–404 | Common bottom tee, tank nozzle, reversible P-401 transfer and preparation supply/return |
| Proposed main and transfer valves | Location collars and actuator reservations, preserving source proposal status |
| TT / FT / PT / LT items | Tagged measurement-location markers; no sensor technology, impulse tubing or wiring selected |
| L-101R/102R/103R and RD-101/102/103 | Separate high-level takeoff/interface stubs and unsized disc-holder reservations |
| B-501 | Three visibly marked unresolved terminations; no receiver, common relief manifold, discharge destination or capacity selected |

The redundant G-401 is not reintroduced. Coolant gas has no connection to the fuel off-gas system. Gas/relief connections remain distinct. P-401 remains a reversible positive-displacement pump. Main pump metadata is refreshed from the current P&ID/shared duty; the existing motor envelopes remain unchanged.

## Exterior nitrogen utility — D-068

The existing outdoor nitrogen tank/vaporizer stays in place. H-601 follows the outside walls of the 5 m service buildings, at 4.65 m above the floor, clear of the receiving doors. N-600 rises beside the vaporizer/regulator, crosses on an illustrative rack to the off-gas building west wall, and follows that wall around the corner to the front header. The earlier freestanding service-area run and riser are removed; the front header now starts at the building corner. Supports are spatial reservations, not sized structural members. Separate branches N-601, N-602 and N-603 enter off-gas treatment, fuel refining/recycling and coolant preparation respectively. The old single-room feed and its obsolete wall opening are replaced.

Each branch drops to an exterior isolation-valve location and regulation/backflow-protection enclosure reservation before entering the room. The generic boxes do not select or qualify protection hardware. The existing off-gas-area distribution station is retained, a fuel-room distribution interface is added, and N-603 terminates at a separate makeup port on B-401. G-400/H-401 remains the bidirectional coolant process-gas path; process returns do not join the clean nitrogen supply. Internal room distribution and coolant return handling remain unresolved.

The blue supply tubes are displayed with **50 mm header/feed OD and 25 mm branch OD**, uninsulated, solely as spatial reservations. Flow, pressure, pipe specification, insulation need, regulator/backflow arrangements, supports and penetration seals remain to be designed. Brackets are illustrative. The header has 0.425 m nominal pipe-surface clearance above the tallest 4.2 m door; access and radiation zoning are not qualified by this geometric check.

P&ID sheet 6 and named 3D routes share the same tags and endpoints. New supply items use the Exterior nitrogen supply collection for boxes/supports, and Coolant gas piping for tagged line geometry; custom properties distinguish clean nitrogen from coolant process gas.

## Spatial assumptions

The gas line diameters are **visual allowances only**: 25 mm branches, 50 mm header and preparation connection, with 25 mm radial insulation. The SG/accumulator salt-gas connections use a 50 mm visual OD and 50 mm insulation. Each collection-vessel envelope is provisionally 0.60 m diameter × 1 m high, not an adopted capacity. Header routing is at R=16.8 m and Z=12 m; vessel and riser/support locations are provisional. Hot gas heating requirements remain unresolved in the engineering source.

Relief stubs use 150 mm display diameter solely to make the interfaces visible. That is **not a selected relief bore or capacity** and does not modify the unresolved P&ID fields. No new steam-generator failure assessment is performed.

## Shortened air header and low transfer tee

The unused fresh-air header arc from approximately **27.19° to 76°** is removed, including its obsolete end and bearings. A new sealed end sits just before SG-102's inlet, which joins at approximately 81.09°. All **ten equipment fresh-air branches and three outdoor intakes** remain connected to the retained header. This is a geometric connectivity check, not an airflow recalculation.

L-401's former 4.90 m-high crossing is removed. It now follows the existing under-vessel/pump level, **0.40 m above the floor**, through a new lower reactor-wall opening. The old high opening/sleeve is removed. L-402 and L-403 fall toward J-401 beneath the tank. J-401 is **0.20 m above the floor**, the lowest modeled centreline in these transfer runs, with 0.125 m nominal clearance below the 150 mm insulation envelope. L-404 rises from the tee into the tank bottom. The preparation run drops before reaching the tank's bottom insulation, with a revised wall penetration.

The under-vessel L-401 run is level; pump internals and construction tolerances are not modeled. Establishing this common low point does **not** establish complete gravity drainage of the reactor/SG circuit. The existing pressure-assisted preparation transfer/sweep concept and operating-state table remain unchanged.

## Checks and use

The builder rejects missing/duplicate tags, checks all 25 line endpoint/via identities against the current P&ID, confirms five coolant gas-header joins, six accumulator terminals and four clean-nitrogen header connections, checks changed routes against nearby evaluated geometry and against one another (including hidden service-building walls/roofs for nitrogen), and verifies the transfer low point and absence of reverse rises. Selected port/tee contacts and valve/instrument association markers are intentional. A main-circulation route fingerprint confirms unchanged main geometry. Source hashes are included in the report. These checks do not qualify support loads, pipe stress, protection, crane operating envelopes or full maintenance access.

In Blender, new items are grouped into Coolant gas piping, Coolant gas vessels, Coolant PID reservations, Coolant pressure-control station, and Unresolved coolant interfaces. Inspect an object's custom properties for its P&ID tag, status and representation. The small valves and instruments are easiest to see in the detail cameras or by selecting their tag in the Outliner. The main scene opens in the overview cutaway; hidden walls/roofs remain available.

[Parameters](../models/wistr_coolant_pid_draft.py) and [builder](../scripts/build_coolant_pid_draft.py) overlay the preceding compact-services scene. Generate that source first if absent.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --python-exit-code 1 \
  --python scripts/build_coolant_pid_draft.py
```

`-- --build-only` skips rendering. `-- --resume` reuses a geometry checkpoint for check/presentation changes; rebuild after geometric/parameter edits. Resume rejects a changed P&ID. `--views sg-detail tank-detail` selects renders. Output models, CSV and reports remain ignored; the new draft is not committed automatically.
