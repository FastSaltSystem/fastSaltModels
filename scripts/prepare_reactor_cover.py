"""Fit individual cassette parts, then export compact driver-free geometry.
Boolean cuts precede merging, so overlapping frame members remain independent solids.
"""
from pathlib import Path
import sys,bpy,json,hashlib,bmesh,math
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'models'),str(ROOT/'src')]
import wistr_reactor as layout
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.reactor_lifting import interface_points
source=ROOT/'outputs/reactor-tgrid-cover/wistr-tgrid-cover.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
for col in bpy.data.collections:col.hide_viewport=False
for ob in bpy.data.objects:
 if ob.get('role')=='captive_vertical_pickup':ob.location.z=0
bpy.context.view_layer.update()
def owned(o):
 while o:
  if o.name=='rigid.cassette':return True
  o=o.parent
 return False
rot=Matrix.Rotation(-math.pi/6,3,'Z');pc=rot@Vector((*layout.SECTOR_PLUG['centre'],0))
ports=[(pc.x,pc.y,.25)]+[(layout.ABSORBER_PLUG['centre_radius']*math.cos(math.pi/6),sign*layout.ABSORBER_PLUG['centre_radius']*.5,.25) for sign in (-1,1)]
pockets=[]
for point,side,station in interface_points(layout,'cap'):
 q=rot@point;pockets.append((q.x+(.0075 if station else -.0075),q.y,.205,.065,.280))
b=SceneBuilder();root=b.assembly('asset_fit','Asset preparation');snapshots=[];dg=bpy.context.evaluated_depsgraph_get()
for o in list(bpy.data.objects):
 if o.type not in ('MESH','CURVE') or not owned(o):continue
 ev=o.evaluated_get(dg);mesh=ev.to_mesh()
 if not mesh.vertices:ev.to_mesh_clear();continue
 category='blocks' if o.name.startswith('rigid.blocks.') else 'frame' if o.name.startswith('rigid.frame.') else 'grid' if o.name.startswith('rigid.grid.') else 'shell' if o.name.startswith('rigid.shell.') else 'other'
 snapshots.append((category,o.data.materials[0],[tuple(o.matrix_world@v.co) for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons]))
 ev.to_mesh_clear()
groups={};cuts=0
for n,(category,mat,verts,faces) in enumerate(snapshots):
 ob=b.mesh(str(n),root,verts,faces,None)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 if category!='other' or mat.name.split('.')[0] in ('facing','joint_cement'):
  for x,y,r in ports:
   if lo[0]<x+r and hi[0]>x-r and lo[1]<y+r and hi[1]>y-r:
    cut=b.cylinder('well',root,r,1.5,(x,y,.5),None,vertices=48,bevel=0);b.cut(ob,cut);cuts+=1
  if lo[2]<.28:
   for x,y,w,h,top in pockets:
    if lo[0]<x+w/2 and hi[0]>x-w/2 and lo[1]<y+h/2 and hi[1]>y-h/2:
     cut=b.box('pocket',root,(w,h,top+.05),(x,y,(top-.05)/2),None);b.cut(ob,cut);cuts+=1
 group=groups.setdefault((category,mat.name),dict(verts=[],faces=[],mat=mat));offset=len(group['verts'])
 group['verts'].extend(tuple(v.co) for v in ob.data.vertices);group['faces'].extend(tuple(offset+i for i in f.vertices) for f in ob.data.polygons)
 bpy.data.objects.remove(ob,do_unlink=True)
objects=set()
for (category,matname),g in groups.items():
 mesh=bpy.data.meshes.new('cassette_asset.'+category+'_'+matname);mesh.from_pydata(g['verts'],[],g['faces']);mesh.materials.append(g['mat']);mesh.update()
 ob=bpy.data.objects.new(mesh.name,mesh);ob['component']=category;objects.add(ob)
 if category=='frame':assert min(v.co.z for v in mesh.vertices)>.50 and max(v.co.z for v in mesh.vertices)<.69,'Invalid fitted frame bounds'
asset=source.parent/'cassette-asset.blend';bpy.data.libraries.write(str(asset),objects)
asset.with_suffix('.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fitted':True,'meshes':len(objects),'part_cuts':cuts}))
print('FITTED_COMPACT_CASSETTE_READY',len(objects),cuts,flush=True)
