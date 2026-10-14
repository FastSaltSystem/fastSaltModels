"""Build an isolated tank-bay and three-item laydown draft from the saved site.

Blender --background --python scripts/build_tank_bay_draft.py -- --build-only
Run without --build-only to render three compact review views.
"""
import argparse, copy, hashlib, json, math, sys
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/p) for p in ('src','models','scripts')]
import wistr_installation as base
import wistr_tank_bay_draft as cfg
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.installation_utilities import build_coolant_tank,build_transfer,service_line,cut,polar
from textual_graphics.installation_maintenance import build_maintenance,check_maintenance,item_bounds
from textual_graphics.installation_clearance import bounds,gapbox,segdist,segment_box
from build_wistr import camera


def remove_prefix(prefix):
    removed={o for o in bpy.data.objects if o.name==prefix or o.name.startswith(prefix+'.')}
    for o in bpy.data.objects:
        for m in list(o.modifiers):
            if m.type=='BOOLEAN' and m.object in removed:o.modifiers.remove(m)
    for o in list(removed):bpy.data.objects.remove(o,do_unlink=True)


def builder():
    b=SceneBuilder();b.collections={c.name:c for c in bpy.data.collections}
    b.materials={m.name:m for m in bpy.data.materials}
    b.assemblies={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
    return b


def hull(points):
    pts=sorted(set((round(p[0],6),round(p[1],6)) for p in points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    low=[];up=[]
    for seq,out in ((pts,low),(pts[::-1],up)):
        for p in seq:
            while len(out)>1 and cross(out[-2],out[-1],p)<=0:out.pop()
            out.append(p)
    return low[:-1]+up[:-1]


def hull_gap(a,b):
    gaps=[]
    for poly in (a,b):
        for u,v in zip(poly,poly[1:]+poly[:1]):
            n=Vector((-(v[1]-u[1]),v[0]-u[0])).normalized()
            aa=[Vector(p).dot(n) for p in a];bb=[Vector(p).dot(n) for p in b]
            gaps.append(max(min(bb)-max(aa),min(aa)-max(bb)))
    return max(gaps)


def bay(b):
    p=cfg.BAY;x,y=p['centre'];w,d,h=p['size'];t=p['wall'];f=base.FLOOR_Z
    root=b.assembly('site.coolant_tank_bay','Coolant tank bay',(x,y,f))
    root['scope']=cfg.SCOPE
    b.material('tank_bay_wall','#ADBFC4',roughness=.7)
    b.box('slab',root,(w,d,.35),(0,0,-.175),'floor')
    for key,xx in [('west',-w/2+t/2),('east',w/2-t/2)]:
        if key=='west':spans=[(-d/2+1.,d/2,0,h)]
        else:
            a,c=[q-y for q in p['door_y']]
            spans=[(-d/2,a,0,h),(c,d/2,0,h),(a,c,p['door_height'],h)]
        for i,(a,c,z0,z1) in enumerate(spans):
            ob=b.box(key+str(i),root,(t,c-a,z1-z0),(xx,(a+c)/2,(z0+z1)/2),'tank_bay_wall')
            ob['draft_bay_wall']=key
    for key,yy in [('south',-d/2+t/2),('north',d/2-t/2)]:
        if key=='south':
            left=-w/2+1.;right=w/2-t
            ob=b.box(key,root,(right-left,t,h),((left+right)/2,yy,h/2),'tank_bay_wall')
        else:ob=b.box(key,root,(w-2*t,t,h),(0,yy,h/2),'tank_bay_wall')
        ob['draft_bay_wall']=key
    chamfer=b.box('service_corner',root,(math.sqrt(2)*(1.-t/2),t,h),(-w/2+(1.+t/2)/2,-d/2+(1.+t/2)/2,h/2),'tank_bay_wall')
    chamfer.rotation_euler.z=-math.pi/4;chamfer['draft_bay_wall']='south'
    roof=b.box('roof',root,(w,d,.25),(0,0,h+.125),'tank_bay_wall');roof['site_roof']=True
    # External door apron, with no changes to the reactor's equipment door.
    b.box('door_apron',root,(2.5,3.4,.04),(w/2+1.25,sum(p['door_y'])/2-y,-.02),'floor')
    return root


def reroute(b,layout):
    result=build_transfer(b,layout)
    p=cfg.TRANSFER;f=layout.FLOOR_Z;z=f+p['low_height'];a=p['crossing_angle'];hi=f+p['crossing_height']
    root=bpy.data.objects['connections.coolant_transfer'];tx,ty,tz=cfg.TANK['position']
    spec=dict(bpy.data.objects['connections.coolant_transfer.reactor_to_pump']['pipe_spec'])
    for name in ('reactor_to_pump','pump_to_storage'):
        for suffix in ('','.metal','.insulation'):remove_prefix(root.name+'.'+name+suffix)
    tap=result['reactor_port'];inlet=result['pump_inlet'];outlet=result['pump_outlet'];tee=(tx,ty,z)
    paths={
        'reactor_to_pump':[tap,(tap[0],tap[1],z),polar(p['rise_radius'],a,z),polar(p['rise_radius'],a,hi),
                          polar(p['drop_radius'],a,hi),polar(p['drop_radius'],a,z),inlet],
        'pump_to_storage':[outlet,(tx,outlet[1],z),tee],
        'tank_bottom_nozzle':[tee,(tx,ty,tz)],
        'preparation_to_tee':[(14.5,27.225,f+.70),(14.5,26.85,f+.70),(17.,26.85,f+.70),
                              (17.,26.85,z),(17.,24.9,z),(tx,24.9,z),tee]}
    routes=[]
    for name,controls in paths.items():
        ob=service_line(b,name,root,controls,spec);ob['draft_tank_route']=True
        ob['flow_direction']='bidirectional';ob['service']='Heated and insulated coolant transfer'
        pts=[tuple(q.co[:3]) for q in ob.data.splines[0].points]
        routes.append(dict(name=ob.name,controls=controls,points=pts,radius=spec['jacket_od']/2,
                           length_m=sum(math.dist(u,v) for u,v in zip(pts,pts[1:]))))
    # True three-way low-point junction: preparation and reactor branches oppose
    # each other on the same horizontal axis; the tank connection is vertical.
    result.update(routes=routes,shared_bottom_tee=tee,storage_port=(tx,ty,tz),
                  crossing_height_above_floor_m=p['crossing_height'])
    tools=bpy.data.objects['utilities.penetrations']
    wall=bpy.data.objects['building.shell.retained_wall']
    cut(b,'draft_transfer_reactor_wall',tools,[polar(20.1,a,hi),polar(21.7,a,hi)],.11,[wall])
    # Sealed sleeve reservations in the bay south wall and the shared preparation wall.
    south=bpy.data.objects['site.coolant_tank_bay.service_corner']
    cut(b,'draft_transfer_bay_wall',tools,[polar(21.5,a,hi),polar(22.4,a,hi)],.11,[south])
    prepwalls=[o for o in bpy.data.objects if o.name.startswith('site.fuel_preparation.south')]
    north=bpy.data.objects['site.coolant_tank_bay.north']
    cut(b,'draft_preparation_wall',tools,[(17,25.4,z),(17,26.5,z)],.11,prepwalls+[north])
    # Short sleeve shells make the intentional penetrations visible.
    from textual_graphics.installation_piping import shell_mesh
    for key,pts in [('reactor_wall',[polar(20.25,a,hi),polar(21.1,a,hi)]),
                    ('bay_wall',[polar(21.75,a,hi),polar(22.3,a,hi)]),
                    ('prep_wall',[(17,25.6,z),(17,26.45,z)])]:
        shell_mesh(b,key+'_sleeve',tools,[Vector(q) for q in pts],.11,.095,'rail')
    return result


def preview_items(b,layout):
    for ob in list(bpy.data.objects):
        if ob.name.startswith('equipment.maintenance_laydown.cap_bearing_'):bpy.data.objects.remove(ob,do_unlink=True)
    col=b.collection('Draft maintenance items');deps=bpy.context.evaluated_depsgraph_get();placements={}
    for key,name in [('cover','reactor.insulation_1'),('cap','reactor.cap_1'),('reflector','reactor.sector_1.top_reflector')]:
        root=bpy.data.objects[name];inv=root.matrix_world.inverted();lo,hi=item_bounds(name)
        R=Matrix.Rotation(math.radians(cfg.PLACEMENT.get(key,{}).get('angle',0)),4,'Z')
        sources=[o for o in [root]+list(root.children_recursive) if o.type in ('MESH','CURVE') and not o.hide_render]
        local=[]
        for o in sources:
            mesh=o.evaluated_get(deps).to_mesh()
            local.extend(R@inv@o.matrix_world@v.co for v in mesh.vertices)
            o.evaluated_get(deps).to_mesh_clear()
        qlo,qhi=bounds(local)
        a,c,d,e=layout.MAINTENANCE['cover_bay' if key=='cover' else 'cap_bay']
        if key=='cover':dx=(a+c-qlo[0]-qhi[0])/2;dy=(d+e-qlo[1]-qhi[1])/2
        else:
            ox,oy=cfg.PLACEMENT[key]['offset'];dx=a+ox-qlo[0];dy=d+oy-qlo[1]
        dz=layout.CATWALK['deck_z']+.105-qlo[2]
        T=Matrix.Translation((dx,dy,dz))@R@inv
        for source in sources:
            mesh=bpy.data.meshes.new_from_object(source.evaluated_get(deps),depsgraph=deps)
            ob=bpy.data.objects.new('DraftLaydown.'+source.name,mesh);col.objects.link(ob);ob.matrix_world=T@source.matrix_world
        footprint=hull([(v.x+dx,v.y+dy) for v in local])
        assert min(v[0] for v in footprint)>a+.04 and max(v[0] for v in footprint)<c-.04,key
        assert min(v[1] for v in footprint)>d+.04 and max(v[1] for v in footprint)<e-.04,key
        if key!='cover':
            # Three independent seating pads per item on the common tray.
            # Pad positions are a provisional support layout, not a load rating.
            centroid=Vector((sum(q[0] for q in footprint)/len(footprint),sum(q[1] for q in footprint)/len(footprint)))
            extremes=[min(footprint,key=lambda q:q[0]),max(footprint,key=lambda q:q[0]),max(footprint,key=lambda q:q[1])]
            for i,point in enumerate(extremes):
                seat=centroid*.55+Vector(point)*.45
                b.box(key+'_seat_'+str(i),bpy.data.objects['equipment.maintenance_laydown'],(.20,.20,.08),
                      (seat.x,seat.y,layout.CATWALK['deck_z']+.065),'dark')
        placements[key]=dict(source=name,rotation_deg=cfg.PLACEMENT.get(key,{}).get('angle',0),
                             footprint=footprint,source_bounds=[list(lo),list(hi)],upright=True)
    gap=hull_gap(placements['cap']['footprint'],placements['reflector']['footprint'])
    assert gap>.12,gap
    col.hide_render=col.hide_viewport=True
    return dict(items=placements,cap_reflector_projected_clearance_m=gap,
                scope='Actual evaluated meshes and lifting hooks projected in plan; tool envelope and crane sweep not qualified')


def check_new_geometry(layout,transfer,maintenance):
    # Broad phase followed by surface checks for new routes; all visible old
    # equipment and service geometry remains in the scene during this check.
    deps=bpy.context.evaluated_depsgraph_get();obstacles=[]
    ignored=('connections.coolant_transfer.','utilities.penetrations.','DraftLaydown.',
             'unused_draft_exclusion.')
    for o in bpy.data.objects:
        if o.type not in ('MESH','CURVE') or o.hide_render or o.get('utility_opening_tool'):continue
        if o.name.startswith(ignored):continue
        if not o.name.startswith(('equipment.','reactor.','connections.','site.fresh_air.',
                                  'site.salt_distribution.','site.fuel_pressure.','site.process_services.',
                                  'site.fuel_preparation.','building.shell.','site.coolant_tank_bay.')):continue
        bb=bounds([o.matrix_world@Vector(q) for q in o.bound_box])
        obstacles.append((o,bb))
    clashes=[];tested=0;minimum=1000.;near=[]
    for route in transfer['routes']:
        pts=[Vector(p) for p in route['points']];rad=route['radius'];rbb=bounds(pts)
        for o,bb in obstacles:
            if gapbox(rbb,bb)>rad+.01:continue
            # Actual nozzle and flange interfaces. Local exclusions only.
            pp=pts
            if o.name.startswith('equipment.coolant_transfer_pump.'):
                pp=[q for q in pts if (q-Vector((*cfg.PUMP_XY,layout.FLOOR_Z+.4))).length>.65]
            if o.name=='equipment.coolant_storage.closed_tank' and route['name'].endswith('tank_bottom_nozzle'):
                continue
            if o.name in ('reactor.vessel.bottom_plate','reactor.baffle.floor_sheet','reactor.well.wall'):
                continue  # Explicit boolean openings inherited from build_transfer.
            if o.name=='site.process_services.Coolant transfer pump' and route['name'].endswith('preparation_to_tee'):
                pp=[q for q in pp if (q-pts[0]).length>.20]  # Existing pump-face terminal.
            if len(pp)<2:continue
            if o.type=='CURVE':
                if not o.data.splines or o.data.splines[0].type!='POLY':continue
                vs=[o.matrix_world@Vector(p.co[:3]) for p in o.data.splines[0].points]
                if len(vs)<2:continue
                gap=min(segdist(a,c,u,v)[0] for a,c in zip(pp,pp[1:]) for u,v in zip(vs,vs[1:]))-rad-o.data.bevel_depth
            else:
                # Evaluate only nearby objects (incl. Boolean wall openings).
                ev=o.evaluated_get(deps);mesh=ev.to_mesh()
                vs=[o.matrix_world@v.co for v in mesh.vertices]
                if not vs:ev.to_mesh_clear();continue
                tree=BVHTree.FromPolygons(vs,[tuple(f.vertices) for f in mesh.polygons]);gap=1000.
                for a,c in zip(pp,pp[1:]):
                    if segment_box(a,c,*bb)>rad+.01:continue
                    length=(c-a).length
                    if length<1e-8:continue
                    # Conservative discretization: ≤25 mm samples with half-step subtraction.
                    n=max(1,math.ceil(length/.025))
                    for i in range(n+1):
                        q=a.lerp(c,i/n);hit=tree.find_nearest(q)
                        if hit[0] is not None:gap=min(gap,hit[3]-rad-length/(2*n))
                    hit=tree.ray_cast(a,(c-a).normalized(),length)
                    if hit[0] is not None:gap=-rad
                ev.to_mesh_clear()
            tested+=1;minimum=min(minimum,gap)
            if gap<.1:near.append((route['name'],o.name,gap))
            if gap<-.002:clashes.append((route['name'],o.name,round(gap,4)))
    # Cylindrical tank envelope versus evaluated nearby visible equipment/ducts.
    x,y,z=cfg.TANK['position'];r=cfg.TANK['radius']+cfg.TANK['insulation']+cfg.TANK['cladding']
    zlo=z-cfg.TANK['insulation']-cfg.TANK['cladding'];zhi=z+cfg.TANK['height']+.416
    tank_near=[]
    for o,bb in obstacles:
        if o.name.startswith(('equipment.coolant_storage.','equipment.coolant_transfer_pump.')):continue
        if bb[1][2]<zlo or bb[0][2]>zhi:continue
        gap=math.hypot(max(bb[0][0]-x,0,x-bb[1][0]),max(bb[0][1]-y,0,y-bb[1][1]))-r
        if gap<0:
            ev=o.evaluated_get(deps);mesh=ev.to_mesh()
            vs=[o.matrix_world@v.co for v in mesh.vertices]
            nv=96;verts=[(x+r*math.cos(i*math.tau/nv),y+r*math.sin(i*math.tau/nv),zz) for zz in (zlo,zhi) for i in range(nv)]
            faces=[(i,(i+1)%nv,(i+1)%nv+nv,i+nv) for i in range(nv)]+[tuple(range(nv-1,-1,-1)),tuple(range(nv,2*nv))]
            cyl=BVHTree.FromPolygons(verts,faces)
            tree=BVHTree.FromPolygons(vs,[tuple(q.vertices) for q in mesh.polygons])
            inside=any((v.x-x)**2+(v.y-y)**2<r*r and zlo<v.z<zhi for v in vs)
            if inside or cyl.overlap(tree):tank_near.append((o.name,gap))
            ev.to_mesh_clear()
    # Bounding-box positives can be hollow shells; inspect the actual candidate set.
    assert not tank_near,('tank envelope candidates',tank_near)
    assert not clashes,clashes[:60]
    bx,by=cfg.BAY['centre'];w,d,h=cfg.BAY['size'];wall=cfg.BAY['wall']
    wall_gap=min(w/2-wall-r,d/2-wall-r)
    assert wall_gap>.65
    assert h-(cfg.TANK['support_height']+cfg.TANK['height']+.7)>1.5
    assert math.hypot(bx-w/2,by-d/2)>layout.BUILDING['diameter']/2
    # No new footprint occupies the original equipment-door/cart corridor.
    angle=math.radians(layout.ACCESS['angle']);end=Vector((27*math.cos(angle),27*math.sin(angle)))
    assert by-d/2>end.y+layout.ACCESS['width']/2
    return dict(route_obstacle_pairs=tested,route_clashes=clashes,tank_envelope_candidates=tank_near,
                nominal_tank_jacket_to_bay_wall_m=wall_gap,
                overhead_ladder_clearance_m=h-(cfg.TANK['support_height']+cfg.TANK['height']+.7),
                minimum_sampled_route_clearance_m=minimum,near_route_surfaces=near,
                scope='Selected geometry screen, explicit nozzle/penetration exclusions; no pipe stress, supports, ventilation or operational qualification')


def show_view(b,cams,key):
    for c in bpy.data.collections:
        if c.name.startswith(('Site annotations.','Annotations.','Draft labels.')):c.hide_render=c.hide_viewport=True
    preview=bpy.data.collections['Draft maintenance items'];preview.hide_render=preview.hide_viewport=key!='laydown'
    for name in ('Shell','Crane'):
        if name in b.collections:b.collections[name].hide_render=b.collections[name].hide_viewport=True
    for o in bpy.data.objects:
        if o.get('site_roof'):o.hide_render=o.hide_viewport=True
        if o.get('draft_bay_wall'):
            hidden=key!='plan' and o['draft_bay_wall'] in ('south','east')
            o.hide_render=o.hide_viewport=hidden
        if o.name.startswith('site.fuel_preparation.') and '.south' in o.name:o.hide_render=o.hide_viewport=key=='bay'
    for name in ('reactor.insulation_1','reactor.cap_1','reactor.sector_1.top_reflector'):
        # Preview represents the removed items, not duplicate installed parts.
        root=bpy.data.objects[name]
        for o in [root]+list(root.children_recursive):
            if o.type in ('MESH','CURVE') and not o.get('utility_opening_tool'):
                if 'preview_original_visibility' not in o:o['preview_original_visibility']=bool(o.hide_render)
                o.hide_render=bool(o['preview_original_visibility']) or key=='laydown'
    for name in ('Stacks','Air distribution','Hot air insulation','Hot air duct metal','Steam generators','Secondary piping','Coolant pumps','Sector handling','Building columns','Pressure pipe metal','Pipe insulation'):
        if name in b.collections:b.collections[name].hide_render=b.collections[name].hide_viewport=key=='laydown'
    bpy.context.scene.camera=cams[key]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
    bpy.context.view_layer.update()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build-only',action='store_true');parser.add_argument('--resume',action='store_true')
    parser.add_argument('--source',type=Path,default=ROOT/cfg.SOURCE)
    parser.add_argument('--output',type=Path,default=ROOT/cfg.OUTPUT)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    args.output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.output/'geometry-checkpoint.blend' if args.resume else args.source))
    for c in bpy.data.collections:c.hide_viewport=False
    for o in bpy.data.objects:o.hide_viewport=False
    bpy.context.view_layer.update()
    if not args.resume:
        # Remove only the superseded equipment, connection geometry and their cutters.
        for prefix in ('equipment.coolant_storage','equipment.coolant_transfer_pump','connections.coolant_transfer',
                       'equipment.maintenance_laydown','equipment.sector_canister_cart',
                       'site.process_services.Coolant_liquid_supply','site.salt_distribution.duct_to_coolant_storage',
                       'site.salt_distribution.coolant_bottom_nozzle_opening'):
            remove_prefix(prefix)
        for o in list(bpy.data.objects):
            if o.name.startswith('utilities.penetrations.') and any(s in o.name for s in ('vessel_bottom','baffle_floor','well_service_sleeve','storage_bottom')):remove_prefix(o.name)
            elif 'duct_to_coolant_storage_saddle_' in o.name:remove_prefix(o.name)
        old_tools=bpy.data.objects.get('utilities.penetrations')
        if old_tools:
            for child in list(old_tools.children):
                matrix=child.matrix_world.copy();child.parent=None;child.matrix_world=matrix
            bpy.data.objects.remove(old_tools,do_unlink=True)
        b=builder();layout=SimpleNamespace(**{k:copy.deepcopy(getattr(base,k)) for k in dir(base) if k.isupper()})
        layout.COOLANT_STORAGE.update(cfg.TANK);layout.COOLANT_TRANSFER['pump_radius']=math.hypot(*cfg.PUMP_XY)
        layout.MAINTENANCE.update(cfg.LAYDOWN)
        print('BUILD_TANK',flush=True)
        build_coolant_tank(b,layout)
        print('TANK_BUILT',flush=True)
        # Scale the four conceptual supports with the enlarged tank. They are layout envelopes.
        for ob in bpy.data.objects:
            if ob.name.startswith('equipment.coolant_storage.') and any(s in ob.name for s in ('.support_','.foot_','.insulation_support_opening_')):
                ob.location.x*=2;ob.location.y*=2;ob.scale.x*=2;ob.scale.y*=2
        bay(b);bpy.context.view_layer.update();print('BUILD_TRANSFER',flush=True);transfer=reroute(b,layout)
        print('BUILD_MAINTENANCE',flush=True)
        maintenance=build_maintenance(b,layout);bpy.context.view_layer.update()
        print('DRAFT_GEOMETRY_BUILT',flush=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'geometry-checkpoint.blend'))
        (args.output/'geometry-checkpoint.json').write_text(json.dumps(dict(transfer=transfer,maintenance=maintenance),default=list))
    else:
        b=builder();layout=SimpleNamespace(**{k:copy.deepcopy(getattr(base,k)) for k in dir(base) if k.isupper()})
        layout.COOLANT_STORAGE.update(cfg.TANK);layout.COOLANT_TRANSFER['pump_radius']=math.hypot(*cfg.PUMP_XY);layout.MAINTENANCE.update(cfg.LAYDOWN)
        data=json.loads((args.output/'geometry-checkpoint.json').read_text());transfer=data['transfer'];maintenance=data['maintenance']
    maintenance_check=check_maintenance(b,layout,maintenance)
    print('MAINTENANCE_CHECKED',flush=True)
    checks=check_new_geometry(layout,transfer,maintenance)
    print('ROUTES_CHECKED',flush=True)
    preview=preview_items(b,layout)
    cams={
        'bay':camera(b,'Draft.Bay',(70,-42,45),(12,14,-1),66),
        'plan':camera(b,'Draft.Plan',(0,8.5,90),(0,8.5,-8),94),
        'laydown':camera(b,'Draft.Laydown',(27,-22,25),(12.5,-.2,.1),16)}
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene['draft_scope']=cfg.SCOPE;scene['draft_parameters']='models/wistr_tank_bay_draft.py'
    report=dict(source=str(args.source.relative_to(ROOT)),source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
        configuration_sha256=hashlib.sha256((ROOT/'models/wistr_tank_bay_draft.py').read_bytes()).hexdigest(),
        bay=cfg.BAY,tank=cfg.TANK,transfer=transfer,laydown=maintenance,laydown_placements=preview,
        checks=checks,maintenance_checks=maintenance_check,scope=cfg.SCOPE)
    (args.output/'tank-bay-report.json').write_text(json.dumps(report,indent=2,default=list)+'\n')
    show_view(b,cams,'bay')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'fast-salt-tank-bay.blend'))
    if not args.build_only:
        for key in cams:
            show_view(b,cams,key);scene.render.filepath=str(args.output/(key+'-draft.png'));bpy.ops.render.render(write_still=True)
        show_view(b,cams,'laydown');bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'maintenance-laydown.blend'))
    print('TANK_BAY_DRAFT_OK',flush=True)

if __name__=='__main__':main()
