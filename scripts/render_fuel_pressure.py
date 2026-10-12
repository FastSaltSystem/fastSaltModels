"""Inspection images for fuel pressure servers and their gas connections."""
from pathlib import Path
import sys,math,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.static_scene import SceneBuilder
from build_wistr import camera
from render_pms import text_on_camera
import wistr_site as site
out=ROOT/'outputs/site-45-bends'
bpy.ops.wm.open_mainfile(filepath=str(out/'fast-salt-site.blend'))
b=SceneBuilder();b.materials={m.name:m for m in bpy.data.materials};b.collections={c.name:c for c in bpy.data.collections}
b.material('gas_plan_floor','#F0F1ED',roughness=.9)
b.material('gas_plan_outline','#7B8990',roughness=.9)
b.material('gas_plan_fill','#CCD5D1',roughness=.9)
source_scene=bpy.context.scene

def render(cam,objects,path,flat=False,square=False):
    preview=bpy.data.scenes.new('Fuel pressure inspection')
    state=[]
    for ob in set(objects+[cam]):
        state.append((ob,ob.hide_render));ob.hide_render=False;preview.collection.objects.link(ob)
    preview.camera=cam;preview.world=source_scene.world
    preview.render.engine='CYCLES';preview.cycles.samples=8 if flat else 24;preview.cycles.use_denoising=True
    preview.render.resolution_x=1800;preview.render.resolution_y=1800 if square else 1200;preview.render.resolution_percentage=100
    preview.render.image_settings.file_format='PNG';preview.render.filepath=str(path)
    materials=[]
    if flat:
        preview.view_settings.view_transform='Standard';preview.view_settings.look='None';preview.view_settings.exposure=0
        for mat in {m for ob in objects if ob.type in ('MESH','CURVE','FONT') for m in ob.data.materials if m}:
            output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');old=[link.from_socket for link in output.inputs['Surface'].links]
            em=mat.node_tree.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=mat.diffuse_color
            mat.node_tree.links.new(em.outputs[0],output.inputs['Surface']);materials.append((mat,output,old,em))
    else:
        preview.view_settings.view_transform='AgX';preview.view_settings.exposure=.1
    bpy.ops.render.render(scene=preview.name,write_still=True)
    for mat,output,old,em in materials:
        mat.node_tree.nodes.remove(em)
        for socket in old:mat.node_tree.links.new(socket,output.inputs['Surface'])
    for ob,hidden in state:ob.hide_render=hidden
    bpy.data.scenes.remove(preview)

def label(root,name,body,pos,size):
    data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size;data.align_x='CENTER';data.align_y='CENTER'
    return b.finish(bpy.data.objects.new(name,data),name,root,'dark',pos)

# One representative pair, with a clear view of the tank headspace connections.
root=b.assembly('gas_detail.context','Gas detail context')
b.box('floor',root,(80,80,.08),(0,0,site.PAD_Z-.05),'gas_plan_floor')
a=math.radians(120)
def world(x,y,z):return (x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z)
cam=camera(b,'Fuel pressure server detail',world(3,8,site.PAD_Z+10.2),world(11.5,.6,site.PAD_Z+3.1),17)
col=b.collection('Gas detail annotations')
text_on_camera('gas_detail.title','FUEL PRESSURE SERVER | One per tank pair',-7.8,5.1,.42,cam,col)
text_on_camera('gas_detail.legend','Blue: supply gas / Purple: off-gas | Two 25 mm tubes to each tank',-7.8,4.45,.24,cam,col,'#526575')
text_on_camera('gas_detail.footer','Box above cylindrical buffer tank; shared headers and other piping hidden for clarity. Provisional equipment envelope.',-7.8,-4.95,.20,cam,col,'#526575')
objects=[o for o in bpy.data.objects if o.name.startswith(('equipment.fuel_pressure_server_1.','equipment.fuel_storage_1.','equipment.fuel_storage_2.','site.fuel_pressure.server_1_','gas_detail.')) or o.type=='LIGHT']
render(cam,objects,out/'site-fuel-pressure-detail.png')
if '--detail-only' in sys.argv:
    print('FUEL_PRESSURE_DETAIL_OK',flush=True)
    raise SystemExit(0)
