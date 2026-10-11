"""Build a separate rigid-block comparison. Does not modify the wool study."""
import sys,math,json,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'models'),str(ROOT/'src'),str(ROOT/'scripts')]
import wistr_rigid_cover as cfg
from rigid_cover_screening import network,solve
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.perforated import perforated_prism,inside_polygon
from textual_graphics.reactor_insulation_cover import materials,pickup,keyed_plate,ceramic_seat
from textual_graphics.reactor_lifting import build_two_bar_head,check_common_head
from textual_graphics.reactor_checks import closed_mesh
from render_pms import text_on_camera
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
b=SceneBuilder();materials(b)
b.material('calcium','#E8DFC3',roughness=.9);b.material('calcium_alt','#CDBF9D',roughness=.9)
b.material('tension','#427C85',metallic=.65,roughness=.35)
root=b.assembly('rigid.cassette','Rigid cassette')
frame=b.assembly('rigid.frame','Upper load frame');frame.parent=root
body=b.assembly('rigid.blocks','Calcium silicate blocks');body.parent=root
tray=b.assembly('rigid.tray','Suspended bottom tray');tray.parent=root
shell=b.assembly('rigid.shell','Exterior skins');shell.parent=root
fixed=b.assembly('fixed.seats','Fixed ceramic seats')
c=cfg.COVER;poly=cfg.outline();nodes,edges,rowids,hooknodes,seatnodes=network(cfg)

def rhs(name,parent,a,d,h,w,t,mat='hot_frame'):
    # Closed walls of an open-ended rectangular hollow section, along local X.
    L=math.dist(a,d);verts=[]
    outer=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
    inner=[(-w/2+t,-h/2+t),(w/2-t,-h/2+t),(w/2-t,h/2-t),(-w/2+t,h/2-t)]
    for x in (-L/2,L/2):verts += [(x,y,z) for y,z in outer+inner]
    faces=[]
    for i in range(4):
        j=(i+1)%4
        faces += [(i,j,j+8,i+8),(i+4,i+12,j+12,j+4),(i,i+4,j+4,j),(i+8,j+8,j+12,i+12)]
    ob=b.mesh(name,parent,verts,faces,mat,tuple((a[i]+d[i])/2 for i in range(3)))
    ob.rotation_euler=(Vector(d)-Vector(a)).to_track_quat('X','Z').to_euler();return ob

z=c['frame_bottom']+cfg.RHS['height']/2
for n,(i,j,kind) in enumerate(edges):
    a=(*nodes[i],z);d=(*nodes[j],z)
    rhs(f'beam_{n}',frame,a,d,cfg.RHS['height'],cfg.RHS['width'],cfg.RHS['wall'])
# Block envelopes have physical horizontal joints; no strength credit across joints.
def clip(poly,axis,limit,above):
    out=[]
    for a,d in zip(poly,poly[1:]+poly[:1]):
        ina=(a[axis]>=limit) if above else (a[axis]<=limit);ind=(d[axis]>=limit) if above else (d[axis]<=limit)
        if ina:out.append(a)
        if ina!=ind:
            t=(limit-a[axis])/(d[axis]-a[axis]);out.append(tuple(a[k]+t*(d[k]-a[k]) for k in range(2)))
    return out
block_holes=[(x,side*max(0.,cfg.halfwidth(x)-.080),.008) for x in cfg.hanger_rows() for side in (-1,0,1)]+[(x,y,.033) for x,y in cfg.supports()]
liner_holes=[(x,y,.0035 if r==.008 else r) for x,y,r in block_holes]
count=0
for layer in range(5):
    for ix in range(-1,8):
        for iy in range(-8,8):
            x=ix*.60+(layer%2)*.30;y=iy*.30+(layer%2)*.15
            p=poly
            for axis,value,above in [(0,x+.00025,True),(0,x+.59975,False),(1,y+.00025,True),(1,y+.29975,False)]:
                if p:p=clip(p,axis,value,above)
            area=abs(sum(a[0]*d[1]-d[0]*a[1] for a,d in zip(p,p[1:]+p[:1])))/2 if p else 0
            if area<.0002:continue
            holes=[(hx,hy,r) for hx,hy,r in block_holes if x-r<=hx<=x+.60+r and y-r<=hy<=y+.30+r]
            ob=perforated_prism(b,f'block_{layer}_{ix}_{iy}',body,p,holes,layer*.100,(layer+1)*.100,'calcium' if (ix+iy+layer)%2 else 'calcium_alt')
            ob['layer']=layer;count+=1
