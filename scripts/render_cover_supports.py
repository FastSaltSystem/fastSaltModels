"""Review cutaway with wool retained, plus additive-volume CM and pickup plan.
Run after scripts/build_insulation_cover.py. Does not overwrite the main study.
"""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
import wistr_insulation_cover as cfg
from textual_graphics.static_scene import SceneBuilder
from render_pms import text_on_camera
OUT=ROOT/'outputs/reactor-insulation-cover'
source=OUT/'wistr-insulation-cover.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.frame_set(21)
root=bpy.data.objects['cover.sector_1'];inv=root.matrix_world.inverted()

def volume_centroid(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    # Local-origin double precision tetrahedral moments avoid cancellation in thin skins.
    origin=[sum(v.co[i] for v in mesh.vertices)/len(mesh.vertices) for i in range(3)]
    vertices=[tuple(float(v.co[i])-origin[i] for i in range(3)) for v in mesh.vertices]
    vs=[];ms=[[],[],[]]
    for tri in mesh.loop_triangles:
        a,b,c=[vertices[i] for i in tri.vertices]
        cr=(b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0])
        v=sum(a[i]*cr[i] for i in range(3))/6;vs.append(v)
        for i in range(3):ms[i].append(v*(a[i]+b[i]+c[i])/4)
    signed=math.fsum(vs);assert abs(signed)>1e-12,obj.name
    local=Vector(tuple(origin[i]+math.fsum(ms[i])/signed for i in range(3)))
    m=inv@ev.matrix_world;centroid=m@local;volume=abs(signed*m.to_3x3().determinant())
    ev.to_mesh_clear();return volume,tuple(centroid)

items=[];groups={}
for obj in bpy.data.objects:
    if not obj.name.startswith('cover.sector_1.') or obj.type not in ('MESH','CURVE'):continue
    volume,centre=volume_centroid(obj);material=obj.data.materials[0].name
    density=128. if material in ('wool','wool_alt','seal') else 7850. if material in ('hot_frame','links') else 8000.
    mass=volume*density
    group='Wool and seam filler' if material in ('wool','wool_alt','seal') else 'Steel and hardware'
    groups[group]=groups.get(group,0)+mass
    items.append(dict(name=obj.name,volume_m3=volume,density_kg_m3=density,mass_kg=mass,centre_local_m=centre,group=group))
