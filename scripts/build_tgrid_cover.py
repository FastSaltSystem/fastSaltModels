"""Build the five-level suspended rigid-block cassette and review sections."""
import sys,math,json,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'models'),str(ROOT/'src'),str(ROOT/'scripts')]
import wistr_tgrid_cover as cfg
from rigid_cover_screening import network,solve
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.perforated import perforated_prism,inside_polygon
from textual_graphics.reactor_insulation_cover import materials,pickup,keyed_plate
from textual_graphics.reactor_lifting import build_two_bar_head,check_common_head
from textual_graphics.reactor_checks import closed_mesh
from render_pms import text_on_camera
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
b=SceneBuilder();materials(b)
b.material('calcium','#E8DFC3',roughness=.9);b.material('calcium_alt','#CDBF9D',roughness=.9)
b.material('tension','#427C85',metallic=.65,roughness=.35)
b.material('crimp','#B78C32',metallic=.7,roughness=.32)
b.material('facing','#D1CFC7',roughness=.85)
b.material('joint_cement','#BDAF98',roughness=.85)
root=b.assembly('rigid.cassette','Rigid cassette')
frame=b.assembly('rigid.frame','Upper load frame');frame.parent=root
body=b.assembly('rigid.blocks','Calcium silicate blocks');body.parent=root
tray=b.assembly('rigid.grid','Recessed T-grid');tray.parent=root
facing=b.assembly('rigid.facing','Bonded refractory facing');facing.parent=root
ceramics=b.assembly('rigid.ceramics','Ceramic hanger breaks');ceramics.parent=root
shell=b.assembly('rigid.shell','Exterior skins');shell.parent=root
fixed=b.assembly('reference.cap','Sector cap seating reference')
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
# Upper frame bears on broad shoes on top of the insulation.
rods=cfg.hangers();g=cfg.GRID;cer=cfg.CERAMIC
for n,(i,j,kind) in enumerate(edges):
    a=nodes[i];d=nodes[j];length=math.dist(a,d)
    shoe=b.box(f'bearing_shoe_{n}',frame,(length,.100,.003),((a[0]+d[0])/2,(a[1]+d[1])/2,c['frame_bottom']-.0015),'hot_frame')
    shoe.rotation_euler.z=math.atan2(d[1]-a[1],d[0]-a[0])
# A flat reference establishes direct seating only; actual cap fittings need reliefs.
perforated_prism(b,'seating_envelope',fixed,poly,[],-.152,-cfg.COATING['thickness'],'context')['scope']='Flat seating envelope; cap hooks, plug sockets and services not integrated'
block_holes=[(x,y,cfg.COLLAR['block_clearance']/2) for x,y in rods]
count=0;bottom_blocks=[]
xbound=[0]+cfg.hanger_rows()+[c['radius']+.01]
def band(poly,axis,lo,hi):return clip(clip(poly,axis,lo,True),axis,hi,False)
for layer in range(cfg.LAYERS):
    print('Building layer',layer+1,flush=True)
    dz=cfg.grid_offset(layer)
    bz=cfg.block_bottom(layer)
    layer_poly=poly if layer==0 else [(x*(c['radius']-.0025)/c['radius'],y*(c['radius']-.0025)/c['radius']) for x,y in poly]
    xb=xbound
    for ix,(x,xend) in enumerate(zip(xb,xb[1:])):
        for iy in range(-8,8):
            y=iy*.30+(layer%2)*.15
            gap=g['joint_width']
            p=band(band(layer_poly,0,x+gap/2,xend-gap/2),1,y+gap/2,y+.30-gap/2)
            area=abs(sum(a[0]*d[1]-d[0]*a[1] for a,d in zip(p,p[1:]+p[:1])))/2 if p else 0
            if area<.00015:continue
            holes=[(hx,hy,r) for hx,hy,r in block_holes if x-r<=hx<=xend+r and y-r<=hy<=y+.30+r]
            if layer==4:holes += [(hx,hy,.10) for hx,hy,_ in cfg.points() if x-.1<=hx<=xend+.1 and y-.1<=hy<=y+.40]
            ob=perforated_prism(b,f'block_{layer}_{ix}_{iy}',body,p,holes,bz,bz+cfg.LAYER_PITCH,'calcium' if (ix+iy+layer)%2 else 'calcium_alt')
            ob['layer']=layer;count+=1
            if layer==0:bottom_blocks.append(ob)
            if layer==0:
                # Recesses in all four block edges receive the grid flanges.
                for axis,edge in [(0,x),(0,xend),(1,y),(1,y+.30)]:
                    size=(2*g['groove_depth'],12,g['slot_top']-g['slot_bottom']) if axis==0 else (12,2*g['groove_depth'],g['slot_top']-g['slot_bottom'])
                    pos=(edge,0,dz+(g['slot_top']+g['slot_bottom'])/2) if axis==0 else (0,edge,dz+(g['slot_top']+g['slot_bottom'])/2)
                    cut=b.box('groove',body,size,pos,None);b.cut(ob,cut)
                # Peripheral rebate matches the inward-facing edge rail.
                cut=b.annulus('rim_groove',body,c['radius']-.027,c['radius']+.05,dz+g['slot_bottom'],dz+g['slot_top'],None);b.cut(ob,cut)
                for sign in (-1,1):
                    ar=sign*math.pi/6
                    cut=b.box('radial_groove',body,(10,.060,g['slot_top']-g['slot_bottom']),(2*math.cos(ar),2*math.sin(ar),dz+(g['slot_top']+g['slot_bottom'])/2),None);cut.rotation_euler.z=ar;b.cut(ob,cut)
