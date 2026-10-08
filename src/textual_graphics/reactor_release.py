"""Curved plate release crossbar with rod uprights and rocking guides; visual concept only."""
import math
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .reactor_handling import property_driver, rectangular_beam
from .reactor_checks import closed_mesh


def round_rod(b,name,parent,points,radius,material):
    """Closed round rod with rounded bends and transported circular sections."""
    points=[Vector(p) for p in points];path=[points[0]]
    for a,c,e in zip(points,points[1:],points[2:]):
        if (c-a).normalized().dot((e-c).normalized())>.995:
            path.append(c);continue
        distance=min(.025,(a-c).length*.4,(e-c).length*.4)
        u=c+(a-c).normalized()*distance;v=c+(e-c).normalized()*distance
        path.append(u)
        for j in range(1,9):
            t=j/8;path.append((1-t)**2*u+2*(1-t)*t*c+t*t*v)
    path.append(points[-1]);vertices=[];faces=[];segments=16
    last=None;normal=None
    for i,p in enumerate(path):
        tangent=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized()
        if last is None:
            reference=Vector((0,0,1)) if abs(tangent.z)<.9 else Vector((1,0,0))
            normal=tangent.cross(reference).normalized()
        else:normal=last.rotation_difference(tangent) @ normal
        normal=(normal-tangent*normal.dot(tangent)).normalized();side=tangent.cross(normal)
        vertices.extend(tuple(p+radius*(math.cos(j*math.tau/segments)*normal+math.sin(j*math.tau/segments)*side)) for j in range(segments))
        last=tangent
    for i in range(len(path)-1):
        for j in range(segments):faces.append((i*segments+j,i*segments+(j+1)%segments,(i+1)*segments+(j+1)%segments,(i+1)*segments+j))
    faces += [tuple(reversed(range(segments))),tuple((len(path)-1)*segments+j for j in range(segments))]
    obj=b.mesh(name,parent,vertices,faces,material);closed_mesh(obj)
    return obj


def dependent_driver(obj,path,index,expression,variables):
    curve=obj.driver_add(path) if index is None else obj.driver_add(path,index)
    for name,(source,data_path) in variables.items():
        v=curve.driver.variables.new();v.name=name;v.type='SINGLE_PROP'
        v.targets[0].id=source;v.targets[0].data_path=data_path
    curve.driver.expression=expression


