"""Isolated WISTR visual study. Metres, Z up; internal bottom is Z=0.

Owner dimensions are kept apart from provisional presentation dimensions.
This module describes geometry only; it has no thermal or neutronic model.
"""
import math

CORE = {"diameter": 3.8, "height": 3.4, "sectors": 6}
LAYERS = {
    "radial_reflector": .30,
    "bottom_reflector": .30,
    "top_reflector": .25,
    "downcomer": 1.00,
    "bottom_plenum": .75,
    "hot_plenum": 1.60,  # Enlarged to fit the 1.4 m outlet, with .1 m above/below.
}
CONNECTIONS = {
    "pipe_diameter": 1.4,
    "count_per_level": 3,
    "cold_angle_offset": 0.0,
    "hot_angle_offset": 30.0,
}
SUPPORTS = {
    "count": 12,
    "wall_thickness": .02,
    "central_clear_diameter": .30,
    "angle_offset": 15.0,  # Two pedestals within each 60-degree sector.
    "pedestal_diameter": LAYERS['radial_reflector'],
    "lip_width": .20,
    "lip_thickness": .02,
    "passage_diameter": .10,
    "stiffener_diameter": .02,
    "stiffener_wall": .002,
    "stiffener_pitch": .20,
}
MAINTENANCE = {"sector": 3, "enabled": True}
ABSORBER_TUBES = {
    "diameters": [.025, .050],
    "wall_thickness": .002,  # Provisional visual wall thickness.
    "floor_centre_height": .25,
    "stack_pitch": .055,
    "pair_connection_spacing": .055,
    "riser_pitch": .060,  # Four side-by-side wall risers.
    "above_cap": .10,
    "wall_clearance": .015,
    "bend_radius": .05,
    "spider_hole_clearance": .001,
}
CORE_TUBES = {
    "diameters": [.025, .050], "wall_thickness": .002,
    "radial_positions": [.35, .95, 1.70],
    "cap_riser_radius": 1.95,
    "radial_edge_lane": .075,
    "bottom_slot_radii": [2.11, 2.04, 1.97],
    "top_pair_radial_offset": .05,
    "pair_vertical_offset": .06,
    "bottom_riser_lanes": [.30, .42, .54],
    "top_riser_lanes": [.36, .48, .60],
    "bottom_run_heights": [.82, .90, .98],
    "additional_rise_before_bend": .30,

    "above_cap": .10, "cutout_clearance": .01, "bend_radius": .04,
}
SEPARATOR_SUPPORTS = {
    "radial_height": .20,
    "absorber_thickness_multiple": 2.0,
    "ledge_height_multiple": 2.0,
    "link_clearance": .03,
    "inlet_clearance": .03,
}
AIR_SYSTEM = {
    # Provisional collector/duct dimensions; the previous exhaust diameter is retained.
    "hood_clear_height": 1.40,
    "insulation": .12,
    "skin": .008,
    "duct_diameter": 2.0,
    "duct_wall": .02,
    "cold_roof_clearance": .60,
    "well_wall_coverage": .85,
    "duct_center_spacing": 2.30,
    "stub_height": .80,
}
PRESENTATION = {
    "vessel_wall": .07,
    "vessel_bottom": .08,
    "cap_thickness": .12,
    "cap_radial_clearance": .10,
    "cap_tube_clearance": .02,  # Retain the former relief allowance, now around a circular opening.
    "downcomer_roof_thickness": .04,
    "support_height": .40,
    "vessel_to_baffle_gap": .22,
    "baffle_thickness": .012,
    "baffle_to_well_gap": .22,
    "well_wall": .40,
    "well_floor": .30,
    "baffle_bottom_z": -.26,
    "baffle_turn_opening_radius": .65,
    "absorber_tank_width": .08,
    "central_clearance_radius": .14,
    "spider_beam_depth": .15,
    "spider_ring_inset": .08,
    "extraction_clearance": .03,
    "spider_web_thickness": .015,
    "spider_web_height": .05,
    "tube_pattern_pitch": .085,
    "tube_pattern_radius": .024,
    "link_lower_above_core_base": .60,
    "link_upper_above_core_base": 2.80,
    "link_pair_spacing": 1.50,
    "link_width": .065 * 4,
    "link_depth": .075 * 4,
    "pin_radius": .075,
    "pin_hole_clearance": .003,
    "moving_link_clearance": .02,
    "cold_inlet_roof_clearance": .10,
}


