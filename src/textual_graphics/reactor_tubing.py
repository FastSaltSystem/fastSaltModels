"""Absorber and core service tubes with open bores and removable edge passages."""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .reactor_checks import closed_mesh


def rounded_path(points, radius):
    points=[Vector(p) for p in points];result=[points[0]]
    for a,b,c in zip(points,points[1:],points[2:]):
        u=(a-b).normalized();v=(c-b).normalized()
        angle=math.acos(max(-1,min(1,u.dot(v))))
        if abs(angle-math.pi)<1e-6:
            result.append(b);continue
        trim=min(radius/math.tan(angle/2),(a-b).length*.4,(c-b).length*.4)
        actual_radius=trim*math.tan(angle/2)
        centre=b+(u+v).normalized()*(actual_radius/math.sin(angle/2))
        start=b+u*trim;end=b+v*trim
        axis=(start-centre).cross(end-centre).normalized()
        sweep=(start-centre).angle(end-centre)
        from mathutils import Quaternion
        result.extend(centre+Quaternion(axis,sweep*i/12) @ (start-centre) for i in range(13))
    result.append(points[-1]);return result


def hollow_tube(b,name,root,points,outer,wall,material):
    vertices=[];faces=[];sides=16;n=len(points)
    normal=None
    for i,p in enumerate(points):
        tangent=(points[min(i+1,n-1)]-points[max(i-1,0)]).normalized()
        if normal is None:
            normal=tangent.cross(Vector((1,0,0))).normalized()
        else:
            normal=(normal-tangent*normal.dot(tangent)).normalized()
        binormal=tangent.cross(normal).normalized()
        for radius in (outer,outer-wall):
            vertices.extend(p+radius*(normal*math.cos(j*2*math.pi/sides)+binormal*math.sin(j*2*math.pi/sides)) for j in range(sides))
    for i in range(n-1):
        for layer in (0,1):
            for j in range(sides):
                a=i*2*sides+layer*sides+j;c=i*2*sides+layer*sides+(j+1)%sides
                faces.append((a,c,c+2*sides,a+2*sides))
    for i in (0,n-1):
        for j in range(sides):
            a=i*2*sides+j;c=i*2*sides+(j+1)%sides
            faces.append((a,c,c+sides,a+sides))
    obj=b.mesh(name,root,vertices,faces,material)
    for polygon in obj.data.polygons:polygon.use_smooth=True
    obj['outside_diameter']=outer*2;obj['wall_thickness']=wall
    obj['centreline']=[tuple(p) for p in points]
    obj['open_ends']=True
    return obj


