"""Cutaway of the same paired fuel jacket used throughout the site model."""
from pathlib import Path
import sys,math,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.site_salt_distribution import fuel_bundle
from build_wistr import camera
from render_pms import text_on_camera
import wistr_site as site
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
b=SceneBuilder();root=b.assembly('bundle_detail','Fuel bundle section')
for key,color,metal in [('fuel_supply','#BE9140',.3),('fuel_return','#BB556C',.3),('rail','#526675',.6),('fuel_bundle_cladding','#BCC5CC',.65),('fuel_bundle_insulation','#E3D7B7',0),('fuel_trace','#A25835',.5),('backdrop','#EDF0F2',0)]:
    b.material(key,color,metallic=metal,roughness=.4)
rr=fuel_bundle(b,root,'sample',[(-1.1,0,0),(1.1,0,0)],site)
cutter=b.box('section_tool',root,(1.5,.6,.5),(.45,0,.251),None);cutter.hide_render=True
for ob in list(root.children):
    if ob is cutter or ob.type!='MESH':continue
    if any(k in ob.name for k in ('.insulation','.cladding','.jacket_band')):
        m=ob.modifiers.new('Inspection cutaway','BOOLEAN');m.operation='DIFFERENCE';m.object=cutter;m.solver='EXACT'
b.box('backdrop',root,(200,200,.04),(0,0,-.16),'backdrop')
cam=camera(b,'Common fuel insulation cutaway',(2,-3.5,2.0),(0,0,0),3.5)
for name,pos,power,size in [('Key',(-1,-2,4),550,4),('Fill',(2,3,3),400,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size
    ob=bpy.data.objects.new(name,data);b.collection('Lights').objects.link(ob);ob.location=pos
    ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1600;s.render.resolution_y=950;s.render.resolution_percentage=100
col=b.collection('Detail annotations')
text_on_camera('title','FUEL SUPPLY + RETURN | Common insulated jacket',-1.55,.88,.068,cam,col)
text_on_camera('subtitle','Same bundle used from refiner to distributor and distributor to each tank',-1.55,.76,.041,cam,col,'#526575')
text_on_camera('note1','2 x 50 mm OD tubes / 80 mm centre spacing / electrical tracing on both tubes',-1.55,-.69,.039,cam,col,'#526575')
text_on_camera('note2','50 mm minimum insulation + 1 mm cladding / 236 mm overall diameter',-1.55,-.79,.039,cam,col,'#526575')
text_on_camera('note3','Cutaway for inspection only. Provisional insulation allowance; heater duty not sized.',-1.55,-.90,.034,cam,col,'#526575')
s.render.image_settings.file_format='PNG';s.render.filepath=str(ROOT/'outputs/site-45-bends/site-fuel-bundle-detail.png')
bpy.ops.render.render(write_still=True)
print('FUEL_BUNDLE_DETAIL_OK',flush=True)
