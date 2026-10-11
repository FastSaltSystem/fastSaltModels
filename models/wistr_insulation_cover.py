"""Independent WISTR removable insulation-cover concept. Metres; unrated hardware."""
import math
import wistr_reactor as reactor

COVER = {
    'radius': reactor.dimensions()['hot_outer_radius'] + .220,
    'sectors': 6, 'insulation': .500, 'layers': 5, 'density': 128.,
    'seam_half_gap': .006, 'skin': .002, 'liner': .002,
    'frame_bottom': .420, 'frame_height': .040,
    'zirconia_diameter': .050, 'zirconia_height': .075,
    'zirconia_top': -.025, 'post_width': .040, 'post_wall': .002,
    'hanger_diameter': .006,
    'travel': .040, 'stem_width': .030, 'frame_slot': .050,
    'guide_slot': .038, 'shoulder_width': .120, 'shoulder_depth': .100,
    'shoulder_thickness': .020, 'hook_foot': .610,
    'guide_bottom': .535, 'guide_top': .550,
    'collar_thickness': .012, 'mesh_pitch': .200, 'mesh_wire_radius': .0015,
    'lift_sector': 1, 'lift_height': 1.50,
    # Spatial reservation only; service penetrations and supports need integration.
    'installed_bottom_z': 7.20,
}

def points():
    """Same bar pitch, hook section and transverse positions as the common head.

    Translate the complete pickup pattern to centre it on the uniform wedge's
    centroid; actual steel/insulation mass balance remains to be established.
    """
    c=reactor.LIFTING_INTERFACE
    cx=2*COVER['radius']/math.pi
    mean=sum(c['stations'])/2
    return [(cx+x-mean,side*(x-2*c['core_edge_offset'])/math.sqrt(3),station)
            for side in (-1,1) for station,x in enumerate(c['stations'])]

def post_points():
    pts=points();y=max(abs(p[1]) for p in pts)+.15
    return [(x,side*y) for x in sorted(set(p[0] for p in pts)) for side in (-1,1)]

def wool_holes():
    return [(x,y,.092) for x,y,_ in points()]+[(x,y,.033) for x,y in post_points()]

def outline():
    r=COVER['radius'];g=COVER['seam_half_gap']
    a=math.pi/6-math.asin(g/r)
    return [(2*g,0)]+[(r*math.cos(-a+2*a*j/64),r*math.sin(-a+2*a*j/64)) for j in range(65)]

def summary():
    c=COVER;a=math.pi*c['radius']**2
    return {'gross_area_m2':a,'gross_wool_mass_kg':a*c['insulation']*c['density'],
            'gross_wool_mass_per_sector_kg':a*c['insulation']*c['density']/6,
            'pickup_centroid_radius_m':2*c['radius']/math.pi,
            'bar_pitch_m':reactor.LIFTING_INTERFACE['stations'][1]-reactor.LIFTING_INTERFACE['stations'][0],
            'resting_shoulder_gap_m':c['travel'],
            'bearing_overlap_per_side_m':(c['shoulder_width']-c['frame_slot'])/2,
            'stem_frame_clearance_per_side_m':(c['frame_slot']-c['stem_width'])/2,
            'stem_guide_clearance_per_side_m':(c['guide_slot']-c['stem_width'])/2,
            'scope':'Visual mechanical concept; no rated capacity, thermal bridge result, complete service routing or automatic-return qualification.'}
