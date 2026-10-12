"""Isolated inspection of low generator cooling-air inlet and exhaust."""
from pathlib import Path
import sys,json,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.static_scene import SceneBuilder
from build_wistr import camera
from render_pms import text_on_camera
import wistr_site as site
out=ROOT/'outputs/site-45-bends'
bpy.ops.wm.open_mainfile(filepath=str(out/'fast-salt-site.blend'))
report=json.loads((out/'site-report.json').read_text())['fresh_air']
cache={}
def world(o):
 if o.name not in cache:cache[o.name]=world(o.parent)@o.matrix_parent_inverse@o.matrix_basis if o.parent else o.matrix_basis.copy()
 return cache[o.name]
scene=bpy.data.scenes.new('Generator cooling air');bpy.context.window.scene=scene
b=SceneBuilder();b.materials={m.name:m for m in bpy.data.materials}
root=b.assembly('air_detail','Air detail')
b.box('floor',root,(80,80,.10),(5,-10,site.PAD_Z-.10),'floor')
selected=[o for o in bpy.data.objects if (o.name.startswith(('equipment.steam_generator_3.','connections.air.generator_3.hot','site.fresh_air_intake_3.')) or o.name in ('connections.air.generator_3.fresh','connections.air.outside_air_intake_3')) and o.type in ('MESH','CURVE') and not o.get('utility_opening_tool')]
# Show just the southeast part of the floor header as a sectional context.
for o in bpy.data.objects:
 if not o.name.startswith('site.fresh_air.') or o.get('fresh_header_part')=='roof':continue
 if o.type=='MESH' and '.180' in o.name:selected.append(o)
tools={m.object for o in selected for m in o.modifiers if m.type=='BOOLEAN' and m.object}
copies={}
for o in selected+list(tools):
 c=o.copy();c.parent=None;c.matrix_world=world(o);scene.collection.objects.link(c)
 c.hide_viewport=False;c.hide_render=o in tools;copies[o]=c
for o,c in copies.items():
 for m in c.modifiers:
  if m.type=='BOOLEAN' and m.object in copies:m.object=copies[m.object]
for name,pos,energy in [('Key',(32,2,35),35000),('Fill',(-5,-22,30),20000)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=18
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((7,-12,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=camera(b,'Generator air connections',(34,2,19),(8,-12,-.4),38)
col=b.collection('Air detail labels')
text_on_camera('Air title','GENERATOR | Low cooling-air inlet',-17,12.3,.62,cam,col)
text_on_camera('Air subtitle','Side valve center 1.35 m above floor / existing top exhaust',-17,11.25,.38,cam,col,'#526575')
text_on_camera('Air dimensions',f"Inlet bore {report['inlet_bore_m']:.3f} m / exhaust bore {report['exhaust_bore_m']:.3f} m / area ratio 0.75",-17,-11.8,.36,cam,col,'#526575')
text_on_camera('Air scope','Air-routing inspection: nearby equipment and process piping omitted.',-17,-12.65,.34,cam,col,'#526575')
scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(out/'site-generator-air-detail.png');bpy.ops.render.render(write_still=True)
print('GENERATOR_AIR_PREVIEW_OK',flush=True)
