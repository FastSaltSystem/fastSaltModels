"""Independent top-reflector and edge-supported core removal, plus temporary release tool."""
import math
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .reactor_checks import closed_mesh
from .reactor_tubing import cut_passage


def build_extraction(b,layout,d):
    from .reactor_lifting import interface_points, lifting_hook, build_two_bar_head
    core_points=interface_points(layout,'core');top_points=interface_points(layout,'top_reflector')
    for number in range(1,7):
        core=bpy.data.objects[f'reactor.sector_{number}.core'];top=bpy.data.objects[f'reactor.sector_{number}.top_reflector']
        root=b.assembly(f'reactor.core_lifting_{number}','Core lifting points');root.parent=core;root['sector_number']=number
        for index,(point,side,station) in enumerate(core_points,1):
            lug=lifting_hook(b,f'edge_hook_{index}',root,(*point[:2],d['top_reflector_z']-.01),'core_edge_pickup',layout,station)
            lug['station_index']=station;lug['attachment']='Short inward tab carried by core side structure'
            angle=0 if side==-1 else math.pi/3
            inward=Vector((0,1,0)) if side==-1 else Vector((math.sin(angle),-math.cos(angle),0))
            edge=point-inward*(layout.LIFTING_INTERFACE['core_edge_offset']-.060)
            strap=b.box(f'side_attachment_{index}',root,(.18,.025,.23),(*edge[:2],d['top_reflector_z']-.115),'links');strap.rotation_euler.z=angle
            middle=edge+inward*.04
            tab=b.box(f'side_tab_{index}',root,(.18,.105,.025),(*middle[:2],d['top_reflector_z']-.015),'links');tab.rotation_euler.z=angle
            middle=point-inward*(layout.LIFTING_INTERFACE['core_edge_offset']-.05)
            cutter=b.box('core_hook_relief',root,(.26,.30,.29),(*middle[:2],d['top_reflector_z']+.125),None)
            cutter.rotation_euler.z=angle;cut_passage(b,top,cutter)
        root=b.assembly(f'reactor.top_reflector_lifting_{number}','Top reflector lifting points');root.parent=top;root['sector_number']=number
        for index,(point,side,station) in enumerate(top_points,1):
            lug=lifting_hook(b,f'hook_{index}',root,(*point[:2],d['hot_plenum_z']),'top_reflector_pickup',layout,station)
            lug['station_index']=station;lug['attachment']='Reflector surface; local attachment reinforcement remains to be designed'
        cutter=b.box('top_service_edge_slot',root,(1.78,.16,.29),(1.09,.03,d['top_reflector_z']+.125),None)
        cut_passage(b,top,cutter)
    number=layout.MAINTENANCE['sector']
    build_two_bar_head(b,layout,d,bpy.data.objects[f'reactor.sector_{number}.top_reflector'],'tool.top_reflector_grapple','top_reflector',d['hot_plenum_z'])
    build_two_bar_head(b,layout,d,bpy.data.objects[f'reactor.sector_{number}.core'],'tool.core_grapple','core',d['top_reflector_z']-.01)
    from .reactor_release import build_release_tool
    build_release_tool(b,layout,d)


