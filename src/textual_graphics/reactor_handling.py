"""Remote lifting and maintenance-lock concept; geometry only, no rated hardware."""
import math
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .perforated import perforated_prism
from .reactor_checks import closed_mesh


def property_driver(obj,path,index,expression,properties):
    curve=obj.driver_add(path) if index is None else obj.driver_add(path,index)
    driver=curve.driver
    for name,prop in properties.items():
        v=driver.variables.new();v.name=name;v.type='SINGLE_PROP'
        v.targets[0].id_type='SCENE';v.targets[0].id=bpy.context.scene
        v.targets[0].data_path=f'["{prop}"]'
    driver.expression=expression


def eye(b,name,root,position,width=.24,height=.30,thickness=.04,hole=.09,turn=0):
    radius=width/2;centre=height-radius
    outline=[(-radius,0),(radius,0)]+[(radius*math.cos(j*math.pi/32),centre+radius*math.sin(j*math.pi/32)) for j in range(33)]
    obj=perforated_prism(b,name,root,outline,[(0,centre,hole/2)],-thickness/2,thickness/2,'links',axis='Y',segments=48,position=position)
    obj.rotation_euler.z=turn;obj['eye_height']=centre
    return obj


def prism(b,name,root,outline,holes,thickness,position,mat='steel'):
    return perforated_prism(b,name,root,outline,holes,-thickness/2,thickness/2,mat,axis='Y',segments=32,position=position)


def rectangular_beam(b,name,root,start,end,width,height,mat='steel'):
    a,c=Vector(start),Vector(end)
    obj=b.box(name,root,((c-a).length,width,height),(a+c)/2,mat)
    obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector((1,0,0)).rotation_difference((c-a).normalized())
    return obj


def build_grapple(b,layout,d,owner,name,cap=False):
    """Common two-bar cap head or peripheral-reflector captive-pin head."""
    if cap:
        from .reactor_lifting import build_two_bar_head
        return build_two_bar_head(b,layout,d,owner,name,'cap',d['top_z']+.15+layout.PRESENTATION['cap_thickness'])
    root=b.assembly(name,'Remote lifting tools',angle=30);root.parent=owner
    root['tool_type']='cap' if cap else 'reflector'
    h=layout.REMOTE_HANDLING
    x=math.sqrt(h['pickup_radius']**2-h['pickup_half_spacing']**2)
    points=[(x,-h['pickup_half_spacing']),(x,h['pickup_half_spacing'])]
    z=d['hot_plenum_z']+.18
    a,c=points;cx=(a[0]+c[0])/2;cy=(a[1]+c[1])/2;beam_z=z+.46
    rectangular_beam(b,'crosshead',root,(*a,beam_z),(*c,beam_z),.18,.18,'handling_tool')
    for j,(x,y) in enumerate(points,1):
        # Fork cheeks straddle the lug. Tapered tips guide docking; pin is captive.
        outline=[(-.13,.38),(.13,.38),(.13,-.04),(.065,-.12),(-.065,-.12),(-.13,-.04)]
        for side in (-1,1):
            position=(x,y+side*.067,z) if cap else (x+side*.067,y,z)
            fork=prism(b,f'fork_{j}_{side}',root,outline,[(0,0,.046)],.03,position,'handling_tool')
            if not cap:fork.rotation_euler.z=math.pi/2
        start=(x,y-.13,z) if cap else (x-.13,y,z)
        end=(x,y+.13,z) if cap else (x+.13,y,z)
        pin=b.beam(f'captive_pin_{j}',root,start,end,.035,'lock_gold');pin['role']='grapple_lock_pin'
        axis=1 if cap else 0;base=y if cap else x
        property_driver(pin,'location',axis,f'{base}+(1-engaged)*{.25 if cap else -.25}',{'engaged':'remote_grapple_engaged'})
        pos=(x,y+.25,z) if cap else (x-.25,y,z)
        b.box(f'pin_drive_{j}',root,(.13,.22,.14) if cap else (.22,.13,.14),pos,'handling_tool')
        b.cylinder(f'engagement_flag_{j}',root,.024,.08,(x,y,beam_z+.13),'lock_gold',vertices=16,bevel=0)
    mast_top=max(d['top_z']+.95,z+.9)
    b.box('lifting_mast',root,(.16,.16,mast_top-beam_z),(cx,cy,(mast_top+beam_z)/2),'handling_tool')
    b.cylinder('toolchanger_stud',root,.055,.18,(cx,cy,mast_top+.09),'links',vertices=32,bevel=0)
    b.cylinder('toolchanger_shoulder',root,.11,.05,(cx,cy,mast_top+.185),'links',vertices=32,bevel=0)
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.11,radius2=.035,depth=.10)
    b.finish(bpy.context.object,'toolchanger_lead_in',root,'links',(cx,cy,mast_top+.26))
    b.box('remote_drive_pack',root,(.38,.28,.20) if cap else (.24,.28,.20),(cx,cy,mast_top-.24),'handling_tool')
    root['scope']='Remote pin-grapple envelope; drives, sensors and load rating not engineered'
    return root


