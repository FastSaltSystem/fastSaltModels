"""Removable sector tube plugs: illustrative seals, captive bolts and core-owned supports."""
import math
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .reactor_tubing import cut_passage
from .reactor_checks import closed_mesh
from .reactor_handling import property_driver, rectangular_beam


def build_support_frame(b,layout,d,root):
    cx,cy=layout.SECTOR_PLUG['centre'];seat=d['top_z']+.15
    x,y=1.648,.135;z=d['top_reflector_z']-.03;high=d['hot_plenum_z']+1.07
    anchor=b.box('core_side_attachment',root,(.055,.160,.040),(x+.025,.105,z),'plug_steel');anchor['role']='plug_support'
    post=b.box('support_frame_1',root,(.028,.025,high-z),(x,y,(high+z)/2),'plug_steel');post['role']='plug_support'
    points=[(x,y,high),(x,.075,high),(cx+.12,.075,high),(cx+.12,cy,high)]
    for index,(a,c) in enumerate(zip(points,points[1:]),2):
        obj=rectangular_beam(b,f'support_frame_{index}',root,a,c,.04 if index==3 else .025,.060,'plug_steel');obj['role']='plug_support'
    obj=b.beam('support_frame_5',root,points[-1],(cx+.12,cy,seat-layout.SECTOR_PLUG['body_height']+.010),.0125,'plug_steel');obj['role']='plug_support'


