"""Geometric checks for the authored reactor review model."""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix


def closed_mesh(obj):
    mesh=bmesh.new();mesh.from_mesh(obj.data)
    count=sum(not edge.is_manifold for edge in mesh.edges);mesh.free()
    assert count==0,(obj.name,count)


def check_supports(b,d,layout):
    s=layout.SUPPORTS;p=layout.PRESENTATION
    for i in range(1,13):
        pair=[bpy.data.objects[f'reactor.{prefix}_support_{i}.pedestal'] for prefix in ('core','vessel')]
        for obj,bottom,top in zip(pair,(0,d['floor_z']),(d['bottom_reflector_z'],-p['vessel_bottom'])):
            assert math.isclose(obj.dimensions.x,.30,abs_tol=1e-6)
            assert math.isclose(obj.dimensions.y,.30,abs_tol=1e-6)
            assert math.isclose(obj.location.z-obj.dimensions.z/2,bottom,abs_tol=1e-6)
            assert math.isclose(obj.location.z+obj.dimensions.z/2,top,abs_tol=1e-6)
            assert math.isclose(obj.location.x,(d['core_radius']+d['reflector_radius'])/2,abs_tol=1e-6)
            closed_mesh(obj)
        assert pair[0].parent.rotation_euler.z==pair[1].parent.rotation_euler.z
        centre=pair[0].matrix_world.translation.copy();centre.z=d['bottom_reflector_z']-.01
        ref=bpy.data.objects[f'reactor.sector_{(i-1)//2+1}.bottom_reflector']
        assert ref.ray_cast(ref.matrix_world.inverted() @ centre,Vector((0,0,1)))[0]
        centre.z=0
        assert not bpy.data.objects['reactor.baffle.floor_sheet'].ray_cast(centre,Vector((0,0,-1)))[0]
    for i in range(1,7):
        for prefix,bottom,top in (('core',0,d['bottom_reflector_z']),('vessel',d['floor_z'],-p['vessel_bottom'])):
            root=b.assemblies[f'reactor.{prefix}_absorber_support_{i}']
            sheet=bpy.data.objects[root.name+'.perforated_sheet'];lip=bpy.data.objects[root.name+'.bearing_lip']
            ribs=bpy.data.objects[root.name+'.welded_half_tube_stiffeners']
            assert sheet['through_hole_count']==18
            assert math.isclose(lip.dimensions.y,s['lip_width'],abs_tol=1e-6)
            assert math.isclose(lip.location.z+lip.dimensions.z/2,top,abs_tol=1e-6)
            assert ribs['count']==20 and math.isclose(ribs['outside_diameter'],.02)
            assert math.isclose(ribs['pitch'],.2)
            for obj in (sheet,lip,ribs):closed_mesh(obj)
            for j in range(9):
                x=.35+j*.20
                for f in (1/3,2/3):
                    z=bottom+(top-s['lip_thickness']-bottom)*f
                    assert not sheet.ray_cast(Vector((x,-.10,z)),Vector((0,1,0)))[0]
                    assert not ribs.ray_cast(Vector((x,-.10,z)),Vector((0,1,0)))[0]
            for obj in root.children:
                assert min(math.hypot(*(obj.matrix_world @ v.co)[:2]) for v in obj.data.vertices)>=.15-1e-6
            if prefix=='core':
                # Both reflector edges rest on the same absorber-support lip.
                for sign,sector in ((1,i),(-1,(i-2)%6+1)):
                    point=root.matrix_world @ Vector((1.0,sign*.06,top-.01))
                    ref=bpy.data.objects[f'reactor.sector_{sector}.bottom_reflector']
                    assert ref.ray_cast(ref.matrix_world.inverted() @ point,Vector((0,0,1)))[0]
    # Radial flow channels through sector bisectors avoid both pedestals and sheets.
    for category,z in (('Core supports',d['bottom_reflector_z']/2),('Vessel supports',(d['floor_z']-p['vessel_bottom'])/2)):
        objects=[obj for root in b.assemblies.values() if root.get('category')==category for obj in root.children]
        for angle in range(30,360,60):
            a=math.radians(angle);direction=Vector((-math.cos(a),-math.sin(a),0))
            origin=Vector((2.5*math.cos(a),2.5*math.sin(a),z))
            for obj in objects:
                inv=obj.matrix_world.inverted()
                assert not obj.ray_cast(inv @ origin,inv.to_3x3() @ direction)[0],(obj.name,angle)
    return ['Twelve diameter-0.30 m pedestals and six lipped absorber sheets per level, with matching footprints',
            'Seated reflector contact verified at pedestals and both sides of absorber-sheet lips',
            'Eighteen open passages and twenty half-tube stiffeners per sheet; radial sector-bisector paths clear']