def build_absorber_tubing(b,layout,d):
    t=layout.ABSORBER_TUBES;p=layout.PRESENTATION
    outer=max(t['diameters'])/2
    b.material('absorber_centre_tube','#27859F',metallic=.55,roughness=.3)
    b.material('absorber_outer_tube','#D7943E',metallic=.55,roughness=.3)
    ring=bpy.data.objects['reactor.spider.outer_ring']
    xwall=layout.ABSORBER_PLUG['centre_radius']
    floor=d['hot_plenum_z']+t['floor_centre_height']
    top=d['top_z']+.15+p['cap_thickness']+t['above_cap']
    for i in range(6):
        root=b.assembly(f'reactor.absorber_tubes_{i+1}','Absorber tubing',angle=i*60)
        root['absorber_number']=i+1
        tank=bpy.data.objects[f'reactor.absorber_{i+1}.rectangular_tank']
        for pair,centre,rank in [('centre',(.10+d['reflector_radius'])/2,0),
                                 ('outer',d['reflector_radius']-.060,2)]:
            for index,(side,sign) in enumerate([('a',-1),('b',1)]):
                outer=t['diameters'][index]/2
                x=centre+sign*t['pair_connection_spacing']/2;y=0
                level=3-rank-index
                run_height=floor+level*t['stack_pitch']
                riser=xwall
                wall_y=(rank+index-1.5)*t['riser_pitch']
                fan_start=d['vessel_inner_radius']+.15
                points=[(x,0,d['hot_plenum_z']),(x,0,run_height),
                        (fan_start,0,run_height),(riser-.10,wall_y,run_height),
                        (riser,wall_y,run_height),
                        (riser,wall_y,top)]
                tube=hollow_tube(b,f'{pair}_{side}',root,rounded_path(points,t['bend_radius']),
                                 outer,t['wall_thickness'],f'absorber_{pair}_tube')
                tube['pair']=pair;tube['connection_point']=(x,y,d['hot_plenum_z'])
                tube['termination']=(riser,wall_y,top)
                tube['stack_level']=level;tube['floor_run_height']=run_height
                # The tank is a solid visual envelope; provide shallow connection sockets.
                socket=b.cylinder('tank_socket',root,outer-t['wall_thickness'],.05,
                                  (x,y,d['hot_plenum_z']-.015),None,vertices=24,bevel=0)
                b.cut(tank,socket)
    for i in range(6):
        mounts=b.assembly(f'reactor.absorber_tube_mounts_{i+1}','Tube wall mounts',angle=i*60)
        for z in (d['hot_plenum_z']+.8,d['top_z']-.2):
            for j in range(4):
                outer=t['diameters'][j%2]/2
                y=(j-1.5)*t['riser_pitch']
                width=d['hot_inner_radius']-xwall+.01
                saddle=b.box(f'saddle_{z}_{j}',mounts,(width,2*outer+.009,.025),
                             (xwall+width/2,y,z),'steel')
                bore=b.cylinder('saddle_bore',mounts,outer+.0005,.04,(xwall,y,z),None,vertices=24,bevel=0)
                b.cut(saddle,bore)
    # A reversible presentation crop exposes one route without the far side of
    # the complete spider ring concealing its absorber connection points.
    scene=bpy.context.scene;scene['tubing_detail_view']=False
    crop_root=b.assembly('study.tubing_detail_crop','Presentation tools')
    for name,size,position,targets in [
        ('spider_crop',(1.4,.40,.5),(3.7,0,d['top_z']+.075),
         ['reactor.spider.outer_ring','reactor.spider.arm_1','reactor.spider.underside_web_1']),
        ('tank_crop',(3,.3,.4),(1.1,0,d['hot_plenum_z']-.15),['reactor.absorber_1.rectangular_tank'])]:
        cutter=b.box(name,crop_root,size,position,None)
        cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE'
        for name in targets:
            modifier=bpy.data.objects[name].modifiers.new('Tube detail crop','BOOLEAN')
            modifier.operation='INTERSECT';modifier.solver='EXACT';modifier.object=cutter
            for prop in ('show_viewport','show_render'):
                driver=modifier.driver_add(prop).driver
                variable=driver.variables.new();variable.name='detail';variable.type='SINGLE_PROP'
                variable.targets[0].id_type='SCENE';variable.targets[0].id=scene
                variable.targets[0].data_path='["tubing_detail_view"]';driver.expression='detail'