def build_release_bar(b,layout,d,fixed,px,pz,angle,props):
    root=b.assembly(fixed.name+'.release','Maintenance locks');root.parent=fixed
    root['sector_number']=fixed['sector_number'];root['swing']=0.0
    root['role']='release_assembly';root['category']='Release subassembly'
    property_driver(root,'["swing"]',None,angle,props)
    # Lower pin axes remain parallel to the hook pivots. A rigid U-bar rocks
    # in its guides while its two ends follow the hook holes exactly.
    hx,hz=-.28,.015;span=layout.REMOTE_HANDLING['pair_half_spacing']-.10
    radius=2.62;height=.59;base=px+hx;tipx=math.sqrt(radius*radius-span*span)
    lean=tipx-base;length=math.hypot(lean,height);initial=math.atan2(lean,height)
    v={'a':(root,'["swing"]')}
    dependent_driver(root,'location',0,f'{px:.8f}-.28*cos(a)+.015*sin(a)',v)
    dependent_driver(root,'location',2,f'{pz:.8f}+.28*sin(a)+.015*cos(a)',v)
    dependent_driver(root,'rotation_euler',1,f'asin(({tipx:.8f}-({px:.8f}-.28*cos(a)+.015*sin(a)))/{length:.8f})-({initial:.8f})',v)
    vertices=[];faces=[];arc=math.asin(span/radius)
    for i in range(41):
        theta=-arc+2*arc*i/40
        for r,z in ((radius-.005,height-.025),(radius+.005,height-.025),(radius+.005,height+.025),(radius-.005,height+.025)):
            vertices.append((r*math.cos(theta)-base,r*math.sin(theta),z))
    for i in range(40):
        for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    faces += [(3,2,1,0),(160,161,162,163)]
    bar=b.mesh('curved_release_plate',root,vertices,faces,'lock_gold');closed_mesh(bar)
    bar['role']='common_release_bar';bar['plate_thickness']=.010;bar['plate_height']=.050
    for side,key in ((-1,'left'),(1,'right')):
        rod=round_rod(b,key+'_upright',root,[(0,side*(span+.15),0),(0,side*span,0),(lean,side*span,height)],.005,'lock_gold')
        rod['role']='release_upright';rod['rod_diameter']=.010
    root['pin_half_spacing']=layout.REMOTE_HANDLING['pair_half_spacing']
    root['guide_span']=span;root['top_height']=height;root['top_center_x']=radius-base
    root['hook_hole']=hx,hz;root['leg_lean']=lean
    for side,key in ((-1,'left'),(1,'right')):
        # Captive end buttons shown as permanent shop-installed retainers.
        b.beam(key+'_end_retainer',root,(0,side*(span+.143),0),(0,side*(span+.155),0),.010,'links')
        y=side*span;z=6.0
        guide=round_rod(b,key+'_U_guide',fixed,[(2.72,y-.045,z),(2.53,y-.045,z),(2.53,y+.045,z),(2.72,y+.045,z)],.006,'lock_blue')
        guide['role']='release_guide';guide['clearance_intent']='Vertical sliding plus radial rocking of the 10 mm rod'
        mount=b.box(key+'_guide_mount',fixed,(.025,.12,.37),(2.72,y,6.175),'steel')
        end=math.sqrt(d['cap_opening_radius']**2-y*y)+.055
        rectangular_beam(b,key+'_guide_spider_bridge',fixed,(2.72,y,6.355),(end,y,6.355),.12,.030,'steel')
        mount['attachment']='Fixed bridge reaches the resized spider ring; no through-rod penetration'
    root['scope']='Curved 10 × 50 mm plate and 10 mm rod uprights follow both rotating hooks. Gravity-return intent only; contact forces, friction and strength not analyzed.'
    return root


def build_release_tool(b,layout,d):
    number=layout.MAINTENANCE['sector'];fixed=b.assemblies[f'reactor.maintenance_locks_{number}']
    bar=b.assemblies[fixed.name+'.release']
    root=b.assembly('tool.local_release_hook','Remote release tools');root.parent=fixed
    root['scope']='Temporary secondary crane/robot hook pulls the common bar; not the sector load'
    cx=bar['top_center_x'];h=bar['top_height']-.024
    v={'x':(bar,'location[0]'),'z':(bar,'location[2]'),'q':(bar,'rotation_euler[1]')}
    dependent_driver(root,'location',0,f'x+{cx:.8f}*cos(q)+{h}*sin(q)',v)
    dependent_driver(root,'location',2,f'z-{cx:.8f}*sin(q)+{h}*cos(q)',v)
    points=[(-.026,0,.14),(-.026,0,.017)]
    points += [(.026*math.cos(a),0,.017+.026*math.sin(a)) for a in [math.pi+i*math.pi/24 for i in range(1,25)]]
    points += [(.026,0,.080)]
    points=[(-x,y,z) for x,y,z in points]
    hook=round_rod(b,'pickup_hook',root,points,.004,'handling_tool')
    hook['role']='temporary_release_hook'
    # Vertical cable with fixed upper elevation; its lower end follows the bar.
    upper=d['top_z']+2.1
    cable=b.beam('secondary_cable',root,(.026,0,.14),(.026,0,1.0),.003,'dark')
    v={'z':(root,'location[2]')}
    dependent_driver(cable,'location',2,f'({upper}-z+.14)/2',v)
    dependent_driver(cable,'scale',2,f'({upper}-z-.14)/.86',v)
    stud=b.cylinder('secondary_hoist_attachment',root,.012,.08,(.026,0,1.0),'links',vertices=24,bevel=0)
    dependent_driver(stud,'location',2,f'{upper}-z+.04',v)
    return root