def check_bores(b,d,layout):
    centres=layout.hole_centres();p=layout.PRESENTATION;pitch=p['tube_pattern_pitch']
    keys={(round(x,7),round(y,7)) for x,y in centres}
    assert any(all((round(x+dx,7),round(y+dy,7)) in keys for dx,dy in ((pitch,0),(pitch/2,pitch*math.sqrt(3)/2))) for x,y in centres)
    for i in range(1,7):
        for part in ('core','bottom_reflector','top_reflector'):
            obj=bpy.data.objects[f'reactor.sector_{i}.{part}'];closed_mesh(obj)
            assert obj['through_hole_count']==len(centres)
            for x,y in centres:
                assert not obj.ray_cast(Vector((x,y,d['top_z']+1)),Vector((0,0,-1)))[0],(obj.name,x,y)
    for root in b.assemblies.values():
        if root.get('category')!='Four-bar hardware':continue
        length=root['link_length']
        for obj in root.children:
            if obj.get('role')!='fourbar_link':continue
            closed_mesh(obj)
            assert min(v.co.x for v in obj.data.vertices)<-length/2-.149
            assert max(v.co.x for v in obj.data.vertices)>length/2+.149
            for x in (-length/2,length/2):
                assert not obj.ray_cast(Vector((x,-1,0)),Vector((0,1,0)))[0]
                assert obj.ray_cast(Vector((x,-1,.11)),Vector((0,1,0)))[0]
    return {'bores_per_sector_per_layer':len(centres),'total_aligned_passages':6*len(centres),
            'pitch_metres':pitch,'diameter_metres':2*p['tube_pattern_radius'],
            'row_directions_relative_to_sector_degrees':[0,60,120],
            'all_three_layers_have_open_aligned_bores':True,'link_pin_holes_and_overhang_checked':True}


def check_spider_passage(b,d,layout):
    p=layout.PRESENTATION;number=layout.MAINTENANCE['sector'];root=b.assemblies[f'reactor.sector_{number}']
    # Project the complete raised sector and attached hardware into the opening.
    unrotate=Matrix.Rotation(-root.rotation_euler.z,4,'Z')
    points=[unrotate @ (obj.matrix_world @ v.co) for obj in root.children if obj.type=='MESH' for v in obj.data.vertices]
    edge_distance=min(min(v.y,math.sqrt(3)*v.x/2-v.y/2) for v in points)
    leg_clearance=edge_distance-d['spider_beam_width']/2
    ring_apothem=(d['hot_inner_radius']-p['spider_ring_inset'])*math.cos(math.pi/128)
    ring_clearance=ring_apothem-max(math.hypot(v.x,v.y) for v in points)
    assert leg_clearance>=p['extraction_clearance']-2e-6,leg_clearance
    assert ring_clearance>=p['extraction_clearance']-2e-6,ring_clearance
    assert min(math.hypot(v.x,v.y) for v in points)>d['spider_hub_radius']+p['extraction_clearance']
    for i in range(1,7):
        arm=bpy.data.objects[f'reactor.spider.arm_{i}'];web=bpy.data.objects[f'reactor.spider.underside_web_{i}']
        span=lambda obj,axis:max(v.co[axis] for v in obj.data.vertices)-min(v.co[axis] for v in obj.data.vertices)
        assert math.isclose(span(arm,1),d['spider_beam_width'],abs_tol=1e-6)
        assert math.isclose(span(web,1),.015,abs_tol=1e-6) and math.isclose(span(web,2),.05,abs_tol=1e-6)
        assert math.isclose(web.location.z+.025,d['top_z'],abs_tol=1e-6)
    return {'leg_width_metres':d['spider_beam_width'],'minimum_leg_clearance_metres':leg_clearance,
            'minimum_ring_clearance_metres':ring_clearance,'underside_web_thickness_metres':.015,
            'underside_web_height_metres':.05,'raised_sector_vertical_projection_checked':True,
            'full_mechanism_collision_sweep_performed':False}
