"""Static WISTR presentation layout. Distances in metres, angles in degrees.

The reference SVG supplies arrangement, not a complete dimensional model.
Keep stated dimensions distinct from illustrative choices when revising this file.
Z is up; plan +Y points toward the top of the source drawing.
"""

from textual_graphics.shared_coolant import ENGINEERING, coolant as shared_coolant

FLOOR_Z = -9.1  # Top of the existing sub-floor slab; old deck datum remains Z=0.

BUILDING = {
    "diameter": 42.0,             # Provisional insulated-pipe layout, 11 October 2026.
    "total_height": None,         # Derived below from generator-to-hoist clearance.
    "lower_level_depth": 9.7,     # SVG label; deck-to-base interpretation.
    "wall_thickness": .65,       # Presentation assumption.
    "dome_rise": 7.5,            # Presentation assumption.
    "intermediate_floor": False,
    "cutaway_angles": (0, 180),  # Retain the rear half; open toward -Y.
}

STEAM_GENERATORS = {
    "count": 3,
    "width": 4.0,                # Owner's stated approximate envelope.
    "height": 17.0,              # Owner's stated approximate envelope.
    "cover_thickness": .13,
    "air_valve_box_size": (2.2,2.2,.6),
    "air_valve_box_xy": (0.0,0.0),
    "radius": 14.0,               # Spread outward for visible connections.
    "angles": (180, 60, 300),
    "rotation_offset": -90.0,
    "frame_height": 0.0,
    "casing_bottom": FLOOR_Z,
}

FUEL_STORAGE = {
    "pair_angles": (120, 240, 0),
    "radius": 12.8,
    "pair_spacing": 2.05,
    "length": 3.5,
    "width": 1.25,
    "height": 5.4,
    "top": FLOOR_Z + 5.4,
    "bay_length": 4.3,
    "bay_width": 4.25,
}

REACTOR = {
    "baseline": "outputs/reactor-study",
    "preserved_baseline": "baselines/wistr-reactor-handling-2026-10-08",
    "source_commit": "working side-air/insulation revision based on 0d981f2",
    "origin_z": -8.32,           # Well floor bottom rests on basement slab at Z=-9.1 m.
    "rotation_degrees": 45.0,  # Coolant pairs straddle the three generator axes.
    "deck_clearance": .15,     # Provisional installation clearance around the well.
}
ACCESS = {"angle": 18.0, "width": 4.5, "height": 6.5,
          "ring_gap_width": 5.5, "inner_radius": 16.5, "outer_radius": 27.0}
COOLANT_STORAGE = {"position": (14.0, -6.5, FLOOR_Z+.90), "radius": 2.0, "height": 8.0, "support_height": .90, "insulation": .350, "cladding": .001}
COOLANT_TRANSFER = {"outside_diameter": .050, "wall": .003, "insulation": .050,
                    "vessel_tap_radius": 2.90, "pump_radius": 12.40,
                    "pipe_z": FLOOR_Z+.40,
                    "scope": "Heated transfer line; provisional wall, insulation, pump and penetrations; not hydraulically sized"}
NITROGEN = {"radius": 28.5, "angle": 330.0, "tank_diameter": 2.5,
            "tank_height": 6.5, "gas_diameter": .050, "liquid_diameter": .025,
            "header_radius": 19.8, "header_z": FLOOR_Z+4.5,
            "header_angles": (315.0,345.0),
            "scope": "Outdoor tank, ambient vaporizer and gas header envelopes; capacity, pressure and demand not selected"}
