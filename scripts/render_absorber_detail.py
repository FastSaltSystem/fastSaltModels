"""Render a local cutaway of one paired absorber station; preserve the complete scene."""
import argparse,math,sys
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src'),str(ROOT/'models')]
from build_wistr import select_view
from render_pms import text_on_camera
parser=argparse.ArgumentParser()
parser.add_argument('--source',type=Path,default=ROOT/'outputs/installation-absorber-reservoirs/wistr-installation.blend')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(args.source.resolve()))
b=SimpleNamespace(collections={c.name:c for c in bpy.data.collections})
cameras={name:bpy.data.objects[obj] for name,obj in [('catwalk','View.Catwalk'),('fuel-services','View.FuelServices'),('plan','View.Plan'),('equipment','View.Equipment'),('cutaway','View.Cutaway')]}
select_view(b,cameras,'catwalk')
# The complete installation opens on the current absorber overview.
bpy.ops.wm.save_as_mainfile(filepath=str(args.source.resolve()))
for c in bpy.data.collections:
 if c.name.startswith('Annotations.'):c.hide_render=True
for ob in bpy.data.objects:
 name=ob.name
 if name.startswith(('equipment.absorber_module_','equipment.absorber_reservoir_')):
  index=int(name.split('.')[1].rsplit('_',1)[-1]);ob.hide_render=index not in (11,12)
 elif name.startswith('connections.absorber_services.'):
  ob.hide_render='.absorber_6.' not in name
  if '.absorber_6.centre_' in name and name.endswith(('.insulation','.cladding')):ob.hide_render=True
 elif name.startswith('connections.absorber_chase_'):
  ob.hide_render=not (name.startswith('connections.absorber_chase_6.') and name.endswith('.bottom'))
 elif name.startswith('connections.fuel_services.'):ob.hide_render=True
 elif name.startswith('equipment.reactor_catwalk.'):
  ob.hide_render=True
 if name.startswith('equipment.absorber_reservoir_11.') and name.endswith(('.insulation','.jacket')):ob.hide_render=True
scene=bpy.context.scene
angle=math.radians(-15)
def rot(v):return Vector((v[0]*math.cos(angle)-v[1]*math.sin(angle),v[0]*math.sin(angle)+v[1]*math.cos(angle),v[2]))
data=bpy.data.cameras.new('AbsorberDetail');cam=bpy.data.objects.new('View.AbsorberDetail',data);scene.collection.objects.link(cam)
cam.location=rot((.5,-6,7));target=rot((5.2,0,.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=12
scene.camera=cam
col=bpy.data.collections.new('Annotations.AbsorberDetail');scene.collection.children.link(col)
text_on_camera('detail_title','WISTR | One paired absorber station',-5.4,4.10,.27,cam,col)
text_on_camera('detail_note','Walkway and service covers removed / one tank jacket removed to show heater bands',-5.4,3.66,.13,cam,col,'#4C5C68')
text_on_camera('detail_footer','6 pairs / 12 reservoirs + 12 modules | 50 mm drains fall to spider | Sizes and thermal allowances provisional',-5.4,-4.10,.13,cam,col,'#4C5C68')
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.render.filepath=str(args.source.parent/'wistr-absorber-detail.png')
bpy.ops.render.render(write_still=True)
print('ABSORBER_DETAIL_OK')
