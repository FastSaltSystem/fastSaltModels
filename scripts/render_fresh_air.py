"""Inspection plan of the current internal cold-air duct and ten branches."""
from pathlib import Path
import sys,math,json,bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.static_scene import SceneBuilder
from build_wistr import camera
from render_pms import text_on_camera
import wistr_site as site
out=ROOT/'outputs/site-45-bends'
bpy.ops.wm.open_mainfile(filepath=str(out/'fast-salt-site.blend'))
report=json.loads((out/'site-report.json').read_text())['fresh_air']
# Static assemblies can be transformed without evaluating the entire plant.
# An isolated scene also keeps unrelated source geometry out of this inspection.
world_cache={}
def world(ob):
 if ob.name not in world_cache:
  world_cache[ob.name]=(world(ob.parent) @ ob.matrix_parent_inverse @ ob.matrix_basis if ob.parent else ob.matrix_basis.copy())
 return world_cache[ob.name]
preview=bpy.data.scenes.new('Fresh-air plan');bpy.context.window.scene=preview
b=SceneBuilder();b.materials={m.name:m for m in bpy.data.materials}
for key,color in [('fresh_plan_floor','#F1F3F0'),('fresh_plan_tank','#CBD5D5'),('fresh_plan_outline','#82949A'),('fresh_plan_column','#A99E8E')]:b.material(key,color,roughness=.8)
root=b.assembly('fresh_plan','Fresh-air inspection')
b.box('floor',root,(80,80,.08),(0,0,site.PAD_Z-.1),'fresh_plan_floor')
def text(name,body,xy,size=.5):
 data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size;data.align_x='CENTER';data.align_y='CENTER'
 ob=bpy.data.objects.new(name,data);b.finish(ob,name,root,'dark',(*xy,site.PAD_Z+.10));return ob
for radius in (20.35,21.):
 for index,(start,end) in enumerate(((0,11.5),(24.5,360))):
  count=math.ceil(end-start)
  b.tube('wall'+str(radius)+'_'+str(index),root,[(radius*math.cos(math.radians(start+(end-start)*i/count)),radius*math.sin(math.radians(start+(end-start)*i/count)),site.PAD_Z+.04) for i in range(count+1)],.028,'fresh_plan_outline')
