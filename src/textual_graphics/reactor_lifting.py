"""Opposed hooks and a common cable-opened, gravity-closing pivot head concept."""
import math
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .reactor_handling import prism, property_driver
from .reactor_checks import closed_mesh


def interface_points(layout,kind):
    cfg=layout.LIFTING_INTERFACE
    offset=cfg['top_edge_offset'] if kind=='top_reflector' else cfg['core_edge_offset']
    shift=cfg['cap_radial_shift'] if kind=='cap' else 0
    turn=Matrix.Rotation(math.pi/6,3,'Z');points=[]
    for side in (-1,1):
        for index,x in enumerate(cfg['stations']):
            half=(x-2*offset)/math.sqrt(3)
            p=turn @ Vector((x+shift,side*half,0))
            points.append((p,side,index))
    return points


def lifting_hook(b,name,owner,position,role,layout,station=0):
    # Rotate the outer station by 180 degrees so each mouth faces away from
    # the head centre. Bars enter below the lips and seat beneath the crowns.
    outline=[(-.075,0),(.075,0),(.075,.255),(-.09,.255),(-.09,.150),(-.055,.150),(-.055,.205),(.035,.205),(.035,.070),(-.075,.070)]
    obj=prism(b,name,owner,outline,[],layout.LIFTING_INTERFACE['hook_thickness'],position,'links')
    obj.rotation_euler.z=math.pi/6+(math.pi if station else 0);obj['role']=role
    obj['pickup_system']='parallel_two_bar_v2';obj['mouth_direction']='outward from the two-bar head centre'
    obj['station_index']=station
    obj['loaded_bar_height']=layout.LIFTING_INTERFACE['loaded_bar_height']
    obj['load_rating']='unrated visual concept'
    return obj


def build_cap_hooks(b,layout,d,cap):
    foot=d['top_z']+.15+layout.PRESENTATION['cap_thickness']
    for index,(point,side,station) in enumerate(interface_points(layout,'cap'),1):
        hook=lifting_hook(b,f'lifting_hook_{index}',cap,(*point[:2],foot),'cap_lifting_hook',layout,station)
        hook['attachment']='welded cap hook; weld sizing and local reinforcement not qualified'
        hook['station_index']=station


def swing_geometry(layout):
    c=layout.LIFTING_INTERFACE
    closed=math.atan2(c['pivot_inset'],c['pivot_above_bar'])
    return closed,math.radians(c['open_angle_degrees'])-closed


def swing_part(obj,pivot,side,delta):
    """Bake the construction transform; animate a rigid mesh about its real pin."""
    matrix=Matrix.Translation(-Vector(pivot)) @ obj.matrix_local
    obj.data.transform(matrix);obj.rotation_mode='XYZ';obj.matrix_local=Matrix.Translation(pivot)
    property_driver(obj,'rotation_euler',1,f'{-side*delta:.9f}*release',{'release':'lifting_bars_open'})
    obj['swing_side']=side;obj['role']=obj.get('role','swing_arm_part')


