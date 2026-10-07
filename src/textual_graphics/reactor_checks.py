"""Geometric checks for the authored reactor review model."""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree


def check_separator_supports(b,d,layout):
    scene=bpy.context.scene;raised=scene['maintenance_position']
    root=b.assemblies['reactor.separator_supports'];ring=bpy.data.objects[root.name+'.wall_ledge']
    braces=[o for o in root.children if o.get('level')]
    assert len(braces)==18
    assert math.isclose(d['ledge_height'],2*d['ledge_width'])
    assert math.isclose(max(v.co.z for v in ring.data.vertices),d['hot_plenum_z']-layout.PRESENTATION['downcomer_roof_thickness'],abs_tol=1e-6)
    assert math.isclose(d['absorber_brace_width'],2*layout.PRESENTATION['absorber_tank_width'])
    initial={o.name:o.matrix_world.copy() for o in root.children}
    for obj in root.children:closed_mesh(obj)
    scene['maintenance_position']=False;scene.update_tag();bpy.context.view_layer.update()
    for i in range(1,7):
        separator=bpy.data.objects[f'reactor.sector_{i}.separator']
        radius=(d['ledge_inner_radius']+d['vessel_inner_radius'])/2
        # Ring contact below the middle of each seated separator's outer edge.
        local=Vector((radius*math.cos(math.pi/6),radius*.5,d['separator_seat_z']+.01))
        point=separator.matrix_world @ local
        hit,where,*_=ring.ray_cast(point,Vector((0,0,-1)))
        assert hit and abs(where.z-d['separator_seat_z'])<1e-6
        for level,z in zip(('bottom','middle','top'),d['absorber_brace_centres']):
            brace=bpy.data.objects[f'{root.name}.absorber_{i}_{level}']
            assert math.isclose(brace.dimensions.z,.20,abs_tol=1e-6)
            assert math.isclose(brace.dimensions.y,d['absorber_brace_width'],abs_tol=1e-6)
            # Each beam starts at the absorber's outer end and reaches the wall.
            assert math.isclose(brace.location.z,z,abs_tol=1e-6)
            if level=='top':
                assert math.isclose(z+.1,d['separator_seat_z'],abs_tol=1e-6)
                a=math.radians((i-1)*60);radius=(d['reflector_radius']+d['ledge_inner_radius'])/2
                for side,number in ((1,i),(-1,(i-2)%6+1)):
                    point=Vector((radius*math.cos(a)-side*.04*math.sin(a),
                                  radius*math.sin(a)+side*.04*math.cos(a),d['separator_seat_z']-.01))
                    sep=bpy.data.objects[f'reactor.sector_{number}.separator']
                    assert sep.ray_cast(sep.matrix_world.inverted() @ point,Vector((0,0,1)))[0]
    inlet_top=d['cold_inlet_z']+layout.CONNECTIONS['pipe_diameter']/2
    lowest_top_support=d['separator_seat_z']-max(d['ledge_height'],layout.SEPARATOR_SUPPORTS['radial_height'])
    assert lowest_top_support-inlet_top>=layout.SEPARATOR_SUPPORTS['inlet_clearance']-1e-6
    def tree(obj):
        return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                                   [tuple(p.vertices) for p in obj.data.polygons])
    supports=[(o,tree(o)) for o in root.children]
    number=layout.MAINTENANCE['sector']
    moving=b.assemblies[f'reactor.sector_{number}']
    hardware=b.assemblies[f'reactor.fourbar_{number}']
    tested=[o for o in hardware.children if o.get('role')=='fourbar_link']
    tested += [o for o in moving.children if '_moving_pin' in o.name or '_moving_cheek_' in o.name]
    for pose in (False,True):
        scene['maintenance_position']=pose;scene.update_tag();bpy.context.view_layer.update()
        for obj in tested:
            mesh=tree(obj)
            for support,bvh in supports:
                assert not mesh.overlap(bvh),(pose,obj.name,support.name)
        assert all(o.matrix_world==initial[o.name] for o in root.children)
    links=[o for o in tested if o.get('role')=='fourbar_link']
    envelope=max(math.hypot(*(o.matrix_world @ v.co)[:2]) for o in links for v in o.data.vertices)
    clearance=d['ledge_inner_radius']*math.cos(math.pi/128)-envelope
    assert clearance>=layout.SEPARATOR_SUPPORTS['link_clearance']-2e-6
    scene['maintenance_position']=raised;scene.update_tag();bpy.context.view_layer.update()
    return {'ledge_radial_width':d['ledge_width'],'ledge_height':d['ledge_height'],
            'bearing_elevation':d['separator_seat_z'],'upright_link_radial_clearance':clearance,
            'radial_support_count':len(braces),'radial_support_height':.20,
            'radial_support_width':d['absorber_brace_width'],'cold_inlet_top_clearance':lowest_top_support-inlet_top,
            'seated_separator_contacts_checked':True,'links_and_moving_hardware_clear_in_both_poses':True,
            'full_motion_sweep_checked':False,'leakage_or_load_analysis':False}


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
    # Project the raised core and top reflector into the reduced opening.
    unrotate=Matrix.Rotation(-root.rotation_euler.z,4,'Z')
    points=[unrotate @ (obj.matrix_world @ v.co) for obj in root.children if obj.name.rsplit('.',1)[-1] in ('core','top_reflector') for v in obj.data.vertices]
    edge_distance=min(min(v.y,math.sqrt(3)*v.x/2-v.y/2) for v in points)
    leg_clearance=edge_distance-d['spider_beam_width']/2
    ring_apothem=d['cap_opening_radius']*math.cos(math.pi/128)
    ring_clearance=ring_apothem-max(math.hypot(v.x,v.y) for v in points)
    assert leg_clearance>=p['extraction_clearance']-2e-6,leg_clearance
    assert ring_clearance>=p['cap_radial_clearance']-2e-6,ring_clearance
    assert min(math.hypot(v.x,v.y) for v in points)>d['spider_hub_radius']+p['extraction_clearance']
    for i in range(1,7):
        arm=bpy.data.objects[f'reactor.spider.arm_{i}'];web=bpy.data.objects[f'reactor.spider.underside_web_{i}']
        span=lambda obj,axis:max(v.co[axis] for v in obj.data.vertices)-min(v.co[axis] for v in obj.data.vertices)
        assert math.isclose(span(arm,1),d['spider_beam_width'],abs_tol=1e-6)
        assert math.isclose(span(web,1),.015,abs_tol=1e-6) and math.isclose(span(web,2),.05,abs_tol=1e-6)
        assert math.isclose(web.location.z+.025,d['top_z'],abs_tol=1e-6)
    return {'leg_width_metres':d['spider_beam_width'],'minimum_leg_clearance_metres':leg_clearance,
            'minimum_ring_clearance_metres':ring_clearance,'underside_web_thickness_metres':.015,
            'underside_web_height_metres':.05,'raised_core_and_top_reflector_vertical_projection_checked':True,
            'full_mechanism_collision_sweep_performed':False}
