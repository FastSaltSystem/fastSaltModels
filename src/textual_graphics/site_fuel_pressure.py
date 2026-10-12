"""Fuel pressure servers and gas interfaces: visual layout, not a control design."""
import math,itertools
import bpy
from mathutils import Vector
from .installation_piping import fillet_path
from .installation_clearance import bounds,gapbox,segment_box,segdist
from .site_salt_distribution import arc
from .installation_utilities import cut


def build_fuel_pressure(b,site,installation,annex):
    cfg=site.FUEL_PRESSURE;floor=site.PAD_Z;root=b.assembly('site.fuel_pressure','Fuel pressure gas piping')
    b.material('pressure_server','#708F98',metallic=.3,roughness=.4)
    b.material('gas_supply','#467AAB',metallic=.15,roughness=.45)
    b.material('gas_return','#946FA8',metallic=.15,roughness=.45)
    routes=[];servers=[];assignments=[]
    def line(name,controls,kind,od=None,insulation=None,**metadata):
        od=cfg['tube_od'] if od is None else od
        insulation=cfg['insulation'] if insulation is None else insulation
        pts,radii=fillet_path(controls,.12)
        ob=b.tube(name,root,pts,(od+2*insulation)/2,'gas_supply' if kind=='supply' else 'gas_return')
        ob['fuel_pressure_route']=True;ob['bare_od_m']=od;ob['radial_insulation_m']=insulation;ob['heated']=False
        ob['service']='Supply gas' if kind=='supply' else 'Off-gas'
        ob['scope']='Visual gas interface; pressure, capacity, valves and operating logic unspecified'
        q=dict(name=ob.name,kind=kind,points=[list(p) for p in pts],controls=[list(p) for p in controls],tube_od_m=od,
               outside_envelope_m=od+2*insulation,insulation_m=insulation,heated=False,**metadata)
        routes.append(q);return q
    # Replace the former above-vessel off-gas placeholder with the actual requested
    # three-server collection interface. Retain the original 150 mm trunk envelope.
    for name in ('reactor_offgas','reserved_offgas_tie_in'):
        ob=bpy.data.objects.get('site.process_services.'+name)
        if ob:bpy.data.objects.remove(ob,do_unlink=True)
    annex['routes']=[q for q in annex['routes'] if not q['name'].endswith('reactor_offgas')]
    zsup=floor+.65;zret=floor+.85
    off_controls=[(-1.95,10.0,zret),(-1.95,16.8,zret),(1.4,16.8,zret),(1.4,16.8,floor+4.2),
                  (1.4,18.6,floor+4.2),(3.3,18.6,floor+4.2),(3.3,27.,floor+4.2),(-1.,27.,floor+4.2),(-1.,27.,floor+2.6),(-1.,27.75,floor+2.6)]
    off=line('offgas_common',off_controls,'return',od=site.PROCESS_ANNEX['gas_pipe_od'],insulation=0,group='common')
    annex['routes'].append(dict(name=off['name'],points=off['points'],outside_envelope_m=off['outside_envelope_m'],service='Three fuel pressure servers to off-gas treatment'))
    annex['tie_ins']['offgas_collection']=off_controls[0]
    annex['scope']='Provisional process envelopes and interfaces; storage and gas distribution are recorded separately'
    # Incoming nitrogen and the outgoing supply header meet this distribution
    # enclosure, not the filtration train. No internal pressure-control circuit.
    station=b.assembly('site.offgas_gas_supply','Off-gas gas supply',( -3.5,28.2,floor))
    b.box('enclosure',station,(.8,.8,2.2),(0,0,1.2),'pressure_server',.04)
    b.box('base',station,(1.,1.,.10),(0,0,.05),'rail')
    panel_port=(-3.5,27.8,floor+2.2)
    supply_controls=[(-1.75,10.0,zsup),(-1.75,17.1,zsup),(1.05,17.1,zsup),(1.05,17.1,floor+4.2),
                     (1.05,18.9,floor+4.2),(2.95,18.9,floor+4.2),(2.95,26.6,floor+4.2),(-3.5,26.6,floor+4.2),(-3.5,26.6,floor+2.2),panel_port]
    sup=line('supply_common',list(reversed(supply_controls)),'supply',group='common')
    module=installation.ABSORBER_MODULES;w,d,_=module['size'];w*=.9;d*=.9
    for index,(angle,side,targets) in enumerate([(120,1,(1,2)),(240,-1,(3,4)),(0,1,(5,6))],1):
        theta=math.radians(angle)
        def world(x,y,z):return Vector((x*math.cos(theta)-y*math.sin(theta),x*math.sin(theta)+y*math.cos(theta),z))
        position=world(10.5,side*2.7,floor)
        server=b.assembly(f'equipment.fuel_pressure_server_{index}','Fuel pressure servers',tuple(position),angle)
        server['tank_pair']=list(targets);server['scope']='Pressure-server envelope copied from absorber-module proportions; no duty or pressure rating selected'
        diameter=module['tank_diameter'];height=module['tank_height'];base=module['tank_base_z']
        b.cylinder('buffer_tank',server,diameter/2,height,(0,0,base+height/2),'pressure_server',vertices=48)
        b.box('control_box',server,(w,d,module['control_height']),(0,0,base+height+module['control_height']/2),'pressure_server',.025)
        b.box('foot',server,(.95,.95,.08),(0,0,.04),'rail',.02)
        b.box('front_panel',server,(.018,d*.72,.5),(-w/2-.011,0,base+height+.55),'panel',.01)
        servers.append(dict(index=index,name=server.name,position=list(position),angle=angle,tanks=list(targets),tank_diameter_m=diameter,tank_height_m=height))
        # Paired common lines branch at three explicit tee positions.
        tee_y={1:10.5,2:10.8,3:11.3}[index]
        for n,kind in enumerate(('supply','return')):
            zz=zsup if n==0 else zret;tee=(-1.75 if n==0 else -1.95,tee_y,zz)
            if index<3:
                radius=(7.86 if index==1 else 7.62)-.12*n
                xx=(-1.6 if index==1 else -1.1)-.12*n
                start=math.acos(xx/radius)
            else:
                radius=7.85-.15*n;xx=1.2+.15*n;start=math.acos(xx/radius)
            # Buffer-side ports are at different heights; the four tank tubes
            # attach to the upper control enclosure.
            endpoint=world(10.5-diameter/2,side*2.7,zz)
            a=math.atan2(endpoint.y,endpoint.x)
            if index==2 and a<0:a+=math.tau
            bend=arc(radius,start,math.radians(22.5) if index==3 else a,zz)
            controls=[tee,(xx,tee_y,zz),*bend,*([(9.3,3.2,zz)] if index==3 else []),tuple(endpoint)]
            branch=line(f'server_{index}_{kind}',controls,kind,group='branch',server=index,junction=list(tee))
            branch['server_port']=list(endpoint)
        # Two independent 25 mm tubes to each tank, terminating in its upper
        # headspace wall. Existing roof fuel bundles and low liquid lines stay.
        for ti,tank_index in enumerate(targets):
            tank=bpy.data.objects[f'equipment.fuel_storage_{tank_index}']
            bpy.context.view_layer.update()
            for n,kind in enumerate(('supply','return')):
                rank=ti*2+n;port_y=-.12 if n==0 else .12
                tank_port=tank.matrix_world@Vector((-installation.FUEL_STORAGE['length']/2,port_y,0));tank_port.z=floor+5.0
                local_y=(-installation.FUEL_STORAGE['pair_spacing']/2 if ti==0 else installation.FUEL_STORAGE['pair_spacing']/2)+port_y
                sz=floor+2.02+rank*.13;sy=side*2.7+(rank-1.5)*.10
                start_port=world(10.5-w/2,sy,sz)
                controls=[start_port,world(9.9,sy,sz),world(9.9,local_y,sz),world(10.6,local_y,sz),world(10.6,local_y,floor+5.0),tank_port]
                q=line(f'server_{index}_tank_{tank_index}_{kind}',controls,kind,group='tank',server=index,tank=tank_index,server_port=list(start_port),tank_port=list(tank_port))
                assignments.append(dict(server=index,tank=tank_index,kind=kind,route=q['name']))
    # Move the entire nitrogen skid, including vaporizer, fill hardware and panel.
    nitrogen=bpy.data.objects['equipment.nitrogen_supply'];nitrogen.location=(*cfg['nitrogen_xy'],floor);nitrogen.rotation_euler.z=0
    for ob in list(bpy.data.objects):
        if ob.name=='connections.nitrogen' or ob.name.startswith('connections.nitrogen.'):
            bpy.data.objects.remove(ob,do_unlink=True)
    oldtool=bpy.data.objects.get('utilities.penetrations.nitrogen_wall_sleeve')
    if oldtool:
        for ob in bpy.data.objects:
            for mod in list(ob.modifiers):
                if mod.type=='BOOLEAN' and mod.object==oldtool:ob.modifiers.remove(mod)
        bpy.data.objects.remove(oldtool,do_unlink=True)
    bpy.context.view_layer.update()
    nx,ny=cfg['nitrogen_xy']
    def nw(q):return tuple(nitrogen.matrix_world@Vector(q))
    feed=[nw((-.65,-3.05,3.0)),nw((-1.7,-3.05,3.0)),nw((-1.7,-3.05,1.25)),nw((-1.7,-3.5,1.25)),nw((-2.1,-3.5,1.25)),
          (nx-2.1,27.6,floor+1.25),(-4.3,27.6,floor+1.25),(-4.3,28.2,floor+1.25),(-3.9,28.2,floor+1.25)]
    nf=line('nitrogen_to_offgas',feed,'supply',od=installation.NITROGEN['gas_diameter'],insulation=0,group='nitrogen')
    westwall=bpy.data.objects['site.off_gas.west.0']
    cut(b,'offgas_nitrogen_wall_sleeve',root,[(-6.3,27.6,floor+1.25),(-5.6,27.6,floor+1.25)],.04,[westwall])
    return dict(parameters=cfg,servers=servers,routes=routes,assignments=assignments,nitrogen_location=list(nitrogen.location),nitrogen_rotation_degrees=0,
                common_supply=sup['name'],common_offgas=off['name'],nitrogen_route=nf['name'],
                scope='Visual pressure-server and gas-routing envelopes only; gas duties, pressure control, containment, treatment and operating logic unqualified')


