# Attached control-annex draft

14 October 2026 — D-069. This overlays the latest [coolant/nitrogen draft](coolant-pid-3d.md), preserving its plant equipment, gas connections and lowered transfer piping.

## Review

- Complete scene: generate `outputs/site-control-annex/fast-salt-control-annex.blend` locally (see Build below). Published previews: [gallery](../results/README.md).
- [Annex exterior and adjacent connections](../results/2026-10-15/control-annex/exterior.png)
- [Interior cutaway](../results/2026-10-15/control-annex/cutaway.png)
- [Whole-site context](../results/2026-10-15/control-annex/site.png)
- [Geometry checks and source hashes](../results/2026-10-15/control-annex/control-annex-checks.json)

## Arrangement

The provisional annex is **20 m east-west × 25 m north-south × 5.5 m wall height**, a 500 m² gross footprint. Its bounds are X = -36 to -16 m and Y = -41 to -16 m at the common floor datum Z = -9.1 m. It attaches to the turbine hall's southeast corner, sharing 4 m of the reactor-facing boundary, south of the steam/feedwater entrance. The operators' area reserves **15 × 12 m = 180 m²**; three console envelopes and an overview display illustrate its scale, not staffing or human-factors requirements.

An east-facing outside entrance has a small canopy and apron. A second outside door faces south. A two-door vestibule connects through an actual opening in the turbine facade. There are separate envelope rooms for control equipment, UPS and dedicated ventilation, with local ceilings; the cutaway hides these ceilings and the annex roof/front walls for inspection. Internal equipment is illustrative. No duct, electrical segregation or safety-control design is implied.

The annex has its own slab reservation and a 0.60 m control-side separating-wall allowance. The existing turbine facade is retained except for the vestibule opening; the two adjacent visual layers indicate a common boundary, not a selected single/double-wall construction detail. The 0.60 m thickness has **no assigned fire, shielding or missile rating**. Foundations, seismic/structural independence and joints remain unresolved. The lowest local support/room ceilings are not structural designs.

## Checks and limits

The build checks the complete annex envelope against nearby existing meshes and saved pipe centrelines, all 18 turbine service reservations and all three withdrawal aprons. It verifies the turbine vestibule opening, unchanged main-circulation geometry and all 121 existing object-to-P&ID associations (90 unique tagged P&ID items). Deliberate common-boundary contact and ground/paving are excluded from collision rejection.

The nearest annex corner is approximately **1.627 m from the 21 m-radius reactor shell**, a geometric gap only, not a vehicle route or qualified access allowance. The nearby feedwater route has approximately **3.51 m** clearance to the annex volume in the selected check. There are no detected envelope/pipe/service overlaps. The access apron and canopy are local architectural allowances; site traffic, full door-swing/egress review, cable routing, ventilation intake location, habitability, fire, turbine missiles, flooding and shielding remain to assess. A separate supplementary shutdown location remains to be reserved in a later draft.

The proposed building size is a project layout allowance, not a standard nuclear control-building size. Historical discussion references: [IAEA control-room requirements 65–66](https://nucleus.iaea.org/sites/nss-oui/Published%20Collections/m_daad92bb-3bb0-4445-a6ec-a287e55e9664/m_daad92bb-3bb0-4445-a6ec-a287e55e9664__65_0.Html) and [NRC example of control-room/turbine-building barrier integrity](https://www.nrc.gov/reading-rm/doc-collections/enforcement/actions/reactors/ea02162). These motivate separation functions; they do not size this annex or its wall.

## Build

[Parameters](../models/wistr_control_annex.py) and [builder](../scripts/build_control_annex.py) read the saved coolant/nitrogen scene. Generate that source first if absent.

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python scripts/build_control_annex.py
```

Add `-- --build-only` to skip rendering. Working scenes and renders remain ignored; no commit or baseline snapshot is created automatically.