for layer in range(cfg.LAYERS):
    print('Building layer',layer+1,flush=True)
    dz=cfg.grid_offset(layer)
    # Main transverse T-runners coincide with each layer’s block boundaries.
    for n,x in enumerate(cfg.hanger_rows()):
        p=band(poly,0,x-g['flange_width']/2,x+g['flange_width']/2)
        perforated_prism(b,f'level_{layer}_main_{n}_flange',tray,p,[(hx,hy,cfg.COLLAR['web_clearance']/2) for hx,hy in rods if abs(hx-x)<1e-8],dz+g['flange_bottom'],dz+g['slot_top'],'stainless')['role']='T_flange'
        p=band(poly,0,x-g['web_thickness']/2,x+g['web_thickness']/2)
        perforated_prism(b,f'level_{layer}_main_{n}_web',tray,p,[(hx,hy,cfg.COLLAR['web_clearance']/2) for hx,hy in rods if abs(hx-x)<1e-8],dz+g['slot_top'],dz+g['slot_top']+g['web_height'],'stainless')
    # Cross-tees are segmented between runners, allowing grid assembly around blocks.
    for ix,(x0,x1) in enumerate(zip(xbound,xbound[1:])):
        for iy in range(-7,8):
            y=iy*.30+(layer%2)*.15;p=band(band(poly,0,x0+.001,x1-.001),1,y-.025,y+.025)
            if len(p)<3:continue
            ob=perforated_prism(b,f'level_{layer}_cross_{ix}_{iy}_flange',tray,p,[(hx,hy,.007) for hx,hy in rods if x0-.007<=hx<=x1+.007 and abs(hy-y)<.032],dz+g['flange_bottom'],dz+g['slot_top'],'stainless');ob['role']='T_flange'
            p=band(band(poly,0,x0+.001,x1-.001),1,y-.001,y+.001)
            if len(p)>2:perforated_prism(b,f'level_{layer}_cross_{ix}_{iy}_web',tray,p,[(hx,hy,.007) for hx,hy in rods if x0-.007<=hx<=x1+.007 and abs(hy-y)<.008],dz+g['slot_top'],dz+g['slot_top']+.030,'stainless')
    # Continuous inward flange and edge web retain trimmed peripheral pieces.
    b.annulus(f'level_{layer}_rim_flange',tray,c['radius']-.025,c['radius'],dz+g['flange_bottom'],dz+g['slot_top'],'stainless',start=-29.9,end=29.9)
    b.annulus(f'level_{layer}_rim_web',tray,c['radius']-.002,c['radius'],dz+g['slot_top'],dz+g['slot_top']+.030,'stainless',start=-29.9,end=29.9)
    for sign in (-1,1):
        ar=sign*math.pi/6;length=c['radius']-.025
        for name,w,z0,z1,offset in [('flange',.025,dz+g['flange_bottom'],dz+g['slot_top'],.0125),('web',.002,dz+g['slot_top'],dz+g['slot_top']+.030,.001)]:
            # Position inward from the wedge's seam line; complete mating detail provisional.
            obj=b.box(f'level_{layer}_edge_{name}_{sign}',tray,(length,w,z1-z0),(length/2*math.cos(ar)+.02+offset*.5,length/2*math.sin(ar)-sign*offset*math.cos(ar),(z0+z1)/2),'stainless');obj.rotation_euler.z=ar