for i in range(1,4):
 ob=bpy.data.objects[f'equipment.steam_generator_{i}.casing'];pts=[world(ob)@Vector(q) for q in ob.bound_box]
 # World convex footprint from the known local box, keeping its rotation.
 lo=[min(q[j] for q in ob.bound_box) for j in range(3)];hi=[max(q[j] for q in ob.bound_box) for j in range(3)]
 xy=[world(ob)@Vector((x,y,0)) for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
 poly=[(q.x,q.y,site.PAD_Z+.03) for q in xy];b.mesh('sg'+str(i),root,poly,[(0,1,2,3)],'fresh_plan_tank');b.tube('sg_edge'+str(i),root,poly+[poly[0]],.025,'fresh_plan_outline')
 c=sum(xy,Vector())/4;text('sg_label'+str(i),'SG '+str(i),(c.x,c.y))
for i in range(1,7):
 ob=bpy.data.objects[f'equipment.fuel_storage_{i}.closed_tank'];lo=[min(q[j] for q in ob.bound_box) for j in range(3)];hi=[max(q[j] for q in ob.bound_box) for j in range(3)]
 xy=[world(ob)@Vector((x,y,0)) for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
 poly=[(q.x,q.y,site.PAD_Z+.03) for q in xy];b.mesh('tank'+str(i),root,poly,[(0,1,2,3)],'fresh_plan_tank');b.tube('tank_edge'+str(i),root,poly+[poly[0]],.025,'fresh_plan_outline')
 c=sum(xy,Vector())/4;text('tank_label'+str(i),'F'+str(i),(c.x,c.y),.40)
for name,xy,r,label in [('reactor',(0,0),4.754,'REACTOR / WELL'),('coolant',(14,-6.5),2.351,'COOLANT\nSTORAGE')]:
 b.cylinder(name,root,r,.03,(*xy,site.PAD_Z+.03),'fresh_plan_tank',vertices=96,bevel=0);text(name+'_label',label,xy,.45)
for q in report['column_recesses']:
 if report['door_gap_degrees'][0]<q['angle']<report['door_gap_degrees'][1]:continue
 ob=bpy.data.objects[q['column']];p=world(ob).translation
 b.box('column_'+q['column'],root,(.45,.45,2.8),(p.x,p.y,site.PAD_Z+1.4),'fresh_plan_column')
text('door','DOOR / CART\nCLEAR PASSAGE',(24,8),.44)
for i,q in enumerate(report['intakes'],1):
 p=Vector(q['points'][-1]);p*=1.12
 text('intake'+str(i),'AIR INLET '+str(i),(p.x,p.y),.44)
# Arrows on open duct floor indicate that air enters the equipment branches.
for q in report['branches']:
 a=Vector(q['points'][-1]);c=Vector(q['points'][-2]);direction=(c-a).normalized()
 if direction.length==0:continue
 side=Vector((-direction.y,direction.x,0));tip=a+direction*.60;base=a-direction*.05
 zz=max(a.z+q['diameter']/2+.06,site.PAD_Z+.20)
 pts=[base+side*.16,tip,base-side*.16]
 b.tube('flow_'+q['component'],root,[(p.x,p.y,zz) for p in pts],.025,'dark')
cam=camera(b,'Fresh air inside building',(0,-2,70),(0,-2,0),65);cam.rotation_euler=(0,0,0)
col=b.collection('Fresh-air annotations')
text_on_camera('fresh_title','FRESH AIR | Inside the reactor building',-29,29.5,.85,cam,col)
text_on_camera('fresh_note','Ten internal equipment connections / three outdoor inlets / covers hidden for inspection',-29,27.9,.42,cam,col,'#526575')
text_on_camera('fresh_footer','Generator inlets: 75% of exhaust area / complete column layout / 5.5 m doorway gap',-29,-29,.42,cam,col,'#526575')
text_on_camera('fresh_scope','Draft routing only. Effective airflow, supports and complete access remain to design.',-29,-30,.38,cam,col,'#526575')
keep={q['name'] for q in report['branches']}|{q['name'] for q in report['intakes']}|{q['name'] for q in report['valves']}|{'reactor.cold_air_manifold.plenum','reactor.cold_air_manifold.sealed_sleeve','reactor.air_ducts.cold_stub'}
preview.camera=cam
selected=[]
for o in list(bpy.data.objects):
 visible=o.name in keep or o.name.startswith(('fresh_plan.','site.fresh_air.','site.fresh_air_intake_')) or o.name in col.objects or o is cam
 if not visible or o.get('fresh_header_part')=='roof' or o.get('fresh_air_opening_tool'):continue
 if o.name not in preview.objects:selected.append(o)
tools={m.object for o in selected for m in o.modifiers if m.type=='BOOLEAN' and m.object and not m.name.startswith('Study cutaway')}
copies={}
for o in selected+list(tools):
 copy=o.copy();copy.parent=None;copy.matrix_world=world(o);preview.collection.objects.link(copy)
 copy.hide_viewport=False;copy.hide_render=o in tools;copies[o]=copy
for o,copy in copies.items():
 for m in list(copy.modifiers):
  if m.name.startswith('Study cutaway'):
   copy.modifiers.remove(m);continue
  if m.type=='BOOLEAN' and m.object in copies:m.object=copies[m.object]
for o in list(preview.objects):
 if o.type not in ('MESH','CURVE','FONT'):continue
 for mat in o.data.materials:
  if not mat or mat.get('fresh_preview_emission'):continue
  output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');em=mat.node_tree.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=mat.diffuse_color;mat.node_tree.links.new(em.outputs[0],output.inputs['Surface']);mat['fresh_preview_emission']=True
preview.render.engine='CYCLES';preview.cycles.samples=8;preview.cycles.use_denoising=True
preview.render.resolution_x=1700;preview.render.resolution_y=1700;preview.render.resolution_percentage=100
preview.view_settings.view_transform='Standard';preview.view_settings.look='None';preview.render.image_settings.file_format='PNG'
preview.render.filepath=str(out/'site-fresh-air-draft.png');bpy.ops.render.render(scene=preview.name,write_still=True)
print('FRESH_AIR_PREVIEW_OK',flush=True)
