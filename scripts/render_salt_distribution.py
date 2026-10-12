"""Readable floor-route inspection: overhead objects hidden, equipment outlined."""
from pathlib import Path
import sys,json,math,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
# The optional input supports checking a scratch scene before the full site build.
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.static_scene import SceneBuilder
from build_wistr import camera
from render_pms import text_on_camera
import wistr_site as site
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=Path(args[0]) if args else ROOT/'outputs/site-45-bends/fast-salt-site.blend'
target=Path(args[1]) if len(args)>1 else ROOT/'outputs/site-45-bends/site-salt-distribution-draft.png'
bpy.ops.wm.open_mainfile(filepath=str(source))
b=SceneBuilder();b.materials={m.name:m for m in bpy.data.materials};b.collections={c.name:c for c in bpy.data.collections}
for ob in list(bpy.data.objects):
    if ob.name.startswith('salt_plan.') or ob.name=='Salt storage floor routing':bpy.data.objects.remove(ob,do_unlink=True)
root=b.assembly('salt_plan.context','Salt routing inspection context')
b.material('plan_floor','#EBEEE9',roughness=.9)
b.material('plan_outline','#83929A',roughness=.8)
b.material('plan_tank','#C9D2CE',roughness=.9)
b.box('floor',root,(80,70,.08),(0,0,site.PAD_Z-.08),'plan_floor')
for r in (21.,):
    b.tube('building_outline_'+str(r),root,[(r*math.cos(math.tau*i/200),r*math.sin(math.tau*i/200),site.PAD_Z-.025) for i in range(201)],.035,'plan_outline')
def text(name,body,loc,size=.55):
    data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size;data.align_x='CENTER';data.align_y='CENTER'
    ob=bpy.data.objects.new(name,data);b.finish(ob,name,root,'dark',loc)
    return ob