MAINTENANCE = {
    "platform_bounds": (8.3, 17.0, -3.7, 2.4), "entry_angle": 15.0,
    "cover_bay": (8.65, 13.0, -3.45, .85),
    "cap_bay": (13.4, 16.65, -2.65, .35),
    "cart_radius": 25.0, "loading_radius": 15.5,
    "cart_length": 3.6, "cart_width": 3.25, "cart_deck": .20,
    "canister_inside_diameter": 2.95, "canister_outside_diameter": 3.05,
    "canister_clear_height": 6.0, "canister_base": .05, "canister_lid": .08,
    "scope": "Provisional handling envelopes; platform loads, canister shielding/cooling, cart capacity and lifting procedure unresolved",
}
# Hurmet calculation cases; bore / nominal metal wall / radial insulation in metres.
COOLANT_LEG_TAGS = ("SG-101", "SG-102", "SG-103")  # identity order for 180, 60, 300 degree placements
PIPE_SPECS = {
    **shared_coolant.pipe_specs(ENGINEERING),
    "steam_branch": {"bore": .425, "wall": .115, "insulation": .350},
    "steam_header": {"bore": .725, "wall": .195, "insulation": .350},
    "water_branch": {"bore": .375, "wall": .075, "insulation": .175},
    "water_header": {"bore": .650, "wall": .120, "insulation": .175},
}
for spec in PIPE_SPECS.values():
    spec['bare_od'] = spec['bore'] + 2 * spec['wall']
    spec['jacket_od'] = spec['bare_od'] + 2 * spec['insulation']
PIPING = {"salt_pipe_diameter": PIPE_SPECS['hot']['bare_od'], "riser_x": 8.0,
          "cold_riser_x": 8.0, "specifications": PIPE_SPECS,
          "scope": "Conditional Hurmet dimensions; pressure and material assumptions remain provisional"}
STACKS = {"radius": 27.0, "angles": (135,), "height": 35, "tube_diameter": 3.6,
          "base_z": FLOOR_Z, "base_height": 1.0}
CRANE = {"bridge_y": 4.4, "trolley_x": -2.8, "generator_clearance": 5.0,
         "trolley_centre_offset": 1.3, "trolley_height": .55,
         "wall_top_above_runway": 2.7, "displayed_hook_raise": 3.0}
GENERATOR_TOP_Z = (STEAM_GENERATORS["casing_bottom"] + STEAM_GENERATORS["height"]
                   + STEAM_GENERATORS["cover_thickness"] + STEAM_GENERATORS["air_valve_box_size"][2])
CRANE["body_underside_z"] = GENERATOR_TOP_Z + CRANE["generator_clearance"]
CRANE["runway_height"] = (CRANE["body_underside_z"] - CRANE["trolley_centre_offset"]
                           + CRANE["trolley_height"] / 2)
BUILDING["total_height"] = (CRANE["runway_height"] + CRANE["wall_top_above_runway"]
                             + BUILDING["dome_rise"] + BUILDING["lower_level_depth"])

# Generator frame is rotated -90 degrees about its centre: -Y faces reactor, +Y faces wall.
# Manifold elevations below are relative to casing bottom.
MANIFOLDS = {"collector_scale": 1.5, "side_offset": 3.4, "half_length": 1.4,
             "hot_z": 15.5, "cold_z": 1.9, "steam_z": 15.5, "water_z": 3.5,
             "salt_diameter": PIPE_SPECS["hot"]["bare_od"], "steam_diameter": .655, "water_diameter": .525,
             "collector_bare_diameters": {"hot": 2.1, "cold": 2.1, "steam": 1.2, "water": .75}}
SECONDARY = {"header_radius": 18.5, "exit_radius": 26.0, "exit_angle": 200.0,
             "steam_header_diameter": 1.815, "water_header_diameter": 1.240,
             "water_exit_riser_radius": 19.5, "water_above_air_ring_clearance": 1.7}
PUMPS = {"count": 3, "local_position": (13.0, -6.0, FLOOR_Z + 4.51),
         "casing_diameter": 2.8, "casing_height": 1.8,
         "motor_width": 2.8, "motor_depth": 2.4, "motor_height": 3.2, "motor_bottom": FLOOR_Z + 5.9,
         **shared_coolant.pump_inputs(ENGINEERING),
         "suction_run_z": FLOOR_Z + 1.9,
         "worksheet": "../fastSalt/calculations/steam-generator/Coolant pump estimate - Hurmet.md"}
