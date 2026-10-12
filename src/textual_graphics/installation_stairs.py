"""Three-flight catwalk access stair and selected clearance checks (draft)."""
import math
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from .installation_clearance import bounds,gapbox


def grate(b,name,root,x0,x1,y0,y1,z):
    """Open steel grating: longitudinal bearing strips and transverse ties."""
    verts=[];faces=[]
    def bar(a,c,d,e,height):
        k=len(verts)
        verts.extend((x,y,zz) for x in (a,c) for y in (d,e) for zz in (z-height,z))
        faces.extend(tuple(k+i for i in f) for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)])
    n=math.ceil((x1-x0)/.04)
    for i in range(n+1):
        x=x0+(x1-x0)*i/n;bar(max(x0,x-.0025),min(x1,x+.0025),y0,y1,.03)
    n=max(1,math.ceil((y1-y0)/.15))
    for i in range(n+1):
        y=y0+(y1-y0)*i/n;bar(x0,x1,max(y0,y-.006),min(y1,y+.006),.015)
    return b.mesh(name,root,verts,faces,'catwalk_mesh')


def offset_edge(points,distance):
    tangents=[Vector((c.x-a.x,c.y-a.y)).normalized() for a,c in zip(points,points[1:])]
    normals=[Vector((-t.y,t.x)) for t in tangents];edge=[]
    for i,p in enumerate(points):
        n=normals[0] if i==0 else normals[-1] if i==len(points)-1 else (normals[i-1]+normals[i]).normalized()
        denom=n.dot(normals[min(i,len(normals)-1)])
        q=Vector((p.x,p.y))+n*(distance/denom);edge.append(tuple(q))
    return edge


def swept_outline(points,half):return offset_edge(points,half)+list(reversed(offset_edge(points,-half)))


