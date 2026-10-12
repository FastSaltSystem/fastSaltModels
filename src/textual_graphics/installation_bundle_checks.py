"""Selected full-size insulated-bundle surface checks."""
import itertools
import bpy
from mathutils.bvhtree import BVHTree
from .installation_clearance import bounds,gapbox

def check_bundle_envelopes(services):
    items=services['catwalk']['bundles']+services['fuel_services']['bundles']
    cache={}
    def info(o):
     if o.name not in cache:
      verts=[o.matrix_world@v.co for v in o.data.vertices]
      cache[o.name]=(bounds(verts),BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in o.data.polygons]))
     return cache[o.name]
    clashes=[];checks=0
    for a,c in itertools.combinations(items,2):
     if set(a['members'])&set(c['members']):continue
     ob=bpy.data.objects[a['name']];other=bpy.data.objects[c['name']];bb,tree=info(ob);bc,tc=info(other)
     if gapbox(bb,bc)>.001:continue
     checks+=1
     if tree.overlap(tc):clashes.append((ob.name,other.name))
    # Closed equipment and frame objects; each intentional own equipment connection is excluded.
    obstacles=[o for o in bpy.data.objects if o.type=='MESH' and (
     (o.name.startswith('equipment.reactor_catwalk.') and any(k in o.name for k in ('.column_','.radial_joist_','_bearer_','.ring_beam_'))) or
     o.name.startswith('connections.air.') or o.get('route_object'))]
    for a in items:
     ob=bpy.data.objects[a['name']];bb,tree=info(ob)
     for other in obstacles:
      bc,tc=info(other)
      if gapbox(bb,bc)>.001:continue
      checks+=1
      if tree.overlap(tc):clashes.append((ob.name,other.name))
    assert not clashes,clashes
    return dict(pairs=checks,clashes=clashes,scope="Surface checks of separate bundle jackets, framing and nearby process/air meshes; intended shared-branch junctions excluded")