# Sliding saddles bridge local web notches; individual crimp stops carry each level. Through-frame ceramic sleeves prevent
# steel-side contact, and upper annular washers interrupt the axial nut load path.
for n,(x,y) in enumerate(rods):
    beamtop=c['frame_bottom']+cfg.RHS['height'];plate_top=beamtop+cer['washer_height']+.003
    rod=b.beam(f'tie_{n}',tray,(x,y,.072),(x,y,plate_top+.018),cfg.HANGER_DIAMETER/2,'tension');rod['role']='grid_tension_rod'
    for layer in range(cfg.LAYERS):
        dz=cfg.grid_offset(layer)
        saddle=perforated_prism(b,f'level_{layer}_saddle_{n}',tray,
            [(x-.006,y-.015),(x+.006,y-.015),(x+.006,y+.015),(x-.006,y+.015)],
            [(x,y,cfg.COLLAR['saddle_bore']/2)],dz+.088,dz+.096,'stainless')
        saddle['role']='sliding_grid_saddle';saddle['layer']=layer
        collar=b.annulus(f'level_{layer}_crimp_{n}',tray,cfg.COLLAR['inner']/2,cfg.COLLAR['outer']/2,
            dz+.078,dz+.088,'crimp',steps=24)
        collar.location.x=x;collar.location.y=y;collar['role']='provisional_crimp_stop';collar['layer']=layer

    # Bore every intersected structural part using observed local bounds.
    for ob in list(frame.children):
        if ob.type!='MESH':continue
        invm=ob.matrix_local.inverted();p=invm@Vector((x,y,(c['frame_bottom']+beamtop)/2))
        # Check planar containment using local mesh limits, independent of Z.
        xx=[v.co.x for v in ob.data.vertices];yy=[v.co.y for v in ob.data.vertices]
        if not xx or not(min(xx)-.009<=p.x<=max(xx)+.009 and min(yy)-.009<=p.y<=max(yy)+.009):continue
        cutter=b.cylinder('hanger_bore',frame,cer['frame_hole']/2,.25,(x,y,c['frame_bottom']+.08),None,vertices=24,bevel=0);b.cut(ob,cutter)
    sleeve=b.annulus(f'sleeve_{n}',ceramics,cer['sleeve_inner']/2,cer['sleeve_outer']/2,c['frame_bottom']-.004,beamtop+cer['washer_height'],'zirconia',steps=32);sleeve.location.x=x;sleeve.location.y=y
    washer=b.annulus(f'washer_{n}',ceramics,cer['washer_inner']/2,cer['washer_outer']/2,beamtop,beamtop+cer['washer_height'],'zirconia',steps=48);washer.location.x=x;washer.location.y=y;washer['role']='ceramic_load_washer'
    spread=b.annulus(f'spreader_{n}',tray,.004,.016,beamtop+cer['washer_height'],plate_top,'stainless',steps=32);spread.location.x=x;spread.location.y=y
    nut=b.annulus(f'nut_{n}',tray,.003,.007,plate_top,plate_top+.010,'links',steps=6);nut.location.x=x;nut.location.y=y
