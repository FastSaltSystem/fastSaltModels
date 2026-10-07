"""Static WISTR presentation layout. Distances in metres, angles in degrees.

The reference SVG supplies arrangement, not a complete dimensional model.
Keep stated dimensions distinct from illustrative choices when revising this file.
Z is up; plan +Y points toward the top of the source drawing.
"""

BUILDING = {
    "diameter": 28.4,             # Label in the SVG side view.
    "total_height": 34.2,         # SVG label; interpreted as base-to-dome height.
    "lower_level_depth": 9.7,     # SVG label; deck-to-base interpretation.
    "wall_thickness": .65,       # Presentation assumption.
    "dome_rise": 7.5,            # Presentation assumption.
    "deck_thickness": .55,
    "cutaway_angles": (0, 180),  # Retain the rear half; open toward -Y.
}

STEAM_GENERATORS = {
    "count": 3,
    "width": 4.0,                # Owner's stated approximate envelope.
    "height": 10.0,              # Owner's stated approximate envelope.
    "radius": 9.3,               # Layout estimated from the top view.
    "angles": (180, 60, 300),
}

FUEL_STORAGE = {
    "pair_angles": (120, 240, 0),
    "radius": 8.1,
    "pair_spacing": 2.05,
    "length": 3.5,
    "width": 1.25,
    "height": 5.4,
    "top": -.65,
    "bay_length": 4.3,
    "bay_width": 4.25,
}

VESSEL = {"radius": 2.3, "bottom": -8.0, "body_top": -.3, "well_radius": 3.2}
COOLANT_STORAGE = {"position": (9.0, -5.8, 0), "radius": 2.0, "height": 8.0}
SECTOR_STORAGE = {"position": (9.4, 4.0, -3.55), "size": (3.4, 2.4, 5.8)}
PIPING = {"salt_pipe_diameter": 1.4}  # Owner-specified visible diameter.
STACKS = {"radius": 15.5, "angles": (180, 60, 300), "height": 28, "tube_diameter": 2.0}
CRANE = {"runway_height": 14.3, "bridge_y": 4.4, "trolley_x": -2.8}

ASSUMPTIONS = [
    "The SVG's 28.4 m, 34.2 m and 9.7 m labels set the building envelope; 34.2 m is interpreted as overall height including the lower level.",
    "Steam-generator casings use the owner's approximate 4 x 4 x 10 m dimensions; pedestals, rails and fittings extend beyond that envelope.",
    "Equipment centres are estimated from the top-view arrangement, not traced as construction coordinates.",
    "Vessel, storage, stack, wall, dome and crane dimensions not explicitly supplied are illustrative and editable.",
    "The reactor vessel and storage equipment are closed exterior shapes; no core or internal process geometry is constructed.",
    "Molten-salt pipes have an owner-specified visible diameter of 1.4 m; stack tubes have a diameter of 2.0 m. Wall thickness and insulation are not modeled.",
    "Major pipe and duct routes indicate the described connections. Other diameters, bends, supports and pump casings are visual placeholders.",
    "Front shell, front dome and selected floor areas are removed for presentation. The source SVG is retained unchanged under references/.",
    "Flanges, panels, ladders, rails, bolts and concrete details provide visual scale; they are not fabrication specifications.",
]