def build_two_bar_head(b,layout,d,owner,name,kind,foot):
    cfg=layout.LIFTING_INTERFACE;shift=cfg['cap_radial_shift'] if kind=='cap' else 0
    scene=bpy.context.scene
    if 'lifting_bars_open' not in scene:
        scene['lifting_bars_open']=0.0
        scene.id_properties_ui('lifting_bars_open').update(min=0.0,max=1.0,description='0 engaged, 1 spread by release cable. Unload and lower the head before spreading; this slider is a kinematic display, not an interlock.')
    if 'lifting_head_lowered' not in scene:
        scene['lifting_head_lowered']=0.0
        scene.id_properties_ui('lifting_head_lowered').update(min=0.0,max=1.0,description='Lower the unloaded head 88 mm before spreading its bars; display pose only.')
    root=b.assembly(name,'Remote lifting tools' if kind=='cap' else 'Extraction tools',position=(shift*math.cos(math.pi/6),shift*.5,0),angle=30)
    root.parent=owner;root['tool_type']=kind;root['pickup_system']='parallel_two_bar_v2'
    root['tool_family']='Common pivoting two-bar head; instances depict the same tool'
    root['radial_shift']=shift;root['base_location']=tuple(root.location)
    property_driver(root,'location',2,f'{cfg["entry_bar_height"]-cfg["loaded_bar_height"]}*lowered',{'lowered':'lifting_head_lowered'})
    z=foot+cfg['loaded_bar_height'];root['bar_height']=z
    closed,delta=swing_geometry(layout);inset=cfg['pivot_inset'];drop=cfg['pivot_above_bar']
    first,last=cfg['stations'];centre=(first+last)/2;pz=z+drop
    half_pivots=(last-first)/2-inset
    length=math.hypot(half_pivots+.12,.20)
    horn_span=f'({half_pivots:.9f}+.12*(cos({delta:.9f}*release)-sin({delta:.9f}*release)))'
    horn_z=f'(.12*(cos({delta:.9f}*release)+sin({delta:.9f}*release)))'
    rise=f'sqrt({length**2:.9f}-{horn_span}**2)'
    equalizer_z=f'({pz:.9f}+{horn_z}+{rise})'
    for index,(x,half) in enumerate(zip(cfg['stations'],cfg['bar_half_lengths']),1):
        side=-1 if index==1 else 1;px=x-side*inset;pivot=(px,0,pz)
        rod=b.beam(f'pickup_bar_{index}',root,(x,-half,z),(x,half,z),cfg['bar_diameter']/2,'lock_gold')
        rod['role']='common_pickup_bar';rod['station_index']=index-1;rod['bar_radius']=cfg['bar_diameter']/2
        rod['closed_local_centre']=(side*inset,0,-drop)
        moving=[rod]
        for sign in (-1,1):
            moving.append(b.beam(f'bar_{index}_end_shoulder_{sign}',root,(x,sign*(half-.008),z),(x,sign*half,z),.026,'links'))
        outline=[(-.045,.04),(.045,.04),(.115,-drop),(.095,-drop-.045),(.04,-drop-.045),(-.025,-.04)]
        arm=prism(b,f'swing_arm_{index}',root,[(side*a,h) for a,h in outline],[(0,0,.017),(side*inset,-drop,.0205)],.040,pivot,'handling_tool');moving.append(arm)
        horn=[(-.03,-.03),(.03,-.03),(.145,.10),(.145,.145),(.09,.145),(-.03,.03)]
        moving.append(prism(b,f'release_horn_{index}',root,[(side*a,h) for a,h in horn],[(0,0,.017),(side*.12,.12,.008)],.020,(px,.18,pz),'lock_gold'))
        moving.append(b.beam(f'swing_hub_{index}',root,(px,-.075,pz),(px,.195,pz),.026,'handling_tool'))
        # The hub sleeve is bored along the pin axis.
        from .reactor_tubing import cut_passage
        sleeve=moving[-1];cutter=b.beam('hub_bore',root,(px,-.10,pz),(px,.22,pz),.017,None);cut_passage(b,sleeve,cutter)
        for obj in moving:swing_part(obj,pivot,side,delta)
        pin=b.beam(f'hinge_pin_{index}',root,(px,-.09,pz),(px,.23,pz),.016,'links');pin['role']='head_pivot_pin'
        for y in (-.06,.06):
            support=b.box(f'pivot_clevis_{index}_{y}',root,(.10,.020,.20),(px,y,pz+.04),'steel')
            cutter=b.beam('pin_bore',root,(px,y-.03,pz),(px,y+.03,pz),.027,None);cut_passage(b,support,cutter)
        # Two constant-length tension branches lift the offset horns together.
        cable=b.beam(f'release_branch_{index}',root,(px+side*.12,.18,pz+.12),(centre,.18,pz+.32),.004,'dark')
        cable.rotation_mode='XYZ';cable.rotation_euler=(0,math.atan2(-side*(half_pivots+.12),.20),0)
        property_driver(cable,'location',0,f'{centre:.9f}+({side})*{horn_span}/2',{'release':'lifting_bars_open'})
        property_driver(cable,'location',2,f'{pz:.9f}+{horn_z}+{rise}/2',{'release':'lifting_bars_open'})
        property_driver(cable,'rotation_euler',1,f'atan2(({ -side })*{horn_span},{rise})',{'release':'lifting_bars_open'})
        cable['role']='release_cable_branch';cable['nominal_length']=length
    b.box('spine',root,(last-first+.16,.10,.10),(centre,0,z+.60),'handling_tool')
    root['suspension_centre']=centre
    root['suspension_scope']='Upright centered between the pivot axes; actual load sharing depends on the lifted assembly centre of mass'
    b.box('suspension_carriage',root,(.18,.15,.12),(centre,0,z+.65),'steel')
    top=z+cfg['mast_above_bars'];root['mast_above_bars']=cfg['mast_above_bars']
    b.box('mast',root,(.12,.10,top-z-.68),(centre,0,(top+z+.68)/2),'handling_tool')
    b.cylinder('toolchanger_stud',root,.055,.18,(centre,0,top+.09),'links',vertices=32,bevel=0)
    b.cylinder('toolchanger_shoulder',root,.11,.05,(centre,0,top+.185),'links',vertices=32,bevel=0)
    eye=b.cylinder('release_equalizer',root,.023,.030,(centre,.18,pz+.32),'lock_gold',vertices=24,bevel=0)
    property_driver(eye,'location',2,equalizer_z,{'release':'lifting_bars_open'})
    cable=b.beam('release_pull_cable',root,(centre,.18,pz+.335),(centre,.18,top+.43),.004,'dark')
    property_driver(cable,'location',2,f'{(pz+.335+top+.43)/2-pz-.32:.9f}+{equalizer_z}',{'release':'lifting_bars_open'})
    root['closed_swing_angle_degrees']=math.degrees(closed);root['open_swing_angle_degrees']=cfg['open_angle_degrees']
    root['scope']='Gravity closing intent from outboard pendulum arms; cable spreads unloaded bars. Hook lips geometrically obstruct opening at carrying height. Dynamics, friction, load sharing, strength and release interlocks are not qualified.'
    return root