# The bonded layer is an assumed protective facing, not a lifting diaphragm.
perforated_prism(b,'underside_coating',facing,poly,[],-cfg.COATING['thickness'],0,'facing')['role']='assumed_bonded_facing'
# Thin joint cement below the recessed flange joins the bottom block edges.
for axis,vals in [(0,cfg.hanger_rows()),(1,[i*.3 for i in range(-7,8)])]:
    for n,value in enumerate(vals):
        p=band(poly,axis,value-.002,value+.002)
        if len(p)>2:perforated_prism(b,f'joint_{axis}_{n}',facing,p,[],0,g['slot_bottom'],'joint_cement')
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
    for side in (-1,1):b.box(f'guide_tab_{n}_{side}',shell,(.015,.080,.012),(x+side*.045,y+.065,c['guide_bottom']+.006),'cold_frame')
    b.box(f'guide_rail_{n}',shell,(.16,.06,.020),(x,y+.115,c['frame_bottom']+.205),'cold_frame')
    b.tube(f'skin_tie_{n}',shell,[(x,y+.115,c['frame_bottom']+.205),(x+.20,y+.115,c['frame_bottom']+.182),(x+.20,y+.20,c['frame_bottom']+.165),(x,y+.20,c['frame_bottom']+.160)],.003,'cold_frame')
perforated_prism(b,'top_skin',shell,poly,[(x,y,.030) for x,y,_ in cfg.points()],c['frame_bottom']+.195,c['frame_bottom']+.196,'stainless')
b.annulus('outer_skirt',shell,c['radius']+.001,c['radius']+.002,.075,c['frame_bottom']+.196,'stainless',start=-29.90,end=29.90)
for sign in (-1,1):
    p1=poly[0];p2=poly[1 if sign<0 else -1];L=math.dist(p1,p2)
    ob=b.box(f'skirt_{sign}',shell,(L,.001,.624+cfg.STACK_RISE),((p1[0]+p2[0])/2,(p1[1]+p2[1])/2,.387+cfg.STACK_RISE/2),'stainless');ob.rotation_euler.z=math.atan2(p2[1]-p1[1],p2[0]-p1[0])
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
print('Checking model geometry',flush=True)
# New load-path geometry checks, independent of the older four-post concept.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
def tree(ob):
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons])
frame_trees=[(ob.name,tree(ob)) for ob in frame.children if ob.type=='MESH']
for ob in tray.children:
    if ob.get('role')=='grid_tension_rod':
        tr=tree(ob)
        assert not any(tr.overlap(ft) for name,ft in frame_trees),('Steel bypass at hanger',ob.name)
assert len([o for o in tray.children if o.get('role')=='provisional_crimp_stop'])==len(rods)*cfg.LAYERS
assert len([o for o in tray.children if o.get('role')=='sliding_grid_saddle'])==len(rods)*cfg.LAYERS
assert len([o for o in ceramics.children if o.get('role')=='ceramic_load_washer'])==len(rods)
assert all(not o.name.startswith(('rigid.frame.post','rigid.tray.liner')) for o in bpy.data.objects)
assert cer['sleeve_inner']>cfg.HANGER_DIAMETER and cer['frame_hole']>cer['sleeve_outer']
assert math.isclose(g['slot_top'],g['flange_bottom']+g['flange_thickness'],abs_tol=1e-10)
for layer in range(1,cfg.LAYERS):
    assert math.isclose(cfg.grid_offset(layer)+g['slot_top'],cfg.block_bottom(layer),abs_tol=1e-10)
    assert math.isclose(cfg.grid_offset(layer)+g['flange_bottom'],cfg.block_bottom(layer-1)+cfg.LAYER_PITCH,abs_tol=1e-10)
assert g['slot_bottom']>0 and g['groove_depth']>g['flange_width']/2
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
    density=240 if material.startswith('calcium') else cer['density'] if material=='zirconia' else cfg.COATING['density'] if material in ('facing','joint_cement') else 7850 if material in ('hot_frame','links') else 8000
    group='Rigid insulation' if density==240 else 'Ceramic breaks' if material=='zirconia' else 'Facing and joint cement' if material in ('facing','joint_cement') else 'Steel and hardware';mass=volume*density
    groups[group]=groups.get(group,0)+mass;items.append(dict(name=ob.name,mass_kg=mass,volume_m3=volume,centre_m=centre,density_kg_m3=density))
