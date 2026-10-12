"""Check the saved fitted reactor assembly; writes a separate integration report."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;scene['maintenance_position']=False;scene['section_cutaway']=False;scene.update_tag();bpy.context.view_layer.update()
assert len([o for o in bpy.data.objects if o.name.startswith('reactor.insulation_') and o.type=='EMPTY'])==6
assert not any(o.name.startswith('reactor.hot_air_hood') for o in bpy.data.objects)
def tree(o,delta=0):
 return BVHTree.FromPolygons([o.matrix_world@v.co+Vector((0,0,delta)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
parts=[o for o in bpy.data.objects['reactor.insulation_1'].children if o.type=='MESH']
hooks=[o for o in bpy.data.objects['reactor.cap_1'].children if o.get('role')=='cap_lifting_hook']
obstacles=[(o.name,tree(o)) for o in hooks]
for height in (0,.05,.20,.40,.80):
 for ob in parts:
  tr=tree(ob,height)
  for name,t in obstacles:assert not tr.overlap(t),(ob.name,name,height)
# Check side-system solid surfaces against all coolant nozzle meshes.
air=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('reactor.hot_air_manifold') or o.name.startswith('reactor.cold_air_manifold') or o.name.startswith('reactor.air_ducts') or o.name.startswith('reactor.hot_air_insulation'))]
nozzles=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('reactor.hot_outlet_') or o.name.startswith('reactor.cold_inlet_')) and 'cutter' not in o.name]
ats=[(o.name,tree(o)) for o in air]
for o in nozzles:
 t=tree(o)
 for name,at in ats:assert not at.overlap(t),(name,o.name,'air/coolant interference')
def mass(o):
 mesh=o.data;mesh.calc_loop_triangles();origin=sum((v.co for v in mesh.vertices),Vector())/len(mesh.vertices)
 total=[]
 for tri in mesh.loop_triangles:
  a,b,c=[mesh.vertices[i].co-origin for i in tri.vertices];total.append(a.dot(b.cross(c))/6)
 vol=abs(math.fsum(total))
 material=mesh.materials[0].name.split('.')[0]
 rho=240 if material.startswith('calcium') or material=='wool' else 6000 if material=='zirconia' else 1500 if material in ('facing','joint_cement') else 7850 if material in ('hot_frame','links') else 8000
 return vol*rho
cassette_mass=sum(mass(o) for o in parts)
inserts=[o for o in bpy.data.objects['reactor.thermal_service_inserts'].children if o.type=='MESH']
report={'checks':['Six covers and no former hot hood','Cap-hook clearances checked for sector 1 at five vertical positions; other sectors share fitted mesh geometry','Side plenums/stubs clear coolant-nozzle meshes'],
 'fitted_cassette_additive_mass_kg':cassette_mass,'all_thermal_inserts_additive_mass_kg':sum(mass(o) for o in inserts),
 'limitations':['Geometric surface checks do not qualify full crane travel, structural capacity, pressure boundary, natural circulation or heat transfer','Frame service collars and local grid cuts require new structural analysis; standalone grillage is not a fitted-cover result','Service inserts cover disconnected terminals; operating service extensions remain to design']}
(ROOT/'outputs/reactor-study/reactor-cover-fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