def check_absorber_tubing(b,layout,d):
    t=layout.ABSORBER_TUBES;outer=max(t['diameters'])/2
    scene=bpy.context.scene;previous=scene['maintenance_position']
    scene['maintenance_position']=False;scene.update_tag();bpy.context.view_layer.update()
    roots=[r for r in b.assemblies.values() if r.get('category')=='Absorber tubing']
    assert len(roots)==6
    ring=bpy.data.objects['reactor.spider.outer_ring'];closed_mesh(ring)
    for i in range(1,7):closed_mesh(bpy.data.objects[f'reactor.cap_{i}.plate'])
    def tree(obj):
        return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                                   [tuple(p.vertices) for p in obj.data.polygons])
    wall=bpy.data.objects['reactor.vessel.wall'];walltree=tree(wall)
    tubes=[];minimum_nozzle_clearance=math.inf
    for root in roots:
        assert len(root.children)==4
        assert sorted(o['pair'] for o in root.children)==['centre','centre','outer','outer']
        for pair in ('centre','outer'):
            assert sorted(o['outside_diameter'] for o in root.children if o['pair']==pair)==t['diameters']
        tank=bpy.data.objects[f'reactor.absorber_{root["absorber_number"]}.rectangular_tank']
        closed_mesh(tank)
        for obj in root.children:
            tubes.append(obj);closed_mesh(obj)
            outer=obj['outside_diameter']/2
            assert obj['outside_diameter'] in t['diameters']
            # Open bores at both ends, and separate clear holes through the spider.
            for key,sign in [('connection_point',1),('termination',-1)]:
                point=Vector(obj[key]);point.z+=sign*.01
                assert not obj.ray_cast(point,Vector((0,0,-sign)),distance=.025)[0]
            end=root.matrix_world @ Vector(obj['termination'])
            assert math.isclose(end.z,d['top_z']+.15+layout.PRESENTATION['cap_thickness']+t['above_cap'],abs_tol=1e-6)
            assert all(abs(p[1])<1e-8 for p in obj['centreline'] if p[0]<d['vessel_inner_radius']+.10)
            for part in ('outer_ring',f'arm_{root["absorber_number"]}',f'underside_web_{root["absorber_number"]}'):
                spider=bpy.data.objects[f'reactor.spider.{part}'];closed_mesh(spider)
                inverse=spider.matrix_world.inverted()
                assert not spider.ray_cast(inverse @ (end+Vector((0,0,.01))),inverse.to_3x3() @ Vector((0,0,-1)),distance=.34)[0]
            for i in range(1,7):
                cap=bpy.data.objects[f'reactor.cap_{i}.plate']
                # Cap objects are seated during construction; parent transforms may raise
                # the selected maintenance cap only via visibility, not its coordinates.
                start=cap.matrix_world.inverted() @ (end+Vector((0,0,.2)))
                assert not cap.ray_cast(start,Vector((0,0,-1)),distance=.2)[0],(obj.name,cap.name)
            assert not tree(obj).overlap(walltree),(obj.name,'wall')
            # At nozzle height all routes are vertical; verify separation from every hot bore.
            for hot in (r for r in b.assemblies.values() if r.get('connection_type')=='hot_outlet'):
                a=math.radians(hot['azimuth_degrees'])
                radial=Vector((math.cos(a),math.sin(a),0))
                if end.dot(radial)>0:
                    clearance=abs(end.x*radial.y-end.y*radial.x)-layout.CONNECTIONS['pipe_diameter']/2-outer
                    minimum_nozzle_clearance=min(minimum_nozzle_clearance,clearance)
    meshes=[tree(o) for o in tubes]
    for i,mesh in enumerate(meshes):
        for j in range(i):assert not mesh.overlap(meshes[j]),(tubes[i].name,tubes[j].name)
    assert minimum_nozzle_clearance>0
    number=layout.MAINTENANCE['sector']
    owner=b.assemblies[f'reactor.sector_{number}'];hardware=b.assemblies[f'reactor.fourbar_{number}']
    length=hardware['link_length'];angle=hardware.rotation_euler.z
    moving=[o for o in owner.children if o.type=='MESH']
    links=[o for o in hardware.children if o.get('role')=='fourbar_link']
    # Use the true parallelogram arc (out=L*(1-cos theta), lift=L*sin theta),
    # rather than interpolating the Boolean endpoint driver.
    poses=list(range(0,91,3))
    for degrees in poses:
        theta=math.radians(degrees)
        shift=Vector((length*(1-math.cos(theta))*math.cos(angle),
                      length*(1-math.cos(theta))*math.sin(angle),length*math.sin(theta)))
        for obj in moving+links:
            if obj in links:
                fixed=Vector(obj['fixed_pivot'])
                centre=Vector((fixed.x-length*math.cos(theta)/2,fixed.y,fixed.z+length*math.sin(theta)/2))
                transform=hardware.matrix_world @ Matrix.Translation(centre) @ Matrix.Rotation(theta,4,'Y')
            else:transform=Matrix.Translation(shift) @ obj.matrix_world
            mesh=BVHTree.FromPolygons([transform @ v.co for v in obj.data.vertices],
                                     [tuple(p.vertices) for p in obj.data.polygons])
            for tube,tubetree in zip(tubes,meshes):
                assert not mesh.overlap(tubetree),(degrees,obj.name,tube.name)
    scene['maintenance_position']=previous;scene.update_tag();bpy.context.view_layer.update()
    return {'tube_count':len(tubes),'pairs_per_absorber':2,'outside_diameters':t['diameters'],
            'wall_thickness':t['wall_thickness'],'spider_penetrations':6,'tubes_per_removable_plug':4,
            'minimum_hot_nozzle_clearance':minimum_nozzle_clearance,'open_bores_checked':True,
            'wall_and_pair_clearances_checked':True,'floor_bundle_width':max(t['diameters']),'wall_bundle_width':3*t['riser_pitch']+sum(t['diameters'])/2,
            'stack_pitch':t['stack_pitch'],'above_cap':t['above_cap'],
            'fourbar_motion_sample_degrees':poses,'sampled_sector_and_link_motion_clear':True,
            'continuous_collision_proof':False}


