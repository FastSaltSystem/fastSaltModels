"""Inspection view of connected services; does not save a hidden-cover model."""
from pathlib import Path
import sys
from types import SimpleNamespace
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from build_wistr import select_view
out=ROOT/'outputs/installation-under-cover-bundles'
bpy.ops.wm.open_mainfile(filepath=str(out/'wistr-installation.blend'))
b=SimpleNamespace(collections={c.name:c for c in bpy.data.collections})
select_view(b,{'catwalk':bpy.data.objects['View.Catwalk']},'catwalk')
for index in range(1,7):
    for ob in bpy.data.objects[f'reactor.insulation_{index}'].children_recursive:ob.hide_render=True
from mathutils import Vector
cam=bpy.data.objects['View.Catwalk'];cam.location=(12,-18,28)
cam.rotation_euler=(Vector((0,0,-1))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['Catwalk.Title'].data.body='WISTR | Connected services beneath insulation'
bpy.data.objects['Catwalk.Note'].data.body='Insulation cassettes hidden for inspection / tubes remain connected'
bpy.data.objects['Catwalk.Footer'].data.body='Open-bottom channels permit cover lift / remote disconnections remain to detail'
scene=bpy.context.scene;scene.cycles.samples=16;scene.render.resolution_percentage=50
scene.render.filepath=str(out/'wistr-under-cover-detail.png')
bpy.ops.render.render(write_still=True)
print('UNDER_COVER_DETAIL_OK')