# Double tank volume with uniform linear scaling; retain the control-box size.
ABSORBER_TANK_SCALE = 2.0 ** (1.0/3.0)
ABSORBER_MODULES = {
    "size": (.85,.9,1.0*ABSORBER_TANK_SCALE+1.5),
    "tank_reference_diameter": .64, "tank_reference_height": 1.0,
    "tank_volume_multiplier": 2.0, "tank_linear_scale": ABSORBER_TANK_SCALE,
    "tank_diameter": .64*ABSORBER_TANK_SCALE, "tank_height": 1.0*ABSORBER_TANK_SCALE,
    "tank_base_z": .12, "control_height": 1.5,
}

# D-038: lower deck and compact under-cover bundles; two stations per absorber.
CATWALK = {"inner_radius": 4.95, "outer_radius": 7.35, "deck_z": -.60,
           "module_radius": 6.60, "drop_radius": 4.50,
           "column_angles": tuple(range(0,360,30))}

# Preliminary standard-stair geometry; structural and egress design remain open.
CATWALK_STAIRS = {"angle": 210.0, "mirror": 1, "radial_offset": 4.90, "tangent_offset": 2.70, "entry_angle": 195.0, "clear_width": 1.20, "tread_width": 1.30,
                  "risers_per_flight": 16, "flights": 3, "going": .28,
                  "landing_depth": 1.20, "handrail_height": .90, "guard_height": 1.10}

# New reservoirs are distinct from the module's existing tank; all sizes are draft allowances.
ABSORBER_RESERVOIRS = {
    "diameter": .64*ABSORBER_TANK_SCALE, "height": ABSORBER_TANK_SCALE,
    "insulation": .10, "cladding": .001, "bottom_above_deck": .55,
    "tank_angle_offset": 5.0, "module_angle_offset": 15.0,
    "pipe_insulation": .05,
}

# Compact routing control points are in installation_bundles.py.
FUEL_SERVICES = {"sector_to_tank": (6,1,2,3,4,5)}

from wistr_air_insulation import AIR_INSULATION

AIR = {"insulation": AIR_INSULATION, "hot_radius": 18.75,
       "hot_z": 10.0,  # Insulated internal header remains below the crane runway.
       "hot_clear_width": 2.50, "hot_clear_height": 2.702,
       "fuel_hot_turn_z": 7.85,
       "hot_diameter": 2.4,  # Stack connector envelope; manifold itself is rectangular.
       "fresh_radius": 22.5, "fresh_z": FLOOR_Z+1.5, "fresh_diameter": 2.0,
       "fresh_start_angle": 0.0, "fresh_end_angle": 360.0,
       "concrete_inner_radius": BUILDING['diameter']/2,
       "concrete_outer_radius": BUILDING['diameter']/2+3.0,
       "concrete_height": 3.0, "concrete_skin": .25,
       "fresh_inside_riser_radius": 19.9,
       "hot_inside_riser_radius": 19.7, "fuel_hot_riser_radius": 19.9,
       "fuel_storage_cross_z": FLOOR_Z+7.0, "reactor_inside_riser_radius": 19.15,
       "intake_angle": 270.0, "intake_radius": 28.0,
       "low_branch_z": FLOOR_Z+.45,
       "generator_hot_diameter": 1.8, "generator_fresh_diameter": .7,
       "fuel_hot_diameter": .5, "fuel_fresh_diameter": .5}

