"""Render a draft entrance close-up without modifying the saved installation."""
from pathlib import Path
import bpy
from mathutils import Vector
folder=Path(__file__).resolve().parents[1]/'outputs/installation-concrete-rings'
bpy.ops.wm.open_mainfile(filepath=str(folder/'wistr-installation.blend'))
scene=bpy.context.scene
for c in bpy.data.collections:
    if c.name.startswith('Annotations.'):c.hide_render=True
root=bpy.data.objects['building.equipment_access']
cam=bpy.data.objects['View.Equipment'];scene.camera=cam
cam.location=root.matrix_world @ Vector((31,-12,10))
target=root.matrix_world @ Vector((17,0,3.0))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=19
scene.render.resolution_x=1100;scene.render.resolution_y=900
scene.render.resolution_percentage=100;scene.cycles.samples=16
scene.render.filepath=str(folder/'wistr-access-detail-draft.png')
bpy.ops.render.render(write_still=True)