def check_fuel_pressure(result,site,annex,salt):
    saved=[(o,o.hide_viewport) for o in [*bpy.data.collections,*bpy.data.objects]]
    for ob,_ in saved:ob.hide_viewport=False
    bpy.context.view_layer.update()
    def prep(name,points,radius,**extra):
        pts=[Vector(p) for p in points]
        return dict(name=name,points=pts,radius=radius,bounds=bounds(pts),segments=[(a,c,bounds([a,c])) for a,c in zip(pts,pts[1:])],**extra)
    def gap(a,c):
        rr=a['radius']+c['radius'];best=(1e6,None,None)
        if gapbox(a['bounds'],c['bounds'])>rr+.03:return best
        for u,v,bb in a['segments']:
            for w,x,bc in c['segments']:
                if gapbox(bb,bc)>rr+.03:continue
                answer=segdist(u,v,w,x)
                if answer[0]-rr<best[0]:best=(answer[0]-rr,answer[1],answer[2])
        return best
    new=[prep(q['name'],q['points'],q['outside_envelope_m']/2,meta=q) for q in result['routes']]
    assert len(result['servers'])==3 and len(result['assignments'])==12
    assert sorted((a['tank'],a['kind']) for a in result['assignments'])==sorted(itertools.product(range(1,7),('supply','return')))
    assert all(q['tube_od_m']==.025 for q in result['routes'] if q['group']=='tank')
    clashes=[];junctions=[]
    for a,c in itertools.combinations(new,2):
        g,p,q=gap(a,c)
        if g>=-.001:continue
        common,branch=(a,c) if a['meta']['group']=='common' else (c,a)
        if common['meta']['group']=='common' and branch['meta']['group']=='branch' and common['meta']['kind']==branch['meta']['kind']:
            if min((Vector(p)-Vector(branch['meta']['junction'])).length,(Vector(q)-Vector(branch['meta']['junction'])).length)<.15:
                remaining=[v for v in branch['points'] if (v-Vector(branch['meta']['junction'])).length>.25]
                if len(remaining)>1:
                    remote,_,_=gap(common,prep(branch['name'],remaining,branch['radius']))
                    if remote<-.001:clashes.append((common['name'],branch['name'],'away from tee',remote))
                junctions.append((common['name'],branch['name']));continue
        clashes.append((a['name'],c['name'],g))
    existing=[]
    for ob in bpy.data.objects:
        if ob.type=='CURVE' and (ob.get('process_route') or ob.get('air_insulated') or ob.get('utility_route') or ob.name.startswith('connections.air.')):
            for sp in ob.data.splines:existing.append(prep(ob.name,[ob.matrix_world@Vector(v.co[:3]) for v in sp.points],ob.data.bevel_depth))
    names={a['name'] for a in new}
    for entry in annex['routes']+salt['routes']:
        if entry['name'] not in names:existing.append(prep(entry['name'],entry['points'],entry['outside_envelope_m']/2))
    for a in new:
        for c in existing:
            g,_,_=gap(a,c)
            if g<-.001:clashes.append((a['name'],c['name'],g))
    boxes=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('equipment.') and not o.get('utility_opening_tool')]
    for a in new:
        meta=a['meta']
        for ob in boxes:
            if meta['group']=='nitrogen' and ob.name.startswith('equipment.nitrogen_supply.'):continue
            pts=a['points']
            if meta.get('server') and ob.name.startswith(f'equipment.fuel_pressure_server_{meta["server"]}.'):
                pts=pts[:-1] if meta['group']=='branch' else pts[1:]
            if meta.get('tank') and ob.name==f'equipment.fuel_storage_{meta["tank"]}.closed_tank':pts=pts[:-1]
            if len(pts)<2:continue
            if gapbox(bounds(pts),bounds([ob.matrix_world@Vector(v) for v in ob.bound_box]))>a['radius']+.03:continue
            inv=ob.matrix_world.inverted();local=[inv@p for p in pts];lo,hi=bounds(ob.bound_box)
            g=min(segment_box(u,v,lo,hi) for u,v in zip(local,local[1:]))-a['radius']
            if g<-.001:clashes.append((a['name'],ob.name,g))
    # Test server envelopes themselves against existing low pipes/equipment.
    server_boxes=[o for o in boxes if o.name.startswith('equipment.fuel_pressure_server_')]
    for ob in server_boxes:
        lo,hi=bounds(ob.bound_box);inv=ob.matrix_world.inverted();bb=bounds([ob.matrix_world@Vector(v) for v in ob.bound_box])
        for c in existing:
            if gapbox(bb,c['bounds'])>c['radius']+.03:continue
            pts=[inv@p for p in c['points']];g=min(segment_box(u,v,lo,hi) for u,v in zip(pts,pts[1:]))-c['radius']
            if g<-.001:clashes.append((ob.name,c['name'],g))
    # Conservative box screen for the three new server bodies and their feet.
    for ob in server_boxes:
        bb=bounds([ob.matrix_world@Vector(v) for v in ob.bound_box])
        for other in boxes:
            if other.name.startswith('equipment.fuel_pressure_server_'):continue
            bc=bounds([other.matrix_world@Vector(v) for v in other.bound_box])
            overlaps=[min(bb[1][k],bc[1][k])-max(bb[0][k],bc[0][k]) for k in range(3)]
            if min(overlaps)>.001:clashes.append((ob.name,other.name,'overlapping equipment bounds'))
    skid=bpy.data.objects['equipment.nitrogen_supply']
    corners=[ob.matrix_world@Vector(v) for ob in skid.children if ob.type=='MESH' for v in ob.bound_box]
    lo,hi=bounds(corners)
    assert hi[0]<-6.4 and hi[1]<34.5
    assert math.hypot(hi[0],lo[1])>24.2
    link=annex['links'][0]
    for entry in result['routes']:
        if entry['group']=='common':
            r=entry['outside_envelope_m']/2
            for x,y,z in entry['points']:
                if link['y0']+.1<y<26.2:
                    assert abs(x-link['x'])+r<link['width']/2-.16
                    assert link['floor_z']+r<z<link['roof_z']-.16-r
    assert len(junctions)==6,junctions
    assert not any(o.name.startswith('connections.nitrogen.') for o in bpy.data.objects)
    assert not bpy.data.objects.get('utilities.penetrations.nitrogen_wall_sleeve')
    assert result['nitrogen_location'][:2]==list(site.FUEL_PRESSURE['nitrogen_xy'])
    for ob,value in saved:ob.hide_viewport=value
    bpy.context.view_layer.update()
    assert not clashes,clashes
    return dict(server_count=3,maintenance_tank_groups=3,tank_connection_pairs=6,tank_tube_count=12,branch_pairs=3,common_tee_connections=junctions,unresolved_clashes=clashes,
                checks=['Three box-over-buffer-tank servers, one per maintenance-tank pair','Two 25 mm OD tubes per maintenance tank','Common supply/off-gas pair through shared duct, branching to all three servers','Nitrogen tank and vaporizer moved together; feed enters off-gas building; old reactor feed and opening removed','Selected tubing, equipment and existing-pipe screens pass'],
                limitations='Visual envelope checks only; no process, pressure, containment, ventilation or complete access qualification')
