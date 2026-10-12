# Horseshoe fuel-handling floor-plan study

**Historical alternative.** D-045 replaces this direction with rectangular
site-layout placeholders and camera observation as a working concept. See the
[current site draft](site-study.md#current-rectangular-reservations-and-fuel-inout--d-045).

**Basis corrected after presentation review, 12 October 2026.** The 28 m
horseshoe, seven bays, shielding bands and 8 m height below are a reference
comparison only. They are not the current sizing basis for the liquid-salt
refiner. Conversion is a separate building; this building refines crude salt
and recycles returned WISTR fuel. See the [presentation review](../../fastSalt/design/conversion-refining-review.md).
No replacement building dimensions are established yet.

12 October 2026 — D-044. The owner added radioactive fuel return for recycling
and requested a horseshoe equipment area around a central observation post,
with shielded viewing and remote manipulation from an outer operating gallery.
This is a **dimensioned architectural study**, preceding a Blender revision.
The current D-043 site scene still contains the smaller rectangular building.

## Drawings and editable definition

- [Floor plan and schematic section](../outputs/fuel-handling-study/fuel-handling-plan.png)
- [Editable floor-plan SVG](../outputs/fuel-handling-study/fuel-handling-plan.svg)
- [Site-placement option](../outputs/fuel-handling-study/fuel-handling-site-option.png)
- [Editable site SVG](../outputs/fuel-handling-study/fuel-handling-site-option.svg)
- [Selected geometry checks](../outputs/fuel-handling-study/layout-report.json)
- [Study parameters](../models/fuel_handling_layout.py) and [drawing generator](../scripts/draw_fuel_handling_plan.py)

Generated drawings remain in ignored outputs. Regenerate SVG and JSON with
`python3 scripts/draw_fuel_handling_plan.py` from this repository. The script
uses the Python standard library. PNG previews can be rendered from SVG with
Sharp (SVG input at 140 dpi); no Blender rebuild is required.

## Proposed space allocation

| Item | Study allowance | Status |
| --- | --- | --- |
| Overall outer span | 28 m | Proposed; not owner-approved final size |
| Central observation room | 7 m clear diameter | Personnel space reservation |
| Inner shielding band | 1.5 m | Reference-inspired placeholder; not radiation sizing |
| Equipment horseshoe | Inner radius 5 m; outer radius 9.5 m; nominal 270° sweep | 4.5 m radial clear width before local end walls |
| Outer shielding band | 1.5 m | Same limitation as inner band |
| Outer operating gallery | 2.5 m clear radial width | Viewing and manipulation area reservation |
| Outer building wall | 0.5 m | Geometric allowance |
| Central approach | 3 m wide through open end | Access topology; doors and egress unresolved |
| Hot-cell clear height | 6.5 m | Reference-scale study |
| Roof / overhead service allowance | 1.5 m | Combined placeholder; not crane or shielding design |
| Total height studied | 8 m | Alternative to the prior 5 m fuel-building envelope |
| Coolant preparation annex | 12 × 12 × 5 m | Separate provisional room |

The equipment area is closed at both ends by schematic shield walls: the
horseshoe opening is a personnel approach outside the cell, not an opening
into radioactive equipment space. Blue window bands indicate locations for
shielded glazing; composition, thickness and penetrations are not specified.
Generic E1–E7 bays (2 × 1.4 m) establish scale only. They do not select process
chemistry, equipment count, fuel inventory or throughput. The low observation
and gallery blocks in the section indicate occupied-space envelopes; their
ceilings and overhead shielding remain to design.

## Site option and interfaces

The horseshoe centre is (18, 43) m in installation XY, open end facing south.
The off-gas envelope remains at its D-043 location, 10 × 11 × 5 m, with separate
release stack. Coolant preparation occupies X=32–44 m, Y=36–48 m, joined to
the outer gallery by a short passage reservation. Fuel preparation/recycling
replaces the function of the prior 15 × 12 m rectangle, shown dashed for comparison.

Retain one shared entry across the reactor fresh-air ring. Reserve an elevated
north-side service-distribution strip and independent fuel supply, radioactive
fuel return, coolant supply and off-gas lines. Dashed branches indicate flow
direction and connectivity only. The radioactive return has **no assigned bore,
pressure, pump, shielding or transfer sequence**. Existing 50 mm supply-line
visual allowances do not establish a suitable return-line size. Containment,
heating, inspectability, remote isolation and maintenance at the interfaces
remain to resolve. The service strip crosses the personnel approach above
grade; final headroom and support positions need a section study.

Canister receiving, equipment transfer/airlocks, laydown, waste handling,
ventilation, full personnel access and crane coverage remain unallocated.
The diagram is not a complete facility footprint or building qualification.

## Historical reference versus our proposal

The historical AEC description gives the EBR-II FCF processing cell as a
16-sided polygon, 62 ft (18.90 m) inside across flats, with a central control-room
enclosure 30 ft (9.14 m) across flats **including shielding**. The annular
process width is 16 ft (4.88 m). The adjacent air cell is 15 × 47 × 21 ft
(4.57 × 14.33 × 6.40 m), and the whole facility floor area about 19,000 ft²
(1,765 m²). These are not an overall 18.9 m building diameter.
[AEC historical report](https://www.osti.gov/servlets/purl/4616012).

[ANL-6853, Figure 1](https://inldigitallibrary.inl.gov/Reports/ANL-6853.pdf)
shows the central control room, processing cell and surrounding operating
annulus. It is the architectural precedent, not a selected process for WISTR.
[INL's FCF inventory](https://nsuf.inl.gov/Home/FacilityLayer/412) lists 21 ft
cell height and 5 ft (1.524 m) concrete walls. Its alternative air-cell dimensions
are internally ambiguous; the historical dimensions above are used for comparison.
Reference wall thickness does not establish WISTR shielding requirements.

## Checks performed

The generator verifies that the corners of every generic equipment bay remain
inside the clear radial equipment band. Using a conservative full 14 m-radius
disk, the proposed building clears the existing off-gas rectangle by 1.232 m
and the reactor's 24 m-radius fresh-air ring by 8.615 m. These are selected
plan-envelope checks only. The SVG and PNG drawings were visually reviewed.
No full clash, egress, structural, thermal, process or radiation validation is implied.