# Plan of the complete gas service network and the moved nitrogen skid.
root=b.assembly('gas_plan.context','Gas plan context')
b.box('floor',root,(100,100,.08),(0,10,site.PAD_Z-.08),'gas_plan_floor')
for r in (21.,):b.tube('building_ring_'+str(r),root,[(r*math.cos(math.tau*i/160),r*math.sin(math.tau*i/160),site.PAD_Z+.005) for i in range(161)],.035,'gas_plan_outline')
def rectangle(name,pts):
    b.mesh(name+'_patch',root,pts,[(0,1,2,3)],'gas_plan_fill')
    b.tube(name+'_outline',root,pts+[pts[0]],.035,'gas_plan_outline')
for i in range(1,7):
    ob=bpy.data.objects[f'equipment.fuel_storage_{i}.closed_tank'];coords=[Vector(q) for q in ob.bound_box]
    lo=[min(p[j] for p in coords) for j in range(3)];hi=[max(p[j] for p in coords) for j in range(3)]
    points=[ob.matrix_world@Vector((x,y,0)) for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
    rectangle('tank_'+str(i),[(p.x,p.y,site.PAD_Z+.02) for p in points])
    c=ob.matrix_world.translation;label(root,'tank_label_'+str(i),'F'+str(i),(c.x,c.y,site.PAD_Z+.06),.6)
for name,params in [('offgas',site.OFF_GAS)]:
    x,y=params['centre'];dx,dy,_=params['size']
    rectangle(name,[(x-dx/2,y-dy/2,site.PAD_Z+.02),(x+dx/2,y-dy/2,site.PAD_Z+.02),(x+dx/2,y+dy/2,site.PAD_Z+.02),(x-dx/2,y+dy/2,site.PAD_Z+.02)])
    label(root,name+'_label','OFF-GAS /\nGAS SUPPLY',(x,y+1,site.PAD_Z+.06),.65)
rectangle('shared_duct',[(2,19.5,site.PAD_Z+.02),(6,19.5,site.PAD_Z+.02),(6,26.2,site.PAD_Z+.02),(2,26.2,site.PAD_Z+.02)])
label(root,'duct_label','SHARED DUCT',(9,23,site.PAD_Z+.06),.55)
b.cylinder('reactor_footprint',root,4.3,.04,(0,0,site.PAD_Z+.01),'gas_plan_fill',vertices=96,bevel=0)
label(root,'reactor_label','REACTOR',(0,0,site.PAD_Z+.06),.8)
for i in range(1,4):
    ob=bpy.data.objects[f'equipment.fuel_pressure_server_{i}'];x,y,z=ob.location
    label(root,'server_label_'+str(i),'P'+str(i),(x-1.1,y,site.PAD_Z+.06),.65)
label(root,'nitrogen_label','NITROGEN TANK\n+ VAPORIZER',(-14.2,34.,site.PAD_Z+.06),.57)
cam=camera(b,'Fuel gas distribution plan',(0,10,85),(0,10,0),70);cam.rotation_euler=(0,0,0)
col=b.collection('Gas plan annotations')
text_on_camera('gas_plan.title','FUEL GAS SERVICES | Three pressure servers',-32,32,.95,cam,col)
text_on_camera('gas_plan.legend','Blue: gas supply / Purple: off-gas / P1-P3: pressure servers',-32,30.3,.62,cam,col,'#526575')
text_on_camera('gas_plan.footer','Each server supplies one pair of maintenance tanks; two 25 mm tubes per tank.',-32,-31,.55,cam,col,'#526575')
text_on_camera('gas_plan.note','Gas connections only; other piping hidden. Provisional layout, insulation and equipment envelopes.',-32,-32.1,.49,cam,col,'#526575')
objects=[o for o in bpy.data.objects if (o.name.startswith(('gas_plan.','site.fuel_pressure.','equipment.fuel_pressure_server_','equipment.nitrogen_supply.','site.offgas_gas_supply.')) and o.type in ('MESH','CURVE','FONT') and not o.get('utility_opening_tool'))]
render(cam,objects,out/'site-gas-distribution-draft.png',flat=True,square=True)
print('FUEL_PRESSURE_VIEWS_OK',flush=True)