# A full liner catches fragments. Broad underside channels spread load.
perforated_prism(b,'liner',tray,poly,liner_holes,-c['liner'],0,'stainless')
rods=[]
for n,x in enumerate(cfg.hanger_rows()):
    width=min(x/math.sqrt(3)-.018, math.sqrt(max(0.,(c['radius']-.018)**2-x*x)))
    strip=clip(clip(poly,0,x-.050,True),0,x+.050,False)
    nearby=[(hx,hy,r) for hx,hy,r in liner_holes if abs(hx-x)<.05+r]
    plate=perforated_prism(b,f'channel_{n}_top',tray,strip,nearby,-.0035,-.0015,'stainless')
    for sign in (-1,1):
        xx=x+sign*.049;span=min(xx/math.sqrt(3)-.010,math.sqrt(max(0.,(c['radius']-.010)**2-xx*xx)))
        b.box(f'channel_{n}_web_{sign}',tray,(.002,2*span,.060),(xx,0,-.0335),'stainless')
    for side in (-1,0,1):
        y=side*max(0.,cfg.halfwidth(x)-.080)
        rod=b.beam(f'tie_{n}_{side}',tray,(x,y,-.017),(x,y,c['frame_bottom']+.025),cfg.HANGER_DIAMETER/2,'tension');rod['role']='tray_tension_rod';rods.append((x,y))
        b.cylinder(f'tie_bottom_plate_{n}_{side}',tray,.025,.005,(x,y,-.006),'stainless',bevel=0)
        b.cylinder(f'tie_nut_{n}_{side}',tray,.007,.008,(x,y,-.0125),'links',vertices=6,bevel=0)
        if side:
            b.box(f'tie_bracket_{n}_{side}',frame,(.05,.13,.008),(x,side*(cfg.halfwidth(x)-.040),c['frame_bottom']+.004),'hot_frame')
        b.cylinder(f'tie_top_nut_{n}_{side}',frame,.007,.012,(x,y,c['frame_bottom']+(.014 if side else .009)),'links',vertices=6,bevel=0)
# Continuous rim retains the bottom tray edge; no intermediate wool grids.
b.annulus('tray_rim',tray,c['radius']-.018,c['radius']-.016,-.060,0,'stainless',start=-29.8,end=29.8)
for sign in (-1,1):
    p1=poly[0];p2=poly[1 if sign<0 else -1];L=math.dist(p1,p2)
    ob=b.box(f'tray_edge_{sign}',tray,(L,.002,.06),((p1[0]+p2[0])/2,(p1[1]+p2[1])/2,-.030),'stainless');ob.rotation_euler.z=math.atan2(p2[1]-p1[1],p2[0]-p1[0])
# Four posts give the same load-bearing upper frame a resting path.
for n,(x,y) in enumerate(cfg.supports()):
    rhs(f'post_{n}',frame,(x,y,c['zirconia_top']+.01),(x,y,c['frame_bottom']),.04,.04,.002)
    b.box(f'post_foot_{n}',frame,(.07,.07,.010),(x,y,c['zirconia_top']+.005),'hot_frame')
    ceramic_seat(b,fixed,c,x,y,n)
sliders=[];hooks=[]
for n,(x,y,station) in enumerate(cfg.points()):
    # Passages through the upper box crossbeam plus a bearing plate beneath.
    for ob in list(frame.children):
        if ob.type!='MESH' or not ob.name.startswith('rigid.frame.beam_'):continue
        idx=int(ob.name.rsplit('_',1)[1]);i,j,_=edges[idx]
        if abs(nodes[i][0]-x)<1e-7 and abs(nodes[j][0]-x)<1e-7 and min(nodes[i][1],nodes[j][1])-.001<=y<=max(nodes[i][1],nodes[j][1])+.001:
            cutter=b.box('stem_slot',frame,(.05,.05,.30),(x,y,z),None);b.cut(ob,cutter)
    keyed_plate(b,f'pickup_bearing_{n}',frame,x,y,c['frame_bottom'],c['frame_bottom']+.012,.18,.16,.05,'hot_frame')
    slider,hook,guide=pickup(b,cfg,root,n,x,y,station,'Sliding pickups');sliders.append(slider);hooks.append(hook)
    for side in (-1,1):b.box(f'guide_tab_{n}_{side}',shell,(.015,.080,.012),(x+side*.045,y+.065,.781),'cold_frame')
    b.box(f'guide_rail_{n}',shell,(.16,.06,.020),(x,y+.115,.770),'cold_frame')
    b.tube(f'skin_tie_{n}',shell,[(x,y+.115,.770),(x+.20,y+.115,.747),(x+.20,y+.20,.730),(x,y+.20,.725)],.003,'cold_frame')
perforated_prism(b,'top_skin',shell,poly,[(x,y,.030) for x,y,_ in cfg.points()],.760,.761,'stainless')
b.annulus('outer_skirt',shell,c['radius']+.001,c['radius']+.002,.075,.761,'stainless',start=-29.90,end=29.90)
for sign in (-1,1):
    p1=poly[0];p2=poly[1 if sign<0 else -1];L=math.dist(p1,p2)
    ob=b.box(f'skirt_{sign}',shell,(L,.001,.686),((p1[0]+p2[0])/2,(p1[1]+p2[1])/2,.418),'stainless');ob.rotation_euler.z=math.atan2(p2[1]-p1[1],p2[0]-p1[0])
