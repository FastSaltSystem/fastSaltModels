"""Removable air collectors and open ducts for the isolated visual study."""
import math
import bpy
from mathutils import Vector


def air_dimensions(layout, d):
    a=layout.AIR_SYSTEM
    roof=d['top_z']+a['hood_clear_height']
    top=roof+a['insulation']+2*a['skin']
    cold_top=top+a['cold_roof_clearance']+a['skin']
    return dict(roof=roof,top=top,base=d['top_z']+.08,
                hot_inner=d['hot_baffle_inner_radius']-a['insulation']-a['skin'],
                partition_inner=d['hot_baffle_inner_radius'],
                partition_outer=d['hot_baffle_outer_radius'],
                cold_outer=d['hot_well_inner_radius']+a['well_wall_coverage']*layout.PRESENTATION['well_wall'],
                cold_top=cold_top,stub_top=cold_top+a['stub_height'],
                hot_duct_x=a['duct_center_spacing']/2,cold_duct_x=-a['duct_center_spacing']/2,
                insulation_full_height=d['top_z']+.50)


def build_air_system(b,layout,d):
    from .reactor_geometry import arrow
    a=layout.AIR_SYSTEM;q=air_dimensions(layout,d);s=a['skin']
    for name,color,metal in [('air_hot_shell','#A76B42',.35),('air_cold_shell','#527F9E',.35),
                              ('insulation','#D9BF7C',0),('air_hot_flow','#C97332',0)]:
        b.material(name,color,metallic=metal)
    hot=b.assembly('reactor.hot_air_hood','Air collectors')
    hot['removable_for_sector_access']=True
    hot['purpose']='Collect air rising between vessel and baffle and across the vessel top'
    # The baffle continues as the chamber partition. Insulation lies on its hot side.
    b.annulus('partition',hot,q['partition_inner'],q['partition_outer'],q['base'],q['top'],'air_hot_shell')
    # Taper the insulation above the spider's overhanging outer ring, preserving
    # the return-air entrance instead of obstructing it with a square insulation lip.
    def revolved(name,profile,material):
        n=128;m=len(profile)
        verts=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for i in range(n) for r,z in profile]
        faces=[(i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m) for i in range(n) for j in range(m)]
        return b.mesh(name,hot,verts,faces,material)
    r0=q['partition_inner'];r1=q['hot_inner'];transition=q['insulation_full_height']
    revolved('wall_insulation',[(r0,q['base']),(r1+s,transition),(r1+s,q['roof']+s),(r0,q['roof']+s)],'insulation')
    revolved('wall_liner',[(r0-s,q['base']),(r1,transition),(r1,q['roof']+s),
                          (r1+s,q['roof']+s),(r1+s,transition),(r0,q['base'])],'steel')
    def roof_plate(name,root,radius,z0,z1,material,ports):
        plate=b.cylinder(name,root,radius,z1-z0,(0,0,(z0+z1)/2),material,vertices=128,bevel=0)
        for i,x in enumerate(ports):
            cutter=b.cylinder(f'{name}_port_{i}',root,a['duct_diameter']/2,z1-z0+.2,
                              (x,0,(z0+z1)/2),None,vertices=64,bevel=0)
            b.cut(plate,cutter)
        return plate
    for name,z0,z1,mat in [('roof_liner',q['roof'],q['roof']+s,'steel'),
                           ('roof_insulation',q['roof']+s,q['top']-s,'insulation'),
                           ('roof_cladding',q['top']-s,q['top'],'air_hot_shell')]:
        roof_plate(name,hot,q['partition_inner'],z0,z1,mat,[q['hot_duct_x']])
    cold=b.assembly('reactor.cold_air_ring','Air collectors')
    cold['purpose']='Enclose the hot hood on top and sides; distribute incoming air to the well-side annulus'
    cold['well_wall_coverage']=a['well_wall_coverage']
    b.annulus('outer_wall',cold,q['cold_outer'],q['cold_outer']+s,d['top_z']+.12,q['cold_top'],'air_cold_shell')
    # The concrete wall supports the wider ring; its open inner edge feeds the existing downflow passage.
    b.annulus('wall_seat',cold,d['hot_well_inner_radius'],q['cold_outer']+s,
              d['top_z']+.12,d['top_z']+.12+s,'air_cold_shell')
    roof_plate('roof',cold,q['cold_outer']+s,q['cold_top']-s,q['cold_top'],'air_cold_shell',
               [q['hot_duct_x'],q['cold_duct_x']])
    b.annulus('demountable_seam',cold,q['cold_outer']-.025,q['cold_outer']+s,
              q['cold_top'],q['cold_top']+.025,'steel')
    ducts=b.assembly('reactor.air_ducts','Air ducts')
    radius=a['duct_diameter']/2
    for name,x,bottom,material in [('hot_stub',q['hot_duct_x'],q['roof']-.02,'air_hot_shell'),
                                  ('cold_stub',q['cold_duct_x'],q['cold_top']-s-.02,'air_cold_shell')]:
        stub=b.annulus(name,ducts,radius-a['duct_wall'],radius,bottom,q['stub_top'],material,steps=64)
        stub.location.x=x
        stub['outside_diameter']=2*radius;stub['open_ends']=True
        stub['connection']='Short stub for later external duct routing'
        flange=b.annulus(name+'_flange',ducts,radius,radius+.07,q['stub_top']-.05,q['stub_top'],'steel',steps=64)
        flange.location.x=x
    flow=b.assembly('reactor.air_flow','Air path arrows');y=-.13
    cold_upper=(q['partition_outer']+q['cold_outer'])/2
    cold_neck=(d['hot_baffle_outer_radius']+d['hot_well_inner_radius'])/2
    cold_lower=(d['baffle_outer_radius']+d['well_inner_radius'])/2
    hot_upper=(d['hot_outer_radius']+d['hot_baffle_inner_radius'])/2
    hot_lower=(d['vessel_outer_radius']+d['baffle_inner_radius'])/2
    cold_step=(d['baffle_step_z']-layout.PRESENTATION['baffle_thickness']+d['well_step_z'])/2
    hot_step=(d['hot_plenum_z']-layout.PRESENTATION['vessel_wall']+d['baffle_step_z'])/2
    cold_cross_z=q['top']+a['cold_roof_clearance']/2
    arrow(b,'supply',flow,[(q['cold_duct_x'],y,q['stub_top']-.10),(q['cold_duct_x'],y,cold_cross_z),
                          (-cold_upper,y,cold_cross_z),(-cold_upper,y,d['top_z']+.35),
                          (-cold_neck,y,d['top_z']+.25),(-cold_neck,y,5.9)],'air',.038)
    arrow(b,'down_by_well',flow,[(-cold_neck,y,5.65),(-cold_neck,y,cold_step),(-cold_lower,y,cold_step),
                               (-cold_lower,y,-.37),(-.50,y,-.37),(-.50,y,-.13)],'air',.032)
    collar_path=(d['hot_outer_radius']+.12+q['partition_inner'])/2
    arrow(b,'heated_return',flow,[(-.70,y,-.12),(-hot_lower,y,-.12),(-hot_lower,y,hot_step),
                                (-hot_upper,y,hot_step),(-hot_upper,y,d['top_z']-.20),
                                (-collar_path,y,d['top_z']-.20),(-collar_path,y,d['top_z']+.16),
                                (-(q['hot_inner']-.10),y,d['top_z']+.40),
                                (-2,y,d['top_z']+.65)],'air_hot_flow',.032)
    arrow(b,'above_vessel',flow,[(-1.8,y,d['top_z']+.65),(q['hot_duct_x'],y,d['top_z']+.65),
                                (q['hot_duct_x'],y,q['stub_top']-.10)],'air_hot_flow',.045)
    return q


