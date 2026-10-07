"""Isolated WISTR visual study. Metres, Z up; internal bottom is Z=0.

Owner dimensions are kept apart from provisional presentation dimensions.
This module describes geometry only; it has no thermal or neutronic model.
"""
import math

CORE = {"diameter": 3.6, "height": 3.4, "sectors": 6}
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
    "count_per_level": 6,
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
    return dict(core_radius=r, reflector_radius=reflector_r,
                vessel_inner_radius=vessel_inner_r, vessel_outer_radius=vessel_outer_r,
                hot_inner_radius=hot_inner_r, hot_outer_radius=hot_outer_r,
                raised_separator_radius=raised_separator_radius,spider_beam_width=spider_width,spider_hub_radius=spider_width,
                maintenance_travel=travel,
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
                cold_inlet_z=hot_z-CONNECTIONS['pipe_diameter']/2-PRESENTATION['cold_inlet_roof_clearance'],
                hot_outlet_z=hot_z+LAYERS['hot_plenum']/2)


ASSUMPTIONS = [
    'An insulated hot-air hood is enclosed above and around its sides by the cold-air hood. The cold ring extends over 85 percent of the concrete well wall width, leaving about 52 mm to its outer edge. The partition continues the cooling-air baffle.',
    'Air collectors are removable for sector extraction. Operating air-system views seat all six sectors and fit all six vessel cap pieces; maintenance views omit the collectors and their ducts.',
    'Two short vertical duct stubs are near the centre, one hot and one cold, 2.30 m apart with 2 m outside diameters and 0.02 m walls. Both end 0.80 m above the outer hood. The hot duct passes through the cold-air space in a separate sealed wall; the cold duct opens only to the outer hood. External routing and the stack are omitted for later connection.',
    'Provisional hood dimensions: hot roof underside 1.40 m above vessel top, insulation 0.12 m, metal skins 0.008 m, cold-air clearance above the hot roof 0.60 m. Reduced heat release to the room is a design intent, not a thermal calculation.',
    'The owner confirmed 3.4 m as core height alone, excluding reflectors and plenums.',
    'The 0.3 m radial reflector and 1.0 m downcomer lie outside the 3.6 m core, giving a 6.2 m lower vessel internal diameter.',
    'Hot-plenum radius is derived from the raised separator envelope, plus the spider outer-ring inset and a provisional 0.03 m extraction clearance; the 128-sided ring is allowed for.',
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
    'Six hot and six cold pipes are modeled at 60-degree intervals within each set, staggered by 30 degrees as requested. All pipe diameters remain 1.4 m.',
    'Flow arrows trace the paths described by the owner; they do not represent calculated flow, pressure or temperature.',
    'The complete model is retained. The section plane is 0.06 m behind the centre to remove the tanks on the viewing plane and expose the core. The section_cutaway scene property restores complete geometry.',
]