def check_release_bar(b,layout,d):
    scene=bpy.context.scene
    old=(scene['maintenance_locks_engaged'],scene['maintenance_release'],scene['maintenance_position'])
    categories=('Remote release tools','Remote lifting tools')
    visibility=[]
    for name in categories:
        col=bpy.data.collections[name];visibility.append((col,col.hide_viewport))
        col.hide_viewport=False
        for obj in col.objects:visibility.append((obj,obj.hide_get()));obj.hide_set(False)
    number=layout.MAINTENANCE['sector'];fixed=b.assemblies[f'reactor.maintenance_locks_{number}'];root=b.assemblies[fixed.name+'.release']
    tool=b.assemblies['tool.local_release_hook'];primary=b.assemblies['tool.reflector_grapple']
    scene['maintenance_position']=True;scene['maintenance_locks_engaged']=True
    def tree(obj):
        return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],[tuple(p.vertices) for p in obj.data.polygons])
    spider=[o for o in b.assemblies['reactor.spider'].children if o.type=='MESH']
    tubes=[o for r in b.assemblies.values() if r.get('category') in ('Core tubing','Absorber tubing','Sector tube plugs') for o in r.children if o.type=='MESH']
    guides=[o for o in fixed.children if o.get('role')=='release_guide']
    fixed_parts=[o for o in fixed.children if o.type=='MESH' and o.get('role')!='maintenance_catch']
    scene.update_tag();bpy.context.view_layer.update()
    fixed_trees=[(o,tree(o)) for o in fixed_parts+spider+tubes+list(primary.children)]
    access_trees=[(o,tree(o)) for o in spider+tubes+list(primary.children)+guides]
    rises=[];rocks=[]
    for degrees in range(0,61,2):
        scene['maintenance_release']=degrees/60;scene.update_tag();bpy.context.view_layer.update()
        for side,key in ((-1,'left'),(1,'right')):
            hook=bpy.data.objects[fixed.name+'.'+key+'_catch']
            p=hook.matrix_world @ Vector((-.28,0,.015))
            q=root.matrix_world @ Vector((0,side*layout.REMOTE_HANDLING['pair_half_spacing'],0))
            assert (p-q).length<2e-6,(degrees,key,'bent rod end alignment')
            # Guide plane intersects the straight leg inside its clear rectangle.
            local=root.matrix_local @ Vector((0,side*root['guide_span'],0))
            tip=root.matrix_local @ Vector((root['leg_lean'],side*root['guide_span'],root['top_height']))
            fraction=(6.0-local.z)/(tip.z-local.z)
            cross=local.lerp(tip,fraction)
            assert 0<fraction<1
            assert 2.53+.006+.005<cross.x<2.72-.0125-.005,(degrees,key,cross.x,'guide clearance')
        for obj in root.children:
            mesh=tree(obj)
            for other,bvh in fixed_trees:
                assert not mesh.overlap(bvh),(degrees,obj.name,other.name,'U-bar sweep')
            for key in ('left','right'):
                other=bpy.data.objects[fixed.name+'.'+key+'_catch']
                assert not mesh.overlap(tree(other)),(degrees,obj.name,other.name,'bent rod in hook hole')
        moving_trees=[(o,tree(o)) for o in root.children]
        for obj in tool.children:
            mesh=tree(obj)
            for other,bvh in access_trees+moving_trees:
                assert not mesh.overlap(bvh),(degrees,obj.name,other.name,'secondary hook access')
            if obj.animation_data:assert all(f.driver.is_valid for f in obj.animation_data.drivers),obj.name
        rises.append((root.matrix_world @ Vector((root['top_center_x'],0,root['top_height']))).z)
        rocks.append(root.rotation_euler.y)
    assert all(b>a for a,b in zip(rises,rises[1:])),rises
    scene['maintenance_locks_engaged'],scene['maintenance_release'],scene['maintenance_position']=old
    scene.update_tag();bpy.context.view_layer.update()
    for item,state in visibility:
        if isinstance(item,bpy.types.Collection):item.hide_viewport=state
        else:item.hide_set(state)
    return {'bar_count':6,'plate_thickness_m':.010,'plate_height_m':.050,'upright_rod_diameter_m':.010,'guide_count':12,'sample_degrees':list(range(0,61,2)),
            'hook_hole_alignment':True,'rocking_guide_clearance':True,'tube_and_spider_clearance':True,
            'pickup_rise_m':rises[-1]-rises[0],'rock_angle_degrees':math.degrees(rocks[-1]),
            'positive_lock_pins':0,'gravity_return_dynamics_verified':False,'load_retention_verified':False}