def check_common_head(root,hooks,layout,obstacles=()):
    cfg=layout.LIFTING_INTERFACE;scene=bpy.context.scene;old=scene['lifting_bars_open']
    def pose(value):
        scene['lifting_bars_open']=value;scene.update_tag();bpy.context.view_layer.update()
    def tree(obj,delta=Vector((0,0,0))):
        return BVHTree.FromPolygons([obj.matrix_world @ v.co+delta for v in obj.data.vertices],[tuple(p.vertices) for p in obj.data.polygons])
    pose(0)
    bars=sorted([o for o in root.children if o.get('role')=='common_pickup_bar'],key=lambda o:o['station_index'])
    assert len(bars)==2 and len(hooks)==4
    midpoint=sum(cfg['stations'])/2
    for part in ('suspension_carriage','mast','toolchanger_stud','toolchanger_shoulder'):
        obj=bpy.data.objects[root.name+'.'+part]
        assert math.isclose(obj.location.x,midpoint,abs_tol=1e-6) and abs(obj.location.y)<1e-6,(obj.name,'centred suspension')
    pins=[bpy.data.objects[f'{root.name}.hinge_pin_{i}'] for i in (1,2)]
    assert math.isclose((pins[0].location.x+pins[1].location.x)/2,midpoint,abs_tol=1e-6)
    for hook in hooks:
        station=hook['station_index'];bar=bars[station]
        centre=hook.matrix_world @ Vector((0,0,cfg['loaded_bar_height']))
        point=bar.matrix_world @ Vector(bar['closed_local_centre'])
        axis=bar.matrix_world.to_3x3() @ Vector((0,1,0));offset=centre-point
        assert (offset-axis*offset.dot(axis)).length<2e-5,(hook.name,'bar alignment')
        assert abs(offset.dot(axis))+cfg['hook_thickness']/2<cfg['bar_half_lengths'][station]-.008
        mouth=hook.matrix_world.to_3x3() @ Vector((-1,0,0))
        radial=root.matrix_world.to_3x3() @ Vector((-1 if station==0 else 1,0,0))
        assert mouth.dot(radial)>.99999,(hook.name,'outward mouth')
    for obj in root.children:closed_mesh(obj)
    lower=cfg['entry_bar_height']-cfg['loaded_bar_height']
    # Pass the service tubes closed, then spread just above the hooks.
    # Keeping the bars open throughout the descent crosses a top service run.
    approach=.17
    steps=[(0,approach+.10*j) for j in range(30,-1,-1)]+[(j/20,approach) for j in range(1,21)]+[(1,approach+(lower-approach)*j/20) for j in range(1,21)]+[(1-j/20,lower) for j in range(1,21)]+[(0,lower*(1-j/10)) for j in range(1,11)]
    fixed=[(o,tree(o)) for o in list(hooks)+list(obstacles)]
    for release,dz in steps:
        pose(release)
        for obj in root.children:
            mesh=tree(obj,Vector((0,0,dz)))
            for other,bvh in fixed:assert not mesh.overlap(bvh),(root.name,release,dz,obj.name,other.name,'pivot-head docking')
        axes=[(o.matrix_world.to_3x3() @ Vector((0,1,0))).normalized() for o in bars]
        assert axes[0].dot(axes[1])>.99999
    body=[(o,tree(o)) for o in root.children if o.name.rsplit('.',1)[-1].startswith(('pivot_clevis','spine','mast','suspension_carriage'))]
    for j in range(21):
        pose(j/20)
        for obj in root.children:
            if 'swing_side' in obj:
                for other,bvh in body:assert not tree(obj).overlap(bvh),(obj.name,other.name,j,'swing arm/body clearance')
        for index in (1,2):
            side=-1 if index==1 else 1
            horn=bpy.data.objects[f'{root.name}.release_horn_{index}']
            cable=bpy.data.objects[f'{root.name}.release_branch_{index}']
            eye=bpy.data.objects[root.name+'.release_equalizer']
            start=horn.matrix_world @ Vector((side*.12,.18,.12))
            # Horn mesh coordinates share the pin origin after baking.
            target=eye.matrix_world.translation
            length=cable['nominal_length']
            assert ((cable.matrix_world @ Vector((0,0,-length/2)))-start).length<5e-6,(index,j,'release branch lower attachment')
            assert ((cable.matrix_world @ Vector((0,0,length/2)))-target).length<5e-6,(index,j,'release branch upper attachment')
    # At carrying height each lip obstructs the arm-opening path; this is a
    # geometric capture check, not a load or failure-mode qualification.
    captured={o.name:False for o in hooks}
    for j in range(1,21):
        pose(j/20)
        for hook in hooks:
            captured[hook.name] |= bool(tree(bars[hook['station_index']]).overlap(tree(hook)))
    assert all(captured.values()),('loaded lip capture',captured)
    pose(old)
    return {'upright_centred_between_pivots':True,'four_outward_facing_hooks':True,'two_parallel_swing_bars':True,'closed_approach_then_spread_lower_close_and_seat_checked':True,'reverse_unloaded_withdrawal_uses_same_path':True,'loaded_opening_obstructed_by_all_hook_lips':True,'swing_arm_body_clearance_checked':True,'constant_length_cable_branches_and_attachments_checked':True,'gravity_return_and_load_capacity_verified':False}
