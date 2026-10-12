"""Low, insulated visual interfaces from the shared duct to storage.

The valve box reserves space only: no internal valves, transfer sequence or
process performance are designed here. Dimensions are presentation allowances.
"""
import math
import itertools
import bpy
from mathutils import Vector
from .installation_piping import fillet_path, shell_mesh
from .installation_bundles import frames
from .installation_clearance import bounds, gapbox, segment_box, segdist


def arc(radius, start, end, z):
    count=max(2, math.ceil(abs(end-start)/math.radians(3)))
    return [(radius*math.cos(start+(end-start)*i/count),
             radius*math.sin(start+(end-start)*i/count), z) for i in range(count+1)]


def fuel_bundle(b, root, name, controls, site, tank=None):
    """Two heat-traced 50 mm tubes inside one continuous removable round jacket."""
    spec=site.SALT_DISTRIBUTION
    spacing=spec['fuel_pair_spacing'];od=site.PROCESS_ANNEX['liquid_pipe_od']
    insulation=site.PROCESS_ANNEX['liquid_insulation'];clad=.001
    inner=spacing/2+od/2+.002;outer=inner+insulation
    points,radii=fillet_path(controls,.30);ff=frames(points);members=[]
    for sign,kind in [(-1,'supply'),(1,'return')]:
        pp=[p+side*(sign*spacing/2) for p,(side,up) in zip(points,ff)]
        # Wall is deliberately not selected by this visualization; solid tube envelopes.
        tube=b.tube(name+'.'+kind,root,pp,od/2,'fuel_'+kind)
        tube['bare_od_m']=od;tube['heat_traced']=True;tube['service']='fuel '+kind
        trace=b.tube(name+'.'+kind+'_electric_trace',root,
            [p+up*(od/2+.001) for p,(side,up) in zip(pp,ff)],.001,'fuel_trace')
        trace['role']='Electrical resistance tape envelope; duty not sized'
        members.append(dict(name=tube.name,service=kind,points=[list(q) for q in pp],bare_od_m=od,heated=True))
    ins=shell_mesh(b,name+'.insulation',root,points,outer,inner,'fuel_bundle_insulation')
    ob=shell_mesh(b,name+'.cladding',root,points,outer+clad,outer,'fuel_bundle_cladding')
    for obj in (ins,ob):
        obj['role']='Common insulated heated fuel supply/return bundle';obj['heat_traced']=True
        obj['minimum_insulation_m']=insulation;obj['paired_tube_od_m']=od
    # Removable cladding bands distinguish insulation from the bare colored tubing.
    distance=0.;next_band=.6
    for i,(u,v) in enumerate(zip(points,points[1:])):
        length=(v-u).length
        while next_band<=distance+length:
            f=(next_band-distance)/length;p=u.lerp(v,f);axis=(v-u).normalized()
            band=shell_mesh(b,name+'.jacket_band',root,[p-axis*.012,p+axis*.012],outer+clad+.002,outer+clad,'rail')
            next_band+=2.0
        distance+=length
    return dict(name=ob.name,service='Paired heated fuel supply / return',tank=tank,
        points=[list(q) for q in points],controls=[list(q) for q in controls],outside_envelope_m=2*(outer+clad),
        insulation_m=insulation,heated=True,members=members,pair_spacing_m=spacing,
        minimum_bend_radius_m=min(radii) if radii else None)