def check_extraction(b,layout,d):
    scene=bpy.context.scene;old=scene['maintenance_position'];old_locked=scene['maintenance_locks_engaged']
    hidden={}
    for name in ('Extraction tools','Remote release tools'):
        col=bpy.data.collections[name];hidden[name]=col.hide_viewport;col.hide_viewport=False
        for obj in col.objects:
            hidden[obj.name]=obj.hide_get();obj.hide_set(False)
    scene['maintenance_position']=True
    scene['maintenance_locks_engaged']=True;scene.update_tag();bpy.context.view_layer.update()
    number=layout.MAINTENANCE['sector'];owner=b.assemblies[f'reactor.sector_{number}']
    def tree(obj,matrix=None,vertices=None):
        matrix=obj.matrix_world if matrix is None else matrix
        vertices=[matrix @ v.co for v in obj.data.vertices] if vertices is None else vertices
        return BVHTree.FromPolygons(vertices,[tuple(p.vertices) for p in obj.data.polygons])
    for category in ('Core lifting points','Top reflector lifting points'):
        objects=[o for root in b.assemblies.values() if root.get('category')==category for o in root.children]
        assert sum(o.get('role') in ('core_edge_pickup','top_reflector_pickup') for o in objects)==24
        for obj in objects:closed_mesh(obj)
    top=bpy.data.objects[f'reactor.sector_{number}.top_reflector'];core=bpy.data.objects[f'reactor.sector_{number}.core']
    core_eyes=list(b.assemblies[f'reactor.core_lifting_{number}'].children)
    top_eyes=list(b.assemblies[f'reactor.top_reflector_lifting_{number}'].children)
    tubes=list(b.assemblies[f'reactor.core_tubes_{number}'].children)
    tubes += list(b.assemblies[f'reactor.sector_plug_{number}'].children)
    tube_trees=[(o,tree(o)) for o in tubes]
    obstacles=tube_trees+[(o,tree(o)) for o in core_eyes]
    # Exact vertical sweep of the top reflector's constant-section perforated mesh.
    vertices=[top.matrix_world @ v.co for v in top.data.vertices]
    low=min(v.z for v in vertices);high=max(v.z for v in vertices)
    # Sub-square-millimetre Boolean slivers can have ~0.1 degree normal noise.
    assert all(abs(p.normal.z)<(3e-3 if p.area<1e-6 else 1e-3) or abs(abs(p.normal.z)-1)<1e-3 for p in top.data.polygons)
    # Boolean triangulation adds intermediate vertices on vertical side faces.
    swept=[Vector((v.x,v.y,low+(v.z-low)*(high-low+3)/(high-low))) for v in vertices]
    volume=tree(top,vertices=swept)
    for other,bvh in obstacles:assert not volume.overlap(bvh),(top.name,other.name,'top-reflector vertical sweep')
    tools=[b.assemblies['tool.top_reflector_grapple'],b.assemblies['tool.core_grapple']]
    for root in tools:
        top_tool=root['tool_type']=='top_reflector'
        parts=(top_eyes if top_tool else core_eyes)+list(root.children)
        for obj in parts:
            closed_mesh(obj)
            for other,bvh in tube_trees:
                assert not tree(obj).overlap(bvh),(obj.name,other.name,'pickup clearance')
        if top_tool:
            for rise in (.15,.30,.50,.75,1.,1.25,1.5,2.,2.5,3.):
                for obj in parts:
                    moved=tree(obj,Matrix.Translation((0,0,rise)) @ obj.matrix_world)
                    for other,bvh in tube_trees:
                        assert not moved.overlap(bvh),(rise,obj.name,other.name,'top pickup lift')
        meshes=parts+[top if top_tool else core]+([] if top_tool else tubes)
        points=[obj.matrix_world @ v.co for obj in meshes for v in obj.data.vertices]
        assert max(math.hypot(v.x,v.y) for v in points)<d['cap_opening_radius']*math.cos(math.pi/128)-.005
        local=[Matrix.Rotation(-owner.rotation_euler.z,4,'Z') @ v for v in points]
        assert min(min(v.y,math.sqrt(3)*v.x/2-v.y/2) for v in local)>d['spider_beam_width']/2+.005
    retained=[o for o in b.assemblies[f'reactor.maintenance_locks_{number}'].children_recursive if o.type=='MESH' and o.users_collection[0].name=='Maintenance locks']
    retained += [bpy.data.objects[f'reactor.sector_{number}.radial_reflector']]
    obstacles=[(o,tree(o)) for o in retained]
    for step in range(31):
        rise=step*.2
        for obj in tubes+list(b.assemblies['tool.core_grapple'].children):
            moved=tree(obj,Matrix.Translation((0,0,rise)) @ obj.matrix_world)
            for other,bvh in obstacles:
                assert not moved.overlap(bvh),(rise,obj.name,other.name,'core extraction')
    from .reactor_lifting import check_common_head
    common_checks={}
    for root in tools:
        top_tool=root['tool_type']=='top_reflector'
        hooks=[o for o in (top_eyes if top_tool else core_eyes) if o.get('pickup_system')=='parallel_two_bar_v2']
        common_checks[root['tool_type']]=check_common_head(root,hooks,layout,tubes+[top if top_tool else core])
    # Sample the hook-foot contact with the perforated reflector surface.
    contact=[]
    for lug in top_eyes:
        hits=0
        for i in range(15):
            for y in (-.008,0,.008):
                p=top.matrix_world.inverted() @ (lug.matrix_world @ Vector((-.070+i*.010,y,.002)))
                hits+=bool(top.ray_cast(p,Vector((0,0,-1)),distance=.01)[0])
        contact.append(hits/45)
        assert hits>=22,(lug.name,hits,'reflector hook footprint support')
    from .reactor_release import check_release_bar
    release_checks=check_release_bar(b,layout,d)
    scene['maintenance_position']=old;scene['maintenance_locks_engaged']=old_locked
    for name in ('Extraction tools','Remote release tools'):
        col=bpy.data.collections[name];col.hide_viewport=hidden[name]
        for obj in col.objects:obj.hide_set(hidden[obj.name])
    scene.update_tag();bpy.context.view_layer.update()
    return {'core_edge_lifting_hooks':24,'top_reflector_lifting_hooks':24,'top_reflector_body_vertical_sweep_clear':True,
            'top_reflector_pickup_sampled_lift_clear':True,'core_and_top_pickups_fit_spider':True,'common_U_bar':release_checks,
            'release_shafts_and_roof_passages_removed':True,'temporary_release_tool_clearance_checked':True,'pivoting_head_checks':common_checks,'common_two_bar_alignment_and_entry_checked':True,'core_extraction_sample_spacing_m':.2,'reflector_hook_foot_contact_fractions':contact,'lifting_capacity_and_control_logic_verified':False}