mass=math.fsum(i['mass_kg'] for i in items)
cm=tuple(math.fsum(i['mass_kg']*i['centre_local_m'][j] for i in items)/mass for j in range(3))
points=cfg.points();xs=sorted(set(p[0] for p in points));nominal=sum(xs)/2
polygon=sorted([(x,y) for x,y,_ in points],key=lambda p:math.atan2(p[1],p[0]-nominal))
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
assert all(cross(a,b,cm)>0 for a,b in zip(polygon,polygon[1:]+polygon[:1]))
margin=min(cross(a,b,cm)/math.dist(a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1]))
reaction_outer=(cm[0]-xs[0])/(xs[1]-xs[0])
# Independent envelope checks use polygon area and authored plate thickness.
outline=cfg.outline()
area=abs(math.fsum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline,outline[1:]+outline[:1])))/2
liner=next(i for i in items if i['name'].endswith('.shell.hot_face_liner'))
assert math.isclose(liner['volume_m3'],(area-sum(8*r*r*math.sin(math.pi/8) for x,y,r in cfg.wool_holes()[4:]))*cfg.COVER['liner'],rel_tol=2e-5)
wool_volume=math.fsum(i['volume_m3'] for i in items if '.wool_layer_' in i['name'])
# Booleans use regular 16-sided hole profiles rather than exact circles.
hole_area=sum(16*r*r*math.sin(2*math.pi/16)/2 for x,y,r in cfg.wool_holes())
assert math.isclose(wool_volume,(area-hole_area)*cfg.COVER['insulation'],rel_tol=2e-5)
assert abs(sum((1-reaction_outer,reaction_outer))-1)<1e-12 and 0<reaction_outer<1
report=dict(scope='Preliminary additive component-volume mass estimate; not a certified assembly mass or lift rating.',
    density_basis={'wool_and_seal':128,'stainless_and_outer_parts':8000,'inner_frame_and_pickup_steel':7850},
    mass_kg=mass,groups_kg=groups,cm_local_m=cm,uniform_wedge_centroid_m=nominal,hook_rows_m=xs,
    head_offset_from_cm_m=nominal-cm[0],support_polygon_m=polygon,cm_inside_pickup_polygon=True,
    minimum_plan_margin_m=margin,ideal_row_reaction_fractions={'inner':1-reaction_outer,'outer':reaction_outer},
    limitations=['Component volumes are summed, not Boolean-unioned; intersecting rods and steel inside wool are double counted.',
                'Wool is assigned to geometric envelopes; voids already modeled are subtracted. Missing connections, fasteners, sleeves and finished joints are excluded.',
                'Densities are provisional. Only sector 1 includes all modeled grids; it is used as the representative cassette.',
                'Crane head is excluded from cassette mass. The complete suspended assembly balance and four-point load sharing are not solved.',
                'Row reactions assume a level cassette with vertical support forces; the actual single-hoist suspension may tilt because of the CM offset.'],
    checks=['CM lies strictly inside four-pickup polygon','Liner mesh volume agrees with polygon-area times thickness','Five wool volumes agree with polygon/hole area times 500 mm','Ideal row reactions sum to unity and are positive'],items=items,source_blend_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(OUT/'cover-mass-report.json').write_text(json.dumps(report,indent=2)+'\n')

# Display copies are sectioned; the maintained whole-cassette model is unchanged.
for collection in bpy.data.collections:
    collection.hide_viewport=False;collection.hide_render=False
    if collection.name.startswith('Labels.') or collection.name in ('Catch sections','Support section','Remote lifting tools'):collection.hide_render=True
for obj in bpy.data.objects:
    obj.hide_render=obj.type in ('MESH','CURVE','FONT')
    if obj.type in ('LIGHT','CAMERA'):obj.hide_render=False
b=SceneBuilder()
for name in ('stainless','wool','wool_alt','hot_frame','cold_frame','links','indicator','dark','seal'):
    b.materials[name]=bpy.data.materials[name]
b.material('mesh_review','#425B60',metallic=.25,roughness=.5)
b.material('cm_marker','#CE3928',roughness=.35)
b.material('pickup_polygon','#187D91',roughness=.5)
b.material('plan_fill','#D7DDE0',roughness=.75)
review=b.assembly('review.cassette','Review cutaway')
# Bake all display copies in cassette-local coordinates, including moved stems.
for ob in list(bpy.data.objects):
    if not ob.name.startswith('cover.sector_1.') or ob.type not in ('MESH','CURVE'):continue
    if '.shell.' in ob.name and not ob.name.endswith('hot_face_liner'):continue
    if ob.name.endswith('compressible_seam'):continue
    cp=ob.copy();cp.data=ob.data.copy();cp.animation_data_clear()
    b.collection('Review cutaway').objects.link(cp);cp.parent=review;cp.matrix_parent_inverse.identity();cp.matrix_local=inv@ob.matrix_world
    cp.name='review.'+ob.name;cp.hide_render=False
    if '.grids.' in ob.name:cp.data.materials.clear();cp.data.materials.append(b.materials['mesh_review'])
    if '.insulation.wool_layer_' in ob.name:
        n=int(ob.name[-1]);edge=.02+.16*(n-1)
        cutter=b.box('layer_section_cutter',review,(12,10+edge,3),(0,(edge-10)/2,.5),None)
        b.cut(cp,cutter)
# Keep the hot-face liner only on the retained half to expose its underside support.
liner=bpy.data.objects['review.cover.sector_1.shell.hot_face_liner']
cutter=b.box('liner_cutter',review,(12,10,3),(0,-5,.5),None);b.cut(liner,cutter)

scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.cycles.samples=40
cameras={}
def camera(name,pos,target,scale,title,subtitle,footer):
    data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);b.collection('Review cameras').objects.link(cam)
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale
    col=b.collection('Review labels.'+name);h=scale*1100/1600
    for key,text,x,y,size in [('title',title,-scale*.465,h*.44,scale*.025),('subtitle',subtitle,-scale*.465,h*.385,scale*.015),('footer',footer,-scale*.465,-h*.45,scale*.014)]:
        text_on_camera(name+'.'+key,text,x,y,size,cam,col)
    cameras[name]=cam;return cam
cam=camera('wool-cutaway',(6.3,-8.5,5.1),(2.15,0,.25),6.2,'WISTR | How the insulation is carried',
    'Stepped cutaway: five wool layers retained at the back; grids and frame exposed at the front',
    'Wool -> separate trays -> tension hangers -> upper frame. At rest: posts -> zirconia -> fixed seats.')
