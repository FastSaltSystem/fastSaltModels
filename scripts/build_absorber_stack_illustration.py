"""Standalone unscaled presentation prop; no engineering inputs or internal circuit."""
from pathlib import Path
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/absorber-stack-illustration'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'NONE'
scene['purpose'] = 'Unscaled presentation illustration. Arbitrary proportions; no capacities or internal routing.'

def mat(name, color, metallic=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=.3
    return m
steel=mat('Frame graphite',(.12,.18,.23),.5)
upper=mat('Pressure tank blue',(.10,.36,.55),.35)
lower=mat('Surge tank teal',(.10,.49,.48),.35)
case=mat('Control enclosure',(.78,.82,.83),.4)
line=mat('Illustrative connection stubs',(.71,.75,.78),.6)
ink=mat('Label ink',(.035,.065,.10))
nodes=ink.node_tree.nodes;nodes.clear()
e=nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.018,.03,.045,1)
e.inputs['Strength'].default_value=1
output=nodes.new('ShaderNodeOutputMaterial');ink.node_tree.links.new(e.outputs[0],output.inputs['Surface'])
floor=mat('Studio ground',(.89,.91,.93))

def cube(name,loc,size,material,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
    o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Soft display edges','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def vessel(name,z,r,h,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=h,location=(0,0,z))
    o=bpy.context.object;o.name=name+'.body';o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    for sign in [-1,1]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=24,location=(0,0,z+sign*h/2))
        o=bpy.context.object;o.name=name+'.display_end';o.scale=(r,r,.20);o.data.materials.append(material)
        for p in o.data.polygons:p.use_smooth=True

def tube(name,points,r=.033):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=4
    s=c.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);o.data.materials.append(line)
    o['status']='Symbolic external connection, no process assignment or designed route'

cube('Display base',(0,0,.10),(1.9,1.65,.20),steel)
for x in [-.82,.82]:
    for y in [-.60,.60]:cube('Illustrative frame',(x,y,2.05),(.08,.08,3.9),steel,.015)
for z in [.42,2.14,3.65]:cube('Display shelf',(0,0,z),(1.75,1.4,.08),steel,.02)
vessel('Surge tank',1.22,.64,1.10,lower)
vessel('Pressure tank',2.88,.54,.92,upper)
cube('Control box',(0,0,4.02),(1.35,.95,.63),case)
cube('Display panel',(0,-.486,4.04),(.69,.026,.29),steel,.015)
# Only exterior stubs are shown. There is no internal flow diagram.
for name,z,r in [('Surge',1.22,.64),('Pressure',2.88,.54)]:
    for dy in [-.18,.18]:tube(name+' symbolic service stub',[(r-.08,dy,z),(1.35,dy,z)])

cube('Ground',(0,0,-.08),(200,200,.08),floor,0)
world=bpy.data.worlds.new('Studio') if not scene.world else scene.world;scene.world=world
world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.87,.93,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.55
for loc,power,size in [((2,-5,8),1400,5),((-4,-2,5),950,4),((3,4,7),1600,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
look=Vector((0,0,2.35));bpy.ops.object.camera_add(location=(6,-12,7));cam=bpy.context.object
cam.rotation_euler=(look-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.2;scene.camera=cam
q=cam.rotation_euler.to_quaternion();right=q@Vector((1,0,0));up=q@Vector((0,1,0));toward=q@Vector((0,0,1))
def label(text,x,y,size=.18):
    c=bpy.data.curves.new(text,'FONT');c.body=text;c.size=size;c.align_x='LEFT';c.extrude=0
    o=bpy.data.objects.new(text,c);scene.collection.objects.link(o);o.location=look+right*x+up*y+toward*4
    o.rotation_euler=cam.rotation_euler;o.data.materials.append(ink)
label('ABSORBER MODULE',-3.6,2.68,.29)
label('Stacked arrangement  /  unscaled illustration',-3.6,2.34,.16)
label('CONTROL BOX',-3.6,1.5,.18)
label('PRESSURE TANK',-3.6,.55,.18)
label('SURGE TANK',-3.6,-.60,.18)
label('Symbolic',1.75,.15,.17)
label('connection stubs',1.75,-.08,.17)
label('Arbitrary proportions. No vessel capacities or internal piping represented.',-3.6,-2.95,.14)
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1500;scene.render.resolution_y=1150;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'absorber-stack.png')
# Open in camera view with useful solid colors for orbiting.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.overlay.show_floor=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'absorber-stack.blend'))
bpy.ops.render.render(write_still=True)