def build_sector_plugs(b,layout,d):
    p=layout.SECTOR_PLUG;cx,cy=p['centre'];seat=d['top_z']+.15;cap_top=seat+layout.PRESENTATION['cap_thickness']
    scene=bpy.context.scene;scene['sector_plug_bolts_retracted']=False
    scene.id_properties_ui('sector_plug_bolts_retracted').update(description='Retract the captive plug screws by 75 mm before lifting a cap. Display pose only; vessel depressurized and external services disconnected.')
    scene['sector_plug_detail_view']=False
    scene['cap_service_view']=False
    crop_root=b.assembly('study.plug_detail_tool','Presentation tools')
    crop=b.cylinder('local_cap_crop',crop_root,.33,.25,(cx,cy,seat+.075),None,vertices=96,bevel=0)
    crop.parent=b.assemblies['reactor.cap_1'];crop.hide_render=True;crop.hide_set(True)
    tube_crop=b.cylinder('local_tube_crop',crop_root,.32,.32,(cx,cy,seat+.09),None,vertices=96,bevel=0)
    tube_crop.hide_render=True;tube_crop.hide_set(True)
    b.material('plug_steel','#66818D',metallic=.6,roughness=.3)
    b.material('plug_seal','#C08A4B',metallic=.7,roughness=.3)
    for number in range(1,7):
        core=bpy.data.objects[f'reactor.sector_{number}.core'];cap=b.assemblies[f'reactor.cap_{number}'];plate=bpy.data.objects[cap.name+'.plate']
        root=b.assembly(f'reactor.sector_plug_{number}','Sector tube plugs');root.parent=core;root['sector_number']=number
        root['scope']='Core-owned welded tube plug and support frame. Provisional geometry; pressure, seal, weld, thermal, support and fastener performance unverified.'
        # One closed stepped solid, with separate through-bores and blind screw holes.
        rings=[(p['flange_radius'],seat-p['body_height']),(p['flange_radius'],seat),(p['pilot_radius'],seat),(p['pilot_radius'],seat+p['pilot_height'])]
        n=96;vertices=[(cx+r*math.cos(j*math.tau/n),cy+r*math.sin(j*math.tau/n),z) for r,z in rings for j in range(n)]
        faces=[tuple(reversed(range(n))),tuple(range(3*n,4*n))]
        for k in range(3):
            for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
        body=b.mesh('stepped_body',root,vertices,faces,'plug_steel');body['role']='tube_plug_body'
        cutter=b.cylinder('circular_cap_opening',root,p['opening_radius'],.40,(cx,cy,seat+.06),None,vertices=96,bevel=0);cut_passage(b,plate,cutter)
        groove=b.annulus('face_seal_groove',cap,p['seal_radius']-.004,p['seal_radius']+.004,seat-.001,seat+.004,None,steps=96);groove.location=(cx,cy,0);cut_passage(b,plate,groove)
        seal=b.annulus('plug_face_seal',cap,p['seal_radius']-p['seal_width']/2,p['seal_radius']+p['seal_width']/2,seat,seat+.003,'plug_seal',steps=96);seal.location=(cx,cy,0)
        seal['role']='plug_face_seal';seal['scope']='Retained annular placeholder for a replaceable metallic face seal; detailed seal section not specified'
        for rank in range(3):
            for connection,diameter in [('top',.025),('bottom',.050)]:
                x,y=layout.core_tube_terminal(rank,connection)
                cutter=b.cylinder('tube_bore',root,diameter/2+.0005,.30,(x,y,seat-.02),None,vertices=32,bevel=0);cut_passage(b,body,cutter)
                weld=b.annulus(f'pair_{rank+1}_{connection}_seal_weld',root,diameter/2-.0005,diameter/2+.003,seat+p['pilot_height']-.002,seat+p['pilot_height']+.002,'links',steps=32);weld.location=(x,y,0);weld['role']='tube_seal_weld'
        build_plug_fasteners(b,p,root,cap,plate,body,cx,cy,seat,cap_top,'sector_plug_bolts_retracted')
        # Frame stands in an existing core-hook relief, then follows the existing
        # reflector edge opening before turning outboard. Tubes do not carry the plug.
        build_support_frame(b,layout,d,root)
        root['seal_perimeter_outside_bolts']=True
        root['maintenance_sequence']='Disconnect external services; retract screws; lift cap; raise/latch sector; lift top reflector; lift core, tubes, frame and plug together'

    for obj,cutter in [(bpy.data.objects['reactor.cap_1.plate'],crop)]+[(o,tube_crop) for o in b.assemblies['reactor.core_tubes_1'].children]:
        mod=obj.modifiers.new('Local plug inspection crop','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=cutter
        for prop in ('show_viewport','show_render'):
            properties={'detail':'sector_plug_detail_view'}
            expression='detail'
            if cutter==tube_crop:properties['service']='cap_service_view';expression='detail or service'
            property_driver(mod,prop,None,expression,properties)


def check_sector_plugs(b,layout,d):
    scene=bpy.context.scene;p=layout.SECTOR_PLUG
    old=(scene['maintenance_position'],scene['sector_plug_bolts_retracted'],scene['maintenance_locks_engaged'])
    scene['maintenance_position']=False;scene['sector_plug_bolts_retracted']=False;scene.update_tag();bpy.context.view_layer.update()
    def tree(obj,delta=Vector((0,0,0))):
        return BVHTree.FromPolygons([obj.matrix_world @ v.co+delta for v in obj.data.vertices],[tuple(f.vertices) for f in obj.data.polygons])
    def meshes(root):return [o for o in root.children_recursive if o.type=='MESH']
    seat=d['top_z']+.15
    for i in range(1,7):
        root=b.assemblies[f'reactor.sector_plug_{i}'];body=bpy.data.objects[root.name+'.stepped_body'];cap=b.assemblies[f'reactor.cap_{i}'];plate=bpy.data.objects[cap.name+'.plate']
        for obj in meshes(root)+[o for o in cap.children if o.users_collection[0].name!='Presentation tools']:
            if obj.type=='MESH':closed_mesh(obj)
        assert root.parent.name==f'reactor.sector_{i}.core'
        bolts=[o for o in cap.children if o.get('role')=='captive_plug_bolt'];assert len(bolts)==12
        # Continuous metal at the sector edge replaces the old open notch.
        assert plate.ray_cast(Vector((1.9,.04,seat+.30)),Vector((0,0,-1)),distance=.4)[0]
        for rank in range(3):
            for connection in ('top','bottom'):
                x,y=layout.core_tube_terminal(rank,connection)
                assert not body.ray_cast(Vector((x,y,seat+.03)),Vector((0,0,-1)),distance=.20)[0]
        for index in range(p['bolt_count']):
            a=index*math.tau/p['bolt_count'];x=p['centre'][0]+p['bolt_circle']*math.cos(a);y=p['centre'][1]+p['bolt_circle']*math.sin(a)
            hit,point,*_=body.ray_cast(Vector((x,y,seat+.001)),Vector((0,0,-1)),distance=.20)
            assert hit and abs(point.z-(seat-p['blind_depth']))<2e-6,(body.name,'blind hole floor')
        assert p['seal_radius']-p['seal_width']/2>p['bolt_circle']+.010
    # Reserve a 700 mm diameter connection workspace clear of all cap hooks.
    clearance=math.inf;cx,cy=p['centre']
    for obj in b.assemblies['reactor.cap_1'].children:
        if obj.get('role')!='cap_lifting_hook':continue
        points=[(obj.matrix_local @ v.co).xy for v in obj.data.vertices];centre=Vector((cx,cy))
        for edge in obj.data.edges:
            a,c=(points[j] for j in edge.vertices);v=c-a
            t=max(0,min(1,(centre-a).dot(v)/v.length_squared)) if v.length_squared else 0
            clearance=min(clearance,(a+t*v-centre).length)
    assert clearance>=.35,('cap hook connection workspace',clearance)
    number=layout.MAINTENANCE['sector'];root=b.assemblies[f'reactor.sector_plug_{number}'];cap=b.assemblies[f'reactor.cap_{number}']
    bodies=meshes(root);tubes=list(b.assemblies[f'reactor.core_tubes_{number}'].children)
    # Tube weld contact is intentional; the independent support must clear every tube.
    for obj in (o for o in bodies if o.get('role')=='plug_support'):
        for tube in tubes:assert not tree(obj).overlap(tree(tube)),(obj.name,tube.name,'support/tube clearance')
    # Screws retract out of the plug before cap, retained seal and screw cages lift.
    body=bpy.data.objects[root.name+'.stepped_body'];bodytree=tree(body)
    for step in range(16):
        scene['sector_plug_bolts_retracted']=step/15;scene.update_tag();bpy.context.view_layer.update()
        for obj in (o for o in cap.children if o.get('role')=='captive_plug_bolt'):
            assert not tree(obj).overlap(bodytree),(step,obj.name,'bolt withdrawal')
    fixed=[(o,tree(o)) for o in bodies+tubes]
    cap_parts=[o for o in cap.children if o.type=='MESH' and o.users_collection[0].name!='Presentation tools']
    for step in range(1,31):
        for obj in cap_parts:
            moving=tree(obj,Vector((0,0,step*.01)))
            for other,bvh in fixed:assert not moving.overlap(bvh),(step,obj.name,other.name,'cap lift with stationary plug')
    # Complete sector movement, including the enlarged plug, past fixed hardware.
    scene['maintenance_locks_engaged']=False;scene.update_tag();bpy.context.view_layer.update()
    fixed=[o for category in ('Spider','Absorber tubing','Absorber plugs','Tube wall mounts','Maintenance locks','Vessel') for o in bpy.data.collections[category].objects if o.type=='MESH']
    obstacles=[(o,tree(o)) for o in fixed]
    travel=d['maintenance_travel'];angle=math.radians((number-1)*60+30)
    for degrees in range(0,91,3):
        a=math.radians(degrees);delta=Vector((travel*(1-math.cos(a))*math.cos(angle),travel*(1-math.cos(a))*math.sin(angle),travel*math.sin(a)))
        for obj in bodies:
            moving=tree(obj,delta)
            for other,bvh in obstacles:assert not moving.overlap(bvh),(degrees,obj.name,other.name,'plug maintenance arc')
    scene['maintenance_position']=True;scene.update_tag();bpy.context.view_layer.update()
    top=bpy.data.objects[f'reactor.sector_{number}.top_reflector'];fixed=[(o,tree(o)) for o in bodies]
    for step in range(1,81):
        moving=tree(top,Vector((0,0,step*.05)))
        for other,bvh in fixed:assert not moving.overlap(bvh),(step,other.name,'top reflector past plug and support')
    # Plug and frame are core-owned; extract past the retained reflector, catches and spider.
    fixed=[(o,tree(o)) for o in [bpy.data.objects[f'reactor.sector_{number}.{part}'] for part in ('radial_reflector','bottom_reflector')]+[o for category in ('Spider','Maintenance locks','Absorber tubing','Absorber plugs') for o in bpy.data.collections[category].objects if o.type=='MESH']]
    for step in range(1,31):
        for obj in bodies:
            moving=tree(obj,Vector((0,0,step*.20)))
            for other,bvh in fixed:assert not moving.overlap(bvh),(step,obj.name,other.name,'core/plug withdrawal')
    scene['maintenance_position'],scene['sector_plug_bolts_retracted'],scene['maintenance_locks_engaged']=old;scene.update_tag();bpy.context.view_layer.update()
    return {'count':6,'nearest_cap_hook_to_plug_axis_m':clearance,'hook_free_connection_workspace_diameter_m':.70,'flange_diameter_m':2*p['flange_radius'],'circular_cap_opening_diameter_m':2*p['opening_radius'],'bolts_per_plug':6,'blind_holes_checked':True,'cap_edge_closed':True,'seal_outside_bolt_circle':True,'bolt_withdrawal_and_cap_lift_sampled':True,'maintenance_arc_sample_degrees':3,'top_reflector_lift_sample_m':.05,'core_plug_lift_sample_m':.20,'support_clears_tubes':True,'external_service_disconnects_not_modeled':True,'pressure_seal_thermal_and_strength_qualification':False}


def build_plug_fasteners(b,p,root,roof,plate,body,cx,cy,seat,cap_top,bolt_property):
    for index in range(p['bolt_count']):
        a=index*math.tau/p['bolt_count'];x=cx+p['bolt_circle']*math.cos(a);y=cy+p['bolt_circle']*math.sin(a)
        cutter=b.cylinder('cap_screw_passage',roof,.010,.30,(x,y,seat+.06),None,vertices=24,bevel=0);cut_passage(b,plate,cutter)
        cutter=b.cylinder('blind_tapped_hole',root,.0085,p['blind_depth']+.001,(x,y,seat-(p['blind_depth']-.001)/2),None,vertices=24,bevel=0);cut_passage(b,body,cutter)
        bottom=seat-.045;top=cap_top+.019
        shaft=b.cylinder(f'plug_bolt_{index+1}_shaft',roof,p['bolt_radius'],top-bottom,(x,y,(bottom+top)/2),'links',vertices=24,bevel=0)
        head=b.cylinder(f'plug_bolt_{index+1}_socket_head',roof,.014,.018,(x,y,cap_top+.028),'links',vertices=32,bevel=0)
        socket=b.cylinder('hex_socket',roof,.006,.010,(x,y,cap_top+.037),None,vertices=6,bevel=0);cut_passage(b,head,socket)
        for obj in (shaft,head):
            z=obj.location.z;property_driver(obj,'location',2,f'{z}+released*{p["bolt_retraction"]}',{'released':bolt_property})
            obj['role']='captive_plug_bolt';obj['bolt_index']=index+1;obj['thread_representation']='Smooth shaft and blind bore; threads omitted'
        for suffix,inner,zlo,zhi in [('lower_keeper',.009,cap_top,cap_top+.019),('upper_keeper',.010,cap_top+.120,cap_top+.130)]:
            ring=b.annulus(f'plug_bolt_{index+1}_{suffix}',roof,inner,.022,zlo,zhi,'plug_steel',steps=32);ring.location=(x,y,0);ring['role']='bolt_retainer'
        for j in range(3):
            t=j*math.tau/3
            b.beam(f'plug_bolt_{index+1}_cage_post_{j+1}',roof,(x+.020*math.cos(t),y+.020*math.sin(t),cap_top+.012),(x+.020*math.cos(t),y+.020*math.sin(t),cap_top+.120),.003,'plug_steel')


def build_absorber_plugs(b,layout,d):
    p=layout.ABSORBER_PLUG;cx=p['centre_radius'];cy=0;seat=d['top_z'];roof_top=seat+.15
    scene=bpy.context.scene;scene['absorber_plug_bolts_retracted']=False
    scene.id_properties_ui('absorber_plug_bolts_retracted').update(description='Withdraw absorber plug screws before lifting the spider; external connections and separate roof attachments must first be disconnected.')
    spider=b.assemblies['reactor.spider'];plate=bpy.data.objects['reactor.spider.outer_ring']
    for i in range(1,7):
        root=b.assembly(f'reactor.absorber_plug_{i}','Absorber plugs',angle=(i-1)*60)
        roof=b.assembly(f'reactor.absorber_plug_fasteners_{i}','Spider',angle=(i-1)*60);roof.parent=spider
        root['maintenance_sequence']='Disconnect external services; withdraw captive screws; detach separate release-guide bridges and other roof attachments; lift spider, retaining supported absorber tubes and plugs.'
        rings=[(p['flange_radius'],seat-p['body_height']),(p['flange_radius'],seat),(p['pilot_radius'],seat),(p['pilot_radius'],seat+p['pilot_height'])]
        n=96;vertices=[(cx+r*math.cos(j*math.tau/n),r*math.sin(j*math.tau/n),z) for r,z in rings for j in range(n)]
        faces=[tuple(reversed(range(n))),tuple(range(3*n,4*n))]
        for k in range(3):
            for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
        body=b.mesh('stepped_body',root,vertices,faces,'plug_steel');body['role']='tube_plug_body'
        cutter=b.cylinder('circular_spider_opening',root,p['opening_radius'],.40,(cx,0,seat+.05),None,vertices=96,bevel=0);cut_passage(b,plate,cutter)
        groove=b.annulus('face_seal_groove',roof,p['seal_radius']-.004,p['seal_radius']+.004,seat-.001,seat+.004,None,steps=96);groove.location=(cx,0,0);cut_passage(b,plate,groove)
        seal=b.annulus('plug_face_seal',roof,p['seal_radius']-.003,p['seal_radius']+.003,seat,seat+.003,'plug_seal',steps=96);seal.location=(cx,0,0);seal['role']='plug_face_seal'
        for j in range(4):
            diameter=layout.ABSORBER_TUBES['diameters'][j%2];y=(j-1.5)*layout.ABSORBER_TUBES['riser_pitch']
            cutter=b.cylinder('tube_bore',root,diameter/2+.0005,.30,(cx,y,seat-.02),None,vertices=32,bevel=0);cut_passage(b,body,cutter)
            weld=b.annulus(f'tube_{j+1}_seal_weld',root,diameter/2-.0005,diameter/2+.003,seat+.013,seat+.017,'links',steps=32);weld.location=(cx,y,0);weld['role']='tube_seal_weld'
        build_plug_fasteners(b,p,root,roof,plate,body,cx,cy,seat,roof_top,'absorber_plug_bolts_retracted')
        # Two vessel-mounted shelves carry the flange independently of the tubes.
        for sign in (-1,1):
            shelf=rectangular_beam(b,f'support_shelf_{sign}',root,(cx,sign*.16,seat-.14),(d['hot_inner_radius'],sign*.16,seat-.14),.040,.040,'plug_steel');shelf['role']='plug_support'
        root['scope']='Illustrative welded four-tube plug with retained face seal, six captive screws and independent wall shelves; pressure, thermal and support capacity unverified.'

    scene['absorber_plug_detail_view']=False
    crop_root=b.assembly('study.absorber_plug_crop','Presentation tools')
    cutter=b.cylinder('local_spider_crop',crop_root,.30,.50,(cx,0,seat+.14),None,vertices=96,bevel=0)
    cutter.parent=spider;cutter.hide_render=True;cutter.hide_set(True)
    modifier=plate.modifiers.new('Absorber plug inspection crop','BOOLEAN');modifier.operation='INTERSECT';modifier.solver='MANIFOLD';modifier.object=cutter
    for prop in ('show_viewport','show_render'):
        property_driver(modifier,prop,None,'detail',{'detail':'absorber_plug_detail_view'})


def check_absorber_plugs(b,layout,d):
    scene=bpy.context.scene;old=scene['absorber_plug_bolts_retracted'];p=layout.ABSORBER_PLUG
    def tree(obj,dz=0):
        return BVHTree.FromPolygons([obj.matrix_world @ v.co+Vector((0,0,dz)) for v in obj.data.vertices],[tuple(f.vertices) for f in obj.data.polygons])
    body_parts=[];tubes=[];shelves=[];roofs=[]
    for i in range(1,7):
        root=b.assemblies[f'reactor.absorber_plug_{i}'];roof=b.assemblies[f'reactor.absorber_plug_fasteners_{i}']
        body=bpy.data.objects[root.name+'.stepped_body'];closed_mesh(body)
        assert roof.parent==b.assemblies['reactor.spider'] and root.parent is None
        for j in range(4):
            end=Vector((p['centre_radius'],(j-1.5)*layout.ABSORBER_TUBES['riser_pitch'],d['top_z']+.03))
            assert not body.ray_cast(end,Vector((0,0,-1)),distance=.20)[0]
        assert len([o for o in roof.children if o.get('role')=='captive_plug_bolt'])==12
        for obj in list(root.children)+list(roof.children):
            if obj.type=='MESH':closed_mesh(obj)
        for j in range(p['bolt_count']):
            a=j*math.tau/p['bolt_count'];point=Vector((p['centre_radius']+p['bolt_circle']*math.cos(a),p['bolt_circle']*math.sin(a),d['top_z']+.001))
            hit,point,*_=body.ray_cast(point,Vector((0,0,-1)),distance=.20)
            assert hit and abs(point.z-(d['top_z']-p['blind_depth']))<2e-6
        body_parts.extend(o for o in root.children if o.type=='MESH')
        shelves.extend(o for o in root.children if o.get('role')=='plug_support')
        tubes.extend(b.assemblies[f'reactor.absorber_tubes_{i}'].children)
        roofs.append(roof)
    obstacles=[(o,tree(o)) for o in body_parts+tubes]
    wall=tree(bpy.data.objects['reactor.vessel.wall'])
    for obj in body_parts:
        if obj.get('role')!='plug_support':assert not tree(obj).overlap(wall),(obj.name,'vessel wall')
    for shelf in shelves:
        for tube in tubes:assert not tree(shelf).overlap(tree(tube)),(shelf.name,tube.name)
    for step in range(16):
        scene['absorber_plug_bolts_retracted']=step/15;scene.update_tag();bpy.context.view_layer.update()
        for roof in roofs:
            body=tree(bpy.data.objects[roof.name.replace('absorber_plug_fasteners','absorber_plug')+'.stepped_body'])
            for obj in roof.children:
                if obj.get('role')=='captive_plug_bolt':assert not tree(obj).overlap(body),(step,obj.name,'screw withdrawal')
    moving=[o for o in b.assemblies['reactor.spider'].children_recursive if o.type=='MESH' and o.users_collection[0].name=='Spider']
    for step in range(1,41):
        for obj in moving:
            mesh=tree(obj,step*.025)
            for other,bvh in obstacles:assert not mesh.overlap(bvh),(step,obj.name,other.name,'spider lift past absorber plugs')
    scene['absorber_plug_bolts_retracted']=old;scene.update_tag();bpy.context.view_layer.update()
    return {'count':6,'tubes_per_plug':4,'flange_diameter_m':.40,'spider_opening_diameter_m':.27,'bolts_per_plug':6,'blind_bores_and_open_tube_passages_checked':True,'independent_wall_shelves':12,'bolt_retraction_sampled':True,'spider_vertical_lift_sample_m':.025,'spider_vertical_lift_checked_m':1.0,'separate_release_guide_bridges_and_other_roof_attachments_must_be_detached':True,'external_connections_not_modeled':True,'pressure_and_strength_qualification':False}
