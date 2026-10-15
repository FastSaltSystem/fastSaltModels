import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[1]
p=repo/'outputs/site-control-annex/fast-salt-control-annex.blend'
out=repo/'outputs/absorber-audit';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(p))
bpy.context.view_layer.update()
def vals(v):
 try:return list(v)
 except TypeError:return v
rows=[]
for o in bpy.data.objects:
 if (o.name.startswith('reactor.absorber_') and o.name.endswith('.rectangular_tank')) or ((o.name.startswith('equipment.absorber_reservoir_') or o.name.startswith('equipment.absorber_module_')) and o.name.endswith(('.salt_vessel_envelope','.control_enclosure'))) or (o.name.startswith('reactor.absorber_tubes_') and o.name.endswith(('.centre_a','.centre_b','.outer_a','.outer_b'))):
  pts=[o.matrix_world@Vector(q) for q in o.bound_box]
  row=dict(name=o.name,local_dimensions=list(o.dimensions),world_min=[min(q[k] for q in pts) for k in range(3)],world_max=[max(q[k] for q in pts) for k in range(3)])
  for key in ['connection_point','termination','points','path_points','centreline','wall_thickness','diameter','outside_diameter']:
   if key in o:
    row[key]=vals(o[key])
    if key in ['connection_point','termination']:row[key+'_world']=list(o.matrix_world@Vector(o[key]))
  rows.append(row)
(out/'absorber-scene-audit.json').write_text(json.dumps(dict(scene=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),objects=rows),indent=2,default=list))
print('AUDIT',len(rows))
