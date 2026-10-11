# Six-sector removable reactor insulation cover

11 October 2026 — zirconia seating and suspended-grid revision, with straight sliding
pickups. The proposed pivoting internal catches are not used.

## Project ownership

This is a **reactor thermal-enclosure and handling subassembly** in
`fastSaltModels`, not a new repository and not part of the pressure-retaining
vessel boundary. The existing steel sector caps and their bolted tube plugs
remain separate beneath it. The project hub keeps the
[design/interface brief](../../fastSalt/design/reactor-insulation-cover.md).

## Review the draft

- [Editable Blender assembly](../outputs/reactor-insulation-cover/wistr-insulation-cover.blend)
- [Six-cassette overview](../outputs/reactor-insulation-cover/cover-overview.png)
- [One cassette raised](../outputs/reactor-insulation-cover/cover-raised.png)
- [Zirconia support detail](../outputs/reactor-insulation-cover/cover-support.png)
- [Internal support construction](../outputs/reactor-insulation-cover/cover-cutaway.png)
- [Resting and carrying hook sections](../outputs/reactor-insulation-cover/cover-mechanism.png)
- [Geometry report and source hashes](../outputs/reactor-insulation-cover/cover-report.json)

The Blend file opens with cassette 1 raised and the existing common lifting head
attached. The gray spider below is a dimensional reference, not a complete
reactor model. The cassette underside is the local Z=0 reference. Placement at
reactor Z=7.20 m is only a reserved starting elevation; seating attachments and
service routing have not yet been integrated.

Use the timeline: frame **1** resting, **21** shoulders taken up, **61** cassette
raised 1.5 m, **101** seated, **121** stems returned to rest. This prescribed
motion illustrates the intended sequence, not dynamics or demonstrated gravity
return. No rotational latch or internal unlatching action is required.

## Geometry and operation

Six wedge cassettes cover an approximately 8.24 m diameter footprint. Each seam
lies over a spider-leg centreline; removing one exposes the half-leg region on
either side. Actual socket and service-disconnection access remains to check.
Rigid edges have clearance and do not interlock. Flexible seam strips are shown
schematically, and the skirts stop short of the hot-face liner; the final
insulating closure of that perimeter gap remains to be detailed.

Each cassette has a provisional 500 mm stone-wool allowance in five 100 mm
layers, thin stainless skins, a separate internal carrying frame and four square
sliding pickup stems. Grid wires at 200 mm pitch are schematic; only cassette 1
contains the detailed grids to limit scene size. The upper frame carries five independently framed trays (four grids and the
bottom liner) on four 6 mm tension hangers. Collars beneath each tray transfer
its load into the rods. Crossed 4 mm wires brace the assembly laterally.
Separate hollow compression posts carry the installed load through zirconia
blocks. Long-path skin ties support the exterior shell. Their sizes, stiffness,
attachments and welds are not calculated. Wool panel joints must be staggered in
fabrication; this rendering uses continuous wedge envelopes.

The main lifting shoulder lies 40 mm below the internal frame at rest. A collar
rests on the cooler outer guide and prevents the stem falling into the cover.
The 30 mm square stem passes through a 38 mm keyed guide and a 50 mm frame slot.
A 120 × 100 × 20 mm lower shoulder remains captive beneath the frame. Nominal
bearing overlap is 35 mm per side across its width and 25 mm along its depth.
All these mechanism dimensions are provisional review choices.

The crane raises the stems 40 mm, then lifts the cassette by the internal frame.
After seating, lowering the tool permits the stems to return to their collars.
The tool can then lower below the external hook crowns and spread its bars using
its existing release cable. Gold bands indicate stem travel; they do not measure
load or prove load sharing. Binding, return reliability and unequal stem motion
still require engineering assessment.

The external hook profile, 25 mm hook thickness, 40 mm pickup bars and 750 mm
bar pitch are reused from the existing common head. The whole pattern is shifted
to the centroid of a uniform wedge (radius about 2.624 m). This is not the actual
assembly centre of mass; metal, cutouts and service fittings may shift it.
The wool-only gross budget is about 569 kg per cassette, before skins, framing
and fittings, using 128 kg/m³. It is not a rated lifted mass.

## Thermal and mechanical boundary

The resting gap breaks the direct shoulder-to-frame conduction path. Other heat
paths remain through skin ties, seating supports, guides, gas and radiation.
The stem clearances are not vacuum breaks. Sleeve insulation, flexible collars
and perimeter seams need development. The earlier Hurmet flat-wall calculation
uses calcium silicate and cannot validate this stone-wool cassette's bridges,
penetrations or surface temperatures without an updated calculation.

This prototype does not remove the existing reactor hood or change the
installation cooling-air circuit. Vessel/well cooling, hot-air collection and
service penetrations must be resolved before adopting it in place of the hood.

## Build and checks

