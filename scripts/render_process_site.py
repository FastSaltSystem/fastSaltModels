"""Refresh site and attached-process views from the current composed scene."""
from pathlib import Path
import sys,bpy,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
from build_site import select
from textual_graphics.static_scene import SceneBuilder
out=ROOT/'outputs/site-45-bends'
bpy.ops.wm.open_mainfile(filepath=str(out/'fast-salt-site.blend'))
b=SceneBuilder();b.collections={c.name:c for c in bpy.data.collections}
# Recheck the saved scene using the current checker before refreshing previews.
import wistr_site as site, wistr_installation as installation
from textual_graphics.site_process_buildings import check_process_annexes
report=json.loads((out/'site-report.json').read_text())
report['process_annexes']['checks']=check_process_annexes(b,site,installation,report['process_annexes'])
(out/'site-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PROCESS_CHECKS '+json.dumps(report['process_annexes']['checks']),flush=True)
cams={key:bpy.data.objects[name] for key,name in [('overview','Site overview'),('plan','Site plan'),('alignment','Aligned reactor and power plant'),('turbine','Turbine equipment draft'),('process','Attached process buildings'),('process-plan','Process buildings plan')]}
s=bpy.context.scene;s.cycles.samples=16;s.render.resolution_x=1800;s.render.resolution_y=1100;s.render.resolution_percentage=100
for view in ('overview','plan','alignment','process','process-plan'):
    select(b,cams,view);s.render.filepath=str(out/f'site-{view}-draft.png');bpy.ops.render.render(write_still=True)
# Dedicated close-up of the two distinct fuel lines in the shared duct.
select(b,cams,'process')
from build_wistr import camera
from render_pms import text_on_camera
cam=camera(b,'Fuel supply and return duct',(6,23.5,35),(6,23.5,-5.1),20)
col=b.collection('Fuel duct close-up annotations')
text_on_camera('Fuel duct title','PAIRED FUEL IN / OUT',-8.5,4.8,.42,cam,col)
text_on_camera('Fuel duct detail','Silver jacket: two heat-traced tubes inside common insulation',-8.5,4.15,.24,cam,col,'#526575')
text_on_camera('Fuel duct footer','Insulated building connections; reactor ends continue to valve box and storage',-8.5,-4.8,.22,cam,col,'#526575')
b.collections['Site annotations.process'].hide_render=True
b.collections['Site annotations.process'].hide_viewport=True
cam.rotation_euler=(0,0,0)
inspection_hidden=[]
for ob in bpy.data.objects:
    if ob.type in ('MESH','CURVE') and not ob.name.startswith(('site.process_services.','site.salt_distribution.','site.shared_service_link.','site.fuel_preparation.')):
        inspection_hidden.append((ob,ob.hide_render));ob.hide_render=True
s.camera=cam;s.render.filepath=str(out/'site-fuel-duct-draft.png');bpy.ops.render.render(write_still=True)
for ob,hidden in inspection_hidden:ob.hide_render=hidden
col.hide_render=col.hide_viewport=True
select(b,cams,'process')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'fast-salt-site.blend'))
print('PROCESS_SITE_VIEWS_OK',flush=True)