def footprint(name,ob,body):
    world=[ob.matrix_world@Vector(q) for q in ob.bound_box]
    local=[Vector(q) for q in ob.bound_box];lo=[min(v[i] for v in local) for i in range(3)];hi=[max(v[i] for v in local) for i in range(3)]
    poly=[ob.matrix_world@Vector((x,y,0)) for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
    pts=[(q.x,q.y,site.PAD_Z+.015) for q in poly]
    b.mesh(name+'_patch',root,pts,[(0,1,2,3)],'plan_tank')
    b.tube(name+'_outline',root,pts+[pts[0]],.035,'plan_outline')
    centre=ob.matrix_world.translation
    text(name+'_label',body,(centre.x,centre.y,site.PAD_Z+.055),.5)
for i in range(1,7):footprint('tank'+str(i),bpy.data.objects[f'equipment.fuel_storage_{i}.closed_tank'],'F'+str(i))
for i in range(1,4):
    ob=bpy.data.objects.get(f'equipment.steam_generator_{i}.casing')
    if ob:footprint('sg'+str(i),ob,'SG '+str(i))
tx,ty=14.,-6.5
b.cylinder('coolant_tank_footprint',root,2.351,.025,(tx,ty,site.PAD_Z+.002),'plan_tank',vertices=96,bevel=0)
b.tube('coolant_outline',root,[(tx+2.351*math.cos(math.tau*i/96),ty+2.351*math.sin(math.tau*i/96),site.PAD_Z+.035) for i in range(97)],.035,'plan_outline')
text('coolant_label','COOLANT\nSTORAGE',(tx,ty-1.0,site.PAD_Z+.06),.48)
b.cylinder('reactor_footprint',root,4.3,.04,(0,0,site.PAD_Z+.01),'plan_tank',vertices=96,bevel=0)
text('reactor_label','REACTOR\nVESSEL / WELL',(0,0,site.PAD_Z+.06),.62)
text('valve_box_label','FUEL\nVALVE BOX',(0,9.1,site.PAD_Z+1.29),.28)
text('duct_label','SHARED DUCT',(4.8,22.0,site.PAD_Z+.04),.6)
text('fuel_bank_12','FUEL TANKS 1 / 2',(-7,15,site.PAD_Z+.06),.52)
text('fuel_bank_34','FUEL TANKS 3 / 4',(-7,-15,site.PAD_Z+.06),.52)
text('fuel_bank_56','FUEL TANKS 5 / 6',(15.8,3.,site.PAD_Z+.06),.52)
cam=camera(b,'Salt storage floor routing',(0,2,60),(0,2,0),58);cam.rotation_euler=(0,0,0)
col=b.collection('Salt routing inspection annotations')
# Remove old annotations if rerunning against the same saved model.
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
text_on_camera('salt_plan.title','INSULATED SALT LINES | Floor routing',-26,24,.92,cam,col)
text_on_camera('salt_plan.legend','Silver: paired fuel tubes, common insulation + heat tracing   /   Teal: coolant',-26,22.4,.53,cam,col,'#526575')
text_on_camera('salt_plan.footer','Six fuel tube pairs via valve box | Fuel centreline 0.18 m / coolant floor run 0.40 m above floor',-26,-22.5,.48,cam,col,'#526575')
text_on_camera('salt_plan.note','Equipment shown as footprints; overhead equipment hidden. Provisional layout and insulation allowances.',-26,-23.4,.44,cam,col,'#526575')
state=[(o,o.hide_render) for o in bpy.data.objects]
cols=[(c,c.hide_render) for c in bpy.data.collections]
oldcam=bpy.context.scene.camera
for c,_ in cols:c.hide_render=False
for ob,_ in state:
    keep=ob.name.startswith(('salt_plan.','site.salt_distribution.')) or ob.type in ('LIGHT','CAMERA')
    ob.hide_render=not keep or bool(ob.get('utility_opening_tool'))
s=bpy.context.scene;s.camera=cam;s.render.resolution_x=1800;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.cycles.samples=24
# Flat, exact material colours make the small tube pairs readable. Restore
# every material link afterwards so this inspection cannot change model shading.
material_state=[]
visible_materials={m for o in bpy.data.objects if not o.hide_render and o.type in ('MESH','CURVE','FONT') for m in o.data.materials if m}
for mat in visible_materials:
    output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
    previous=[link.from_socket for link in output.inputs['Surface'].links]
    emission=mat.node_tree.nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=mat.diffuse_color
    mat.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    material_state.append((mat,output,previous,emission))
view_state=(s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure)
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.cycles.samples=8
# Render only explicitly selected objects in a temporary scene. This avoids
# inherited collection instances exposing unrelated maintenance components.
preview=bpy.data.scenes.new('Salt routing isolated preview')
for ob in bpy.data.objects:
    if not ob.hide_render and ob.type in ('MESH','CURVE','FONT','LIGHT','CAMERA'):
        preview.collection.objects.link(ob)
preview.camera=cam;preview.render.engine='CYCLES';preview.cycles.samples=8;preview.cycles.use_denoising=True
preview.render.resolution_x=1800;preview.render.resolution_y=1600;preview.render.resolution_percentage=100
preview.view_settings.view_transform='Standard';preview.view_settings.look='None';preview.view_settings.exposure=0
preview.render.image_settings.file_format='PNG';preview.render.filepath=str(target.resolve())
bpy.ops.render.render(scene=preview.name,write_still=True)
bpy.data.scenes.remove(preview)
for mat,output,previous,emission in material_state:
    mat.node_tree.nodes.remove(emission)
    for socket in previous:mat.node_tree.links.new(socket,output.inputs['Surface'])
s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure=view_state
s.cycles.samples=16
for ob,value in state:ob.hide_render=value
for c,value in cols:c.hide_render=value
root.users_collection[0].hide_render=root.users_collection[0].hide_viewport=True
col.hide_render=col.hide_viewport=True
s.camera=oldcam;s.render.resolution_x=1800;s.render.resolution_y=1100
# Keep the diagram camera and context available but hidden in normal model views.
if not args:bpy.ops.wm.save_as_mainfile(filepath=str(source))
print('SALT_ROUTING_PREVIEW_OK',flush=True)
