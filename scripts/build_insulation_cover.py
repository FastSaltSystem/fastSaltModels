"""Standalone cover concept: six cassettes, existing common head, sliding-hook sections."""
import sys,json,math,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'models'),str(ROOT/'src'),str(ROOT/'scripts')]
import wistr_insulation_cover as cfg
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.reactor_insulation_cover import build,detail,checks,set_pose,support_detail
from render_pms import text_on_camera

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
b=SceneBuilder();sectors,head=build(b,cfg)
head.driver_remove('location',2)
details=detail(b,cfg)
support_detail(b,cfg)
report=checks(b,sectors,head,cfg)
out=ROOT/'outputs/reactor-insulation-cover';out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.render.engine='CYCLES'
scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Cover studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.85,.9,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
scene.view_settings.view_transform='AgX'
for name,pos,energy,size in [('Key',(-5,-8,12),2200,8),('Fill',(8,2,9),1800,8),('Rim',(-6,8,5),1600,6)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
 obj=bpy.data.objects.new(name,data);b.collection('Presentation').objects.link(obj);obj.location=pos
 obj.rotation_euler=(Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
# Bright close lighting for the small true-scale detail section.
ld=bpy.data.lights.new('Detail light','AREA');ld.energy=45;ld.size=2
lo=bpy.data.objects.new('Detail light',ld);b.collection('Presentation').objects.link(lo);lo.location=(0,-2,2)
lo.rotation_euler=(Vector((.35,0,.4))-lo.location).to_track_quat('-Z','Y').to_euler()

cameras={}
def camera(name,pos,target,scale,title,subtitle,foot):
 data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);b.collection('Presentation').objects.link(obj)
 obj.location=pos;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;data.clip_end=200
 col=b.collection('Labels.'+name);h=scale*scene.render.resolution_y/scene.render.resolution_x
 text_on_camera(name+'.title',title,-scale*.46,h*.43,scale*.025,obj,col)
 text_on_camera(name+'.subtitle',subtitle,-scale*.46,h*.385,scale*.014,obj,col)
 text_on_camera(name+'.foot',foot,-scale*.46,-h*.45,scale*.013,obj,col)
 cameras[name]=obj
 return obj
camera('overview',(-11,-15,12),(0,0,.4),12.8,'WISTR | Removable insulation cover','Six stainless cassettes / seams over spider-leg centrelines / 500 mm stone-wool allowance','Concept study: pressure caps remain separate below. Seating and service penetrations require integration.')
camera('raised',(11,-15,13),(0,0,.65),13.5,'WISTR | One cassette lifted','Existing two-bar lifting head / four captive sliding stems / 40 mm take-up','One cassette lifts vertically. The other five remain seated; no overlapping metal seam traps its edges.')
camera('cutaway',(7,-9,7),(2.25,1.3,.30),6.5,'WISTR | Cassette construction','Skins and wool hidden to expose the carrying frame and first support grid','Brown: steel carrying frame. Blue: skin supports and long-path ties. Mesh representation is schematic.')
cam=camera('mechanism',(.35,-5,.45),(.35,0,.45),1.9,'WISTR | Straight sliding pickup','Same parts, two positions. Frame and guide shown in section.','Position indication only; no load rating or automatic-return qualification.')
col=b.collection('Labels.mechanism')
for name,text,x,y in [('rest','RESTING',-.53,.47),('carry','LOAD TAKEN UP',.17,.47),('gap','40 mm thermal gap',-.56,-.45),('seat','Shoulder bears on frame',.15,-.45)]:
 text_on_camera('mechanism.'+name,text,x,y,.030,cam,col)
text_on_camera('mechanism.notes','Square stem keeps hook aligned | Gold band rises with stem',-.87,-.56,.023,cam,col)

# A simple repeatable handling sequence; only one selected sector moves.
scene.frame_start=1;scene.frame_end=121;scene.render.fps=24
for f,stroke,lift in [(1,0,0),(21,1,0),(61,1,1.5),(101,1,0),(121,0,0)]:
 set_pose(sectors,head,cfg,stroke,lift)
 sectors[0]['root'].keyframe_insert(data_path='location',index=2,frame=f)
 for slider in sectors[0]['sliders']:slider.keyframe_insert(data_path='location',index=2,frame=f)
 head.keyframe_insert(data_path='location',index=2,frame=f)
for f,label in [(1,'REST - shoulders clear'),(21,'TAKE UP - shoulders seated'),(61,'CASSETTE RAISED'),(101,'SET DOWN'),(121,'RESTORED THERMAL GAP')]:scene.timeline_markers.new(label,frame=f)
# Linear travel avoids interpolation overshoot at stops.
for action in bpy.data.actions:
 for layer in action.layers:
  for strip in layer.strips:
   for slot in action.slots:
    bag=strip.channelbag(slot)
    if bag:
     for fc in bag.fcurves:
      for key in fc.keyframe_points:key.interpolation='LINEAR'

camera('support',(2,-5,1.2),(.04,0,.15),1.40,'WISTR | Zirconia seating break','White: fixed ceramic / brown: removable post and upper frame','50 mm diameter x 75 mm tall. No through-bolt. Provisional, unrated geometry.')

for view in ['overview','raised','cutaway','mechanism','support']:
 for collection in b.collections.values():
  collection.hide_render=False;collection.hide_viewport=False
  if collection.name.startswith('Labels.'):collection.hide_render=collection.name!='Labels.'+view
 b.collection('Catch sections').hide_render=view!='mechanism'
 b.collection('Support section').hide_render=view!='support'
 b.collection('Remote lifting tools').hide_render=view not in ('raised',)
 for obj in bpy.data.objects:
  obj.hide_render=False
 if view=='support':
  for name,col in b.collections.items():
   if not(name in ('Support section','Presentation') or name=='Labels.support'):col.hide_render=True
 elif view=='mechanism':
  for name,col in b.collections.items():
   if not(name in ('Catch sections','Presentation') or name=='Labels.mechanism'):col.hide_render=True
 elif view=='cutaway':
  for obj in bpy.data.objects:
   if obj.name.startswith('cover.sector_') and not obj.name.startswith('cover.sector_1.') and obj.name!='cover.sector_1':obj.hide_render=True
   if obj.name.startswith(('cover.sector_1.shell','reference.')):obj.hide_render=True
   if obj.name.startswith('cover.sector_1.insulation.'):obj.hide_render=True
   if obj.name.startswith('cover.sector_1.grids.grid') and not obj.name.startswith('cover.sector_1.grids.grid0'):obj.hide_render=True
 scene.frame_set(61 if view=='raised' else 1)
 scene.camera=cameras[view];scene.render.filepath=str(out/f'cover-{view}.png')
 bpy.ops.render.render(write_still=True)
# Open the editable scene in the raised view, with detail exemplars hidden.
for col in b.collections.values():col.hide_render=False;col.hide_viewport=False
for obj in bpy.data.objects:obj.hide_render=False
for name,col in b.collections.items():
 if name.startswith('Labels.') or name in ('Catch sections','Support section'):col.hide_render=True;col.hide_viewport=True
scene.camera=cameras['raised'];scene.frame_set(61)
scene['study_scope']='Separate removable thermal cover. Pressure boundary unchanged; complete vessel cooling and service integration not designed.'
scene['operation']='Timeline 1 resting, 21 take-up, 61 raised, 101 set-down, 121 restored gap.'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(out/'wistr-insulation-cover.blend'))
report['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'models/wistr_insulation_cover.py',ROOT/'models/wistr_reactor.py',ROOT/'src/textual_graphics/reactor_insulation_cover.py',Path(__file__)]}
report['timeline_frames']={'resting':1,'take_up':21,'raised':61,'set_down':101,'released':121}
(out/'cover-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('COVER CHECKS PASSED',len(report['passed_checks']))