mass=sum(i['mass_kg'] for i in items);cm=[sum(i['mass_kg']*i['centre_m'][axis] for i in items)/mass for axis in range(3)]
assert inside_polygon(tuple(cm[:2]),sorted([(x,y) for x,y,_ in cfg.points()],key=lambda p:math.atan2(p[1],p[0]-2*c['radius']/math.pi)))
screening=solve(cfg,mass,lift_only=True)
# Simply-supported T-runner screening; no block or coating stiffness credit.
fw=g['flange_width'];ft=g['flange_thickness'];wh=g['web_height'];wt=g['web_thickness']
a1=fw*ft;a2=wh*wt;centroid=(a1*ft/2+a2*(ft+wh/2))/(a1+a2)
I=fw*ft**3/12+a1*(ft/2-centroid)**2+wt*wh**3/12+a2*(ft+wh/2-centroid)**2
maxspan=max(max(ys[i+1]-ys[i] for i in range(len(ys)-1)) for x in cfg.hanger_rows() if len(ys:=sorted(y for xx,y in rods if xx==x))>1)
area=math.pi*c['radius']**2/6
layer_masses=[]
for layer in range(cfg.LAYERS):
    block_mass=sum(i['mass_kg'] for i in items if i['name'].startswith(f'rigid.blocks.block_{layer}_'))
    grid_mass=sum(i['mass_kg'] for i in items if i['name'].startswith(f'rigid.grid.level_{layer}_'))
    facing_mass=groups['Facing and joint cement'] if layer==0 else 0
    layer_masses.append(dict(layer=layer+1,block_kg=block_mass,grid_kg=grid_mass,facing_kg=facing_mass,
        supported_kg=block_mass+grid_mass+facing_mass))
line_loads=[i['supported_kg']*9.80665/area*.6 for i in layer_masses]
line_load=max(line_loads)
# Accumulated rod load includes every grid level plus the shared rod/upper hardware.
shared_mass=sum(i['mass_kg'] for i in items if i['name'].startswith('rigid.grid.') and '.level_' not in i['name'])+groups['Ceramic breaks']
force=(sum(line_loads)+shared_mass*9.80665/area*.6)*maxspan
support_screen={'runner_span_m':maxspan,'runner_I_m4':I,'runner_line_load_N_m':line_load,
 'layer_masses':layer_masses,'layer_line_loads_N_m':line_loads,'shared_hanger_hardware_kg':shared_mass,
 'runner_deflection_mm':5*line_load*maxspan**4/(384*cfg.E*I)*1000,
 'runner_gross_stress_MPa':line_load*maxspan**2/8*max(centroid,ft+wh-centroid)/I/1e6,
 'max_single_collar_force_N':line_load*maxspan,
 'rod_force_N':force,'rod_gross_stress_MPa':force/(math.pi*cfg.HANGER_DIAMETER**2/4)/1e6,
 'ceramic_bearing_MPa':force/(math.pi*(.032**2-cer['washer_inner']**2)/4)/1e6,
 'gross_seated_pressure_kPa':mass*9.80665/area/1000}
out=ROOT/'outputs/reactor-tgrid-cover';out.mkdir(parents=True,exist_ok=True)
report=dict(scope=cfg.SCOPE,mass_kg=mass,groups_kg=groups,cm_local_m=cm,head_offset_m=2*c['radius']/math.pi-cm[0],block_count=count,tension_rods=len(rods),grid_levels=cfg.LAYERS,block_stack_top_m=cfg.block_bottom(cfg.LAYERS-1)+cfg.LAYER_PITCH,grooved_layers=[1],direct_bearing_layers=[2,3,4,5],crimp_stops=len(rods)*cfg.LAYERS,closed_meshes=closed_count,
    geometric_checks=['All mesh parts closed','Four-hook footprint surrounds estimated CM','Common head docking, capture and release checked at both stem endpoints','Every hanger rod clears all upper-frame steel meshes','One ceramic load washer per rod','Five sliding grid saddles and crimp stops per rod','No old tray or compression posts','Upper block bottoms coincide with supporting flange tops','Positive bottom-groove and sleeve clearances'],
    screening=screening,support_screening=support_screen,items=items,
    limitations=['Additive volumes double-count grid intersections; welds, cross-tee clips and final cut list remain provisional.',
                 'Coating adhesion is assumed as authorized; no block/coating composite action credited in lifting calculation.',
                 '500 mm of blocks in a 512 mm stack with four 3 mm supporting-flange interfaces. Local seated bearing beneath these strips is unresolved. Collar adjustment, crimp retention and thermal load redistribution are unresolved; complete bridge/surface-temperature analysis has not been performed.',
                 'Lifted-only grillage uses area-distributed total mass and four equal-elevation hooks. Previous four-post seated solution is inapplicable.',
                 'Local grid screen smears each layer and grid mass over gross area; collar and groove strength are not established. Steel properties provisional; no local buckling, slot reinforcement, weld, fatigue, or hot-strength assessment.'],
    source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'models/wistr_tgrid_cover.py',ROOT/'scripts/rigid_cover_screening.py']})
