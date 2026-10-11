"""Parameter-driven sections showing the groove and upper ceramic break."""
import sys,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'models'),str(ROOT/'src'),str(ROOT/'scripts')]
import wistr_tgrid_cover as cfg
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.reactor_insulation_cover import materials
from render_pms import text_on_camera
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
b=SceneBuilder();materials(b);b.material('block','#DED0AC',roughness=.9);b.material('facing','#C1BDB3',roughness=.9);b.material('tie','#427C85',metallic=.6);b.material('crimp','#B78C32',metallic=.7)
g=cfg.GRID;c=cfg.COVER;cer=cfg.CERAMIC
def grid_section(parent,layer):
 dz=cfg.grid_offset(layer)
 bz=cfg.block_bottom(layer)
 for sign in (-1,1):
    height=cfg.LAYER_PITCH-(cfg.LAYER_CLEARANCE if layer<cfg.LAYERS-1 else 0)
    block=b.box(f'block_{layer}_{sign}',parent,(.158,.12,height),(sign*.081,0,bz+height/2),'block')
    if layer==0:
     cut=b.box('groove_cut',parent,(.054,.16,.005),(0,0,dz+.0405),None);b.cut(block,cut)
    hole=b.cylinder('rod_clearance',parent,cfg.COLLAR['block_clearance']/2,.12,(0,0,bz+.05),None,bevel=0);b.cut(block,hole)
    cut=b.box('section_cut',parent,(.6,.2,.12),(0,-.1,bz+.05),None);b.cut(block,cut)
 for name,size,z in [('flange',(.050,.12,.003),.0415),('web',(.002,.12,.045),.0655)]:
    ob=b.box(f'T_{name}_{layer}',parent,size,(0,0,dz+z),'stainless')
    cut=b.cylinder('slide_clearance',parent,cfg.COLLAR['web_clearance']/2,.15,(0,0,dz+.06),None,vertices=24,bevel=0);b.cut(ob,cut)
 saddle=b.box(f'saddle_{layer}',parent,(.012,.030,.008),(0,0,dz+.092),'stainless')
 cut=b.cylinder('saddle_bore',parent,cfg.COLLAR['saddle_bore']/2,.02,(0,0,dz+.092),None,vertices=24,bevel=0);b.cut(saddle,cut)
 b.annulus(f'crimp_stop_{layer}',parent,cfg.COLLAR['inner']/2,cfg.COLLAR['outer']/2,dz+.078,dz+.088,'crimp',steps=32)
low=b.assembly('detail.groove','Groove section')
grid_section(low,0)
b.beam('tension_rod',low,(0,0,.072),(0,0,.19),.003,'tie')
b.box('bottom_facing',low,(.32,.12,.002),(0,0,-.001),'facing')
b.box('joint_cement',low,(.004,.06,.038),(0,.03,.019),'facing')
b.box('cap',low,(.34,.14,.02),(0,0,-.012),'context')
levels=b.assembly('detail.layers','Five layer section',position=(2,0,0))
for layer in range(cfg.LAYERS):grid_section(levels,layer)
b.beam('shared_rod',levels,(0,0,.072),(0,0,.694+cfg.STACK_RISE),.003,'tie')
frame=b.box('upper_frame',levels,(.060,.12,.160),(0,0,.583),'hot_frame')
cut=b.box('frame_void',levels,(.054,.16,.154),(0,0,.583),None);b.cut(frame,cut)
cut=b.cylinder('frame_bore',levels,.008,.20,(0,0,.583),None,vertices=32,bevel=0);b.cut(frame,cut)
cut=b.box('frame_section',levels,(.3,.2,.2),(0,-.1,.583),None);b.cut(frame,cut)
for name,inner,outer,z0,z1,mat in [('sleeve',.004,.007,.499,.673,'zirconia'),('washer',.007,.020,.663,.673,'zirconia'),('spreader',.004,.016,.673,.676,'stainless'),('nut',.003,.007,.676,.686,'links')]:
 ob=b.annulus(name,levels,inner,outer,z0,z1,mat,steps=32)
 if mat=='zirconia':
  cut=b.box('ceramic_section',levels,(.3,.2,.3),(0,-.1,.6),None);b.cut(ob,cut)
