"""Refresh the full-height stair camera without rebuilding installation geometry."""
from pathlib import Path
from types import SimpleNamespace
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from build_wistr import select_view
out=ROOT/'outputs/installation-under-cover-bundles'
bpy.ops.wm.open_mainfile(filepath=str(out/'wistr-installation.blend'))
b=SimpleNamespace(collections={c.name:c for c in bpy.data.collections})
cameras={k:bpy.data.objects[v] for k,v in [('stairs','View.Stairs'),('catwalk','View.Catwalk'),('fuel-services','View.FuelServices'),('plan','View.Plan'),('equipment','View.Equipment'),('cutaway','View.Cutaway')]}
cam=cameras['stairs'];cam.location=(-27,-30,17)
cam.rotation_euler=(Vector((-3,-2,-3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=36
select_view(b,cameras,'stairs')
scene=bpy.context.scene;scene.cycles.samples=16;scene.render.resolution_percentage=50
scene.render.filepath=str(out/'wistr-stairs-draft.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'wistr-installation.blend'))
print('STAIR_VIEW_OK')