def build_remote_handling(b,layout,d):
    h=layout.REMOTE_HANDLING;scene=bpy.context.scene
    for key,value,description in [
        ('maintenance_locks_engaged',True,'Close gravity-return catches; disable to show the selected pair fully released. Visual pose only.'),
        ('maintenance_release',0.0,'Pull the common U-bar: 0 closed, 1 fully open. Only selected sector; no dynamics or load verification.'),
        ('remote_grapple_engaged',True,'Show captive pickup pins engaged; tool collections are displayed in dedicated handling views.')]:
        scene[key]=value;scene.id_properties_ui(key).update(description=description)
    scene.id_properties_ui('maintenance_release').update(min=0.0,max=1.0)
    b.material('handling_tool','#B29A54',metallic=.5,roughness=.35)
    b.material('lock_gold','#DEA345',metallic=.5,roughness=.3)
    b.material('lock_blue','#348092',metallic=.5,roughness=.32)
    lift=d['maintenance_travel'];half=h['pair_half_spacing'];floor=d['hot_plenum_z']
    pickup_x=math.sqrt(h['pickup_radius']**2-h['pickup_half_spacing']**2)
    keeper_x=math.sqrt(h['keeper_radius']**2-half**2)
    bar_z=floor+.18;raised_x=keeper_x+lift;raised_z=bar_z+lift
    pivot_x=raised_x+.28;pivot_z=raised_z+.12
    for number in range(1,7):
        owner=b.assemblies[f'reactor.sector_{number}']
        moving=b.assembly(f'reactor.handling_pickups_{number}','Reflector lifting points',angle=30);moving.parent=owner
        moving['sector_number']=number
        fixed=b.assembly(f'reactor.maintenance_locks_{number}','Maintenance locks',angle=30+(number-1)*60)
        fixed['sector_number']=number
        angle='max(1-locked,pull)*1.0471975512' if number==layout.MAINTENANCE['sector'] else '0'
        props={'locked':'maintenance_locks_engaged','pull':'maintenance_release'}
        for side in (-1,1):
            y=side*half;key='left' if side<0 else 'right'
            lug=eye(b,key+'_pickup_eye',moving,(pickup_x,side*h['pickup_half_spacing'],floor),turn=math.pi/2)
            lug['role']='reflector_pickup_eye'
            # A U-bar has two legs and a tangential crossbar, separate from the crane pickup.
            for offset in (-.09,.09):
                b.beam(key+f'_ubar_leg_{offset}',moving,(keeper_x,y+offset,floor),(keeper_x,y+offset,bar_z),.025,'lock_gold')
            bar=b.beam(key+'_ubar',moving,(keeper_x,y-.09,bar_z),(keeper_x,y+.09,bar_z),.025,'lock_gold')
            bar['role']='maintenance_keeper';bar['catch_side']=side
            wy=side*h['wall_half_spacing'];wx=math.sqrt(d['hot_inner_radius']**2-wy**2)-.025
            b.box(key+'_wall_backplate',fixed,(.07,.30,.60),(wx,wy,pivot_z),'steel')
            rectangular_beam(b,key+'_bracket',fixed,(pivot_x+.35,y,pivot_z+.04),(wx,wy,pivot_z+.04),.15,.16)
            rectangular_beam(b,key+'_brace',fixed,(pivot_x+.27,y,pivot_z-.04),(wx,wy,pivot_z-.24),.07,.08)
            # Outward stop prevents movement past the upright-link position.
            stop=b.box(key+'_outward_stop',fixed,(.035,.32,.10),(raised_x+.046,y,raised_z-.03),'steel')
            stop['role']='maintenance_outward_stop'
            for rail in (-1,1):
                rectangular_beam(b,key+f'_stop_support_{rail}',fixed,(raised_x+.046,y+rail*.13,raised_z-.03),(pivot_x+.35,y+rail*.13,pivot_z+.04),.045,.045)
            cheek_outline=[(-.10,-.10),(.42,-.10),(.42,.23),(-.10,.23)]
            for s in (-1,1):
                prism(b,key+f'_cheek_{s}',fixed,cheek_outline,[(0,0,.034)],.03,(pivot_x,y+s*.05,pivot_z))
            hook_outline=[(.10,-.08),(.10,.22),(-.10,.22),(-.10,.08),(-.35,.08),(-.40,.03),(-.40,-.22),(-.33,-.22),(-.33,-.10),(-.31,-.07),(-.24,-.07),(-.20,-.10),(-.15,-.08)]
            hook=prism(b,key+'_catch',fixed,hook_outline,[(0,0,.034),(-.28,.015,.008)],.04,(pivot_x,y,pivot_z),'lock_blue')
            hook['role']='maintenance_catch';hook['catch_side']=side
            property_driver(hook,'rotation_euler',1,angle,props)
            b.beam(key+'_pivot',fixed,(pivot_x,y-.105,pivot_z),(pivot_x,y+.105,pivot_z),.03,'links')
            rest=b.box(key+'_closing_rest',fixed,(.05,.15,.0495),(pivot_x-.075,y,pivot_z-.10525),'steel')
            rest['role']='fixed_closed_position_stop'
        from .reactor_release import build_release_bar
        build_release_bar(b,layout,d,fixed,pivot_x,pivot_z,angle,props)
        fixed['scope']='Gravity-return catches linked by a curved 10 × 50 mm plate with 10 mm uprights in stand-off U-guides. No powered catch pins or pressure-boundary release penetrations; load retention and return forces unverified.'
    number=layout.MAINTENANCE['sector']
    build_grapple(b,layout,d,b.assemblies[f'reactor.sector_{number}'],'tool.reflector_grapple')
    build_grapple(b,layout,d,b.assemblies['reactor.cap_1'],'tool.cap_grapple',cap=True)
    from .reactor_extraction import build_extraction
    build_extraction(b,layout,d)