def check_air_system(b,layout,d):
    from .reactor_checks import closed_mesh
    q=air_dimensions(layout,d);a=layout.AIR_SYSTEM
    for name in ('Air collectors','Air ducts'):
        for obj in b.collection(name).objects:
            if obj.type=='MESH':closed_mesh(obj)
    # Rays verify the two open stubs and that the cold inlet cannot pass into the hot hood.
    def hit(name,origin,direction,distance):
        obj=bpy.data.objects[name]
        inverse=obj.matrix_world.inverted()
        return obj.ray_cast(inverse @ Vector(origin),inverse.to_3x3() @ Vector(direction),distance=distance)[0]
    hx=q['hot_duct_x'];cx=q['cold_duct_x'];r=a['duct_diameter']/2
    for name,x in [('hot_stub',hx),('cold_stub',cx)]:
        assert not hit('reactor.air_ducts.'+name,(x,0,q['stub_top']+.1),(0,0,-1),2)
        assert not hit('reactor.cold_air_ring.roof',(x,0,q['cold_top']+.1),(0,0,-1),.3)
    for name in ('roof_liner','roof_insulation','roof_cladding'):
        assert not hit('reactor.hot_air_hood.'+name,(hx,0,q['roof']-.1),(0,0,1),1)
        assert hit('reactor.hot_air_hood.'+name,(cx,0,q['roof']-.1),(0,0,1),1)
    # Hot-stub wall isolates its exhaust from the cold-air space it passes through.
    cross_z=q['top']+a['cold_roof_clearance']/2
    assert hit('reactor.air_ducts.hot_stub',(hx-r-.1,0,cross_z),(1,0,0),.2)
    assert not hit('reactor.cold_air_ring.outer_wall',(cx,0,cross_z),(-1,0,0),q['cold_outer']+cx-.05)
    assert not hit('reactor.hot_air_hood.partition',(cx,0,cross_z),(-1,0,0),q['cold_outer']+cx-.05)
    assert hit('reactor.hot_air_hood.partition',(-q['cold_outer']+.03,0,q['roof']-.2),(1,0,0),1)
    neck=(q['partition_outer']+d['hot_well_inner_radius'])/2
    assert not hit('reactor.cold_air_ring.wall_seat',(-neck,0,d['top_z']+.3),(0,0,-1),.3)
    assert math.isclose(q['cold_outer']-q['partition_outer'],.56,abs_tol=1e-6)
    assert q['cold_outer']+a['skin']<d['hot_well_outer_radius']
    assert hx-cx>2*r+.14  # Stub flanges remain separate.
    assert 'reactor.air_ducts.exhaust_duct_and_stack' not in bpy.data.objects
    assert q['roof']>d['top_z']+layout.PRESENTATION['cap_thickness']+.15
    # The tapered liner clears the spider-ring overhang at its top elevation.
    z=d['top_z']+.15
    t=(z-q['base'])/(q['insulation_full_height']-q['base'])
    liner_radius=(q['partition_inner']-a['skin'])*(1-t)+q['hot_inner']*t
    assert liner_radius>d['hot_outer_radius']+.12+.05
    assert not hit('reactor.hot_air_hood.wall_liner',((liner_radius+d['hot_outer_radius']+.12)/2,0,z),(0,0,-1),.20)
    return {'dimensions':q,'parameters':a,'open_supply_and_exhaust':True,
            'hot_cold_partition_checked':True,'cold_hood_surrounds_hot_roof_and_sides':True,
            'cold_ring_clear_radial_width':q['cold_outer']-q['partition_outer'],
            'short_central_stubs_only':True,
            'thermal_or_airflow_analysis':False,'hood_removal_required_for_sector_extraction':True}
