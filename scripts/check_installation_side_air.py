"""Check selected side-air clearances in a loaded installation Blender scene."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from textual_graphics.installation_clearance import bounds,segment_box
scene=bpy.context.scene;scene['section_cutaway']=False;scene.update_tag();bpy.context.view_layer.update()
boxes=[o for o in scene.objects if o.type=='MESH' and ('absorber' in o.name) and o.name.endswith(('.deck','.closed_enclosure'))]
curves=[o for o in scene.objects if o.type=='CURVE' and o.name.startswith('connections.air.') and 'reactor' in o.name]
assert boxes and curves,([o.name for o in boxes],[o.name for o in curves])
results=[]
for ob in curves:
 for box in boxes:
  inv=box.matrix_world.inverted();lo,hi=bounds(box.bound_box)
  pts=[inv@ob.matrix_world@Vector(p.co[:3]) for p in ob.data.splines[0].points]
  gap=min(segment_box(a,b,lo,hi) for a,b in zip(pts,pts[1:]))-ob.data.bevel_depth
  results.append(dict(route=ob.name,obstacle=box.name,clearance_m=gap))
assert min(r['clearance_m'] for r in results)>0,sorted(results,key=lambda x:x['clearance_m'])[:4]
air=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith('reactor.hot_air_manifold') or o.name.startswith('reactor.cold_air_manifold'))]
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
for a in air:
 for b in boxes:assert not tree(a).overlap(tree(b)),(a.name,b.name)
report={'checks':['Reactor side air branches clear absorber decks and enclosures','Side plenums have no intersecting surfaces with absorber decks and enclosures'],'minimum_branch_to_absorber_clearance_m':min(r['clearance_m'] for r in results),'scope':'Selected route capsules and solid surfaces; not all equipment or maintenance travel'}
(R/'outputs/installation-insulated/side-air-clearance-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
