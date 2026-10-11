"""Refresh fitted covers in an already generated reactor after cassette edits."""
from pathlib import Path
import sys,json,hashlib
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
import wistr_reactor as layout
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.reactor_cover import build_cover
from build_reactor import select_view
out=ROOT/'outputs/reactor-study'
bpy.ops.wm.open_mainfile(filepath=str(out/'wistr-reactor-study.blend'))
scene=bpy.context.scene;scene['maintenance_position']=False;scene['section_cutaway']=False;scene.update_tag()
for name in ('Insulation covers','Insulation service inserts'):
 col=bpy.data.collections.get(name)
 if col:
  for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.collections.remove(col)
b=SceneBuilder();b.collections={c.name:c for c in scene.collection.children};b.assemblies={o.name:o for o in scene.objects if o.type=='EMPTY' and 'category' in o};b.materials={m.name:m for m in bpy.data.materials}
cover=build_cover(b,layout,layout.dimensions())
cutter=bpy.data.objects['study.section_tool.front_half']
for category in ('Insulation covers','Insulation service inserts'):
 for ob in b.collections[category].objects:
  if ob.type!='MESH':continue
  mod=ob.modifiers.new('Presentation section','BOOLEAN');mod.object=cutter;mod.operation='DIFFERENCE';mod.solver='EXACT'
  for prop in ('show_viewport','show_render'):
   driver=mod.driver_add(prop).driver;v=driver.variables.new();v.name='cut';v.type='SINGLE_PROP';v.targets[0].id_type='SCENE';v.targets[0].id=scene;v.targets[0].data_path='["section_cutaway"]';driver.expression='cut'
cut_objects=[o for o in scene.objects if o.type=='MESH' and any(m.type=='BOOLEAN' and m.object==cutter for m in o.modifiers)]
cameras={'air-system':bpy.data.objects['View.AirCollectors'],'air-section':bpy.data.objects['View.AirCircuit']}
for view in cameras:
 select_view(b,cameras,cut_objects,view);scene.render.filepath=str(out/f'reactor-{view}-draft.png');bpy.ops.render.render(write_still=True)
select_view(b,cameras,cut_objects,'air-section');bpy.ops.wm.save_as_mainfile(filepath=str(out/'wistr-reactor-study.blend'))
p=out/'reactor-study-report.json';report=json.loads(p.read_text());report['insulation_cover']=cover;p.write_text(json.dumps(report,indent=2)+'\n')
(out/'manifest.json').write_text(json.dumps({'status':'working generated source','files':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (out/'wistr-reactor-study.blend',out/'reactor-study-report.json')}},indent=2))
print('FITTED_COVER_REFRESHED')
