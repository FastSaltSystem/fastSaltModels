"""Rebuild isolated, reproducible turbine views without saving the site file."""
from pathlib import Path
import sys,json,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.static_scene import SceneBuilder
from turbine_equipment import add_equipment
from turbine_pipe_geometry import add_piping
from build_wistr import camera
from render_pms import text_on_camera
import wistr_site as site
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
b=SceneBuilder()
for name,color in [('floor','#E3E6E7'),('dark','#253746'),('crane','#D3AC57')]:b.material(name,color)
report=add_equipment(b,ROOT,site);piping=add_piping(b,ROOT,site)
out=ROOT/'outputs/site-45-bends';out.mkdir(parents=True,exist_ok=True)
(out/'turbine-equipment-detail.json').write_text(json.dumps(report,indent=2)+'\n')
origin=Vector((-96,-20,site.PAD_Z))
def xyz(p):return origin+Vector(p)
root=b.assembly('turbine.inspection','Turbine inspection')
floor=b.box('floor',root,(68,52,.12),xyz((30,17,-.1)),'floor')
scene=bpy.context.scene
scene.world=bpy.data.worlds.new('Turbine inspection world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.84,.90,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for name,pos,power in [('Key',(10,-20,65),100000),('Fill',(75,25,45),75000),('Rim',(5,60,40),60000)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=35
 ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=xyz(pos)
 ob.rotation_euler=(xyz((30,20,5))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
views=[('site-turbine-machinery',(85,-65,68),(30,19,9),99,'TURBINE HALL | Machinery and main piping','Existing layout / motor-driven feed pumps / illustrative equipment exteriors','all'),
       ('turbine-trains-detail',(78,-28,47),(30,25,15.5),72,'TURBINE TRAINS | Casings, bearings and generators','550 MVA HP/IP train / 350 MVA LP train / pipework omitted for inspection','upper'),
       ('turbine-ground-equipment',(78,-50,62),(29,17,3),80,'GROUND EQUIPMENT | Pumps and heat exchangers','Three feed-pump sets / three condensate pumps / condensers, reheaters and feedwater heaters','ground')]
for name,loc,target,scale,title,subtitle,mode in views:
 floor.location.z=site.PAD_Z+(11.9 if mode=='upper' else -.1)
 for ob in bpy.data.objects:
  if ob.get('turbine_detail') or ob.get('turbine_detail_label'):
   upper=bool(ob.get('turbine_upper'));service=ob.get('service','')
   hidden=(mode=='ground' and upper) or (mode=='upper' and (not upper or service.startswith('DA'))) or service=='BFP electrical annex'
   ob.hide_render=ob.hide_viewport=hidden
  if ob.get('route_name'):ob.hide_render=ob.hide_viewport=mode!='all'
  if ob.name.startswith('turbine.equipment.service'):ob.hide_render=mode=='upper'
 cam=camera(b,name,xyz(loc),xyz(target),scale)
 col=b.collection('Labels '+name)
 text_on_camera(name+' title',title,-scale*.46,scale*.30,scale*.016,cam,col)
 text_on_camera(name+' subtitle',subtitle,-scale*.46,scale*.271,scale*.0095,cam,col,'#526575')
 text_on_camera(name+' footer','Concept geometry within reserved envelopes; vendor outlines, structures and remaining circuits are still to develop.',-scale*.46,-scale*.305,scale*.0088,cam,col,'#526575')
 scene.camera=cam;scene.render.filepath=str(out/(name+'.png'))
 bpy.ops.render.render(write_still=True);col.hide_render=True
print('TURBINE_DETAIL_OK '+json.dumps({'items':len(report['items']),'parts':sum(i['parts'] for i in report['items']),'ports':sum(len(i['ports']) for i in report['items'])}),flush=True)