def build_salt_distribution(b, site, installation, annex):
    cfg=site.SALT_DISTRIBUTION;floor=site.PAD_Z
    root=b.assembly('site.salt_distribution','Salt storage distribution')
    b.material('valve_box','#8A9EAA',metallic=.6,roughness=.35)
    box=b.box('fuel_valve_box',root,cfg['valve_box_size'],cfg['valve_box_centre'],'valve_box',.06)
    box['scope']='Insulated valve-box space reservation; internal circuit and valves unspecified'
    box['insulated']=True
    x,y,z=cfg['valve_box_centre'];dx,dy,dz=cfg['valve_box_size']
    b.box('valve_box_removable_lid',root,(dx+.06,dy+.06,.06),(x,y,z+dz/2+.03),'rail',.025)
    for yy in (y-dy/2+.2,y+dy/2-.2):
        b.box('valve_box_skid'+str(yy),root,(dx+.12,.12,.08),(x,yy,floor+.04),'rail')
    for key,color,metal in [('fuel_bundle_cladding','#BCC5CC',.65),('fuel_bundle_insulation','#E3D7B7',0),('fuel_trace','#A25835',.5)]:
        b.material(key,color,metallic=metal,roughness=.4)
    routes=[];assignments=[];diameter=site.PROCESS_ANNEX['liquid_pipe_od']+2*site.PROCESS_ANNEX['liquid_insulation']
    def pipe(name,controls,material,service,tank=None):
        points,radii=fillet_path(controls,.20)
        ob=b.tube(name,root,points,diameter/2,material)
        ob['salt_distribution_route']=True;ob['insulated']=True;ob['heat_traced']=True
        ob['bare_od_m']=site.PROCESS_ANNEX['liquid_pipe_od'];ob['radial_insulation_m']=site.PROCESS_ANNEX['liquid_insulation']
        ob['service']=service;ob['scope']='Insulated outer envelope; pipe, heat trace, supports and pressure design provisional'
        entry=dict(name=ob.name,service=service,tank=tank,points=[list(q) for q in points],controls=[list(q) for q in controls],
                   outside_envelope_m=diameter,insulation_m=site.PROCESS_ANNEX['liquid_insulation'],heated=True,
                   minimum_bend_radius_m=min(radii) if radii else None)
        routes.append(entry)
        return entry
    # Remove the now-connected reactor-side caps; the former refiner return cap
    # is replaced by the paired interface below.
    for suffix in ('Fuel_reactor_side_tie_in','Fuel_return_reactor_tie_in','Coolant_reactor_side_tie_in'):
        ob=bpy.data.objects.get('site.process_services.'+suffix)
        if ob:bpy.data.objects.remove(ob,do_unlink=True)
    low=floor+cfg['fuel_centre_height']
    north=y+dy/2
    # Replace both separate fuel envelopes with one continuous bundle, from the
    # paired process interface in the refiner through the duct to the valve box.
    for ob in list(bpy.data.objects):
        if ob.name.startswith('site.process_services.') and (
            ob.name.split('.')[-1] in ('Fuel_liquid_supply','Fuel_liquid_return','Fuel_return_refiner_tie_in')
            or 'fuel_direction_' in ob.name):bpy.data.objects.remove(ob,do_unlink=True)
    annex['routes']=[r for r in annex['routes'] if not r['name'].endswith(('Fuel_liquid_supply','Fuel_liquid_return'))]
    # Return terminal is reserved beside the existing supply-pump face. Internal
    # refiner circuitry remains unspecified. Bundle stays paired at that interface.
    main=fuel_bundle(b,root,'refiner_to_distributor',[
        (7.5,27.225,floor+.70),(7.5,26.7,floor+.70),
        (7.5,26.7,-5.35),(4.55,26.7,-5.35),(4.55,25.7,-5.35),
        (4.55,25.7,-4.85),(4.55,16.5,-4.85),
        (4.55,16.5,low),(0,16.5,low),(0,north,low)],site)
    routes.append(main)
    annex['tie_ins']['fuel_liquid']=main['members'][0]['points'][0]
    annex['tie_ins']['fuel_return_refiner']=main['members'][1]['points'][0]
    annex['tie_ins'].pop('fuel_return_reactor',None)
    annex['fuel_routing_owner']='salt_distribution: continuous paired insulated bundle'
    bpy.context.view_layer.update()
    for tank_index,r,direction in [(1,9.5,1),(2,9.1,1),(3,8.5,1),(4,8.1,1),(6,9.65,-1),(5,9.25,-1)]:
        tank=bpy.data.objects[f'equipment.fuel_storage_{tank_index}']
        port=tank.matrix_world@Vector((-installation.FUEL_STORAGE['length']/2,0,0));port.z=low
        end_angle=math.atan2(port.y,port.x)
        if direction==1 and end_angle<0:end_angle+=math.tau
        start_angle=math.acos(-direction*1.1/r)
        curve=arc(r,start_angle,end_angle,low)
        controls=[(-direction*dx/2,curve[0][1],low),*curve,tuple(port)]
        entry=fuel_bundle(b,root,f'tank_{tank_index}_pair',controls,site,tank_index)
        entry['tank_port']=list(port);entry['valve_port']=list(controls[0]);routes.append(entry)
        for member in entry['members']:
            assignments.append(dict(tank=tank_index,service=member['service'],route=member['name']))
    # The coolant line is slightly higher at crossings, but remains below 0.5 m
    # over the long floor run and underneath the storage tank's bottom jacket.
    c=annex['tie_ins']['coolant_liquid'];cz=floor+cfg['coolant_centre_height'];r=10.1
    a=math.acos(3.8/r)
    tx,ty,tz=installation.COOLANT_STORAGE['position'];port=(tx,ty+.60,tz)
    controls=[c,(5.3,18.5,-4.1),(5.3,17.,-4.1),(3.8,16.5,-4.1),(3.8,16.5,cz),*arc(r,a,math.radians(-20),cz),
              (10.,-4.2,cz),(tx,-4.2,cz),(tx,port[1],cz),port]
    coolant=pipe('duct_to_coolant_storage',controls,'coolant_supply','Coolant supply: shared duct to storage bottom')
    coolant['tank_port']=list(port)
    # Independent bottom nozzle alongside the existing reactor-transfer nozzle.
    # Openings affect the composed site copy only.
    from .installation_utilities import cut
    targets=[bpy.data.objects['equipment.coolant_storage.'+suffix] for suffix in ('closed_tank','bottom_insulation','bottom_cladding')]
    cut(b,'coolant_bottom_nozzle_opening',root,[(port[0],port[1],tz-.43),(port[0],port[1],tz+.08)],diameter/2+.012,targets)
    for entry in routes:
        # Small representative saddles on straight floor sections, not qualified supports.
        for i,(u,v) in enumerate(zip(entry['controls'],entry['controls'][1:])):
            if abs(u[2]-v[2])<1e-5 and floor+.15<u[2]<floor+.5 and (Vector(v)-Vector(u)).length>2:
                mid=(Vector(u)+Vector(v))/2;h=mid.z-entry['outside_envelope_m']/2-floor
                b.box(entry['name'].split('.')[-1]+'_saddle_'+str(i),root,(.18,.18,h),(mid.x,mid.y,floor+h/2),'rail',.015)
    return dict(parameters=cfg,routes=routes,assignments=assignments,coolant_bottom_port=list(port),valve_box=box.name,
                scope='Visual insulated routing and box envelope; no valve internals, flow sizing, pressure/shielding design or transfer operating sequence')