def linkage_dimensions():
    p=PRESENTATION
    reflector_r=CORE['diameter']/2+LAYERS['radial_reflector']
    lower_r=reflector_r+LAYERS['downcomer']
    half=p['link_pair_spacing']/2
    moving=math.sqrt(reflector_r**2-(half-p['link_width']/2)**2)+p['link_depth']/2+p['moving_link_clearance']
    fixed=math.sqrt((lower_r-p['link_depth'])**2-half**2)
    return {'moving':moving,'fixed':fixed,'length':fixed-moving}


def hole_centres():
    """One triangular lattice, shared by both reflectors and the core."""
    p=PRESENTATION;r=CORE['diameter']/2;pitch=p['tube_pattern_pitch']
    margin=p['absorber_tank_width']/2+.008+p['tube_pattern_radius']+.012
    origin=(math.sqrt(3)*margin,margin)
    centres=[]
    for i in range(int(2*r/pitch)+1):
        for j in range(int(2*r/pitch)+1):
            x=origin[0]+pitch*(i+j/2);y=origin[1]+pitch*math.sqrt(3)*j/2
            radius=math.hypot(x,y)
            if p['central_clearance_radius']+p['tube_pattern_radius']+.01<radius<r-p['tube_pattern_radius']-.02:
                centres.append((x,y))
    return centres


def raised_core_tube_envelope():
    """Conservative radial bound for every tube, including its curved meeting bends.

    Rounded path corners stay within the control-point hull. Adding the outer
    tube radius bounds the complete tube wall without depending on Blender.
    """
    t=CORE_TUBES;travel=linkage_dimensions()['length']
    dx=travel*math.cos(math.pi/6);dy=travel*.5
    radii=[]
    for rank,x in enumerate(t['radial_positions']):
        for connection,diameter in zip(('top','bottom'),t['diameters']):
            gather=t['bottom_slot_radii'][rank]-(t['top_pair_radial_offset'] if connection=='top' else 0)
            lane=t['radial_edge_lane'];gy=t[connection+'_riser_lanes'][rank]
            cap_x=math.sqrt(t['cap_riser_radius']**2-gy**2)
            radii.extend(math.hypot(px+dx,py+dy)+diameter/2
                         for px,py in ((x,lane),(gather,lane),(gather,gy),(cap_x,gy)))
    return max(radii)