for ob in list(levels.children):
 if ob.name.rsplit('.',1)[-1] in ('upper_frame','sleeve','washer','spreader','nut'):ob.location.z+=cfg.STACK_RISE
b.box('facing',levels,(.32,.12,.002),(0,0,-.001),'facing')
b.box('cap_reference',levels,(.34,.14,.02),(0,0,-.012),'context')
upper=b.assembly('detail.ceramic','Ceramic section',position=(1,0,0))
# Local elevation is shifted for compact display; dimensions match the full model.
frame=b.box('hollow_frame',upper,(.060,.12,.160),(0,0,.08),'hot_frame')
cut=b.box('box_void',upper,(.054,.16,.154),(0,0,.08),None);b.cut(frame,cut)
cut=b.cylinder('hanger_bore',upper,.008,.25,(0,0,.08),None,vertices=32,bevel=0);b.cut(frame,cut)
cut=b.box('frame_section',upper,(.3,.2,.4),(0,-.1,.10),None);b.cut(frame,cut)
sleeve=b.annulus('ceramic_sleeve',upper,.004,.007,-.004,.170,'zirconia',steps=48)
washer=b.annulus('ceramic_washer',upper,.007,.020,.160,.170,'zirconia',steps=64)
for ob in (sleeve,washer):
    cut=b.box('ceramic_section',upper,(.3,.2,.4),(0,-.1,.1),None);b.cut(ob,cut)
b.annulus('steel_spreader',upper,.004,.016,.170,.173,'stainless',steps=48)
b.annulus('nut',upper,.003,.007,.173,.183,'links',steps=6)
b.beam('tie_rod',upper,(0,0,-.05),(0,0,.191),.003,'tie')
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Detail studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.85,.9,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
scene.view_settings.view_transform='AgX'
for x in (0,1,2):
 d=bpy.data.lights.new(f'Light{x}','AREA');d.energy=65;d.size=1;ob=bpy.data.objects.new(f'Light{x}',d);b.collection('Presentation').objects.link(ob);ob.location=(x-.4,-.8,1);ob.rotation_euler=(Vector((x,0,.08))-ob.location).to_track_quat('-Z','Y').to_euler()
views=[('layers',(2,-4,.65),(2,0,.34),1.2,'WISTR | Bottom grooves; plain blocks above','Bottom recessed; upper four on flat flanges','Assemble bottom-up. Each collar carries one level; rod load accumulates upward.'),('groove',(0,-4,.65),(0,0,.065),.49,'WISTR | T-bar recessed into the block edges','Section through the lowest 100 mm layer','Gold: crimp stop below sliding saddle. Silver flange bears on the groove roof.'),
       ('ceramic',(1,-4,.55),(1,0,.070),.39,'WISTR | Ceramic-isolated hanger','Cut frame and ceramic sleeve; continuous steel tension rod','Load: nut / spreader -> zirconia washer -> frame. Sleeve prevents side contact.')]
out=ROOT/'outputs/reactor-tgrid-cover'
for name,pos,target,scale,title,subtitle,foot in views:
 data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);b.collection('Presentation').objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale
 col=b.collection('Labels.'+name);height=scale*1000/1400
 for key,txt,y,size in [('title',title,.44,.026),('subtitle',subtitle,.38,.016),('footer',foot,-.45,.013)]:text_on_camera(name+key,txt,-scale*.46,height*y,scale*size,cam,col)
 for nm,collection in b.collections.items():
  collection.hide_render=(nm.startswith('Labels.') and nm!='Labels.'+name) or (nm=='Groove section' and name!='groove') or (nm=='Ceramic section' and name!='ceramic') or (nm=='Five layer section' and name!='layers')
 scene.camera=cam;scene.render.filepath=str(out/f'tgrid-detail-{name}.png');bpy.ops.render.render(write_still=True)
# Leave the five-layer section visible on opening.
scene.camera=bpy.data.objects['layers']
for nm,collection in b.collections.items():
 collection.hide_viewport=(nm.startswith('Labels.') and nm!='Labels.layers') or nm in ('Groove section','Ceramic section')
 collection.hide_render=collection.hide_viewport
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(out/'tgrid-connection-details.blend'))