owner=b.assembly('tool.owner','Remote lifting tools')
head=build_two_bar_head(b,cfg.reactor,{},owner,'rigid.tool','cap',c['hook_foot']+c['travel'])
head.driver_remove('location',2);head.rotation_euler.z=0
head.location=(2*c['radius']/math.pi-sum(cfg.reactor.LIFTING_INTERFACE['stations'])/2,0,0)
# Review the loaded configuration; fixed seats are independently visible.
for slider in sliders:slider.location.z=c['travel']
bpy.context.view_layer.update()
obstacles=[o for o in shell.children if o.type=='MESH']+[o for o in bpy.data.objects if '.guide_' in o.name and o.type=='MESH']
check_common_head(head,hooks,cfg.reactor,obstacles)
for slider in sliders:slider.location.z=0
head.location.z=-c['travel'];bpy.context.view_layer.update();check_common_head(head,hooks,cfg.reactor,obstacles)
for slider in sliders:slider.location.z=c['travel']
head.location.z=0;bpy.context.view_layer.update()
closed_count=0
for ob in bpy.data.objects:
    if ob.type=='MESH':closed_mesh(ob);closed_count+=1
# Additive evaluated volume: include every cassette part; exclude fixed seats/tool.
inv=root.matrix_world.inverted()

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

def belongs(ob):
    while ob:
        if ob==root:return True
        ob=ob.parent
    return False
items=[];groups={}
for ob in bpy.data.objects:
    if ob.type not in ('MESH','CURVE') or not belongs(ob):continue
    volume,centre=volume_centroid(ob);material=ob.data.materials[0].name
    density=240 if material.startswith('calcium') else 7850 if material in ('hot_frame','links') else 8000
    group='Rigid insulation' if density==240 else 'Steel and hardware';mass=volume*density
    groups[group]=groups.get(group,0)+mass;items.append(dict(name=ob.name,mass_kg=mass,volume_m3=volume,centre_m=centre,density_kg_m3=density))
mass=sum(i['mass_kg'] for i in items);cm=[sum(i['mass_kg']*i['centre_m'][axis] for i in items)/mass for axis in range(3)]
assert inside_polygon(tuple(cm[:2]),sorted([(x,y) for x,y,_ in cfg.points()],key=lambda p:math.atan2(p[1],p[0]-2*c['radius']/math.pi)))
screening=solve(cfg,mass)
# Strip screening below the liner, independently from the upper-frame grillage.
w=cfg.TRAY['width'];t=cfg.TRAY['wall'];h=cfg.TRAY['depth'];A1=w*t;A2=t*h;zc=(A1*(-t/2)+2*A2*(-t-h/2))/(A1+2*A2)
Ic=w*t**3/12+A1*(-t/2-zc)**2+2*(t*h**3/12+A2*(-t-h/2-zc)**2)
span=max(cfg.halfwidth(x)-.080 for x in cfg.hanger_rows());pressure=c['density']*9.80665*c['insulation'];line_load=(pressure+8000*9.80665*c['liner'])*cfg.TRAY['pitch']+(A1+2*A2)*8000*9.80665
tray_screen={'max_half_span_m':span,'I_m4':Ic,'line_load_N_m':line_load,'deflection_mm':5*line_load*span**4/(384*cfg.E*Ic)*1000,'bending_stress_MPa':line_load*span**2/8*max(abs(zc),abs(-t-h-zc))/Ic/1e6}
max_rod_force=line_load*span # approximate central rod reaction from two simple half-spans
tray_screen.update({'max_rod_load_N':max_rod_force,'rod_axial_stress_MPa':max_rod_force/(math.pi*cfg.HANGER_DIAMETER**2/4)/1e6,'rod_extension_mm':max_rod_force*.59/(cfg.E*math.pi*cfg.HANGER_DIAMETER**2/4)*1000})
clear=cfg.TRAY['pitch']-cfg.TRAY['width'];Isheet=c['liner']**3/12
tray_screen['liner_strip_deflection_mm']=5*pressure*clear**4/(384*cfg.E*Isheet)*1000
out=ROOT/'outputs/reactor-rigid-cover';out.mkdir(parents=True,exist_ok=True)
report=dict(scope=cfg.SCOPE,mass_kg=mass,groups_kg=groups,cm_local_m=cm,head_offset_m=2*c['radius']/math.pi-cm[0],block_count=count,tension_rods=len(rods),closed_meshes=closed_count,
    geometric_checks=['All mesh parts closed','Four-hook footprint surrounds estimated CM','Common head docking, capture and release checked at both stem endpoints'],
    screening=screening,tray_screening=tray_screen,items=items,
    limitations=['Additive component volumes double count member intersections; rod/post clearances are cut in insulation and liner. Fasteners and details incomplete.',
                 'Block joints and thin retaining liner give no structural composite action in the calculation.',
                 'The 500 mm insulation thickness is retained; complete bridge/surface-temperature analysis has not been performed.',
                 'Grillage uses area-distributed total mass and fixed-elevation supports, not a flexible crane head or actual seat compliance.',
                 'Steel properties provisional; no local buckling, slot reinforcement, weld, fatigue, or hot-strength assessment.'],
    source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'models/wistr_rigid_cover.py',ROOT/'scripts/rigid_cover_screening.py']})
