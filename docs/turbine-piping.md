# Turbine-hall main piping draft

Cleanup note — 12 October 2026: superseded generated drafts have been removed. Current site plans and the saved scene are together in `outputs/site-45-bends/`. The current site imports the maintenance/utility installation and adds attached process buildings (D-043); the turbine layout remains unchanged. Historical output links below may require rebuilding.

11 October 2026. First internal routing study on the D-031 **60 × 40 × 28 m**
hall. This adds geometry to the motor-BFP arrangement; cycle results and equipment
sizes are unchanged. Equipment nozzles are provisional points on reservation boxes.

- [Two-level piping plan](../outputs/site-45-bends/turbine-piping-plan.png)
- [Editable SVG](../outputs/site-45-bends/turbine-piping-plan.svg)
- [Blender model](../outputs/site-45-bends/fast-salt-site.blend)
- [Aligned site view](../outputs/site-45-bends/site-alignment-draft.png)
- [Route schedule](../outputs/site-45-bends/turbine-pipe-schedule.csv)
- [Geometry and verification report](../outputs/site-45-bends/turbine-piping.json)
- [Routing definition and independent checks](../models/turbine_piping.py)

## HP/IP connection correction

The owner identified that the three LP crossover pipes appeared to come directly
from HP. The original combined HP/IP box had ambiguous and inconsistent stage
port positions: admission, cold reheat, hot reheat and crossover locations were
not assigned to distinct stages. The corrected draft divides the same 14 m train
reservation into labeled IP (west) and HP (east) sections, each 6.5 m long with
a 1 m coupling gap. These are illustrative subdivisions, not vendor casing sizes.

**Main steam → HP → reheaters → IP → LP** is now explicit. Both cold-reheat
sources lie on HP; both hot-reheat returns land on IP; all three LP crossover
sources lie on IP. Stage-specific contact checks accompany endpoint and clearance
checks. No steam bypass from HP directly to LP is modeled. The separate heating
branch still supplies main steam to the reheaters and returns condensate to HP4.
Both sections share the existing generator train; power and cycle values are unchanged.
The earlier ambiguous geometry is preserved in `outputs/site-piping` for provenance.

## Building alignment update

D-032 translates the hall 10 m north to align its centre with the reactor. External
steam/feedwater bends near the reactor now provide a straight east–west approach
normal to the turbine wall. The local internal terminal stays at (57, 15.80516) m,
but its world Y is now −4.19484 m. Both internal entry tangents are changed to
match the new external run. All stage, connectivity and interference screens are
rerun. Earlier diagonal-approach outputs remain in `outputs/site-piping-v2`.

## Included paths

59 pipe sections represent main-steam admission and the reheater heating split;
two cold and two hot reheat trains serving four parallel modules; reheater heating
condensate to HP4; three IP-to-LP crossovers; condensers to condensate pumps;
condensate through LP1–LP3 to the two DA storage reservations; two DA downcomers
and the common BFP suction collector; three BFP discharges through HP1–HP4 back
to the existing feedwater interface. Main steam and water match the D-032
wall-normal site terminal positions and approach directions. The two serial heater circuits
have separate inlet and outlet ports, not tees that bypass their heaters.

The condensate suction collector is at **−1.3 m centreline below the hall floor**.
It requires a new service channel and floor penetrations; these civil details are
not cut into the current slab mesh. This avoids routing suction over the 5 m
reserved aisle volume, but does **not** establish hotwell submergence or available
NPSH. Supplier nozzle/hotwell levels and pump suction requirements must determine
the final arrangement. The plan identifies below-floor routing; it is hidden by
the floor in the normal Blender cutaway.

## Dimensions and assumptions

Bores originate in the current motor-equipment sizing JSON in the sibling
`fastSalt` repository. Existing main steam keeps 725 mm bore / 195 mm conditional
wall / 350 mm insulation; feedwater keeps 650 / 120 / 175 mm. Internal wall and
insulation values below are **geometric allowances**, not pressure-rated selections
or new heat-loss results. Modules retain upstream header bores conservatively;
this does not imply that four modules each carry the full header flow.