(out/'tgrid-cover-report.json').write_text(json.dumps(report,indent=2)+'\n')
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
camera('assembly',(7,-9,6),(2,0,.65),6.7,'WISTR | Recessed T-grid insulation cassette','Five individually supported layers / 512 mm stack / bottom groove only / coated underside / direct cap seating','Coating adhesion is assumed for this draft. Cap fittings and service reliefs need integration.')
camera('frame',(6,-8,5),(2.05,0,.30),6.3,'WISTR | Five suspended grids and upper lifting frame',f'160 x 60 x 3 mm upper box members / {len(rods)} ceramic-isolated ties / no bottom tray or posts',f'Gross-section screening at estimated dead weight: lifted apex {screening["lifted"]["apex_deflection_mm"]:.1f} mm; not a qualified lifting design.')
camera('cutaway',(5,-9,3.4),(2.05,0,.30),6.3,'WISTR | Bottom grooves; upper blocks rest on T-bars','Tan: insulation / silver: embedded grids / teal: shared rods / gold: crimp stops',f'Additive estimate {mass/1000:.2f} t, including coating and ceramic washers. Seated on a flat cap reference.')
# A display copy of the block pack exposes front rods and bottom supports.
review=b.assembly('review.blocks','Cutaway blocks')
for ob in list(body.children):
    edge=.10+.15*ob['layer']
    ys=[v.co.y for v in ob.data.vertices]
    if not ys or max(ys)<=edge:continue
    cp=ob.copy();cp.data=ob.data.copy();b.collection('Cutaway blocks').objects.link(cp);cp.parent=review;cp.name='review.'+ob.name
    if min(ys)<edge:
        cut=b.box('display_cut',review,(12,10+edge,3),(0,(edge-10)/2,.5),None);b.cut(cp,cut)
for view in ('assembly','frame','cutaway'):
    for name,col in b.collections.items():
        col.hide_render=name.startswith('Labels.') and name!='Labels.'+view
    b.collection('Remote lifting tools').hide_render=True
    b.collection('Cutaway blocks').hide_render=view!='cutaway'
    b.collection('Calcium silicate blocks').hide_render=view!='assembly'
    b.collection('Exterior skins').hide_render=view!='assembly'
    print('Rendering',view,flush=True)
    scene.camera=cameras[view];scene.render.filepath=str(out/f'tgrid-cover-{view}.png');bpy.ops.render.render(write_still=True)
# Open the real stepped block cutaway, with its explanatory labels visible.
for name,col in b.collections.items():
    col.hide_viewport=name in ('Calcium silicate blocks','Exterior skins','Remote lifting tools') or (name.startswith('Labels.') and name!='Labels.cutaway')
    col.hide_render=col.hide_viewport
scene.camera=cameras['cutaway']
scene['review_scope']=cfg.SCOPE;scene['mass_estimate_kg']=mass
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(out/'wistr-tgrid-cover.blend'))
print(json.dumps({k:report[k] for k in ['mass_kg','groups_kg','cm_local_m','head_offset_m','tension_rods']},indent=2))
print(json.dumps({k:{p:v for p,v in screening[k].items() if p!='nodal_displacements_m'} for k in ['lifted']},indent=2));print('SUPPORTS',support_screen)
