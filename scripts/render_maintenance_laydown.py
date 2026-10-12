"""Inspection-only placement of one actual cover and cap on their receiving bays.

Does not save the Blender scene or change installed equipment in the working model.
"""
from pathlib import Path
import sys,math
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from build_wistr import camera,select_view
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.installation_maintenance import item_bounds
from render_pms import text_on_camera
import wistr_installation as layout
out=ROOT/'outputs/installation-under-cover-bundles'
bpy.ops.wm.open_mainfile(filepath=str(out/'wistr-installation.blend'))
b=SceneBuilder();b.collections={c.name:c for c in bpy.data.collections}
cameras={k:bpy.data.objects[v] for k,v in [('stairs','View.Stairs'),('catwalk','View.Catwalk'),('fuel-services','View.FuelServices'),('plan','View.Plan'),('equipment','View.Equipment'),('cutaway','View.Cutaway')]}
select_view(b,cameras,'equipment')
for c in bpy.data.collections:c.hide_viewport=False
bpy.context.view_layer.update()
col=b.collection('Maintenance preview');deps=bpy.context.evaluated_depsgraph_get()
for key,name in [('cover','reactor.insulation_1'),('cap','reactor.cap_1')]:
    root=bpy.data.objects[name];lo,hi=item_bounds(name);a,c,d,e=layout.MAINTENANCE[key+'_bay']
    target=Vector(((a+c-lo[0]-hi[0])/2,(d+e-lo[1]-hi[1])/2,layout.CATWALK['deck_z']+.105-lo[2]))
    transform=Matrix.Translation(target)@root.matrix_world.inverted()
    sources=[root]+list(root.children_recursive)
    for source in sources:
        if source.type not in ('MESH','CURVE') or source.hide_render:continue
        mesh=bpy.data.meshes.new_from_object(source.evaluated_get(deps),depsgraph=deps)
        ob=bpy.data.objects.new('LaydownPreview.'+source.name,mesh);col.objects.link(ob)
        ob.matrix_world=transform@source.matrix_world
    for source in sources:source.hide_render=True
for c in bpy.data.collections:
    if c.name.startswith('Annotations.') or c.name in ('Shell','Crane','Stacks','Air distribution','Hot air insulation','Hot air duct metal','Nitrogen supply','Sector handling'):
        c.hide_render=True
# Pipe insulation remains for context; distant generators are omitted for the close view.
for cat in ('Steam generators','Secondary piping','Coolant pumps'):
    if cat in b.collections:b.collections[cat].hide_render=True
cam=camera(b,'View.MaintenancePreview',(28,-24,23),(7.5,0,-1.6),28)
bpy.context.scene.camera=cam
ann=b.collection('Maintenance preview labels')
# Opaque camera-space bands keep the labels legible against the equipment.
mat=bpy.data.materials.new('MaintenanceLabelBackground');mat.use_nodes=True
node=mat.node_tree.nodes.new('ShaderNodeEmission');node.inputs['Color'].default_value=(.97,.97,.95,1)
mat.node_tree.links.new(node.outputs[0],mat.node_tree.nodes.get('Material Output').inputs['Surface'])
for i,(bottom,top) in enumerate(((8.15,10.5),(-10.5,-9.0))):
    mesh=bpy.data.meshes.new('MaintenanceLabelBand');mesh.from_pydata([(-14,bottom,0),(14,bottom,0),(14,top,0),(-14,top,0)],[],[(0,1,2,3)])
    ob=bpy.data.objects.new('MaintenanceLabelBand'+str(i),mesh);ann.objects.link(ob)
    ob.parent=cam;ob.location=(0,0,-3.1);ob.data.materials.append(mat);ob.visible_shadow=False
text_on_camera('Maintenance.Title','WISTR | Cover and cap laydown',-12.5,9.3,.53,cam,ann)
text_on_camera('Maintenance.Note','One insulation cover + one sector cap / platform at catwalk level',-12.5,8.45,.28,cam,ann,'#4C5C68')
text_on_camera('Maintenance.Footer','Illustrated maintenance placement / receiving frame and load rating provisional',-12.5,-9.4,.26,cam,ann,'#4C5C68')
s=bpy.context.scene;s.render.resolution_x=2000;s.render.resolution_y=1500;s.render.resolution_percentage=75;s.cycles.samples=24
s.render.filepath=str(out/'wistr-maintenance-laydown-draft.png');bpy.ops.render.render(write_still=True)
print('MAINTENANCE_PREVIEW_OK',flush=True)