def dimensions():
    r = CORE['diameter']/2
    bottom_reflector_z = LAYERS['bottom_plenum']
    core_z = bottom_reflector_z + LAYERS['bottom_reflector']
    top_reflector_z = core_z + CORE['height']
    hot_z = top_reflector_z + LAYERS['top_reflector']
    top_z = hot_z + LAYERS['hot_plenum']
    reflector_r = r + LAYERS['radial_reflector']
    vessel_inner_r = reflector_r + LAYERS['downcomer']
    vessel_outer_r = vessel_inner_r + PRESENTATION['vessel_wall']
    travel=linkage_dimensions()['length']
    raised_separator_radius=vessel_inner_r+travel
    hot_inner_r=(raised_separator_radius+PRESENTATION['extraction_clearance'])/math.cos(math.pi/128)+PRESENTATION['spider_ring_inset']
    # Separator edges are 2 mm clear of each radial sector boundary.
    spider_width=2*(travel*.5+.002-PRESENTATION['extraction_clearance'])
    if hot_inner_r<=vessel_inner_r:
        raise ValueError('Hot plenum must be wider than the lower vessel.')
    hot_outer_r = hot_inner_r + PRESENTATION['vessel_wall']
    baffle_inner_r = vessel_outer_r + PRESENTATION['vessel_to_baffle_gap']
    baffle_outer_r = baffle_inner_r + PRESENTATION['baffle_thickness']
    hot_baffle_inner_r = hot_outer_r + PRESENTATION['vessel_to_baffle_gap']
    hot_baffle_outer_r = hot_baffle_inner_r + PRESENTATION['baffle_thickness']
    well_inner_r = baffle_outer_r + PRESENTATION['baffle_to_well_gap']
    hot_well_inner_r = hot_baffle_outer_r + PRESENTATION['baffle_to_well_gap']
    baffle_step_z = hot_z-PRESENTATION['vessel_wall']-PRESENTATION['vessel_to_baffle_gap']
    well_step_z = baffle_step_z-PRESENTATION['baffle_thickness']-PRESENTATION['baffle_to_well_gap']
    seat_z=hot_z-PRESENTATION['downcomer_roof_thickness']
    # Conservative outer corner of either parallel bar in the upright pose.
    upright_link_radius=math.hypot(linkage_dimensions()['fixed']+PRESENTATION['link_depth']/2,
                                  (PRESENTATION['link_pair_spacing']+PRESENTATION['link_width'])/2)
    ledge_inner=(upright_link_radius+SEPARATOR_SUPPORTS['link_clearance'])/math.cos(math.pi/128)
    ledge_width=vessel_inner_r-ledge_inner
    if ledge_width<=0:raise ValueError('No room for the separator ledge outside the upright links.')
    ledge_height=SEPARATOR_SUPPORTS['ledge_height_multiple']*ledge_width
    radial_height=SEPARATOR_SUPPORTS['radial_height']
    bottom_support_z=bottom_reflector_z+radial_height/2
    top_support_z=seat_z-radial_height/2
    inlet_top=min(hot_z-PRESENTATION['cold_inlet_roof_clearance'],
                  seat_z-max(radial_height,ledge_height)-SEPARATOR_SUPPORTS['inlet_clearance'])
    return dict(core_radius=r, reflector_radius=reflector_r,
                vessel_inner_radius=vessel_inner_r, vessel_outer_radius=vessel_outer_r,
                hot_inner_radius=hot_inner_r, hot_outer_radius=hot_outer_r,
                raised_separator_radius=raised_separator_radius,spider_beam_width=spider_width,spider_hub_radius=spider_width,
                maintenance_travel=travel,
                raised_core_tube_radius=raised_core_tube_envelope(),
                cap_opening_radius=max(r+travel+PRESENTATION['cap_radial_clearance'],
                                       raised_core_tube_envelope()+PRESENTATION['cap_tube_clearance'])/math.cos(math.pi/128),
                separator_seat_z=seat_z,ledge_inner_radius=ledge_inner,
                ledge_width=ledge_width,ledge_height=ledge_height,
                absorber_brace_width=SEPARATOR_SUPPORTS['absorber_thickness_multiple']*PRESENTATION['absorber_tank_width'],
                absorber_brace_centres=[bottom_support_z,(bottom_support_z+top_support_z)/2,top_support_z],
                baffle_inner_radius=baffle_inner_r, baffle_outer_radius=baffle_outer_r,
                hot_baffle_inner_radius=hot_baffle_inner_r, hot_baffle_outer_radius=hot_baffle_outer_r,
                well_inner_radius=well_inner_r,
                well_outer_radius=well_inner_r+PRESENTATION['well_wall'],
                hot_well_inner_radius=hot_well_inner_r,
                hot_well_outer_radius=hot_well_inner_r+PRESENTATION['well_wall'],
                baffle_step_z=baffle_step_z, well_step_z=well_step_z,
                pipe_end_radius=hot_well_inner_r+PRESENTATION['well_wall']+.85,
                floor_z=-PRESENTATION['vessel_bottom']-PRESENTATION['support_height'],
                bottom_reflector_z=bottom_reflector_z, core_z=core_z,
                top_reflector_z=top_reflector_z, hot_plenum_z=hot_z, top_z=top_z,
                cold_inlet_z=inlet_top-CONNECTIONS['pipe_diameter']/2,
                hot_outlet_z=hot_z+LAYERS['hot_plenum']/2)


