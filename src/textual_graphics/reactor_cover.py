"""Fit six instances of the developed cassette to the pressure caps.
Service wells and blind hook pockets are provisional integration details.
"""
import math,hashlib,json
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from .reactor_insulation_cover import materials
from .perforated import perforated_prism

def split_frame_for_sections():
 """Keep each closed RHS member separate for reliable presentation Booleans."""
 cache={};count=0
 for ob in list(bpy.context.scene.objects):
  if ob.type!='MESH' or not ob.name.startswith('reactor.insulation_') or ob.get('component')!='frame':continue
  for mod in ob.modifiers:
   if mod.type=='BOOLEAN':mod.use_self=False
  mesh=ob.data
  if mesh.name not in cache:
   parent=list(range(len(mesh.vertices)))
   def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
   for edge in mesh.edges:
    a,c=map(find,edge.vertices);parent[c]=a
   groups={}
   for face in mesh.polygons:groups.setdefault(find(face.vertices[0]),[]).append(tuple(face.vertices))
   pieces=[]
   if len(groups)<2:continue
   for i,faces in enumerate(groups.values()):
    ids=sorted({v for face in faces for v in face});mapping={old:new for new,old in enumerate(ids)}
    part=bpy.data.meshes.new(mesh.name+'.member_'+str(i));part.from_pydata([mesh.vertices[v].co for v in ids],[],[[mapping[v] for v in face] for face in faces]);part.update()
    for material in mesh.materials:part.materials.append(material)
    pieces.append(part)
   cache[mesh.name]=pieces
  for i,meshpart in enumerate(cache[mesh.name]):
   child=ob.copy();child.data=meshpart;child.name=ob.name+'.member_'+str(i)
   for col in ob.users_collection:col.objects.link(child)
   count+=1
  bpy.data.objects.remove(ob,do_unlink=True)
 return count

def build_cover(b,layout,d):
 import wistr_tgrid_cover as cfg
 repo=Path(__file__).resolve().parents[2]
 source=repo/'outputs/reactor-tgrid-cover/wistr-tgrid-cover.blend'
 report=repo/'outputs/reactor-tgrid-cover/tgrid-cover-report.json'
 if not source.exists():raise FileNotFoundError('Build scripts/build_tgrid_cover.py before the reactor.')
 materials(b)
 scene=bpy.context.scene
 asset=source.parent/'cassette-asset.blend'
 meta=json.loads(asset.with_suffix('.json').read_text())
 assert meta['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest(),'Rebuild cassette asset'
 with bpy.data.libraries.load(str(asset),link=False) as (available,loaded):loaded.objects=available.objects
 imported=list(loaded.objects)
 print('Fitting compact cover',len(imported),flush=True)
 z=d['top_z']+.15+layout.PRESENTATION['cap_thickness']+.002
 first=b.assembly('reactor.insulation_1','Insulation covers',position=(0,0,z),angle=30)
 parts=[]
 for ob in imported:
  category=ob['component'];ob.name='reactor.insulation_1.'+ob.name.removeprefix('cassette_asset.')
  b.collection('Insulation covers').objects.link(ob);ob.parent=first;parts.append(ob)
 # All holes are defined in the source cassette's bisector coordinate system.
 rot=Matrix.Rotation(-math.pi/6,3,'Z')
 pc=rot@Vector((*layout.SECTOR_PLUG['centre'],0))
 ports=[(pc.x,pc.y,.25)]+[(layout.ABSORBER_PLUG['centre_radius']*math.cos(math.pi/6),sign*layout.ABSORBER_PLUG['centre_radius']*.5,.25) for sign in (-1,1)]
 from .reactor_lifting import interface_points
 pockets=[]
 for point,side,station in interface_points(layout,'cap'):
  q=rot@point
  pockets.append((q.x+(.0075 if station else -.0075),q.y,.205,.065,.280))
 assert meta.get('fitted'),'Prepare fitted cassette asset first'
 # Local framing collars bridge cut frame members; split at the sector seams.
 # Their welds/load redistribution are not covered by the standalone grillage result.
 for i,(x,y,radius) in enumerate(ports):
  collar=b.annulus('service_frame_collar_'+str(i),first,radius,radius+.07,cfg.COVER['frame_bottom'],cfg.COVER['frame_bottom']+cfg.RHS['height'],'hot_frame',steps=64)
  collar.location.x=x;collar.location.y=y
  void=b.annulus('collar_box_void',first,radius+.003,radius+.067,cfg.COVER['frame_bottom']+.003,cfg.COVER['frame_bottom']+cfg.RHS['height']-.003,None,steps=64)
  void.location.x=x;void.location.y=y;b.cut(collar,void)
  clip=perforated_prism(b,'sector_clip',first,cfg.outline(),[],0,1.2,None)
  bpy.context.view_layer.update();mod=collar.modifiers.new('Keep within sector','BOOLEAN');mod.operation='INTERSECT';mod.object=clip;mod.solver='EXACT';bpy.context.view_layer.objects.active=collar;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(clip,do_unlink=True)
  parts.append(collar)
 print('Cover pockets and collars complete',flush=True)
 # Replicate fitted source geometry, using linked mesh data for compact saved files.
 for n in range(2,7):
  root=b.assembly('reactor.insulation_'+str(n),'Insulation covers',position=(0,0,z),angle=30+(n-1)*60)
  for ob in parts:
   copy=ob.copy();copy.data=ob.data;b.collection('Insulation covers').objects.link(copy);copy.parent=root;copy.name=ob.name.replace('insulation_1','insulation_'+str(n))
 split_frame_for_sections()
 # Lift-out thermal inserts leave access to the existing disconnected service stubs.
 inserts=b.assembly('reactor.thermal_service_inserts','Insulation service inserts')
 port_world=[]
 for n in range(6):
  turn=Matrix.Rotation(n*math.pi/3,3,'Z');q=turn@Vector((*layout.SECTOR_PLUG['centre'],0));port_world.append((q.x,q.y,'core_'+str(n+1)))
  angle=n*math.pi/3;port_world.append((layout.ABSORBER_PLUG['centre_radius']*math.cos(angle),layout.ABSORBER_PLUG['centre_radius']*math.sin(angle),'absorber_'+str(n+1)))
 for x,y,name in port_world:
  plug=b.cylinder(name+'_insulation',inserts,.244,.512-.18,(x,y,z+(.512+.18)/2),'wool',vertices=48,bevel=0)
  cap=b.cylinder(name+'_lid',inserts,.246,.006,(x,y,z+cfg.COVER['frame_bottom']+.199),'stainless',vertices=48,bevel=0)
  b.box(name+'_handle',inserts,(.13,.025,.035),(x,y,z+cfg.COVER['frame_bottom']+.22),'links')
 scene['insulation_cover_integration']=json.dumps(dict(source=str(source.relative_to(repo)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
   nominal_source_mass_kg=json.loads(report.read_text())['mass_kg'],cover_count=6,base_z=z,stack_height=.512,
   hook_pockets_per_cover=4,service_wells=12,hood_replaced=True,
   limitations=['Service inserts cover disconnected tube terminals; external service extensions remain to design',
   'Fitted wells and local frame collars require renewed strength, bearing and thermal checks; source mass and grillage do not qualify the fitted covers',
   'Air plenums remain outside the vertical cassette envelope; complete crane/extraction routing is not qualified']))
 return json.loads(scene['insulation_cover_integration'])