From the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_insulation_cover.py
```

Inputs: [cover parameters](../models/wistr_insulation_cover.py) plus the existing
reactor dimensions and lifting interface. Builder:
[scripts/build_insulation_cover.py](../scripts/build_insulation_cover.py);
geometry: [reactor_insulation_cover.py](../src/textual_graphics/reactor_insulation_cover.py).
Outputs stay in ignored `outputs/reactor-insulation-cover/`.

The build checks six sets of four sliders, captivity dimensions, slot clearances,
21 stroke positions, shoulder-to-bearing contact at full travel, loaded bar
alignment, pickup placement and closed manifold meshes. It also runs the existing
head's sampled approach/release and geometric hook-lip capture checks at both
slider endpoints, against 24 modeled outer-skin/guide/support obstacles.

Those checks do not establish strength, equal loading, thermal performance,
complete reactor/crane swept volumes or suitability for remote nuclear service.
The two section examples are display copies, hidden in the default Blender view.


## Wool cutaway and estimated centre of mass — 11 October review

- [Stepped cutaway with wool and grids](../outputs/reactor-insulation-cover/cover-wool-cutaway.png)
- [Pickup footprint and CM plan](../outputs/reactor-insulation-cover/cover-cm-plan.png)
- [Separate editable review scene](../outputs/reactor-insulation-cover/wistr-cover-support-review.blend)
- [Component mass/CM report](../outputs/reactor-insulation-cover/cover-mass-report.json)

The stepped cuts are display cuts only. Five layers remain visible at the back;
the front exposes all four intermediate grids, their tray frames, tension
hangers, diagonal bracing and upper carrying frame. The bottom layer bears on the liner. Grid/support
sizes remain conceptual, and this depiction does not verify sag, compression or
connection strength. The full cassette source remains unchanged.

To rebuild after generating the main cover:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/render_cover_supports.py
```

The script integrates signed tetrahedral mesh volumes and first moments for
all modeled parts of cassette 1 (the cassette containing the detailed grids),
including evaluated curve geometry. It excludes the crane head, reference
spider and section-display copies. Assumed densities are 128 kg/m³ for wool/seam
filler, 7,850 kg/m³ for the inner steel frame and pickups, and 8,000 kg/m³ for
stainless skins, grids and outer parts. Densities are provisional model inputs.

| Quantity | Preliminary estimate |
|---|---:|
| Wool plus seam filler | 561 kg |
| Steel and hardware | 899 kg |
| Cassette total | 1460 kg |
| CM along wedge bisector | 2.617 m |
| CM transverse offset | 1.8 mm |
| CM height above underside, loaded stems | 0.279 m |
| Inner / outer hook rows | 2.249 / 2.999 m |
| Lifting-head centre | 2.624 m |
| CM inward offset from head | 7 mm |
| Minimum CM plan distance inside pickup polygon | 368 mm |

The four hooks surround the updated CM. Ideal level-cassette row reactions are
50.9% inner and
49.1% outer. These do not solve
individual hook loads or exact suspended balance. The tool and fixed zirconia
seats are excluded. This revision supersedes the earlier 1,242 kg estimate.

This is an additive volume budget, not a disjoint solid assembly. Intersecting
steel parts and steel embedded in wool are counted twice in their overlap;
modeled voids are subtracted, but unmodeled fasteners, sleeves, connections and
fabrication details are absent. Do not use the total as a lifting rating.

Checks verify the CM is inside the pickup polygon, mesh liner volume agrees
with polygon area × thickness, wool volume agrees with area minus modeled
16-sided holes × 500 mm, and ideal row reactions are positive and sum to unity.
The report records each part, density, volume, mass, centroid and source hash.

## Zirconia seating and upper-frame load paths

Each cassette rests on four provisional Ø50 × 75 mm zirconia blocks, 24 total.
The ceramic stays in a fixed shallow cup when the cassette is lifted. A broad
70 × 70 × 10 mm upper steel bearing foot contacts its top face. There is no
through-bolt, metal sleeve or retaining strap between its faces. A lower cup
rises only 10 mm, leaving 65 mm to the upper foot; nominal radial clearance is
1 mm. These are cold geometry choices, not qualified operating clearances.
Gray pedestals reserve the reactor support interface; their attachment to the
vessel/spider is not designed.

Four 40 × 40 × 2 mm hollow steel posts rise from the feet to the upper frame.
The frame bearing pads are 420–460 mm above the cassette underside. The frame
is within the wool; it is not assumed to be at room temperature. Each tray has
16 × 25 mm edge/cross framing and its own hanger collars. Grid pitch and all
member sizes remain provisional pending deflection, strength and joint design.
The rods are tension members; the separate posts are compression members.
Clearance holes keep the mesh/liner from directly touching those posts.

At rest: wool → grid trays/liner → tension hangers → upper frame → steel posts
→ zirconia → fixed seats. During lifting: the upper frame transfers the load
to the four sliding shoulders and hooks; the posts lift clear of the ceramics.
The 40 mm resting shoulder gap and common lifting-head geometry are retained.

[Hurmet screening](../../fastSalt/calculations/reactor/Zirconia%20cover%20supports%20-%20Hurmet.md)
uses a 1,500 kg mass allowance, an illustrative load-sharing factor and axial
ceramic conduction. It is not a whole-cover thermal calculation or a ceramic
strength qualification. Grade-specific hot properties, thermal cycling, contact
flatness, expansion, fracture containment and environmental suitability remain
open. Insulation around exposed post sides and liner clearances needs detailing;
radiation and side heating could bypass the intended axial thermal resistance.
The remaining skin ties also conduct heat.

The model checks 24 fixed ceramic breaks, four tension hangers per cassette,
post-hole clearance, cup-to-foot separation, retained pickup travel and sampled
common-tool clearance. Closed mesh checks and updated mass/CM checks pass.