ASSUMPTIONS = [
    'Caps cover openings sized for the raised core, top reflector and attached service tubes, with at least 100 mm radial clearance for the core. The spider outer band fills the remaining roof area. Peripheral and bottom reflectors and separators remain below this opening.',
    'Each absorber has two pairs of 25/50 mm OD tubes, vertically stacked at 55 mm pitch across the plenum, with the lowest centreline 250 mm above the plenum floor. At the wall they fan out to four side-by-side risers at 60 mm pitch, through the enlarged spider, ending 100 mm above cap plate tops. Walls, bends, wall attachment clips and route offsets are provisional.',
    'Each sector carries three core service pairs. All six tubes remain in one radial plane 75 mm inside the sector edge until the top tubes meet the bottom tubes. Bottom 50 mm runs are vertically stacked in a single upward/edge-open groove and rise in one radial slot in the peripheral reflector. Top 25 mm runs retain the extra 300 mm rise and follow that same plane to their paired bottom tube. Above the reflector, the paired bundles offset into the existing cap opening, ending 100 mm above its seated top.',
    'The common slot reaches 110 mm from the nominal sector boundary, only 62 mm into the reflector beyond its 48 mm edge gap. Bottom riser positions 2.11, 2.04 and 1.97 m are nested to avoid crossings. Staggered heights, pair offsets, cap fan-out, 2 mm tube walls and 10 mm slot clearance remain provisional. Bore-footprint comparisons use the illustrative 85 mm lattice and measure geometric intersections, not coolant flow loss. External service disconnections are not modeled.',
    'The caps have smooth enlarged outer arcs and the spider has a correspondingly narrower outer annulus, without local tube reliefs or cap extensions. The circular opening is sized from the conservative raised core-tube envelope plus 20 mm, while retaining at least 100 mm radial clearance for the core/top reflector. Tube penetrations in the cap edge and absorber penetrations through the ring remain.',
    'A fixed annular vessel ledge seats the separator underside, 0.04 m below the hot-plenum floor. Its radial projection is limited by the upright link envelope plus provisional 0.03 m clearance; its height is twice its projection.',
    'Three fixed radial braces at each of six absorber locations join the absorber outer end to the vessel wall. Braces are 0.20 m tall and twice the current 0.08 m absorber thickness. Top braces share the separator bearing elevation; bottom braces start at the absorber bottom, with middle braces equally spaced vertically.',
    'Cold inlets are lowered as needed to clear the ledge and top radial braces by a provisional 0.03 m. The ledge and braces extend the leakage path geometrically; leakage rate and load capacity are not calculated.',
    'An insulated hot-air hood is enclosed above and around its sides by the cold-air hood. The cold ring extends over 85 percent of the concrete well wall width, leaving about 52 mm to its outer edge. The partition continues the cooling-air baffle.',
    'Air collectors are removable for sector extraction. Operating air-system views seat all six sectors and fit all six vessel cap pieces; maintenance views omit the collectors and their ducts.',
    'Two short vertical duct stubs are near the centre, one hot and one cold, 2.30 m apart with 2 m outside diameters and 0.02 m walls. Both end 0.80 m above the outer hood. The hot duct passes through the cold-air space in a separate sealed wall; the cold duct opens only to the outer hood. External routing and the stack are omitted for later connection.',
    'Provisional hood dimensions: hot roof underside 1.40 m above vessel top, insulation 0.12 m, metal skins 0.008 m, cold-air clearance above the hot roof 0.60 m. Reduced heat release to the room is a design intent, not a thermal calculation.',
    'The owner confirmed 3.4 m as core height alone, excluding reflectors and plenums.',
    'The owner corrected the core diameter to 3.8 m on 2026-10-07, adopting slide 6 of Fast Salt System 5.pptx over the earlier recalled 3.6 m dimension. The 0.3 m radial reflector and 1.0 m downcomer give a 6.4 m lower vessel internal diameter.',
    'Hot-plenum radius retains the allowance derived from the raised separator envelope, former 0.08 m spider ring inset and provisional 0.03 m clearance. The enlarged spider band now reduces the roof opening independently of the vessel diameter.',
    'Six separator segments are parented to their respective core-sector assemblies, together with the neutron reflectors; they are not attached to the vessel.',
    'The top reflector fits inside the peripheral reflector and rests directly on the core. The peripheral reflector extends alongside it and carries the separator at its upper outer edge.',
    'The hot plenum remains 1.6 m high to fit the 1.4 m pipe. The bottom plenum is reduced by 25 percent to 0.75 m, giving 6.30 m total internal height.',
    'Twelve cylindrical pedestals support the peripheral reflector, at 15 and 45 degrees within each sector. Their 0.30 m diameter matches the reflector width as directed by the owner.',
    'Six 0.02 m radial sheets under the absorbers carry provisional 0.20 m wide by 0.02 m thick bearing lips, supporting the absorber and both neighboring bottom-reflector edges. The central 0.30 m diameter remains clear.',
    'Each support sheet has eighteen provisional 0.10 m diameter coolant openings. Vertical half-tube stiffeners have 0.02 m outside diameter and 0.20 m pitch on both faces; their 0.002 m tube-wall thickness is provisional.',
    'The same pedestals, lipped sheets, passage holes and half-tube stiffeners support the vessel externally, at the existing provisional 0.40 m height. Load capacity and pressure loss are not evaluated.',
    'Vessel metal, cap, spider, well, air clearances and absorber tank widths are presentation assumptions, not supplied dimensions.',
    'Six absorber tanks are represented as radial rectangular envelopes between the sectors; no absorber inventories or operating mechanism are specified.',
    'Aligned through-bores in top reflector, core and bottom reflector use a triangular lattice with rows parallel to the sector edges. The existing illustrative 0.085 m pitch and 0.048 m bore diameter are retained; these are visual geometry, not a specified tube design.',
    'Each sector has two upper and two lower links in parallel planes spaced 1.5 m apart. Spacing and pivot heights are illustrative. Sector 3 is shown in the raised maintenance pose with four vertical links and its cap removed from view.',
    'Links are 0.26 m wide by 0.30 m deep. Wall-pin centres are set 0.30 m inward from the lower vessel inner surface. Larger clevis mounts join the wall to each pin; sector-side lugs provide 0.02 m nominal bar-to-reflector clearance in the upright pose.',
    'Rounded link ends extend 0.15 m beyond each pin centre. Real through-holes have 0.003 m radial clearance around the 0.075 m radius pins; hole clearance is provisional.',
    'Spider radial-leg widths are derived from the translated separator edge clearance, leaving a provisional 0.03 m passage clearance. Each leg has a welded underside web 0.015 m thick and 0.05 m high.',
    'Maintenance position follows the equal-length parallelogram geometry: outward travel and lift both equal the revised pivot-to-pivot link length. Endpoint alignment is checked; a full collision sweep or mechanical simulation is not performed.',
    'The floor baffle has a central turning opening, twelve pedestal holes and six slots around the externally stiffened support sheets; baffle clearances are provisional.',
    'Three hot outlets and three cold inlets serve three coolant legs. Each set is spaced by 120 degrees; hot outlets have been moved 30 degrees toward the cold inlets, giving a 30 degree stagger and clearing the six absorber tube routes. The shared hot plenum and cold downcomer distribute flow among the six sectors, without external branch manifolds. All pipe outside diameters remain 1.4 m; the illustrative 0.035 m wall gives a 1.33 m clear bore.',
    'Flow arrows trace the paths described by the owner; they do not represent calculated flow, pressure or temperature.',
    'The complete model is retained. The section plane is 0.06 m behind the centre to remove the tanks on the viewing plane and expose the core. The section_cutaway scene property restores complete geometry.',
]