def check_salt_distribution(result,site,annex):
    """Selected geometry and connectivity; do not qualify an operating system."""
    saved=[(o,o.hide_viewport) for o in [*bpy.data.collections,*bpy.data.objects]]
    for o,_ in saved:o.hide_viewport=False
    bpy.context.view_layer.update()
    routes=result['routes'];assert len(routes)==8
    assert len([q for q in routes if 'members' in q])==7
    for q in routes:
        if 'members' not in q:continue
        assert len(q['members'])==2 and q['heated'] and q['insulation_m']==.05
        for a,c in zip(q['members'][0]['points'],q['members'][1]['points']):
            assert abs((Vector(a)-Vector(c)).length-q['pair_spacing_m'])<1e-5
        assert q['outside_envelope_m']/2-q['pair_spacing_m']/2-.025>=.05
    assert sorted((a['tank'],a['service']) for a in result['assignments'])==sorted(itertools.product(range(1,7),('supply','return')))
    radius=max(q['outside_envelope_m']/2 for q in routes)
    collisions=[]
    def route_gap(a,c):
        best=1e6;rr=a['radius']+c['radius']
        if gapbox(a['bounds'],c['bounds'])>rr+.1:return best
        for u,v,bb in a['segments']:
            for w,x,bc in c['segments']:
                if gapbox(bb,bc)>rr+.1:continue
                best=min(best,segdist(u,v,w,x)[0]-rr)
        return best
    def prepared(name,points,r):
        pts=[Vector(q) for q in points]
        return dict(name=name,points=pts,radius=r,bounds=bounds(pts),segments=[(u,v,bounds([u,v])) for u,v in zip(pts,pts[1:])])
    new=[prepared(q['name'],q['points'],q['outside_envelope_m']/2) for q in routes]
    gaps=[]
    for a,c in itertools.combinations(new,2):
        g=route_gap(a,c);gaps.append(g)
        if g<-.001:collisions.append((a['name'],c['name'],g))
    existing=[]
    for ob in bpy.data.objects:
        if ob.type=='CURVE' and (ob.get('process_route') or ob.get('air_insulated') or ob.get('utility_route') or ob.name.startswith('connections.air.')):
            for sp in ob.data.splines:
                existing.append(prepared(ob.name,[ob.matrix_world@Vector(q.co[:3]) for q in sp.points],ob.data.bevel_depth))
    annex_routes=[prepared(q['name'],q['points'],q['outside_envelope_m']/2) for q in annex['routes']]
    joins={'duct_to_valve_supply':'Fuel_liquid_supply','valve_to_duct_return':'Fuel_liquid_return','duct_to_coolant_storage':'Coolant_liquid_supply'}
    for a in new:
        for c in annex_routes:
            if joins.get(a['name'].split('.')[-1])==c['name'].split('.')[-1]:continue
            g=route_gap(a,c)
            if g<-.001:collisions.append((a['name'],c['name'],g))
        for c in existing:
            g=route_gap(a,c)
            if g<-.001:collisions.append((a['name'],c['name'],g))
    # Equipment, support posts and stairs, including bottom tank insulation.
    boxes=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('equipment.') and not o.get('utility_opening_tool')]
    box_count=0
    for entry,a in zip(routes,new):
        radius=a['radius']
        for ob in boxes:
            # The nozzle intentionally enters its own tank. Check the rest of that
            # route against the tank; omit only the final vertical connection leg.
            pts=a['points'];own=entry.get('tank') and ob.name.startswith(f'equipment.fuel_storage_{entry["tank"]}.')
            if own and ob.name.endswith('.closed_tank'):pts=pts[:-1]
            if entry['name'].endswith('duct_to_coolant_storage') and ob.name in ('equipment.coolant_storage.closed_tank','equipment.coolant_storage.bottom_insulation','equipment.coolant_storage.bottom_cladding','equipment.coolant_storage.cladding','equipment.coolant_storage.insulation'):
                pts=[p for p in pts if p.z<=site.PAD_Z+.425]
            bc=bounds([ob.matrix_world@Vector(v) for v in ob.bound_box])
            if len(pts)<2 or gapbox(bounds(pts),bc)>radius+.03:continue
            box_count+=1;inv=ob.matrix_world.inverted();local=[inv@v for v in pts];lo,hi=bounds(ob.bound_box)
            g=min(segment_box(u,v,lo,hi) for u,v in zip(local,local[1:]))-radius
            if g<-.001:collisions.append((a['name'],ob.name,g))
    # Ground-level lines must remain inside the equipment/cart access boundary.
    for a in new:
        for x,y,z in a['points']:
            if z<site.PAD_Z+1 and x>15:assert abs(y-x*math.tan(math.radians(18)))>2.4
    for a in routes:
        assert min(p[2] for p in a['points'])-a['outside_envelope_m']/2>site.PAD_Z
        if a.get('tank'):assert max(p[2] for p in a['points'])<site.PAD_Z+.21
    coolant=next(q for q in routes if q['name'].endswith('duct_to_coolant_storage'))
    assert (Vector(coolant['points'][0])-Vector(annex['tie_ins']['coolant_liquid'])).length<1e-5
    main=routes[0];link=annex['links'][0];radius=main['outside_envelope_m']/2
    for x,y,z in main['points']:
        if link['y0']+.1<y<26.2:
            assert abs(x-link['x'])+radius<link['width']/2-.16
            assert link['floor_z']+radius<z<link['roof_z']-.16-radius
    for ob,value in saved:ob.hide_viewport=value
    bpy.context.view_layer.update()
    assert not collisions,collisions
    assert min(gaps)>.025, min(gaps)
    return dict(route_count=len(routes),heated_fuel_bundles=7,fuel_tube_count=14,fuel_tank_pairs=6,selected_equipment_tests=box_count,unresolved_clashes=collisions,
                minimum_new_line_gap_m=min(gaps),fuel_floor_centre_height_m=site.SALT_DISTRIBUTION['fuel_centre_height'],coolant_floor_centre_height_m=site.SALT_DISTRIBUTION['coolant_centre_height'],
                checks=['Six separate supply/return pairs connect valve box to low inner ends of tanks','Coolant reaches an independent bottom tank nozzle','Seven common fuel jackets contain 14 continuous heat-traced tubes; pair spacing and minimum insulation checked','Fuel bundle fits the shared duct; coolant terminal matches exactly','Selected pipe, equipment, support and stair screens pass','Main equipment-door approach remains clear'],
                limitations='Selected envelope screening, not a full plant/access, thermal, structural or process qualification')
