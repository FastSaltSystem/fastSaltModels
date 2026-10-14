"""Compose the attached control-annex draft on the latest coolant/nitrogen site."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/p) for p in ('src','models','scripts')]
import wistr_control_annex as cfg
import turbine_layout
from build_tank_bay_draft import builder
from build_attached_services_draft import fingerprint
from build_compact_services_draft import view as site_view
from build_wistr import camera
from textual_graphics.installation_clearance import bounds,gapbox,segment_box
F=cfg.ORIGIN[2]

def label(b,root,name,text,x,y,size=.45):
    d=bpy.data.curves.new(name,'FONT');d.body=text;d.size=size;d.align_x='CENTER';d.align_y='CENTER'
    ob=b.finish(bpy.data.objects.new(name,d),name,root,'control_ink',(x,y,.026));return ob

def wall(b,root,name,axis,at,lo,hi,height,mat,t,opening=None):
    spans=[(lo,hi,0,height)]
    if opening:
        a,c,h=opening;assert lo<=a<c<=hi
        spans=[(lo,a,0,height),(c,hi,0,height),(a,c,h,height)]
    out=[]
    for i,(a,c,z0,z1) in enumerate(spans):
        if c-a<1e-6 or z1-z0<1e-6:continue
        size=(t,c-a,z1-z0) if axis=='x' else (c-a,t,z1-z0)
        pos=(at,(a+c)/2,(z0+z1)/2) if axis=='x' else ((a+c)/2,at,(z0+z1)/2)
        ob=b.box(name+str(i),root,size,pos,mat);out.append(ob)
    return out

def door(b,root,name,axis,at,a,c,height=2.4):
    size=(.065,c-a,height) if axis=='x' else (c-a,.065,height)
    pos=(at,(a+c)/2,height/2) if axis=='x' else ((a+c)/2,at,height/2)
    ob=b.box(name,root,size,pos,'control_door',.015);ob['scope']='Door envelope only; rating, interlocks and seals unresolved';return ob

def build(b):
    root=b.assembly('site.control_annex','Control annex',cfg.ORIGIN);root['scope']=cfg.SCOPE;root['dimensions_m']=cfg.SIZE
    root['operator_area_m2']=180.;root['gross_footprint_m2']=500.
    for name,col in [('control_wall','#C7D2D5'),('control_roof','#A4B5BC'),('control_barrier','#899EA7'),('control_door','#527D8E'),('control_floor','#CAD8D7'),('control_zone','#B8CACC'),('control_ink','#254350'),('control_screen','#274E64')]:b.material(name,col,roughness=.55)
    w,d,h=cfg.SIZE;t=cfg.WALL
    b.box('independent_slab',root,(w,d,.45),(w/2,d/2,-.225),'floor')['scope']='Separate control-annex slab reservation; foundation and structural joint not designed'
    # The control-side barrier meets the existing turbine facade along 4 m.
    wall(b,root,'west_barrier','x',cfg.BARRIER/2,0,d,h,'control_barrier',cfg.BARRIER,(*cfg.VESTIBULE['door_y'],2.4))
    for ob in wall(b,root,'east','x',w-t/2,0,d,h,'control_wall',t,(6.,7.6,2.4)):ob['control_cutaway']=True
    for ob in wall(b,root,'south','y',t/2,cfg.BARRIER,w,h,'control_wall',t,(9.,10.4,2.4)):ob['control_cutaway']=True
    wall(b,root,'north','y',d-t/2,cfg.BARRIER,w,h,'control_wall',t)
    roof=b.box('roof',root,(w,d,.3),(w/2,d/2,h+.15),'control_roof');roof['control_roof']=True
    door(b,root,'outside_entry','x',w-.03,6.,7.6)
    door(b,root,'outside_exit','y',.03,9.,10.4)
    b.box('entry_canopy',root,(2.2,3.,.15),(w+1.1,6.8,2.8),'control_roof')
    b.box('entry_apron',root,(3.,4.,.10),(w+1.5,6.8,-.05),'floor')
    v=cfg.VESTIBULE
    wall(b,root,'vestibule_inner','y',v['y'][0],v['x'][0],v['x'][1],3.,'control_wall',.2,(*v['inner_door_x'],2.4))
    wall(b,root,'vestibule_side','x',v['x'][1],v['y'][0],v['y'][1],3.,'control_wall',.2)
    door(b,root,'vestibule_outer_door','x',.30,*v['door_y'])
    door(b,root,'vestibule_inner_door','y',v['y'][0],*v['inner_door_x'])
    b.box('vestibule_ceiling',root,(4.2,3.8,.15),(2.6,22.8,3.075),'control_roof')['control_ceiling']=True
    label(b,root,'vestibule_label','VESTIBULE',2.55,23.7,.32)
    # Actual corresponding opening in the turbine hall facade.
    toolroot=b.assembly('draft.control_openings','Control opening tools')
    ya,yb=[cfg.ORIGIN[1]+y for y in v['door_y']]
    tool=b.box('turbine_entry',toolroot,(1.4,yb-ya,2.42),(-36.1,(ya+yb)/2,F+1.2),None)
    tool.hide_render=True;tool.hide_set(True);tool['utility_opening_tool']=True
    wallobj=bpy.data.objects['site.turbine.east.0'];mod=wallobj.modifiers.new('Control-annex vestibule opening','BOOLEAN');mod.object=tool;mod.operation='DIFFERENCE';mod.solver='EXACT'
    p=cfg.OPERATORS;x,y=p['origin'];dx,dy=p['size']
    b.box('operator_area',root,(dx,dy,.025),(x+dx/2,y+dy/2,.0125),'control_zone')
    label(b,root,'operator_label','CONTROL ROOM / 180 m2',x+dx/2,y+1.0,.48)
    for i,cx in enumerate((3.5,7.8,12.1),1):
        b.box('console_'+str(i),root,(3.2,1.15,.9),(cx,6.,.45),'control_door',.08)
        for j,off in enumerate((-.9,0,.9)):
            b.box(f'screen_{i}_{j}',root,(.75,.07,.46),(cx+off,6.48,1.18),'control_screen',.025)
        b.box('seat_'+str(i),root,(.52,.52,.12),(cx,4.9,.48),'control_door',.04)
        b.box('seat_back_'+str(i),root,(.52,.10,.55),(cx,4.65,.78),'control_door',.03)
        b.box('seat_base_'+str(i),root,(.12,.12,.45),(cx,4.9,.225),'rail')
    b.box('overview_display',root,(11.,.15,1.4),(8.,11.8,2.1),'control_screen',.04)
    for x in (3.,13.):b.box('display_post_'+str(x),root,(.1,.1,2.1),(x,11.8,1.05),'rail')
    for idx,room in enumerate(cfg.ROOMS):
        x0,x1=room['x'];y0,y1=room['y'];cx=(x0+x1)/2
        wall(b,root,'service_front_'+str(idx),'y',y0,x0,x1,3.,'control_wall',.2,(cx-.6,cx+.6,2.3))
        for side,xx in enumerate((x0,x1)):wall(b,root,f'service_side_{idx}_{side}','x',xx,y0,y1,3.,'control_wall',.2)
        door(b,root,'service_door_'+str(idx),'y',y0,cx-.6,cx+.6,2.3)
        b.box('service_ceiling_'+str(idx),root,(x1-x0+.2,y1-y0+.2,.15),(cx,(y0+y1)/2,3.075),'control_roof')['control_ceiling']=True
        label(b,root,'service_label_'+str(idx),room['name'].upper().replace(' RESERVATION',''),cx,y0+1.2,.33)
        for k in range(3 if idx<2 else 1):
            size=(.7,1.,2.) if idx<2 else (3.,2.,2.)
            b.box(f'service_equipment_{idx}_{k}',root,size,(cx,y1-1.3-k*1.5,size[2]/2),'control_door',.04)['scope']='Equipment space only; no electrical or ventilation design'
    label(b,root,'annex_label','CONTROL ANNEX / 20 x 25 m',10.,14.2,.55)
    return root

def check(root,signature,pid_before):
    assert fingerprint()==signature,'Main circulation changed'
    pid_after=sorted((o.name,o.get('pid_tag')) for o in bpy.data.objects if o.get('pid_tag'))
    assert pid_after==pid_before,'Existing P&ID object associations changed'
    lo=Vector(cfg.ORIGIN);hi=lo+Vector(cfg.SIZE);body=(lo,hi)
    # Exact box overlap against all reserved turbine service volumes/aprons.
    service=[]
    for item in turbine_layout.SERVICE:
        a=Vector(item['min'])+Vector((-96,-20,F));c=a+Vector(item['size'])
        assert not all(min(hi[k],c[k])-max(lo[k],a[k])>1e-5 for k in range(3)),item['name']
        service.append(item['name'])
    for p in turbine_layout.APRONS:
        a=Vector((p['min'][0]-96,p['min'][1]-20,F));c=a+Vector((*p['size'],.1))
        assert not all(min(hi[k],c[k])-max(lo[k],a[k])>1e-5 for k in range(2)),p['name']
    # All saved pipe centrelines against the complete annex volume.
    near=[];collisions=[]
    for ob in bpy.data.objects:
        if ob.type!='CURVE' or ob.get('utility_opening_tool'):continue
        for sp in ob.data.splines:
            if not sp.points:continue
            pts=[ob.matrix_world@Vector(p.co[:3]) for p in sp.points];r=ob.data.bevel_depth
            if len(pts)<2 or gapbox(bounds(pts),body)>r+.1:continue
            gap=min(segment_box(a,c,*body) for a,c in zip(pts,pts[1:]))-r
            near.append((ob.name,round(gap,4)))
            if gap<-.005:collisions.append((ob.name,gap))
    assert not collisions,collisions
    # Check existing nearby meshes against the occupied rectangular envelope.
    # Ground/paving and the intended common boundary are explicitly excluded.
    eps=.005;boxlo=lo+Vector((eps,eps,eps));boxhi=hi-Vector((eps,eps,eps))
    verts=[Vector((x,y,z)) for x,y,z in ((boxlo.x,boxlo.y,boxlo.z),(boxhi.x,boxlo.y,boxlo.z),(boxhi.x,boxhi.y,boxlo.z),(boxlo.x,boxhi.y,boxlo.z),(boxlo.x,boxlo.y,boxhi.z),(boxhi.x,boxlo.y,boxhi.z),(boxhi.x,boxhi.y,boxhi.z),(boxlo.x,boxhi.y,boxhi.z))]
    tree=BVHTree.FromPolygons(verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    deps=bpy.context.evaluated_depsgraph_get();tested=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH' or ob.get('utility_opening_tool') or ob.name.startswith(('site.control_annex.','draft.','site.ground.')):continue
        if not ob.name.startswith(('site.','equipment.','building.','reactor.')):continue
        bb=bounds([ob.matrix_world@Vector(v) for v in ob.bound_box])
        if gapbox(bb,body)>.01:continue
        if max(v.z for v in [ob.matrix_world@Vector(q) for q in ob.bound_box])<=F+.005:continue
        ev=ob.evaluated_get(deps);mesh=ev.to_mesh();vv=[ob.matrix_world@v.co for v in mesh.vertices]
        bt=BVHTree.FromPolygons(vv,[tuple(f.vertices) for f in mesh.polygons]);tested.append(ob.name)
        inside=any(all(boxlo[k]<v[k]<boxhi[k] for k in range(3)) for v in vv)
        assert not inside and not tree.overlap(bt),(ob.name,'annex envelope overlap')
        ev.to_mesh_clear()
    # Verify the opening actually removes the turbine-wall material at passage centre.
    ob=bpy.data.objects['site.turbine.east.0'];ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
    bt=BVHTree.FromPolygons([ob.matrix_world@v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons])
    hit=bt.ray_cast(Vector((-37.,-18.2,F+1.2)),Vector((1,0,0)),2.)[0];assert hit is None,'Turbine vestibule passage blocked';ev.to_mesh_clear()
    return dict(footprint_m2=500,operator_area_m2=180,shared_boundary_length_m=4.,reactor_shell_plan_clearance_m=round(math.hypot(16,16)-21,3),
        turbine_service_volumes_checked=len(service),turbine_aprons_checked=len(turbine_layout.APRONS),nearby_pipes=near,nearby_meshes_checked=tested,
        collisions=[],vestibule_opening_checked=True,pid_objects_unchanged=len(pid_before),main_circulation_unchanged=True,scope=cfg.SCOPE)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build-only',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=ROOT/cfg.OUTPUT;out.mkdir(parents=True,exist_ok=True);source=ROOT/cfg.SOURCE
    bpy.ops.wm.open_mainfile(filepath=str(source));b=builder()
    for c in bpy.data.collections:c.hide_viewport=False
    for o in bpy.data.objects:o.hide_viewport=False
    bpy.context.view_layer.update();sig=fingerprint();pid=sorted((o.name,o.get('pid_tag')) for o in bpy.data.objects if o.get('pid_tag'))
    root=build(b);bpy.context.view_layer.update();report=check(root,sig,pid)
    report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (source,Path(__file__),ROOT/'models/wistr_control_annex.py',ROOT/'models/turbine_layout.py')}
    (out/'control-annex-checks.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTROL_ANNEX_CHECKS_OK',report,flush=True)
    cams={'exterior':camera(b,'ControlAnnex.Exterior',(-3,-68,27),(-27,-24,-5),57),
          'cutaway':camera(b,'ControlAnnex.Inside',(-3,-63,37),(-26,-28,-6),40),
          'site':camera(b,'ControlAnnex.Site',(-112,-134,111),(-31,0,0),152)}
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    def view(key):
        site_view(b,{'exterior':cams[key]},'exterior')
        for ob in bpy.data.objects:
            if ob.get('control_roof') or ob.get('control_cutaway') or ob.get('control_ceiling'):ob.hide_render=ob.hide_viewport=key=='cutaway'
        scene.camera=cams[key]
    view('exterior');bpy.ops.wm.save_as_mainfile(filepath=str(out/'fast-salt-control-annex.blend'))
    if not args.build_only:
        for key in cams:
            view(key);scene.render.filepath=str(out/(key+'.png'));bpy.ops.render.render(write_still=True)
    print('CONTROL_ANNEX_DRAFT_OK',flush=True)

if __name__=='__main__':main()