def prism_data(poly,z0,z1):
    n=len(poly);verts=[(*q,z) for z in (z0,z1) for q in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return verts,faces


def prism(b,name,root,poly,z0,z1,mat):
    vs,fs=prism_data(poly,z0,z1);return b.mesh(name,root,vs,fs,mat)


def build_stairs(b,layout,services):
    cfg=layout.CATWALK_STAIRS;deck=layout.CATWALK['deck_z'];floor=layout.FLOOR_Z
    rise=(deck-floor)/(cfg['flights']*cfg['risers_per_flight']);run=15*cfg['going']
    assert abs(run-4.2)<1e-8
    offset=cfg.get('radial_offset',0);angle=math.radians(cfg['angle'])
    tangent=cfg.get('tangent_offset',0)
    root=b.assembly('equipment.catwalk_stair','Reactor catwalk',(offset*math.cos(angle)-tangent*math.sin(angle),offset*math.sin(angle)+tangent*math.cos(angle),0),angle=cfg['angle'])
    root.scale.y=cfg.get('mirror',1)
    root['scope']='Provisional independent steel stair; no load rating or complete egress qualification'
    def line(name,pts,rad=.025,mat='catwalk_rail'):return b.tube(name,root,pts,rad,mat)
    def rail(name,a,c):
        for h in (.55,.90,1.10):line(name+str(h),[(a[0],a[1],a[2]+h),(c[0],c[1],c[2]+h)])
        length=math.dist(a,c);n=max(1,math.ceil(length/1.2))
        for i in range(n+1):
            q=Vector(a).lerp(Vector(c),i/n);b.beam(name+'_post'+str(i),root,q,q+Vector((0,0,1.10)),.025,'catwalk_rail')
    for flight in range(3):
        x0,x1=(7.7,9.0) if flight%2==0 else (9.2,10.5)
        z0=floor+flight*16*rise;direction=1 if flight%2==0 else -1
        ya=-4.8 if direction==1 else -.6;yb=ya+direction*run
        for step in range(1,16):
            ys=ya+direction*(step-1)*cfg['going'];ye=ys+direction*cfg['going']
            tread=grate(b,f'flight_{flight+1}_tread_{step}',root,x0,x1,min(ys,ye),max(ys,ye),z0+step*rise)
            tread['stair_tread']=True
        for x in (x0-.035,x1+.035):
            # Deep flat stringer web follows the nosing line.
            pts=[(x-.025,ya,z0-.20),(x-.025,yb,z0+16*rise-.20),(x-.025,yb,z0+16*rise-.03),(x-.025,ya,z0-.03)]
            vs=pts+[(q[0]+.05,q[1],q[2]) for q in pts]
            b.mesh(f'flight_{flight+1}_stringer_{x}',root,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'catwalk_frame')
            # Rail height follows the first through last stair nosings.
            rail_end=yb-.10 if flight==2 and x<x0 else yb
            rail(f'flight_{flight+1}_rail_{x}',(x,ya,z0+rise),(x,rail_end,z0+16*rise))
    # Full-width reversing landings; top bridge joins the existing deck.
    landings=[('bottom',7.7,9.0,-6,-4.8,floor),('lower',7.65,10.55,-.6,.6,floor+16*rise),
              ('upper',7.65,10.55,-6,-4.8,floor+32*rise),('top',7.65,10.55,-.6,.6,deck)]
    for name,x0,x1,y0,y1,z in landings:
        grate(b,name+'_landing',root,x0,x1,y0,y1,z)
        if name!='bottom':
            for y in (y0+.05,y1-.05):b.box(name+'_edge_'+str(y),root,(x1-x0,.08,.20),((x0+x1)/2,y,z-.13),'catwalk_frame')
            for x in (x0+.025,x1-.025):b.box(name+'_bearer_'+str(x),root,(.08,y1-y0,.20),(x,(y0+y1)/2,z-.13),'catwalk_frame')
            # Closed external edge and sides; reversing-flight edge stays open.
            yy=y0-.05 if name=='upper' else y1+.05
            rail(name+'_back',(x0,yy,z),(x1,yy,z))
            rail(name+'_outer',(x1+.05,y0,z),(x1+.05,y1,z))
            if name!='top':rail(name+'_inner',(x0-.05,y0,z),(x0-.05,y1,z))
            else:
                rail('top_front_bridge',(x0,y0-.05,z),(7.68,y0-.05,z))
                rail('top_front_outer',(9.05,y0-.05,z),(x1,y0-.05,z))
            # Toe boards on exposed edges.
            b.box(name+'_toe',root,(x1-x0,.01,.10),((x0+x1)/2,yy,z+.05),'catwalk_frame')
    for x in (7.62,10.58):
        for y in (-6.05,.65):
            column_top=floor+32*rise if y<0 else deck
            b.box(f'column_{x}_{y}',root,(.14,.14,column_top-floor),(x,y,(column_top+floor)/2),'catwalk_frame')
            b.box(f'base_{x}_{y}',root,(.32,.32,.025),(x,y,floor+.0125),'catwalk_frame')
        # Back-face diagonal bracing stays outside the walking lanes.
        for z in (floor,floor+16*rise):
            b.beam(f'brace_{x}_{z}',root,(x,-6.05,z+.10),(x,.65,z+16*rise-.20),.035,'catwalk_frame')
    # A dogleg bridge avoids the vertical hot-salt riser beside the upper entry.
    bpy.context.view_layer.update();inverse=root.matrix_world.inverted()
    entry=math.radians(cfg['entry_angle'])
    path=[inverse@Vector((rr*math.cos(entry),rr*math.sin(entry),deck)) for rr in (7.30,8.50)]
    path.extend([Vector((6.50,0,deck)),Vector((7.68,0,deck))])
    root['bridge_points']=[list(q) for q in path]
    poly=swept_outline(path,.65)
    bridge=prism(b,'bridge_grated_deck',root,poly,deck-.035,deck,'catwalk_mesh')
    bridge['scope']='Bridge deck envelope; grating and side-truss sections provisional'
    for side in (-1,1):
        edge=offset_edge(path,side*.70)
        for h in (-.12,.55,.90,1.10):line('bridge_chord_'+str(side)+'_'+str(h),[(q[0],q[1],deck+h) for q in edge],.035 if h in (-.12,1.10) else .025,'catwalk_frame' if h in (-.12,1.10) else 'catwalk_rail')
        for j,(u,v) in enumerate(zip(edge,edge[1:])):
            count=math.ceil(math.dist(u,v)/1.2)
            for k in range(count):
                a=Vector(u).lerp(Vector(v),k/count);c=Vector(u).lerp(Vector(v),(k+1)/count)
                b.beam(f'bridge_web_{side}_{j}_{k}',root,(*a,deck-.12),(*c,deck+1.10),.025,'catwalk_frame')
                b.beam(f'bridge_post_{side}_{j}_{k}',root,(*a,deck-.12),(*a,deck+1.10),.025,'catwalk_rail')
    # Replace the outer catwalk rails/toe board with open arcs at the entrance.
    cat=bpy.data.objects['equipment.reactor_catwalk'];rr=layout.CATWALK['outer_radius']
    half=math.degrees(math.asin(.65/rr));a0=cfg['entry_angle']+half;a1=cfg['entry_angle']+360-half
    for ob in list(cat.children):
        if ob.name.startswith(cat.name+'.outer_rail_') or ob.name.endswith('.outer_toeplate'):
            bpy.data.objects.remove(ob,do_unlink=True)
        elif '.outer_post_' in ob.name:
            a=math.degrees(math.atan2(ob.location.y,ob.location.x))%360
            # Beam locations can be centred between their endpoints.
            if abs((a-cfg['entry_angle']+180)%360-180)<half:bpy.data.objects.remove(ob,do_unlink=True)
    for h in (.55,1.10):
        pts=[(rr*math.cos(math.radians(a0+(a1-a0)*i/360)),rr*math.sin(math.radians(a0+(a1-a0)*i/360)),h) for i in range(361)]
        b.tube(f'outer_rail_{h}',cat,pts,.025,'catwalk_rail')
    b.annulus('outer_toeplate',cat,rr-.005,rr+.005,0,.10,'catwalk_frame',start=a0,end=a1,steps=192)
    for a in (a0,a1):
        q=Vector((rr*math.cos(math.radians(a)),rr*math.sin(math.radians(a)),0));b.beam('stair_entry_jamb_'+str(a),cat,q,q+Vector((0,0,1.10)),.025,'catwalk_rail')
    bpy.context.view_layer.update()
    result=dict(parameters=cfg,total_rise_m=deck-floor,riser_m=rise,risers=48,treads=45,flight_run_m=run,
        pitch_degrees=math.degrees(math.atan(rise/cfg['going'])),landing_levels_m=[floor+16*rise,floor+32*rise,deck],
        nominal_clear_width_m=1.20,entry_opening_m=1.30,bridge_path_length_m=sum((c-a).length for a,c in zip(path,path[1:])),scope='Draft standard-stair layout; structural and complete access/egress review pending',
        reference='https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.25')
    result['clearance']=check_stairs(root,layout)
    services['stairs']=result
    return result


def check_stairs(root,layout):
    """Check actual stair solids and pedestrian headroom with all geometry active."""
    visibility=[(c,c.hide_viewport) for c in bpy.data.collections]+[(o,o.hide_viewport) for o in bpy.data.objects]
    for ob,_ in visibility:ob.hide_viewport=False
    bpy.context.view_layer.update()
    transform=root.matrix_world.copy();inverse=transform.inverted();offset=layout.CATWALK_STAIRS.get('radial_offset',0)
    floor=layout.FLOOR_Z;deck=layout.CATWALK['deck_z'];rise=(deck-floor)/48
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    obstacles=[];own=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH':continue
        if not ob.name.startswith(('equipment.','connections.','reactor.')) and not ob.get('route_object'):continue
        vs=[ob.matrix_world@v.co for v in ob.data.vertices]
        if not vs:continue
        data=(ob,vs,bounds(vs),BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in ob.data.polygons]))
        (own if ob.parent==root else obstacles).append(data)
    for ob,value in visibility:ob.hide_viewport=value
    bpy.context.view_layer.update()
    zones=[('approach',(7.75,-7.25,floor+.04),(8.95,-6.0,floor+2.10))]
    for flight in range(3):
        x0,x1=(7.75,8.95) if flight%2==0 else (9.25,10.45)
        z0=floor+flight*16*rise;direction=1 if flight%2==0 else -1
        ya=-4.8 if direction==1 else -.6
        for step in range(1,16):
            ys=ya+direction*(step-1)*.28;ye=ys+direction*.28;z=z0+step*rise
            zones.append((f'flight_{flight+1}_step_{step}',(x0,min(ys,ye)+.005,z+.04),(x1,max(ys,ye)-.005,z+2.10)))
    for name,x0,x1,y0,y1,z in [('bottom',7.75,8.95,-6,-4.8,floor),('lower',7.70,10.50,-.6,.6,floor+16*rise),('upper',7.70,10.50,-6,-4.8,floor+32*rise),('top',7.70,10.50,-.6,.6,deck)]:
        zones.append((name,(x0,y0+.04,z+.04),(x1,y1-.04,z+2.10)))
    volumes=[]
    for name,lo,hi in zones:
        vs=[transform@Vector((x,y,z)) for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
        volumes.append((name,vs,faces))
    path=[Vector(q) for q in root['bridge_points']]
    poly=swept_outline(path,.60)
    vs,fs=prism_data(poly,deck+.04,deck+2.10)
    volumes.append(('bridge_headroom',[transform@Vector(v) for v in vs],fs))
    entry=math.radians(layout.CATWALK_STAIRS['entry_angle'])
    ep=[(rr*math.cos(entry)-yy*math.sin(entry),rr*math.sin(entry)+yy*math.cos(entry)) for rr,yy in [(5.85,-.575),(7.4,-.575),(7.4,.575),(5.85,.575)]]
    vs,fs=prism_data(ep,deck+.04,deck+2.10);volumes.append(('catwalk_entry',[Vector(v) for v in vs],fs))
    collisions=[];pairs=0
    # Closed-volume surface intersection plus point containment catches contained members.
    for name,vs,fs in volumes:
        box=bounds(vs);tree=BVHTree.FromPolygons(vs,fs)
        for ob,ov,bb,ot in obstacles+own:
            if gapbox(box,bb)>.001:continue
            pairs+=1
            collision=bool(tree.overlap(ot))
            if not collision:
                # A ray parity test for one point is sufficient once surfaces do not cross.
                origin=ov[0].copy();direction=Vector((.9123,.3141,.2637)).normalized();hits=0
                for _ in range(12):
                    hit,_,_,_=tree.ray_cast(origin,direction)
                    if hit is None:break
                    hits+=1;origin=hit+direction*1e-5
                collision=bool(hits%2)
            if collision:collisions.append((name,ob.name))
    solid_pairs=0
    for ob,vs,bb,tree in own:
        for other,ov,bc,ot in obstacles:
            # The bridge deliberately seats on the existing deck/ring framing and rail jambs.
            if other.name.startswith('equipment.reactor_catwalk.') and any(k in other.name for k in ('expanded_panel_','ring_beam_','radial_joist_','outer_','stair_entry_jamb_')):continue
            if gapbox(bb,bc)>.001:continue
            solid_pairs+=1
            if tree.overlap(ot):collisions.append((ob.name,other.name))
    assert not collisions,collisions[:40]
    max_radius=max(math.hypot(v.x,v.y) for _,vs,_,_ in own for v in vs)
    wall_clearance=layout.BUILDING['diameter']/2-layout.BUILDING['wall_thickness']-max_radius
    assert wall_clearance>.30,wall_clearance
    return dict(building_wall_gap_m=wall_clearance,walking_zone_count=len(volumes),headroom_pairs=pairs,solid_pairs=solid_pairs,collisions=collisions,headroom_reserved_m=2.10,
        scope='Actual stair meshes plus tread, landing, top-entry and lower-approach headroom volumes; all equipment collections evaluated; intentional catwalk attachment and floor contacts excluded; complete egress not assessed')