def check_remote_handling(b,layout,d):
    scene=bpy.context.scene
    previous=(scene['maintenance_position'],scene['maintenance_locks_engaged'],scene['remote_grapple_engaged'],scene['maintenance_release'])
    # Hidden tool collections can retain stale driver transforms after a file reload.
    # Evaluate the pickup assemblies while visible, then restore their saved display state.
    tool_collection=bpy.data.collections['Remote lifting tools']
    tool_visibility=(tool_collection.hide_viewport,tool_collection.hide_render)
    object_visibility=[(o,o.hide_get(),o.hide_render) for o in tool_collection.objects]
    tool_collection.hide_viewport=False;tool_collection.hide_render=False
    for obj,_,_ in object_visibility:obj.hide_set(False);obj.hide_render=False
    scene['maintenance_position']=False;scene['maintenance_locks_engaged']=False;scene['maintenance_release']=0.0
    scene.update_tag();bpy.context.view_layer.update()
    groups={category:[o for root in b.assemblies.values() if root.get('category')==category for o in root.children_recursive if o.type=='MESH' and o.users_collection[0].name==category] for category in ('Reflector lifting points','Maintenance locks','Remote lifting tools')}
    for meshes in groups.values():
        for obj in meshes:closed_mesh(obj)
    for number in range(1,7):
        hooks=[o for o in b.assemblies[f'reactor.cap_{number}'].children if o.get('role')=='cap_lifting_hook']
        assert len(hooks)==4
        for hook in hooks:closed_mesh(hook)
    assert sum(o.get('role')=='reflector_pickup_eye' for o in groups['Reflector lifting points'])==12
    assert sum(o.get('role')=='maintenance_catch' for o in groups['Maintenance locks'])==12
    assert not any(o.get('role') in ('maintenance_locking_pin','local_release_eye','local_release_rocker') for o in groups['Maintenance locks'])
    assert sum(o.get('role')=='common_release_bar' for o in groups['Maintenance locks'])==6
    assert sum(o.get('role')=='release_guide' for o in groups['Maintenance locks'])==12
    assert not any('_shaft_guide_' in o.name or '_remote_socket_' in o.name for o in groups['Maintenance locks'])
    # Former shaft positions must now be solid spider metal.
    ring=bpy.data.objects['reactor.spider.outer_ring']
    for root in b.assemblies.values():
        if root.get('category')!='Maintenance locks':continue
        for side in (-1,1):
            wy=side*layout.REMOTE_HANDLING['wall_half_spacing'];wx=math.sqrt(d['hot_inner_radius']**2-wy**2)-.025
            for dy in (-.065,.065):
                p=root.matrix_world @ Vector((wx-.17,wy+dy,d['top_z']+.3))
                assert ring.ray_cast(ring.matrix_world.inverted() @ p,Vector((0,0,-1)),distance=.4)[0]
    def tree(obj,matrix=None):
        matrix=obj.matrix_world if matrix is None else matrix
        return BVHTree.FromPolygons([matrix @ v.co for v in obj.data.vertices],[tuple(p.vertices) for p in obj.data.polygons])
    # Fixed supports must clear the tubing and nozzle hardware in the seated pose.
    tubes=[o for category in ('Absorber tubing','Core tubing') for root in b.assemblies.values() if root.get('category')==category for o in root.children if o.type=='MESH']
    nozzles=[o for root in b.assemblies.values() if root.get('connection_type') in ('hot_outlet','cold_inlet') for o in root.children if o.type=='MESH']
    obstacles=[(o,tree(o)) for o in tubes+nozzles]
    for obj in groups['Maintenance locks']:
        mesh=tree(obj)
        for other,bvh in obstacles:
            assert not mesh.overlap(bvh),(obj.name,other.name,'fixed handling clearance')
    # Fixed hardware stays above the raised separator, except wall plates which lie outside it.
    raised_floor=d['hot_plenum_z']+d['maintenance_travel']
    for obj in groups['Maintenance locks']:
        points=[obj.matrix_world @ v.co for v in obj.data.vertices]
        if obj.name.endswith('_wall_backplate'):
            assert min(math.hypot(v.x,v.y) for v in points)>d['raised_separator_radius'],obj.name
        else:
            assert min(v.z for v in points)>raised_floor+.005,obj.name
    # Sample the new moving pickups and core tubes against fixed locks, spider and absorber tubing.
    number=layout.MAINTENANCE['sector'];owner=b.assemblies[f'reactor.sector_{number}'];turn=owner.rotation_euler.z+math.pi/6;length=d['maintenance_travel']
    moving=list(b.assemblies[f'reactor.handling_pickups_{number}'].children)+list(b.assemblies[f'reactor.core_tubes_{number}'].children)
    fixed=[o for o in groups['Maintenance locks']]+[o for root in b.assemblies.values() if root.get('category') in ('Spider','Absorber tubing') for o in root.children if o.type=='MESH']
    fixed_bvhs=[(o,tree(o)) for o in fixed]
    for degrees in range(0,91,3):
        t=math.radians(degrees);shift=Vector((length*(1-math.cos(t))*math.cos(turn),length*(1-math.cos(t))*math.sin(turn),length*math.sin(t)))
        for obj in moving:
            mesh=tree(obj,Matrix.Translation(shift) @ obj.matrix_world)
            for other,bvh in fixed_bvhs:
                assert not mesh.overlap(bvh),(degrees,obj.name,other.name,'pickup motion')
    # Catch closes around each keeper U-bar.
    scene['maintenance_locks_engaged']=True
    scene['maintenance_position']=True;scene.update_tag();bpy.context.view_layer.update()
    root=b.assemblies[f'reactor.maintenance_locks_{number}']
    for side,key in ((-1,'left'),(1,'right')):
        hook=bpy.data.objects[root.name+'.'+key+'_catch'];bar=bpy.data.objects[f'reactor.handling_pickups_{number}.{key}_ubar']
        for angle in range(0,61,3):
            matrix=root.matrix_world @ Matrix.Translation(hook.location) @ Matrix.Rotation(math.radians(angle),4,'Y')
            for obstacle in root.children:
                if obstacle.type=='MESH' and obstacle!=hook:
                    assert not tree(hook,matrix).overlap(tree(obstacle)),(angle,hook.name,obstacle.name,'hook release path')
            for keeper in b.assemblies[f'reactor.handling_pickups_{number}'].children:
                if key+'_ubar' in keeper.name:
                    assert not tree(hook,matrix).overlap(tree(keeper)),(angle,hook.name,keeper.name,'catch closure')
        assert not tree(hook).overlap(tree(bar))
        local=hook.matrix_world.inverted() @ bar.matrix_world.translation
        assert (local-Vector((-.28,0,-.12))).length<1e-5
        assert hook.ray_cast(local,Vector((-1,0,0)),distance=.12)[0],('catch not restraining inward motion',key)
    # Docked tools must clear the cap plate and core tubing, and pickup pins align with eye holes.
    for tool in (b.assemblies['tool.cap_grapple'],b.assemblies['tool.reflector_grapple']):
        cap=tool['tool_type']=='cap'
        body=bpy.data.objects['reactor.cap_1.plate'] if cap else bpy.data.objects[f'reactor.sector_{number}.radial_reflector']
        collisions=[body]+list(b.assemblies[f'reactor.core_tubes_{1 if cap else number}'].children)
        if cap:
            old_bolts=scene['sector_plug_bolts_retracted'];scene['sector_plug_bolts_retracted']=True
            scene.update_tag();bpy.context.view_layer.update()
            collisions += [o for o in b.assemblies['reactor.cap_1'].children if o.type=='MESH' and o!=body and o.get('role')!='cap_lifting_hook' and o.users_collection[0].name!='Presentation tools']
        if not cap:collisions += [o for o in root.children if o.type=='MESH']
        for obj in tool.children:
            mesh=tree(obj)
            for other in collisions:
                assert not mesh.overlap(tree(other)),(obj.name,other.name,'docked grapple')
        if not cap:
            vertices=[o.matrix_world @ v.co for o in tool.children for v in o.data.vertices]
            assert max(math.hypot(v.x,v.y) for v in vertices)<d['cap_opening_radius']*math.cos(math.pi/128)-.01, max((math.hypot(*(o.matrix_world @ v.co)[:2]),o.name) for o in tool.children for v in o.data.vertices)
            unrotate=Matrix.Rotation(-owner.rotation_euler.z,4,'Z')
            local=[unrotate @ p for p in vertices]
            assert min(min(v.y,math.sqrt(3)*v.x/2-v.y/2) for v in local)>d['spider_beam_width']/2+.01
        if cap:
            from .reactor_lifting import check_common_head
            cap_head_checks=check_common_head(tool,[o for o in b.assemblies['reactor.cap_1'].children if o.get('role')=='cap_lifting_hook'],layout,collisions)
            scene['sector_plug_bolts_retracted']=old_bolts;scene.update_tag();bpy.context.view_layer.update()
            continue
        eyes=[o for o in b.assemblies[f'reactor.handling_pickups_{number}'].children if o.get('role')=='reflector_pickup_eye']
        pins=[o for o in tool.children if o.get('role')=='grapple_lock_pin']
        for pin in pins:
            assert min((pin.matrix_world.translation-(eye.matrix_world @ Vector((0,0,eye.get('eye_height',eye.get('eye_centre_height',0)))))).length for eye in eyes)<1e-5
    scene['maintenance_locks_engaged']=False;scene.update_tag();bpy.context.view_layer.update()
    assert all(math.isclose(o.rotation_euler.y,math.pi/3,abs_tol=1e-6) for o in root.children if o.get('role')=='maintenance_catch')
    scene['maintenance_position'],scene['maintenance_locks_engaged'],scene['remote_grapple_engaged'],scene['maintenance_release']=previous
    scene.update_tag();bpy.context.view_layer.update()
    tool_collection.hide_viewport,tool_collection.hide_render=tool_visibility
    for obj,hidden,render_hidden in object_visibility:obj.hide_set(hidden);obj.hide_render=render_hidden
    return {'cap_lifting_hooks':24,'common_bar_head_cap_docking_checked':True,'pivoting_cap_head_checks':cap_head_checks,'retracted_plug_screw_cages_clear_crane_head':True,'reflector_pickup_eyes':12,'wall_catches':12,'positive_lock_pins':0,'common_release_bars':6,'stand_off_U_guides':12,'release_penetrations_through_spider':0,'former_release_passages_closed':True,'all_hardware_meshes_closed':True,
            'seated_tubing_and_nozzle_clearance_checked':True,'fixed_hardware_above_sector_envelope_checked':True,'pickup_motion_sample_degrees':list(range(0,91,3)),
            'raised_keeper_capture_checked':True,'catch_rotation_sample_degrees':list(range(0,61,3)),
            'reflector_grapple_vertical_spider_passage_checked':True,'docked_grapple_clearance_and_pickup_pin_alignment_checked':True,'release_pose_checked':True,
            'load_capacity_and_thermal_qualification':False,'actuator_transmission_and_safety_interlocks_implemented':False,
            'service_disconnects_modeled':False,'continuous_collision_proof':False}
