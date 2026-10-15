"""Apply the owner-selected chamber bottom to the saved site without rebuilding other systems."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'outputs/site-control-annex/fast-salt-control-annex.blend'
out=ROOT/'outputs/absorber-review';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
rows=[]
for n in range(1,7):
 o=bpy.data.objects[f'reactor.absorber_{n}.rectangular_tank']
 before=[o.matrix_world@v.co for v in o.data.vertices];low=min(p.z for p in before);high=max(p.z for p in before)
 assert abs(low+7.57)<1e-4 and abs(high+3.62)<1e-4
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if abs(p.z-low)<1e-4:p.z=-7.27;v.co=inv@p
 o.data.update();o['chamber_bottom_basis']='Active-core bottom; bottom-reflector volume excluded by owner 2026-10-15'
 after=[o.matrix_world@v.co for v in o.data.vertices]
 assert abs(min(p.z for p in after)+7.27)<1e-5
 assert abs(max(p.z for p in after)-high)<1e-5
 rows.append(dict(name=o.name,bottom_before_m=low,bottom_after_m=min(p.z for p in after),top_m=high))
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'fast-salt-absorber-review.blend'))
report={'changes':rows,'checks':['All six chamber envelopes start at active-core bottom','Upper connection elevations retained'],'limitations':['Chamber partitions and supports remain unresolved','External bottom-fed salt routes not yet modeled; existing top tube terminations retained as historical placeholders'], 'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,Path(__file__),ROOT/'src/textual_graphics/reactor_geometry.py']}}
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print('ABSORBER_BOTTOMS_OK')