| Circuit | Bore, mm | Wall allowance, mm | Radial insulation allowance, mm |
| --- | ---: | ---: | ---: |
| Reheater heating supply | 350 | 100 | 350 |
| Cold reheat, each of two trains | 775 | 25 | 200 |
| Hot reheat, each of two trains | 1,000 | 35 | 350 |
| IP–LP crossover, each of three | 1,400 | 25 | 200 |
| Reheater heating return | 500 | 140 | 250 |
| Condensate / LP water | 475 | 15 | 100 |
| DA downcomers / BFP branches | 500 | 15 | 100 |
| Common BFP suction collector | 725 | 15 | 100 |
| Below-floor condensate collector | 650 | 15 | 0 |

The two enlarged common suction collectors are layout assumptions, not additions
to the approved hydraulic schedule. The Blender objects show the outer pipe or
insulation envelope with service colors; they are not separate pressure-metal
and insulation meshes. Rounded elbows are geometric transitions, not standard
fitting selections. No fabrication detail is implied.

## Check results and open constraints

All drawn endpoints meet an explicit same-service junction, a designated equipment
port, or an existing plant terminal. Checks use the same rounded polylines rendered
in Blender. Pipe-pair checks use centreline segment distance plus jacket radii;
local fitting neighborhoods at explicit junctions are exempt. Equipment and
maintenance-volume checks sample at intervals no greater than 0.15 m, adding
0.075 m to the tube radius conservatively. Local nozzle-contact neighborhoods are
exempt only for named connected equipment. Simple analytic distance and bend
cases were checked independently.

- No detected pipe-to-pipe or equipment-envelope clashes; drawn jackets clear
  wall planes and the +25 m crane-underside plane. Bend radii exceed jacket radii.
- The **east feedwater bay remains flagged**: the existing pipe underside is
  **4.70 m above floor**, below the cross aisle's provisional **5 m reservation**.
  The reservation has not been silently reduced. Either accept a locally lower
  route clearance after vehicle/access review, or revise the incoming water line.
- Tube withdrawal reservations, BFP laydown and pump-side access are clear of the
  drawn pipe envelopes, apart from that explicit east cross-aisle flag.
- Crossovers occupy the space above the LP turbines: their underside is +20.275 m
  and top +22.125 m. This leaves 2.875 m below the reserved crane underside.
  It is **not** proof of adequate crane/rotor-removal access. Overhead pipe routing
  and removal/disconnection sequences need a dedicated maintenance review.
- The three crossover route lengths are approximately **71.6, 56.3 and 41.3 m**;
  the heating-return route is **48.3 m**. These exceed the prior 40 m pipe-screen
  length. Recalculate distributed pressure losses, including fittings and valves,
  before using the previous cycle pressure assumptions. The schedule's geometric
  lengths do not include equipment internals, valve bodies or expansion loops.

Heater extraction steam, cascading drains, DA heating steam, LP exhaust transitions,
cooling water, bypasses, vents/drains, minimum-flow lines and valve stations are
still to route. Equipment lifting paths, columns/decks, pipe racks, anchors, thermal
expansion, structural loads and hydraulic/stress qualification remain open. The
59-route fit does not establish complete-plant fit in the smaller building.

## Reproduce

Run from `fastSaltModels`; the sibling `fastSalt` calculation repository is required.

```sh
python3 models/turbine_piping.py outputs/site-45-bends
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_site.py -- \
  --output outputs/site-45-bends --view alignment --with-piping
```

The first command writes checked JSON, CSV and SVG; PNG is a rasterization of the
SVG. The Blender command rebuilds the same routes and embeds the report in its
site report. Use collections named `Turbine pipes | ...` to hide individual services.
Earlier equipment-only drafts remain in `outputs/site-study-motor-v4` and earlier
revision directories. Source hashes identify both the sizing and layout inputs.

D-033 changes only the external site route to two 45° offset bends, with a
separate 20° reactor outlet alignment turn. Internal pipe coordinates, dimensions
and the retained aisle-clearance limitation are unchanged. See the site guide.
