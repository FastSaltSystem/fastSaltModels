"""Compact shared-wall tank enclosure; overlay on the attached-services draft."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/p) for p in ('src','models','scripts')]
import wistr_compact_services_draft as cfg
import wistr_installation as layout
from build_tank_bay_draft import builder,remove_prefix
from build_attached_services_draft import fingerprint,curved_slab,arced_footprint,wall_y
from build_wistr import camera
from textual_graphics.installation_utilities import service_line,cut,polar
from textual_graphics.installation_clearance import bounds,gapbox,segment_box,segdist
F=layout.FLOOR_Z

def slab(b,name,root,poly,z0,z1,mat):
    points=[Vector((x,y,0)) for x,y in poly];n=len(points)
    triangles=tessellate_polygon([points]);index={tuple(p):i for i,p in enumerate(points)}
    faces=[]
    for tri in triangles:
        ids=tuple(p if isinstance(p,int) else index[tuple(p)] for p in tri);faces.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return b.mesh(name,root,[(*p,z) for z in (z0,z1) for p in poly],faces,mat)

def copy_wall_mods(ob):
    for m in bpy.data.objects['building.shell.retained_wall'].modifiers:
        if m.type=='BOOLEAN' and m.object:
            k=ob.modifiers.new(m.name,'BOOLEAN');k.operation=m.operation;k.solver='EXACT';k.object=m.object

def geometry():
    for prefix in ('site.coolant_silo','site.coolant_preparation','draft.shared_wall_display'):
        remove_prefix(prefix)
    for name in ('coolant_preparation_entry','reactor_transfer_entry','silo_access'):
        remove_prefix('draft.attached_openings.'+name)
    remove_prefix('site.combined_process.coolant_receiving_apron')
    b=builder();cx,cy=cfg.TANK_XY;ri=cfg.ENCLOSURE['inside_radius'];t=cfg.ENCLOSURE['wall'];r=ri+t;h=cfg.ENCLOSURE['height'];x0=13.
    d=math.hypot(cx,cy);theta=math.atan2(cy,cx)-math.asin(r/d)
    # Straight radial wall is tangent to the circular outer wall.
    a=math.degrees(theta)-90;end=math.degrees(math.acos((x0-cx)/r))
    start=polar(21,math.degrees(theta),0)[:2]
    arc=[(cx+r*math.cos(math.radians(a+(end-a)*i/160)),cy+r*math.sin(math.radians(a+(end-a)*i/160))) for i in range(161)]
    junction=math.degrees(math.acos(x0/21))
    inner=[polar(21,junction+(math.degrees(theta)-junction)*i/64,0)[:2] for i in range(65)]
    poly=[start,*arc,*inner[:-1]]
    root=b.assembly('site.coolant_silo','Coolant silo');root['scope']=cfg.SCOPE
    floor=slab(b,'floor',root,poly,F-.35,F,'floor')
    tool=bpy.data.objects['draft.floor_join.existing_slab_footprint']
    m=floor.modifiers.new('Use existing reactor slab','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=tool
    roof=slab(b,'roof',root,poly,F+h,F+h+.25,'silo_enclosure');roof['site_roof']=True
    length=math.dist(start,arc[0]);mid=((start[0]+arc[0][0])/2,(start[1]+arc[0][1])/2)
    radial=b.box('radial_wall',root,(length,t,h),(mid[0]-math.sin(theta)*t/2,mid[1]+math.cos(theta)*t/2,F+h/2),'silo_enclosure')
    radial.rotation_euler.z=theta;radial['silo_shell']='front'
    circle=b.assembly('site.coolant_silo_curve','Coolant silo',(cx,cy,F))
    for key,aa,bb in [('front',a,0),('rear',0,end)]:
        ob=b.annulus('wall_'+key,circle,ri,r,0,h,'silo_enclosure',start=aa,end=bb,steps=128);ob['silo_shell']=key
    # Fuel building's existing east wall is the sole lower common wall.
    # Extend it upwards only beside the tall enclosure.
    y0=math.sqrt(21**2-x0*x0);y1=arc[-1][1]
    b.box('shared_west_upper',root,(t,y1-y0,h-5),(x0-t/2,(y0+y1)/2,F+5+(h-5)/2),'silo_enclosure')['silo_shell']='rear'
    viewroot=b.assembly('draft.shared_wall_display','Shared wall inspection')
    for name,aa,bb,height in [('tank',math.degrees(theta),junction,h),('process',junction,math.degrees(math.acos(-7/21)),5)]:
        ob=b.annulus(name,viewroot,20.35,21,F,F+height,'concrete',start=aa,end=bb,steps=128)
        ob['presentation_only']=True;ob['represents']='building.shell.retained_wall';copy_wall_mods(ob)
    # Coolant preparation shares X=13 with the fuel room; no second wall there.
    p=cfg.COOLANT_PREP;x1=cx+r;north=p['north_y'];height=5
    cool=b.assembly('site.coolant_preparation','Attached service buildings')
    cp=arced_footprint(x0,x1,north,cx,cy,r)
    curved_slab(b,'floor',cool,cp,F-.35,F,'floor')
    ob=curved_slab(b,'roof',cool,cp,F+height,F+height+.25,'coolant_annex');ob['site_roof']=True
    # Beyond the fuel building, continue the same west boundary northwards.
    b.box('west_extension',cool,(t,north-31,height),(x0-t/2,(north+31)/2,F+height/2),'coolant_annex')['annex_outer_wall']=True
    b.box('east',cool,(t,north-cy,height),(x1-t/2,(north+cy)/2,F+height/2),'coolant_annex')['annex_outer_wall']=True
    wall_y(b,'north',cool,x0,x1,north-t/2,height,'coolant_annex',(16.5,20.5,4.2),t)
    b.box('receiving_apron',cool,(x1-x0,4,.10),((x1+x0)/2,north+2,F-.05),'floor')
    # Shift the tank, its actual bottom penetration, and the coolant equipment.
    delta=Vector((cx-20.5,cy-20.5,0));bpy.data.objects['equipment.coolant_storage'].location+=delta
    bpy.data.objects['utilities.penetrations.storage_bottom'].location+=delta
    moved=[]
    for o in bpy.data.objects:
        if o.name.startswith('site.process_services.Coolant') or (o.type=='FONT' and o.name.startswith('Coolant')):
            o.location+=Vector(cfg.COOLANT_EQUIPMENT_SHIFT)
            if o.type=='MESH' and not o.hide_render:moved.append(o.name)
        if o.type=='FONT' and o.name.startswith('Attached.CoolantLabel'):o.location.x=cx;o.location.y=north-1
    pump=bpy.data.objects['equipment.coolant_transfer_pump'];pump.location=(*cfg.PUMP_XY,F+.4);pump.rotation_euler.z=math.pi/2
    bpy.context.view_layer.update()
    out=[];rootpipe=bpy.data.objects['connections.coolant_transfer']
    spec=dict(bpy.data.objects[rootpipe.name+'.reactor_to_pump']['pipe_spec'])
    old=bpy.data.objects[rootpipe.name+'.reactor_to_pump'];tap=tuple(old.data.splines[0].points[0].co[:3]);lo=F+.4;hi=F+4.9
    inlet=tuple(pump.matrix_world@Vector((-.225,0,0)));outlet=tuple(pump.matrix_world@Vector((.225,0,0)));tee=(cx,cy,lo)
    pumpface=(18.5,26.225,F+.70)
    routes={
      'reactor_to_pump':[tap,(tap[0],tap[1],lo),polar(16.4,45,lo),polar(16.4,45,hi),polar(21.4,45,hi),polar(21.4,45,lo),(17.6,13.1,lo),(20.5,13.1,lo),inlet],
      'pump_to_storage':[outlet,(cx,outlet[1],lo),tee],
      'tank_bottom_nozzle':[tee,(cx,cy,F+.9)],
      'preparation_to_tee':[pumpface,(cx,25.7,F+.70),(cx,25.7,lo),tee]}
    for key,controls in routes.items():
        remove_prefix(rootpipe.name+'.'+key)
        ob=service_line(b,key,rootpipe,controls,spec);ob['flow_direction']='bidirectional';ob['compact_revision']=True
        points=[list(q.co[:3]) for q in ob.data.splines[0].points]
        out.append(dict(name=ob.name,points=points,controls=controls,radius=spec['jacket_od']/2))
    tools=bpy.data.objects['draft.attached_openings'];walls=[bpy.data.objects['site.coolant_silo_curve.wall_rear']]
    cut(b,'compact_preparation_entry',tools,[(cx,cy+ri-.2,lo),(cx,cy+r+.2,lo)],.11,walls)
    # Small personnel opening faces east; installation/removal route remains a reservation.
    cutter=b.box('compact_silo_access',tools,(1.,1.5,2.5),(cx+r-.175,cy,F+1.25),None)
    cutter.hide_render=True;cutter.hide_set(True);cutter['utility_opening_tool']=True
    for name in ('front','rear'):
        ob=bpy.data.objects['site.coolant_silo_curve.wall_'+name];m=ob.modifiers.new('Access opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    # Relocate housing, connecting duct, and both opening tools as one assembly.
    R=Matrix.Rotation(math.radians(cfg.INTAKE_ANGLE-33),4,'Z')
    for name in ('connections.air.outside_air_intake_2','site.fresh_air_intake_2','site.fresh_air_openings.outdoor_intake_duct_2','site.fresh_air_openings.outdoor_intake_wall_2'):
        ob=bpy.data.objects[name];ob.matrix_world=R@ob.matrix_world;ob['draft_intake_angle']=cfg.INTAKE_ANGLE
    bpy.context.view_layer.update()
    # Refresh displayed wall cutouts after moving the intake cutters.
    return b,dict(footprint=poly,coolant_footprint=cp,radial_wall_angle_deg=math.degrees(theta),moved_equipment=moved,routes=out,
        tank_clearance_to_reactor_m=d-21-4.451,common_wall_x_m=13,common_wall_y_m=[y1,31],tank_xy=cfg.TANK_XY,pump_xy=cfg.PUMP_XY,
        inlet_angle_deg=cfg.INTAKE_ANGLE,inlet_xy=list(bpy.data.objects['site.fresh_air_intake_2'].location[:2]))

def check(data):
    deps=bpy.context.evaluated_depsgraph_get();cx,cy=cfg.TANK_XY;theta=math.radians(data['radial_wall_angle_deg']);r=cfg.ENCLOSURE['inside_radius'];t=cfg.ENCLOSURE['wall']
    gaps=[]
    # Check every actual tank/pump vertex against each physical enclosure boundary.
    for ob in bpy.data.objects:
        if ob.type!='MESH' or ob.hide_render or ob.get('utility_opening_tool') or not ob.name.startswith(('equipment.coolant_storage.','equipment.coolant_transfer_pump.')):continue
        for v in ob.data.vertices:
            q=ob.matrix_world@v.co
            radial=-q.x*math.sin(theta)+q.y*math.cos(theta)-t
            wall=math.hypot(q.x,q.y)-21
            west=q.x-13
            angle=math.atan2(q.y-cy,q.x-cx)
            curve=r-math.hypot(q.x-cx,q.y-cy) if angle>=theta-math.pi/2 else 999
            gap=min(radial,wall,west,curve);gaps.append(gap)
            assert gap>0,(ob.name,'enclosure',gap,list(q))
    # Coolant placeholders remain within the room and outside the curved tank wall.
    for name in data['moved_equipment']:
        ob=bpy.data.objects[name]
        for v in ob.bound_box:
            q=ob.matrix_world@Vector(v)
            assert 13+.1<q.x<cx+r and q.y<cfg.COOLANT_PREP['north_y']-.4,(name,'side/north')
            assert q.y>cy and math.hypot(q.x-cx,q.y-cy)>r+t+.05,(name,'tank wall')
    # Capsule checks on changed transfer routes against nearby evaluated solids.
    obstacles=[]
    for ob in bpy.data.objects:
        if ob.type not in ('MESH','CURVE') or ob.hide_render or ob.get('utility_opening_tool') or ob.get('presentation_only'):continue
        if ob.name.startswith(('connections.coolant_transfer.','utilities.penetrations.','draft.','DraftLaydown.')):continue
        if not ob.name.startswith(('equipment.','connections.','reactor.','site.','building.shell.','building.stack_')):continue
        if ob.name.startswith(('site.ground.','site.converter.','site.turbine.','site.secondary.')):continue
        obstacles.append((ob,bounds([ob.matrix_world@Vector(q) for q in ob.bound_box])))
    clashes=[];tested=0
    for route in data['routes']:
        pts=[Vector(q) for q in route['points']];rad=route['radius'];bb=bounds(pts)
        for ob,bc in obstacles:
            if gapbox(bb,bc)>rad+.02:continue
            terminals=[]
            if ob.name.startswith('equipment.coolant_transfer_pump.'):
                terminals=[Vector((*cfg.PUMP_XY,F+.4))]
            if ob.name=='equipment.coolant_storage.closed_tank' and route['name'].endswith('tank_bottom_nozzle'):continue
            if ob.name in ('reactor.vessel.bottom_plate','reactor.baffle.floor_sheet','reactor.well.wall'):continue
            if ob.name=='site.process_services.Coolant transfer pump' and route['name'].endswith('preparation_to_tee'):terminals=[pts[0]]
            pp=[q for q in pts if all((q-v).length>(.65 if ob.name.startswith('equipment.coolant_transfer_pump.') else .25) for v in terminals)]
            if len(pp)<2:continue
            ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
            if not mesh or not len(mesh.vertices):ev.to_mesh_clear();continue
            tree=BVHTree.FromPolygons([ob.matrix_world@q.co for q in mesh.vertices],[tuple(q.vertices) for q in mesh.polygons]);gap=999;tested+=1
            for a,c in zip(pp,pp[1:]):
                if segment_box(a,c,*bc)>rad+.02:continue
                length=(c-a).length
                if length<1e-7:continue
                n=max(1,math.ceil(length/.035))
                for i in range(n+1):
                    hit=tree.find_nearest(a.lerp(c,i/n))
                    if hit[0] is not None:gap=min(gap,hit[3]-rad-length/(2*n))
                if tree.ray_cast(a,(c-a).normalized(),length)[0] is not None:gap=-rad
            ev.to_mesh_clear()
            if gap<-.003:clashes.append((route['name'],ob.name,round(gap,4)))
    # Relocated intake housing against stack, nitrogen skid, annexe and nearby equipment.
    intake=bpy.data.objects['site.fresh_air_intake_2'];inletpoints=[o.matrix_world@Vector(v) for o in intake.children_recursive if o.type=='MESH' for v in o.bound_box]
    ib=bounds(inletpoints);intake_gaps=[]
    for ob,bc in obstacles:
        if ob.name.startswith(('equipment.nitrogen_supply.','site.combined_process.','building.stack_')):
            gap=gapbox(ib,bc);intake_gaps.append(gap)
            assert gap>.05,(ob.name,'inlet envelope',gap)
    # The three transfer branches meet only at their deliberate bottom tee.
    tee=Vector((*cfg.TANK_XY,F+.4))
    for i,a in enumerate(data['routes']):
        for c in data['routes'][i+1:]:
            pa=[Vector(q) for q in a['points'] if (Vector(q)-tee).length>.30]
            pc=[Vector(q) for q in c['points'] if (Vector(q)-tee).length>.30]
            if len(pa)<2 or len(pc)<2:continue
            gap=min(segdist(u,v,w,x)[0] for u,v in zip(pa,pa[1:]) for w,x in zip(pc,pc[1:]))-a['radius']-c['radius']
            assert gap>-.003,(a['name'],c['name'],gap)
    assert not clashes,clashes[:40]
    return dict(minimum_equipment_enclosure_gap_m=min(gaps),transfer_obstacle_pairs=tested,transfer_clashes=clashes,
       minimum_intake_selected_envelope_gap_m=min(intake_gaps),scope='Selected geometry checks only; no structural, thermal, process, maintenance-access or intake/exhaust recirculation qualification')

def view(b,cams,key):
    from build_attached_services_draft import view as oldview
    oldview(b,cams,key)
    # This upper west wall is a common internal boundary, not a duplicate facade.
    bpy.data.objects['site.combined_process.east'].hide_render=False
    bpy.data.objects['site.combined_process.east'].hide_viewport=False
    for name in ('draft.shared_wall_display.tank','site.coolant_silo.shared_west_upper'):
        bpy.data.objects[name].hide_render=bpy.data.objects[name].hide_viewport=key=='cutaway'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build-only',action='store_true');parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=ROOT/cfg.OUTPUT;out.mkdir(parents=True,exist_ok=True);source=ROOT/cfg.SOURCE
    bpy.ops.wm.open_mainfile(filepath=str(out/'geometry-checkpoint.blend' if args.resume else source))
    for col in bpy.data.collections:col.hide_viewport=False
    for ob in bpy.data.objects:ob.hide_viewport=False
    bpy.context.view_layer.update()
    if args.resume:
        data=json.loads((out/'geometry-checkpoint.json').read_text());b=builder()
    else:
        signature=fingerprint();b,data=geometry();data['original_main_route_signature']=signature
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'geometry-checkpoint.blend'))
        (out/'geometry-checkpoint.json').write_text(json.dumps(data,default=list))
    assert fingerprint()==data['original_main_route_signature'],'Main circulation changed'
    data['checks']=check(data);data['source']=cfg.SOURCE;data['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    data['builder_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();data['configuration_sha256']=hashlib.sha256((ROOT/'models/wistr_compact_services_draft.py').read_bytes()).hexdigest()
    data['scope']=cfg.SCOPE;print('COMPACT_GEOMETRY_CHECKED',flush=True)
    (out/'compact-services-report.json').write_text(json.dumps(data,indent=2,default=list)+'\n')
    cams={'cutaway':camera(b,'Compact.Cutaway',(52,70,49),(7,20,-1.8),57),
          'plan':camera(b,'Compact.Plan',(4,13,90),(4,13,-8),85),
          'exterior':camera(b,'Compact.Exterior',(65,64,44),(5,17,-.5),69)}
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    view(b,cams,'cutaway');bpy.ops.wm.save_as_mainfile(filepath=str(out/'fast-salt-compact-services.blend'))
    if not args.build_only:
        for key in cams:
            view(b,cams,key);scene.render.filepath=str(out/(key+'-draft.png'));bpy.ops.render.render(write_still=True)
    print('COMPACT_SERVICES_DRAFT_OK',flush=True)

if __name__=='__main__':main()