def cut_passage(b,target,cutter):
    """Apply a robust closed-solid cut, including cuts intersecting existing bores."""
    mesh=bmesh.new();mesh.from_mesh(target.data)
    bmesh.ops.triangulate(mesh,faces=list(mesh.faces))
    mesh.to_mesh(target.data);mesh.free();target.data.update()
    bpy.context.view_layer.update()
    modifier=target.modifiers.new('Service tube edge cutout','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='MANIFOLD';modifier.object=cutter
    bpy.context.view_layer.objects.active=target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    closed_mesh(target)


def build_core_tubing(b,layout,d):
    t=layout.CORE_TUBES;p=layout.PRESENTATION
    b.material('core_tube_25','#5388B6',metallic=.5,roughness=.3)
    b.material('core_tube_50','#C47B47',metallic=.5,roughness=.3)
    top=d['top_z']+.15+p['cap_thickness']+t['above_cap']
    bpy.context.scene['core_tube_detail_view']=False
    for i in range(1,7):
        owner=b.assemblies[f'reactor.sector_{i}']
        root=b.assembly(f'reactor.core_tubes_{i}','Core tubing')
        root.parent=bpy.data.objects[owner.name+'.core'];root['sector_number']=i
        top_reflector=bpy.data.objects[f'{owner.name}.top_reflector']
        bottom_reflector=bpy.data.objects[f'{owner.name}.bottom_reflector']
        peripheral=bpy.data.objects[f'{owner.name}.radial_reflector']
        ends=[]
        lane=t['radial_edge_lane']
        # One narrow edge-open groove replaces the three L-shaped routes.
        margin=t['diameters'][1]/2+t['cutout_clearance']
        xlo=min(t['radial_positions'])-margin;xhi=max(t['bottom_slot_radii'])+margin
        edge_depth=lane+margin
        low=min(t['bottom_run_heights'])-margin;high=d['core_z']+.01
        cutter=b.box('common_bottom_edge_groove',root,(xhi-xlo,edge_depth+.05,high-low),
                     ((xlo+xhi)/2,(edge_depth-.05)/2,(low+high)/2),None)
        cut_passage(b,bottom_reflector,cutter)
        inside=d['core_radius']-.04
        cutter=b.box('common_peripheral_radial_slot',root,(xhi-inside,edge_depth+.05,d['hot_plenum_z']-d['core_z']+.02),
                     ((inside+xhi)/2,(edge_depth-.05)/2,(d['core_z']+d['hot_plenum_z'])/2),None)
        cut_passage(b,peripheral,cutter)
        for rank,x in enumerate(t['radial_positions']):
            bottom_x=t['bottom_slot_radii'][rank]
            # Inner origins use the outer, higher meeting points; nested paths do not cross.
            meeting=d['hot_plenum_z']+t['additional_rise_before_bend']+.34+(2-rank)*.14
            for connection,diameter in [('top',t['diameters'][0]),('bottom',t['diameters'][1])]:
                cap_x,gy=layout.core_tube_terminal(rank,connection)
                z=d['top_reflector_z'] if connection=='top' else d['core_z']
                gather=bottom_x-t['top_pair_radial_offset'] if connection=='top' else bottom_x
                turn=meeting+t['pair_vertical_offset'] if connection=='top' else meeting
                level=turn if connection=='top' else t['bottom_run_heights'][rank]
                points=[(x,lane,z),(x,lane,level),(gather,lane,level)]
                # A single rising diagonal replaces the orthogonal side-step and
                # return doglegs. Keep the lower radial slot and rise above the latches.
                upper=d['top_z']-.03-rank*.03
                if connection=='bottom':
                    points.append((gather,lane,turn))
                points.extend([(cap_x,gy,upper-(.14 if connection=='top' else 0)),(cap_x,gy,top)])
                # Omit coincident control points when a lane already aligns.
                points=[q for j,q in enumerate(points) if j==0 or Vector(q)!=Vector(points[j-1])]
                tube=hollow_tube(b,f'pair_{rank+1}_{connection}_{int(diameter*1000)}mm',root,
                                 rounded_path(points,t['bend_radius']),diameter/2,t['wall_thickness'],
                                 f'core_tube_{int(diameter*1000)}')
                tube['bend_count']=len(points)-2;tube['control_points']=points
                tube['bend_centre_height']=level;tube['connection_type']=connection
                tube['meeting_height']=turn;tube['radial_gather_x']=gather
                tube['pair_number']=rank+1;tube['connection_point']=(x,lane,z)
                tube['termination']=(cap_x,gy,top);tube['moves_with_sector']=i
                ends.append((cap_x,gy,diameter/2))
                if connection=='top':
                    margin=diameter/2+t['cutout_clearance']
                    cutter=b.box('top_reflector_notch',root,(2*margin,lane+margin+.05,.35),
                                 (x,(lane+margin-.05)/2,d['top_reflector_z']+.125),None)
                    cut_passage(b,top_reflector,cutter)


def check_core_tubing(b,layout,d):
    scene=bpy.context.scene;previous=scene['maintenance_position']
    scene['maintenance_position']=False;scene.update_tag();bpy.context.view_layer.update()
    roots=[r for r in b.assemblies.values() if r.get('category')=='Core tubing']
    assert len(roots)==6
    def tree(obj,transform=None):
        matrix=transform if transform is not None else obj.matrix_world
        return BVHTree.FromPolygons([matrix @ v.co for v in obj.data.vertices],
                                   [tuple(p.vertices) for p in obj.data.polygons])
    tubes=[]
    for root in roots:
        assert len(root.children)==6 and root.parent.name==f'reactor.sector_{root["sector_number"]}.core'
        assert sorted(o['outside_diameter'] for o in root.children)==[.025]*3+[.05]*3
        reflectors=[bpy.data.objects[f'reactor.sector_{root["sector_number"]}.'+part] for part in ('top_reflector','bottom_reflector','radial_reflector')]
        for obj in reflectors:closed_mesh(obj)
        cap=bpy.data.objects[f'reactor.cap_{root["sector_number"]}.plate']
        assert math.isclose(max(math.hypot(v.co.x,v.co.y) for v in cap.data.vertices),d['cap_opening_radius']+.015,abs_tol=1e-6)
        for obj in root.children:
            closed_mesh(obj);tubes.append(obj)
            rank=obj['pair_number']-1;connection=obj['connection_type']
            assert obj['bend_count']==(4 if connection=='bottom' else 3)
            assert obj['outside_diameter']==(.025 if connection=='top' else .05)
            assert math.isclose(obj['connection_point'][2],d['top_reflector_z'] if connection=='top' else d['core_z'],abs_tol=1e-6)
            expected=(d['hot_plenum_z']+.30+.34+(2-rank)*.14+layout.CORE_TUBES['pair_vertical_offset'] if connection=='top'
                      else layout.CORE_TUBES['bottom_run_heights'][rank])
            assert math.isclose(obj['bend_centre_height'],expected,abs_tol=1e-6)
            lane=layout.CORE_TUBES['radial_edge_lane']
            assert math.isclose(obj['connection_point'][1],lane,abs_tol=1e-6)
            for point in obj['centreline']:
                if point[2]<obj['meeting_height']-layout.CORE_TUBES['bend_radius']-.001:
                    assert math.isclose(point[1],lane,abs_tol=1e-6),(obj.name,point)
            assert math.isclose(obj['termination'][2],d['top_z']+.15+layout.PRESENTATION['cap_thickness']+.1,abs_tol=1e-6)
            for key,sign in [('connection_point',1 if connection=='top' else -1),('termination',-1)]:
                point=Vector(obj[key]);point.z+=sign*.005
                assert not obj.ray_cast(point,Vector((0,0,-sign)),distance=.01)[0]
            for reflector in reflectors:
                assert not tree(obj).overlap(tree(reflector)),(obj.name,reflector.name)
            assert not tree(obj).overlap(tree(cap)),(obj.name,'circular cap opening')
    meshes=[tree(o) for o in tubes]
    for j,mesh in enumerate(meshes):
        for i in range(j):assert not mesh.overlap(meshes[i]),(tubes[j].name,tubes[i].name)
    # Full core tube assemblies are sampled along the same true parallelogram arc.
    fixed=[o for category in ('Absorber tubing','Absorber plugs','Spider','Tube wall mounts','Core supports','Separator supports','Absorber tanks')
           for root in b.assemblies.values() if root.get('category')==category
           for o in root.children if o.type=='MESH']
    obstacles=[(o,tree(o)) for o in fixed]
    number=layout.MAINTENANCE['sector'];owner=b.assemblies[f'reactor.sector_{number}']
    hardware=b.assemblies[f'reactor.fourbar_{number}'];length=hardware['link_length'];angle=hardware.rotation_euler.z
    moving=list(b.assemblies[f'reactor.core_tubes_{number}'].children)
    for degrees in range(0,91,3):
        theta=math.radians(degrees)
        shift=Vector((length*(1-math.cos(theta))*math.cos(angle),length*(1-math.cos(theta))*math.sin(angle),length*math.sin(theta)))
        for obj in moving:
            mesh=tree(obj,Matrix.Translation(shift) @ obj.matrix_world)
            for obstacle,bvh in obstacles:
                assert not mesh.overlap(bvh),(degrees,obj.name,obstacle.name)
    # All core-mounted tubing must also fit through the opening during vertical extraction.
    unrotate=Matrix.Rotation(-owner.rotation_euler.z,4,'Z')
    projected=[unrotate @ (Matrix.Translation(shift) @ obj.matrix_world @ v.co)
               for obj in moving for v in obj.data.vertices]
    tube_ring_clearance=d['cap_opening_radius']*math.cos(math.pi/128)-max(math.hypot(v.x,v.y) for v in projected)
    tube_leg_clearance=min(min(v.y,math.sqrt(3)*v.x/2-v.y/2) for v in projected)-d['spider_beam_width']/2
    assert tube_leg_clearance>0
    assert tube_ring_clearance>=layout.PRESENTATION['cap_tube_clearance']-1e-6
    # Verify a continuous circular inner ring, with no local service reliefs.
    ring=bpy.data.objects['reactor.spider.outer_ring']
    for j in range(128):
        a=(j+.5)*2*math.pi/128
        direction=Vector((math.cos(a),math.sin(a),0))
        hit,point,*_=ring.ray_cast(Vector((0,0,d['top_z']+.075)),direction)
        assert hit and math.isclose(math.hypot(point.x,point.y),d['cap_opening_radius']*math.cos(math.pi/128),abs_tol=2e-6)
    # Test conservative convex projected envelopes against the complete spider.
    def hull(points):
        points=sorted(set((float(p.x),float(p.y)) for p in points))
        def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lower=[];upper=[]
        for point in points:
            while len(lower)>=2 and cross(lower[-2],lower[-1],point)<=0:lower.pop()
            lower.append(point)
        for point in reversed(points):
            while len(upper)>=2 and cross(upper[-2],upper[-1],point)<=0:upper.pop()
            upper.append(point)
        return lower[:-1]+upper[:-1]
    spider=[(o,tree(o)) for o in b.assemblies['reactor.spider'].children if o.type=='MESH']
    for obj in moving:
        outline=hull([Matrix.Translation(shift) @ obj.matrix_world @ v.co for v in obj.data.vertices])
        n=len(outline)
        vertices=[(x,y,z) for z in (d['top_z']-.06,d['top_z']+.16) for x,y in outline]
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        faces.extend((j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n))
        envelope=BVHTree.FromPolygons(vertices,faces)
        for fixed_obj,bvh in spider:assert not envelope.overlap(bvh),(obj.name,fixed_obj.name,'vertical projection')
    assert min(math.hypot(v.x,v.y) for v in projected)>d['spider_hub_radius']
    # With the top reflector removed, core tubes can rise out of the open bottom/peripheral slots.
    extraction_heights=[.05,.25,.75,2,4,6]
    stationary=[tree(bpy.data.objects[owner.name+'.'+part]) for part in ('bottom_reflector','radial_reflector')]
    for lift in extraction_heights:
        for obj in moving:
            mesh=tree(obj,Matrix.Translation((0,0,lift)) @ obj.matrix_world)
            for fixed_tree in stationary:assert not mesh.overlap(fixed_tree),(lift,obj.name,'extraction slot')
    # The core and top reflector retain their specified radial clearance.

    radius=(d['cap_opening_radius']*math.cos(math.pi/128))
    assert radius-d['core_radius']-length>=.10-1e-6
    def touched(rectangles):
        radius=layout.PRESENTATION['tube_pattern_radius']
        return [(x,y) for x,y in layout.hole_centres() if any(
            (max(xlo-x,0,x-xhi)**2+max(ylo-y,0,y-yhi)**2)<radius**2
            for xlo,xhi,ylo,yhi in rectangles)]
    old=[]
    for x,gy in zip(layout.CORE_TUBES['radial_positions'],[.30,.42,.54]):
        gather=math.sqrt(1.97**2-gy**2)
        old.extend([(x-.035,x+.035,.17-.035,gy+.035),
                    (x-.035,gather+.035,gy-.035,gy+.035)])
    margin=.025+layout.CORE_TUBES['cutout_clearance']
    current=[(min(layout.CORE_TUBES['radial_positions'])-margin,
              max(layout.CORE_TUBES['bottom_slot_radii'])+margin,-.05,
              layout.CORE_TUBES['radial_edge_lane']+margin)]
    old_bores=touched(old);new_bores=touched(current)
    assert len(new_bores)<len(old_bores)
    scene['maintenance_position']=previous;scene.update_tag();bpy.context.view_layer.update()
    return {'tube_count':len(tubes),'pairs_per_sector':3,'bottom_tube_bends':4,'top_tube_bends':3,'outside_diameters':[.025,.05],
            'additional_rise_before_bend':layout.CORE_TUBES['additional_rise_before_bend'],
            'above_seated_cap':.1,'gather_at':'peripheral reflector',
            'top_connection_diameter':.025,'bottom_connection_diameter':.05,
            'bottom_and_peripheral_slots_checked':True,
            'common_radial_plane':layout.CORE_TUBES['radial_edge_lane'],
            'slot_depth_from_sector_boundary':current[0][3],
            'illustrative_bottom_bore_footprints_intersected_per_sector':len(new_bores),
            'previous_bottom_bore_footprints_intersected_per_sector':len(old_bores),
            'bore_footprint_comparison_is_not_a_flow_calculation':True,
            'tube_vertical_passage_ring_clearance':tube_ring_clearance,
            'continuous_circular_spider_opening_checked':True,
            'tube_vertical_passage_through_spider_checked':True,
            'tube_vertical_passage_leg_clearance':tube_leg_clearance,
            'slot_extraction_sample_heights':extraction_heights,
            'cap_opening_radius':d['cap_opening_radius'],'radial_core_extraction_clearance':radius-d['core_radius']-length,
            'reflector_edge_slots_and_circular_cap_openings_checked':True,'open_ends_and_pair_clearances_checked':True,
            'sampled_motion_degrees':list(range(0,91,3)),'sampled_motion_clear':True,
            'continuous_collision_proof':False}
