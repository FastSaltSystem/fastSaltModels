"""Render a draft detail from the current installation .blend without modifying it.

Run after build_wistr.py with Blender --background --python this_file.
"""
import bpy
from mathutils import Vector
from pathlib import Path
folder=Path(__file__).resolve().parents[1]/'outputs/installation-concrete-rings'
bpy.ops.wm.open_mainfile(filepath=str(folder/'wistr-installation.blend'))
scene=bpy.context.scene
root=bpy.data.objects['equipment.steam_generator_1']
keep={root,*root.children,bpy.data.objects['connections.air.generator_1.hot'],bpy.data.objects['connections.air.generator_1.fresh']}
for o in scene.objects:
    if o.type not in ('CAMERA','LIGHT'):o.hide_render=o not in keep
visible_collections={c for o in keep for c in o.users_collection}
visible_collections.update(c for o in scene.objects if o.type in ('CAMERA','LIGHT') for c in o.users_collection)
for c in bpy.data.collections:
    c.hide_render=c not in visible_collections or c.name.startswith('Annotations.')
cam=bpy.data.objects['View.Equipment'];scene.camera=cam
cam.location=root.matrix_world @ Vector((-9,12,13))
target=root.matrix_world @ Vector((0,1.7,9.2))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=24;scene.render.resolution_x=900;scene.render.resolution_y=900
scene.render.resolution_percentage=100;scene.cycles.samples=16
scene.render.filepath=str(folder/'wistr-generator-detail-draft.png')
bpy.ops.render.render(write_still=True)