col=b.collection('Review labels.wool-cutaway')
text_on_camera('wool-note','500 mm total wool; support sizes remain provisional',-2.88,-1.66,.085,cam,col)
scene.camera=cam;scene.render.filepath=str(OUT/'cover-wool-cutaway.png');bpy.ops.render.render(write_still=True)

# Plan diagram: top footprint and the actual pickup polygon, distinct from the crane axis.
b.collection('Review cutaway').hide_render=True;b.collection('Review labels.wool-cutaway').hide_render=True
plan=b.assembly('review.mass_plan','CM plan')
poly=cfg.outline();verts=[(x,y,0) for x,y in poly];b.mesh('footprint',plan,verts,[tuple(range(len(verts)))],'plan_fill')
b.tube('outline',plan,[(x,y,.005) for x,y in poly+[poly[0]]],.009,'cold_frame')
b.tube('pickup_polygon',plan,[(x,y,.02) for x,y in polygon+[polygon[0]]],.012,'pickup_polygon')
for n,(x,y,station) in enumerate(points):
    b.cylinder(f'hook_{n}',plan,.043,.025,(x,y,.035),'links',vertices=48,bevel=0)
for st,x in enumerate(xs):
    half=cfg.reactor.LIFTING_INTERFACE['bar_half_lengths'][st]
    b.beam(f'bar_line_{st}',plan,(x,-half,.028),(x,half,.028),.014,'pickup_polygon')
b.cylinder('cm',plan,.035,.03,(cm[0],cm[1],.07),'cm_marker',vertices=48,bevel=0)
# Offset leader makes the small separation readable without moving either marker.
b.tube('cm_leader',plan,[(cm[0],cm[1],.07),(cm[0]-.32,-.96,.07),(1.23,-.96,.07)],.006,'cm_marker')
b.beam('hoist_cross_x',plan,(nominal-.025,0,.07),(nominal+.025,0,.07),.004,'links')
b.beam('hoist_cross_y',plan,(nominal,-.045,.07),(nominal,.045,.07),.004,'links')
b.tube('hoist_leader',plan,[(nominal,0,.07),(nominal+.26,.92,.07),(3.80,.92,.07)],.005,'links')
cam=camera('cm-plan',(2.15,0,12),(2.15,0,0),7.6,'WISTR | Hooks surround the estimated cassette CM',
    f'Modeled cassette: {mass/1000:.2f} t | CM radius {cm[0]:.3f} m | hook rows {xs[0]:.3f} / {xs[1]:.3f} m',
    'Additive-volume estimate with provisional densities. Steel/wool overlaps and unfinished details limit accuracy.')
cam.rotation_euler=(0,0,0)
col=b.collection('Review labels.cm-plan')
for name,txt,x,y,color in [('CM',f'CM: {cm[0]:.3f} m',-1.37,-1.10,'#B82F26'),('hoist',f'Head centre: {nominal:.3f} m',.45,1.04,'#26364A'),('margin',f'CM is {nominal-cm[0]:.3f} m inward of the head axis',-2.84,-1.58,'#26364A')]:
    text_on_camera(name,txt,x,y,.105,cam,col,color)
scene.camera=cam;scene.render.filepath=str(OUT/'cover-cm-plan.png');bpy.ops.render.render(write_still=True)
# Save a separate review file opening on the actual wool cutaway.
b.collection('CM plan').hide_render=True;b.collection('CM plan').hide_viewport=True
b.collection('Review labels.cm-plan').hide_render=True;b.collection('Review labels.cm-plan').hide_viewport=True
b.collection('Review cutaway').hide_render=False;b.collection('Review labels.wool-cutaway').hide_render=False
for ob in bpy.data.objects:
    if ob.name.startswith(('cover.','reference.','detail.','support_detail')):ob.hide_set(True)
for collection in bpy.data.collections:
    if collection.name.startswith('Labels.') or collection.name in ('Catch sections','Support section'):collection.hide_viewport=True
scene.camera=cameras['wool-cutaway'];scene['review_mass_kg']=mass;scene['review_CM_local_m']=cm
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'wistr-cover-support-review.blend'))
print(json.dumps({k:report[k] for k in ('mass_kg','groups_kg','cm_local_m','head_offset_from_cm_m','minimum_plan_margin_m','ideal_row_reaction_fractions')},indent=2))
