# Fast Salt site and service checkpoint — 12 October 2026

Preserved after the owner accepted the lowered generator inlets and requested a commit.

Open [the complete Blender site](fast-salt-site.blend). This snapshot includes
rectangular converter, refining/recycling and off-gas building reservations;
a shared service duct; paired heated/insulated fuel supply and return;
coolant supply to storage; three fuel pressure servers; and the relocated
nitrogen supply feeding the off-gas building (D-043 through D-048).

The fresh-air header is now inside the reactor building (D-049). D-050 adds
all 18 wall-column positions, three outdoor intakes near the generators and
side butterfly-valve boxes. The accepted inlet centers are **1.35 m above
floor**, with short level ducts and approximately 0.37 m beneath the boxes.
Clear inlet bore is **1.55365 m**, 75% of the existing exhaust's clear area;
inlet OD is 1.55965 m with the provisional 3 mm wall allowance.

Review the [site arrangement](site-process-draft.png),
[site plan](site-process-plan-draft.png), [fresh-air plan](site-fresh-air-draft.png),
[low generator inlet](site-generator-air-detail.png),
[salt distribution](site-salt-distribution-draft.png) and
[fuel bundle section](site-fuel-bundle-detail.png).

The [site report](site-report.json) records selected geometry checks, with no
unresolved clashes in the annex, salt, gas and fresh-air screens. The lowered
inlet screen checks 15 nearby comparisons, finding about 95 mm minimum pipe
envelope clearance. Cold-header nominal clear section is 6.25 m²; the local
column pocket beside coolant storage narrows it to 4.725 m². These are visual
geometry checks, not airflow, pressure-loss, structural or process qualification.

The [manifest](manifest.json) records sizes, SHA-256 hashes and source paths.
Routine `outputs/` remains ignored. Earlier named baselines remain intact.
The inherited installation and report exactly match the retained
[maintenance checkpoint](../wistr-maintenance-2026-10-12/).

To rebuild on a fresh checkout, copy that checkpoint's `wistr-installation.blend`
and `wistr-model-report.json` into `outputs/installation-under-cover-bundles/`,
then run `scripts/build_site.py` in Blender with
`-- --output outputs/site-45-bends --with-piping --build-only --view process`.
See the [site guide](../../docs/site-study.md) for preview scripts and scope.