ASSUMPTIONS = [
    "Generator roof exhausts are centred and 1.8 m metal OD; 100 mm insulation plus 1 mm jacket gives 2.002 m outside. Valve housings remain 0.6 m high, preserving the hoist clearance.",
    "Coolant transfer uses 50 mm OD tube with provisional 3 mm wall and 50 mm insulation. A motor-pump envelope connects the reactor bottom to storage bottom. The storage tank is raised 0.9 m and has 350 mm side/top/bottom insulation plus 1 mm jacket. Thermal, structural and hydraulic sizing remain open.",
    "The outdoor liquid-nitrogen tank, ambient vaporizer, regulator envelope and common gas header are provisional visual equipment; demand, capacity, pressure, final siting and individual consumers are not yet defined.",
    "All ten hot-air branches, stack connector/barrel and reactor hot side collector carry a provisional 100 mm insulation allowance with 1 mm metal cladding. Material and thickness are not thermally sized. The upper exterior concrete ring is replaced by a sheet-metal internal header with 2.50 x 2.702 m clear section and external insulation. The reactor exhaust connects directly to the stack at installation angle 135 degrees; cold air remains uninsulated.",
    "Reactor fresh air runs directly along the floor at the fresh-ring centre elevation (1.5 m above floor), with a single rise to the reactor side manifold. The 2 m duct leaves 0.5 m beneath its envelope; support design remains provisional.",
    "Twelve independent absorber reservoir/module stations sit on the shared catwalk, radii 4.95–7.35 m at Z=-0.60 m. Compact insulated absorber and heated maintenance bundles pass beneath liftable open-bottom insulation channels. Absorber salt drains have 1.60 m fall to the spider; gas lines are insulated but unheated. Local insulation strips and extended cover pickups remain provisional, as do frame sizing, heat-trace duty, remote disconnects and stair access.",
    "42 m equipment shell is a provisional expansion of the prior 36 m draft to accommodate insulated process piping. The lower exterior concrete fresh-air ring adds 3 m per side, giving 48 m outer diameter; the hot header is inside the shell.",
    "Pipe bore, metal wall and insulation follow the conditional 11 October Hurmet calculation cases, not approved material or pressure specifications. Separate hollow metal and insulation meshes permit inspection; collector shells remain visual envelopes.",
    "Salt hot/cold: 1.425 m bore, 25 mm nominal wall, 400/350 mm radial insulation. Steam branch/header: 425/725 mm bore, 115/195 mm wall, 350 mm insulation. Water branch/header: 375/650 mm bore, 75/120 mm wall, 175 mm insulation.",
    "Three 4 x 4 x 17 m generators remain on the floor, centres at radius 14 m. Low salt ports rise to 1.9 m and water ports to 3.5 m above floor to clear insulation and the reactor fresh-air duct. Salt collectors face reactor; secondary collectors face wall.",
    "Pumps remain provisional 2 MW vertical centrifugal envelopes with bottom suction and side discharge. Raised open frames leave space for insulated suction bends. No hydraulic losses, pump selection or support loads are recalculated.",
    "The current working reactor with six fitted insulation covers and side air plenums is imported at full scale using a generated hash manifest. Preserved baselines remain unchanged. Installed coolant sleeves retain their conditional bore/wall adaptation.",
    "External salt insulation begins at the reactor connection terminals, outside the concrete well. Vessel and in-well cooling surfaces are not insulated by this revision.",
    "Collector insulation follows the pipe-service radial allowance; D-shaped collector sizes and pressure walls remain provisional and require separate pressure design.",
    "Generator roof valve-box tops retain 5 m clearance to hoist body underside. The intermediate floor and perimeter railings remain absent. Equipment rests on the sub-floor at Z=-9.1 m.",
    "Fuel pairs move to radius 12.8 m, coolant storage to (14,-6.5) m, with fixed sector storage removed in favour of a mobile canister/cart and catwalk-level cover/cap laydown. The 4.5 x 6.5 m entrance and interrupted fresh-air ring remain; full equipment extraction paths are not qualified.",
    "The internal hot header serves three steam generators and six fuel tanks, preserving 6.755 square metres of clear area provisionally for the peak generator heat load. The reactor has a separate straight 2 m exhaust to the aligned stack; no airflow, pressure-drop, thermal or support qualification. Hot header remains below crane; feedwater crossing remains above the exterior fresh ring.",
    "Geometry checks use insulated envelopes, selected equipment bounds and pipe centreline segments. They do not establish complete maintenance access, seismic clearance, pressure integrity or support adequacy.",
]



def manifold_point(kind, end=0):
    """Manifold point in a leg's radial frame, with Z in installation coordinates.

    end is the generator-local X end (-1, 0, +1); generator rotation maps it
    onto the negative tangential direction. Salt faces inward, secondary outward.
    """
    side=-1 if kind in ('hot','cold') else 1
    return (STEAM_GENERATORS['radius']+side*MANIFOLDS['side_offset'],
            -end*MANIFOLDS['half_length'],
            STEAM_GENERATORS['casing_bottom']+MANIFOLDS[kind+'_z'])