(out/'rigid-cover-report.json').write_text(json.dumps(report,indent=2)+'\n')
# Studio and review views.
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Rigid studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.85,.9,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
scene.view_settings.view_transform='AgX'
for name,pos,power in [('Key',(0,-6,8),1600),('Fill',(7,5,8),1500)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=6;ob=bpy.data.objects.new(name,data);b.collection('Presentation').objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((2,0,.3))-ob.location).to_track_quat('-Z','Y').to_euler()
cameras={}
def camera(name,pos,target,scale,title,subtitle,foot):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);b.collection('Presentation').objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale
    col=b.collection('Labels.'+name);height=scale*1100/1600
    for key,txt,yy,sz in [('title',title,.44,.025),('subtitle',subtitle,.385,.014),('foot',foot,-.45,.013)]:text_on_camera(name+key,txt,-.465*scale,yy*height,sz*scale,ob,col)
    cameras[name]=ob;return ob
camera('assembly',(7,-9,6),(2,0,.65),6.7,'WISTR | Rigid-block insulation cassette','500 mm calcium silicate / stainless enclosure / existing four sliding hooks','Alternative study: same footprint. Upper frame raises the cover top by 240 mm compared with the wool draft.')
camera('frame',(6,-8,5),(2.05,0,.30),6.3,'WISTR | A frame reaching the apex and rim',f'160 x 60 x 3 mm upper box members / {len(rods)} slender tray ties / no intermediate grids',f'Gross-section screening at estimated dead weight: lifted apex {screening["lifted"]["apex_deflection_mm"]:.1f} mm; not a qualified lifting design.')
camera('cutaway',(6,-8,5),(2.05,0,.30),6.3,'WISTR | Rigid blocks bear directly on one another','Staggered layers / one broad-strip bottom tray / distributed tension rods',f'Additive estimate {mass/1000:.2f} t: {groups["Rigid insulation"]:.0f} kg insulation + {groups["Steel and hardware"]:.0f} kg steel/hardware.')
# A display copy of the block pack exposes front rods and bottom supports.
review=b.assembly('review.blocks','Cutaway blocks')
for ob in list(body.children):
    cp=ob.copy();cp.data=ob.data.copy();b.collection('Cutaway blocks').objects.link(cp);cp.parent=review;cp.name='review.'+ob.name
    edge=.10+.15*ob['layer'];cut=b.box('display_cut',review,(12,10+edge,3),(0,(edge-10)/2,.5),None);b.cut(cp,cut)
for view in ('assembly','frame','cutaway'):
    for name,col in b.collections.items():
        col.hide_render=name.startswith('Labels.') and name!='Labels.'+view
    b.collection('Remote lifting tools').hide_render=True
    b.collection('Cutaway blocks').hide_render=view!='cutaway'
    b.collection('Calcium silicate blocks').hide_render=view!='assembly'
    b.collection('Exterior skins').hide_render=view!='assembly'
    scene.camera=cameras[view];scene.render.filepath=str(out/f'rigid-cover-{view}.png');bpy.ops.render.render(write_still=True)
# Full geometry stays editable; opening view hides only enclosing skins.
for name,col in b.collections.items():
    col.hide_viewport=name in ('Cutaway blocks','Exterior skins','Remote lifting tools') or name.startswith('Labels.')
    col.hide_render=col.hide_viewport
scene.camera=cameras['frame'];b.collection('Calcium silicate blocks').hide_viewport=True;b.collection('Calcium silicate blocks').hide_render=True
scene['review_scope']=cfg.SCOPE;scene['mass_estimate_kg']=mass
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(out/'wistr-rigid-cover.blend'))
print(json.dumps({k:report[k] for k in ['mass_kg','groups_kg','cm_local_m','head_offset_m','tension_rods']},indent=2))
print(json.dumps({k:{p:v for p,v in screening[k].items() if p!='nodal_displacements_m'} for k in ['lifted','seated']},indent=2));print('TRAY',tray_screen)
