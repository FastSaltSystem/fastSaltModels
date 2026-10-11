"""Provisional equipment entrance and selected access-envelope checks."""
import math
import bpy
from mathutils import Vector


def equipment_access(b,layout):
    p=layout.ACCESS;r=layout.BUILDING['diameter']/2
    root=b.assembly('building.equipment_access','Access',(0,0,layout.FLOOR_Z),p['angle'])
    width=p['width'];height=p['height'];centre=r-layout.BUILDING['wall_thickness']/2
    # A true wall opening, continuing through the pilaster at this location.
    cut=b.box('opening_tool',root,(3.5,width,height+.02),(centre,0,height/2-.01),None)
    for obj in list(bpy.data.objects):
        if obj.name=='building.shell.retained_wall' or obj.name.startswith('building.shell.pilaster'):
            mod=obj.modifiers.new('Equipment doorway','BOOLEAN');mod.operation='DIFFERENCE'
            mod.object=cut;mod.solver='EXACT'
    cut.hide_render=True;cut.hide_set(True)
    for side in (-1,1):
        b.box(f'jamb{side}',root,(.9,.22,height),(centre,side*(width/2+.11),height/2),'rail',.03)
        # Floor markings delimit a level, unobstructed transfer lane.
        b.box(f'lane_edge{side}',root,(p['outer_radius']-p['inner_radius'],.07,.006),
              ((p['inner_radius']+p['outer_radius'])/2,side*(width/2+.08),.004),'crane')
    b.box('lintel',root,(.9,width+.44,.25),(centre,0,height+.125),'rail',.03)
    b.box('raised_door_housing',root,(.95,width+.6,.85),(r+.15,0,height+.7),'equipment',.05)
    root['door_state']='Open; overhead door envelope, construction provisional'
    root['clear_width_m']=width;root['clear_height_m']=height
    # Extension of the floor through the interrupted ring, no curb at the crossing.
    start=r-.8
    b.box('level_apron',root,(p['outer_radius']-start,p['ring_gap_width'],.3),
          ((p['outer_radius']+start)/2,0,-.15),'floor')
    return dict(p,scope='Visual access envelope; no door containment rating or vehicle swept-path qualification')


def check_access(b,layout,services):
    p=layout.ACCESS;root=b.assemblies['building.equipment_access']
    inverse=root.matrix_world.inverted();half=p['width']/2
    bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    # Actual evaluated wall/pilaster aperture, sampled across the usable opening.
    for y in (-half+.05,0,half-.05):
        for z in (.05,p['height']/2,p['height']-.05):
            origin=root.matrix_world @ Vector((layout.BUILDING['diameter']/2-2,y,z))
            direction=root.matrix_world.to_3x3() @ Vector((1,0,0))
            hit=bpy.context.scene.ray_cast(deps,origin,direction,distance=3.5)
            assert not hit[0], ('Blocked doorway',y,z,hit[4].name if hit[0] else '')
    # Conservative boxes for equipment intersecting the full-height straight lane.
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or not obj.name.startswith('equipment.'):continue
        points=[inverse @ obj.matrix_world @ Vector(q) for q in obj.bound_box]
        lo=[min(q[i] for q in points) for i in range(3)]
        hi=[max(q[i] for q in points) for i in range(3)]
        overlap=(hi[0]>p['inner_radius'] and lo[0]<p['outer_radius'] and
                 hi[1]>-half and lo[1]<half and hi[2]>.01 and lo[2]<p['height'])
        assert not overlap, ('Equipment in access lane',obj.name,lo,hi)
    # Floor-level service pipes must also stay outside this transfer envelope.
    for obj in bpy.context.scene.objects:
        if obj.type!='CURVE' or not obj.name.startswith('connections.'):continue
        radius=obj.data.bevel_depth
        for spline in obj.data.splines:
            for point in spline.points:
                q=inverse @ obj.matrix_world @ Vector(point.co[:3])
                if p['inner_radius']-radius<q.x<p['outer_radius']+radius and abs(q.y)<half+radius:
                    assert q.z-radius>=p['height'] or q.z+radius<=0, ('Pipe in access lane',obj.name,list(q))
    # All fresh plenum solids (including floor and end walls) leave the opening clear.
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH' and obj.name.startswith('connections.air.fresh_plenum.'):
            for v in obj.data.vertices:
                q=inverse @ obj.matrix_world @ v.co
                assert not (layout.BUILDING['diameter']/2-2<q.x<layout.AIR['concrete_outer_radius']+1 and abs(q.y)<p['ring_gap_width']/2-1e-5)
    apron=bpy.data.objects[root.name+'.level_apron']
    assert abs(max((apron.matrix_world @ Vector(q)).z for q in apron.bound_box)-layout.FLOOR_Z)<1e-5
    services['access']['coolant_storage_relocated']=False
    return ['Equipment doorway cuts wall and pilaster; clear aperture and level apron verified',
            'Access lane clears equipment (including coolant/sector storage), service pipes and interrupted fresh plenum']
