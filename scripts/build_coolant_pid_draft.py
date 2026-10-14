"""Reconcile coolant P&ID identities with an inspectable 3D draft."""
import argparse,csv,hashlib,json,math,sys,tomllib
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/p) for p in ('src','models','scripts')]
import wistr_coolant_pid_draft as cfg
import wistr_installation as layout
import wistr_site as site
import nitrogen_draft
from textual_graphics.shared_coolant import HUB,coolant,ENGINEERING
from textual_graphics.installation_utilities import cut,service_line,polar
from textual_graphics.installation_piping import fillet_path,shell_mesh
from textual_graphics.installation_stairs import prism
from textual_graphics.site_fresh_air import outer_radius,inner_radius
from textual_graphics.installation_clearance import bounds,gapbox,segment_box,segdist
from build_tank_bay_draft import builder,remove_prefix
from build_attached_services_draft import fingerprint
from build_compact_services_draft import view as compact_view
from build_wistr import camera
F=layout.FLOOR_Z
GROUPS=('equipment','boundaries','lines','valves','instruments','relief_devices')

def model():
    raw=tomllib.loads((HUB/cfg.PID).read_text());return coolant.merge_pid(raw,ENGINEERING)

def points(ob):return [ob.matrix_world@Vector(q.co[:3]) for q in ob.data.splines[0].points]

def bind(data,group,tag,objects,representation='modeled',note=''):
    record=data['model'][group][tag]
    for name in objects:
        ob=bpy.data.objects[name];ob['pid_tag']=tag;ob['pid_group']=group;ob['pid_status']=record.get('status','concept interface')
        ob['pid_representation']=representation
        if 'from' in record:ob['pid_from']=record['from'];ob['pid_to']=record['to']
        if 'line' in record:ob['pid_line']=record['line']
        if 'on' in record:ob['pid_on']=record['on']
    data['coverage'].append(dict(group=group,tag=tag,objects=objects,status=record.get('status','concept interface'),representation=representation,note=note))

def trim_air(b):
    p=site.FRESH_AIR;recesses=[]
    for ob in bpy.data.objects:
        if ob.type=='MESH' and ob.name.startswith('building.shell.pilaster'):
            vs=[ob.matrix_world@v.co for v in ob.data.vertices];c=sum(vs,Vector())/len(vs)
            recesses.append(dict(angle=math.degrees(math.atan2(c.y,c.x))%360,radius=min(math.hypot(v.x,v.y) for v in vs)-.06))
    root=bpy.data.objects['site.fresh_air'];toolroot=b.assembly('draft.pid_openings','Coolant PID opening tools')
    start=27.194199187148484;end=cfg.FRESH_HEADER_END_ANGLE
    poly=[(0,0)]+[polar(24,start-.1+(end-start+.1)*i/120,0)[:2] for i in range(121)]
    tool=prism(b,'remove_unused_air_section',toolroot,poly,F-.2,F+3,None);tool.hide_render=True;tool.hide_set(True);tool['utility_opening_tool']=True
    for ob in list(root.children):
        if ob.get('fresh_header_part') in ('floor','roof','inner','outer') and ob.name.endswith(str(start)):
            m=ob.modifiers.new('Shorten fresh-air header to SG-102','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=tool
        if ob.name=='site.fresh_air.door_end_1' or (ob.name.startswith('site.fresh_air.bearing_') and start<float(ob.name.rsplit('_',1)[1])<end):bpy.data.objects.remove(ob,do_unlink=True)
    ro=outer_radius(end,p,recesses);ri=inner_radius(end,p,recesses);low=F+p['base_height'];high=low+p['clear_height']+2*p['wall']
    cap=b.box('sg102_end',root,(ro-ri,p['wall'],high-low),polar((ro+ri)/2,end,(high+low)/2),'fresh_duct');cap.rotation_euler.z=math.radians(end);cap['fresh_header_part']='end'
    branches=[]
    for ob in bpy.data.objects:
        if ob.type=='CURVE' and ob.get('fresh_internal_branch'):
            q=points(ob)[-1];angle=math.degrees(math.atan2(q.y,q.x))%360
            assert not start<angle<end,(ob.name,'removed connection')
            branches.append(dict(name=ob.name,angle_deg=angle))
    assert len(branches)==10
    return dict(removed_angles_deg=[start,end],retained_equipment_branches=branches,new_end_cap=cap.name)

def lower_transfer(b,data):
    root=bpy.data.objects['connections.coolant_transfer'];old=bpy.data.objects[root.name+'.reactor_to_pump'];tap=points(old)[0];spec=dict(old['pipe_spec'])
    pump=bpy.data.objects['equipment.coolant_transfer_pump'];inlet=pump.matrix_world@Vector((-.225,0,0));outlet=pump.matrix_world@Vector((.225,0,0))
    tee=(18.5,18.5,F+cfg.TEE_HEIGHT)
    # The retained under-vessel clearance fixes the inner line at 0.40 m.
    # Runs outside the pump and from preparation fall to the lower common tee.
    paths={
       'L-401':('reactor_to_pump',[tap,(tap.x,tap.y,F+.40),polar(16.4,45,F+.40),polar(21.4,45,F+.40),(17.6,13.1,F+.40),(20.5,13.1,F+.40),inlet]),
       'L-402':('pump_to_storage',[outlet,(18.5,outlet.y,F+.28),tee]),
       'L-403':('preparation_to_tee',[(18.5,26.225,F+.70),(18.5,25.7,F+.65),(18.5,23.4,F+.40),tee]),
       'L-404':('tank_bottom_nozzle',[tee,(18.5,18.5,F+.9)])}
    for tag,(name,controls) in paths.items():
        remove_prefix(root.name+'.'+name);ob=service_line(b,name,root,controls,spec);ob['flow_direction']='bidirectional'
        bind(data,'lines',tag,[ob.name,ob.name+'.metal',ob.name+'.insulation'])
        data['routes'][tag]=dict(name=ob.name,points=[list(q) for q in points(ob)],radius=spec['jacket_od']/2,controls=[list(q) for q in controls])
    remove_prefix('utilities.penetrations.draft_transfer_reactor_wall');remove_prefix('utilities.penetrations.reactor_wall_sleeve')
    remove_prefix('draft.attached_openings.compact_preparation_entry')
    tools=bpy.data.objects['draft.pid_openings']
    walls=[bpy.data.objects[n] for n in ('building.shell.retained_wall','draft.shared_wall_display.tank')]
    cut(b,'low_transfer_wall',tools,[polar(20.1,45,F+.4),polar(21.7,45,F+.4)],.11,walls)
    # Sloping preparation line through the north enclosure wall.
    def prep_z(y):return F+.40+(y-23.4)*(.65-.40)/(25.7-23.4)
    cut(b,'low_preparation_wall',tools,[(18.5,24.2,prep_z(24.2)),(18.5,25.,prep_z(25.))],.11,[bpy.data.objects['site.coolant_silo_curve.wall_rear']])
    j=b.assembly('coolant.pid.J-401','Coolant PID',tee);b.cylinder('tee_envelope',j,.09,.19,(0,0,0),'cold',vertices=24,bevel=0)
    bind(data,'equipment','J-401',[j.name]);data['tee']=tee
    return paths

def route(b,data,tag,controls,od,insulation=.025,group='lines',rounded=True):
    root=bpy.data.objects['coolant.pid.routes'];pts,radii=fillet_path(controls,.16) if rounded else ([Vector(q) for q in controls],[])
    ob=b.tube(tag,root,pts,od/2+insulation,'pid_gas');ob['coolant_only_gas']=tag.startswith('G-') or tag=='H-401';ob['nominal_visual_od_m']=od;ob['visual_insulation_m']=insulation
    ob['engineering_dimensions']='Unresolved; displayed dimensions are spatial reservations'
    bind(data,group,tag,[ob.name],'spatial_reservation','Unresolved dimensions retained in P&ID')
    data['routes'][tag]=dict(name=ob.name,points=[list(q) for q in pts],radius=od/2+insulation,controls=[list(q) for q in controls])
    return ob

def gas_geometry(b,data):
    g=cfg.GAS;b.assembly('coolant.pid.routes','Coolant gas piping');headerpts=[polar(g['header_radius'],a,g['header_z']) for a in range(45,301)]
    top=headerpts[0];base=(*top[:2],F+1.4);common=g['common_tee']
    headerpts=list(reversed(headerpts))+[base,polar(21.5,45,F+1.4),(13.6,17.8,F+1.4),common]
    # Round the riser/bottom corners separately, retaining sampled smooth arc.
    turn,_=fillet_path([top,base,polar(21.5,45,F+1.4),(13.6,17.8,F+1.4),common],.18)
    headerpts=[polar(g['header_radius'],a,g['header_z']) for a in range(300,44,-1)]+list(turn)[1:]
    route(b,data,'H-401',headerpts,g['header_od'],g['insulation'],group='equipment',rounded=False)
    ports={};tools=bpy.data.objects['draft.pid_openings']
    for i in (1,2,3):
        tag=f'AC-10{i}';sg=bpy.data.objects[f'equipment.steam_generator_{i}'];w=lambda q:tuple(sg.matrix_world@Vector(q));xy=g['accumulator_xy_local'];bottom=g['accumulator_bottom_local'];h=g['accumulator_height']
        root=b.assembly('coolant.pid.'+tag,'Coolant gas vessels',w((*xy,bottom)))
        b.cylinder('vessel_envelope',root,g['accumulator_diameter']/2,h,(0,0,h/2),'pid_gas',vertices=48,bevel=.07)
        b.cylinder('top_head',root,.24,.08,(0,0,h+.02),'rail',vertices=48)
        # Small support reservation, attached to the SG casing top.
        support=b.box('support_reservation',sg,(.8,1.0,.10),(xy[0],-2.2,17.55),'rail')
        support['scope']='Nominal support reservation; not a load-rated design'
        cut(b,'sg_gas_support_'+str(i),tools,[w((*xy,17.4)),w((*xy,17.7))],.13,[support])
        bind(data,'equipment',tag,[root.name],'spatial_reservation','Nominal 0.60 m diameter × 1 m vessel; capacity unresolved')
        start=w(g['gas_takeoff_local']);saltend=w((*xy,bottom))
        route(b,data,f'L-10{i}G',[start,w((xy[0],-2.1,17.3)),w((*xy,17.3)),saltend],.05,.05)
        cut(b,'sg_gas_'+str(i),tools,[start,w((xy[0],-2.1,17.4))],.105,[bpy.data.objects[f'equipment.steam_generator_{i}.hot_manifold']])
        gasstart=w((*xy,bottom+h));vertical=(*gasstart[:2],g['header_z']);angle=layout.STEAM_GENERATORS['angles'][i-1]
        end=polar(g['header_radius'],angle,g['header_z']);route(b,data,f'G-10{i}',[gasstart,vertical,end],g['branch_od'],g['insulation'])
        ports[tag]={'bottom':saltend,'top':gasstart,'root':root.name}
        # Separate unsized relief takeoff. It ends at a local unresolved interface marker.
        reliefstart=w((-.05,-2.55,16.39));reliefend=w((-.05,-4.5,17.4))
        route(b,data,f'L-10{i}R',[reliefstart,w((-.05,-2.55,17.4)),reliefend],cfg.RELIEF['display_od'],0)
        data['coverage'][-1]['representation']='interface_stub';data['coverage'][-1]['note']=cfg.RELIEF['scope']
        cut(b,'sg_relief_'+str(i),tools,[reliefstart,w((-.05,-2.55,17.45))],.085,[bpy.data.objects[f'equipment.steam_generator_{i}.hot_manifold']])
        marker=b.assembly(f'coolant.pid.B-501.sg10{i}','Unresolved coolant interfaces',reliefend)
        for axis in ((.25,0,0),(0,.25,0),(0,0,.25)):
            b.beam('interface_'+str(axis),marker,tuple(-v for v in axis),axis,.025,'pid_unresolved')
        marker['scope']='Unresolved discharge destination; no receiver or release path selected';ports[f'B-501.sg10{i}']=marker.name
    # The tank-top nozzle is distinct from its existing access cover.
    tanktop=(17.3,18.5,F+.9+16+.065+.351)
    route(b,data,'G-402',[tanktop,(17.3,18.5,9.3),(14.1,20.,9.3),(14.1,20.,F+1.65),(14.1,21.5,F+1.65),(14.1,21.5,F+1.4),common],g['branch_od'],g['insulation'])
    tankpieces=[bpy.data.objects['equipment.coolant_storage.'+n] for n in ('roof','top_insulation','top_cladding')]
    cut(b,'tank_top_gas',tools,[(17.3,18.5,F+.9+15.98),(17.3,18.5,tanktop[2]+.2)],.065,tankpieces)
    panel=g['panel'];root=b.assembly('coolant.pid.B-401','Coolant pressure-control station',panel)
    b.box('station_envelope',root,(.9,.45,1.0),(0,.225,0),'pid_gas',.04)
    for x in (-.32,.32):b.box('leg'+str(x),root,(.06,.06,.9),(x,.22,-.95),'rail')
    bind(data,'boundaries','B-401',[root.name],'functional_envelope','Coolant-only makeup/return station; internal hardware unresolved')
    bind(data,'boundaries','B-501',[ports[f'B-501.sg10{i}'] for i in (1,2,3)],'unresolved_interface','Three separate marked terminations; no common relief receiver selected')
    route(b,data,'G-400',[common,(13.7,24,F+1.4),(14.4,24,F+1.4),panel],g['header_od'],g['insulation'])
    cut(b,'gas_common_wall',tools,[polar(20.1,45,F+1.4),polar(21.7,45,F+1.4)],.09,[bpy.data.objects[n] for n in ('building.shell.retained_wall','draft.shared_wall_display.tank')])
    cut(b,'gas_preparation_wall',tools,[(13.7,21.6,F+1.4),(13.7,23.5,F+1.4)],.065,[bpy.data.objects['site.coolant_silo_curve.wall_rear']])
    data['gas_ports']=ports

def locate(route,fraction):
    pts=[Vector(q) for q in route['points']];lengths=[(c-a).length for a,c in zip(pts,pts[1:])];at=sum(lengths)*fraction
    for a,c,length in zip(pts,pts[1:],lengths):
        if at<=length:return a.lerp(c,at/length),(c-a).normalized()
        at-=length
    return pts[-1],(pts[-1]-pts[-2]).normalized()

def collar(b,name,root,position,tangent,inner,outer,width,mat):
    ob=b.annulus(name,root,inner,outer,-width/2,width/2,mat,steps=32)
    ob.location=position;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Vector((0,0,1)).rotation_difference(tangent)
    return ob

def symbols(b,data):
    root=b.assembly('coolant.pid.symbols','Coolant PID reservations');allmodel=data['model']
    for tag,record in allmodel['valves'].items():
        line=record['line'];q,t=locate(data['routes'][line],.28 if line.startswith('G-10') else .70 if line=='G-402' else .50)
        if tag in data.get('nitrogen_valve_positions',{}):q=Vector(data['nitrogen_valve_positions'][tag]);t=Vector((0,0,-1))
        radius=data['routes'][line]['radius'];normal=Vector((0,0,1)) if abs(t.z)<.8 else Vector((1,0,0))
        mat='pid_proposed' if record['status']=='proposed' else 'pid_gas';base=collar(b,tag,root,q,t,radius+.003,radius+.055,.12,mat)
        b.beam(tag+'.stem',root,q+normal*(radius+.03),q+normal*(radius+.25),.025,mat)
        b.box(tag+'.actuator_reservation',root,(.25,.20,.16),q+normal*(radius+.30),mat,.02)
        bind(data,'valves',tag,[base.name],'spatial_reservation','Generic valve location; type, actuator, bore and fail position unresolved')
    for tag,record in allmodel['relief_devices'].items():
        q,t=locate(data['routes'][record['line']],.65);r=data['routes'][record['line']]['radius'];ob=collar(b,tag,root,q,t,r,r+.055,.10,'pid_unresolved')
        bind(data,'relief_devices',tag,[ob.name],'spatial_reservation',cfg.RELIEF['scope'])
    for tag,record in allmodel['instruments'].items():
        on=record['on'];normal=Vector((0,0,1));rad=0
        if on in data['routes']:
            route=data['routes'][on]
            if tag.endswith('S') and on.startswith('L-20'):route=data['cold_suction'][on]
            fraction=.26 if tag.startswith('TT') else .40 if tag.startswith('FT') else .74
            q,t=locate(route,fraction);rad=route['radius'];normal=Vector((0,0,1)) if abs(t.z)<.8 else Vector((1,0,0))
        elif on.startswith('AC-'):
            q=Vector(data['gas_ports'][on]['top']);q.z-=.25 if tag.startswith('PT') else .75;normal=Vector((1,0,0));rad=.30
        elif on=='TK-401':
            q=Vector((18.5,18.5,F+(.9+16 if tag.startswith('PT') else 13 if tag.startswith('LT') else 7)));normal=Vector((1,0,0));rad=4.451
        else:raise ValueError((tag,'unknown physical association',on))
        mat='pid_proposed' if record['status']=='proposed' else 'pid_gas';base=q+normal*(rad+.04);head=base+normal*.23
        b.beam(tag+'.mount_reservation',root,base,head,.018,mat)
        ob=b.box(tag,root,(.19,.16,.19),head,mat,.025)
        bind(data,'instruments',tag,[ob.name],'measurement_location','Technology unresolved; no specific sensor, impulse piping or wiring implied')

def existing(b,data):
    mapping={'R-101':'reactor.vessel','TK-401':'equipment.coolant_storage','P-401':'equipment.coolant_transfer_pump'}
    for i in (1,2,3):mapping[f'SG-10{i}']=f'equipment.steam_generator_{i}';mapping[f'P-10{i}']=f'equipment.coolant_pump_{i}'
    for tag,name in mapping.items():
        if name not in bpy.data.objects and tag.startswith('P-10'):
            candidates=[o for o in bpy.data.objects if o.type=='EMPTY' and 'pump' in o.name and o.name.endswith('_'+tag[-1])];assert len(candidates)==1,(tag,[o.name for o in candidates]);name=candidates[0].name
        bind(data,'equipment',tag,[name])
        if tag.startswith('P-10'):
            ob=bpy.data.objects[name];record=data['model']['equipment'][tag]
            for key in ('flow_m3_s','pressure_rise_pa','motor_rating_kw','electrical_kw'):ob[key]=record[key]
            ob['shaft_demand_kw']=record['shaft_kw']
    for i in (1,2,3):
        for tag,name in [(f'L-10{i}',f'connections.loop_{i}.hot_outlet'),(f'L-20{i}',f'connections.loop_{i}.cold_inlet')]:
            ob=bpy.data.objects[name];objects=[name,name+'.metal',name+'.insulation']
            if tag.startswith('L-20'):objects.extend(f'connections.loop_{i}.cold_suction'+s for s in ('','.metal','.insulation'))
            bind(data,'lines',tag,objects)
            data['routes'][tag]=dict(name=name,points=[list(q) for q in points(ob)],radius=ob.data.bevel_depth)
        ob=bpy.data.objects[f'connections.loop_{i}.cold_suction'];data['cold_suction'][f'L-20{i}']=dict(name=ob.name,points=[list(q) for q in points(ob)],radius=ob.data.bevel_depth)

def topology_check(data):
    expected={
      'L-401':('R-101.bottom','P-401.reactor_side',[]),
      'L-402':('P-401.storage_side','J-401.pump',[]),
      'L-403':('B-401.salt_transfer','J-401.preparation',[]),
      'L-404':('J-401.tank','TK-401.bottom',[]),
      'G-402':('TK-401.gas_return','H-401.tank',[]),
      'G-400':('H-401.preparation','B-401.coolant_gas',[]),
      'N-600':('B-601.gas_supply','H-601.supply',[]),
      'N-601':('H-601.offgas','B-602.nitrogen_makeup',[]),
      'N-602':('H-601.fuel','B-603.nitrogen_makeup',[]),
      'N-603':('H-601.coolant','B-401.nitrogen_makeup',[])}
    for i in (1,2,3):
        expected.update({f'L-10{i}':(f'R-101.H{i}',f'SG-10{i}.salt_inlet',[]),
          f'L-20{i}':(f'SG-10{i}.salt_outlet',f'R-101.C{i}',[f'P-10{i}']),
          f'L-10{i}G':(f'SG-10{i}.gas_top',f'AC-10{i}.salt',[]),
          f'G-10{i}':(f'AC-10{i}.gas',f'H-401.sg{i}',[]),
          f'L-10{i}R':(f'SG-10{i}.relief_high',f'B-501.sg10{i}',[])})
    assert set(expected)==set(data['model']['lines'])
    for tag,(a,c,via) in expected.items():
        m=data['model']['lines'][tag];assert (m['from'],m['to'],m['via'])==(a,c,via),(tag,'P&ID topology changed; revise physical routing')
    header=[Vector(q) for q in data['routes']['H-401']['points']]
    for tag in ('G-101','G-102','G-103','G-402','G-400'):
        q=Vector(data['routes'][tag]['points'][0 if tag=='G-400' else -1])
        assert min(segdist(q,q,a,c)[0] for a,c in zip(header,header[1:]))<1e-5,(tag,'header disconnected')
    for i in (1,2,3):
        port=data['gas_ports'][f'AC-10{i}']
        assert math.dist(data['routes'][f'L-10{i}G']['points'][-1],port['bottom'])<1e-5
        assert math.dist(data['routes'][f'G-10{i}']['points'][0],port['top'])<1e-5
    return dict(line_topologies_checked=len(expected),header_joins_checked=5,accumulator_terminals_checked=6)


def route_pair_check(data):
    names=[tag for tag in data['routes'] if tag not in ('L-101','L-102','L-103','L-201','L-202','L-203')]
    clashes=[];tests=0
    for i,tag in enumerate(names):
        a=data['routes'][tag]
        for other in names[i+1:]:
            c=data['routes'][other];radius=a['radius']+c['radius']
            if gapbox(bounds(a['points']),bounds(c['points']))>radius:continue
            joins=[]
            if tag in ('L-402','L-403','L-404') and other in ('L-402','L-403','L-404'):joins=[Vector(data['tee'])]
            if 'H-401' in (tag,other):
                g=other if tag=='H-401' else tag
                if g in ('G-101','G-102','G-103','G-402','G-400'):joins=[Vector(data['routes'][g]['points'][0 if g=='G-400' else -1])]
            if 'H-601' in (tag,other):
                n=other if tag=='H-601' else tag
                if n.startswith('N-60'):joins=[Vector(data['routes'][n]['points'][-1 if n=='N-600' else 0])]
            if {tag,other}=={'G-402','G-400'}:joins=[Vector(cfg.GAS['common_tee'])]
            tests+=1
            for u,v in zip(a['points'],a['points'][1:]):
                for w,x in zip(c['points'],c['points'][1:]):
                    if gapbox(bounds([u,v]),bounds([w,x]))>radius:continue
                    dist,pa,pc=segdist(u,v,w,x)
                    if dist>=radius-.004:continue
                    if any((Vector(pa)-j).length<.25 and (Vector(pc)-j).length<.25 for j in joins):continue
                    clashes.append((tag,other,dist-radius));break
                if clashes and clashes[-1][:2]==(tag,other):break
    assert not clashes,clashes
    return dict(route_pairs_checked=tests,clashes=[])


def coverage_check(data):
    expected={(g,t) for g in GROUPS for t in data['model'][g]};actual=[(q['group'],q['tag']) for q in data['coverage']]
    assert len(actual)==len(set(actual)) and set(actual)==expected,(expected-set(actual),set(actual)-expected)
    for record in data['coverage']:
        assert record['objects'] and all(name in bpy.data.objects for name in record['objects'])
    assert 'G-401' not in data['routes']
    # No valve can accidentally isolate a continuously open SG/accumulator connection.
    assert not any(q['line'].endswith('G') for q in data['model']['valves'].values())
    tee=data['tee'][2];lows={tag:min(q[2] for q in data['routes'][tag]['points']) for tag in ('L-401','L-402','L-403','L-404')}
    assert min(lows.values())>=tee-2e-6 and lows['L-401']>tee+.15
    for tag in ('L-401','L-402','L-403'):
        pts=data['routes'][tag]['points'];assert all(c[2]<=a[2]+2e-6 for a,c in zip(pts,pts[1:])),(tag,'unintended rise')
    # Existing horizontal under-vessel line is explicit, not claimed gravity-draining.
    return dict(counts={g:len(data['model'][g]) for g in GROUPS},represented=len(actual),missing=[],lowest_transfer_centreline_z=tee,
                tee_height_above_floor_m=tee-F,lowest_line_centrelines=lows,low_route_scope='No reverse rise; L-401 retains a level under-vessel/pump run. Complete drainage is not established.')

def clash_check(data):
    deps=bpy.context.evaluated_depsgraph_get();obstacles=[]
    newtags=set(data['routes'])-{'L-101','L-102','L-103','L-201','L-202','L-203'}
    for ob in bpy.data.objects:
        if ob.type not in ('MESH','CURVE') or (ob.hide_render and not (ob.get('annex_outer_wall') or ob.get('site_roof'))) or ob.get('utility_opening_tool') or ob.get('fresh_air_opening_tool') or ob.get('presentation_only'):continue
        if ob.name.startswith(('draft.','DraftLaydown.','utilities.penetrations.','coolant.pid.routes.','coolant.pid.symbols.','connections.coolant_transfer.')):continue
        if not ob.name.startswith(('equipment.','reactor.','connections.','site.','building.','coolant.pid.')):continue
        if ob.name.startswith(('site.ground.','site.turbine.','site.converter.','site.secondary.')):continue
        obstacles.append((ob,bounds([ob.matrix_world@Vector(v) for v in ob.bound_box])))
    cache={};clashes=[];tests=0
    for tag in sorted(newtags):
        route=data['routes'][tag];pts=[Vector(q) for q in route['points']];rad=route['radius'];bb=bounds(pts)
        for ob,bc in obstacles:
            if ob.hide_render and not (tag.startswith('N-60') or tag=='H-601'):continue
            if gapbox(bb,bc)>rad+.015:continue
            pp=pts;terminals=[]
            if ob.name.startswith('equipment.coolant_transfer_pump.') and tag in ('L-401','L-402'):terminals=[Vector((20.5,13.8,F+.4))]
            if tag=='L-404' and ob.name=='equipment.coolant_storage.closed_tank':continue
            if tag=='L-401' and ob.name in ('reactor.vessel.bottom_plate','reactor.baffle.floor_sheet','reactor.well.wall'):continue
            if tag=='L-403' and ob.name=='site.process_services.Coolant transfer pump':terminals=[pts[0]]
            if tag in ('G-400','N-603') and ob.name.startswith('coolant.pid.B-401.'):terminals=[pts[-1]]
            if tag=='N-600' and ob.name.startswith('equipment.nitrogen_supply.'):continue # Retained vaporizer/regulator skid connections
            if tag=='N-601' and ob.name.startswith('site.offgas_gas_supply.'):terminals=[pts[-1]]
            if tag=='N-602' and ob.name.startswith('site.nitrogen_fuel_station.'):terminals=[pts[-1]]
            if ob.name.startswith('site.nitrogen_distribution.'):continue # Dedicated supports/control reservations checked visually
            if tag.startswith('L-10') and tag.endswith(('G','R')):
                i=tag[4]
                if ob.name.startswith(f'equipment.steam_generator_{i}.hot_manifold'):terminals=[pts[0]]
                if ob.name.startswith(f'coolant.pid.AC-10{i}.'):terminals=[pts[-1]]
            if tag.startswith('G-10') and ob.name.startswith('coolant.pid.AC-'+tag[2:]+'.'):terminals=[pts[0]]
            if ob.name.startswith('coolant.pid.J-401.') and tag in ('L-402','L-403','L-404'):terminals=[Vector(data['tee'])]
            if ob.name.startswith('coolant.pid.B-501.') and tag.endswith('R'):terminals=[pts[-1]]
            if terminals:pp=[q for q in pts if all((q-v).length>(.65 if ob.name.startswith('equipment.coolant_transfer_pump.') else .25) for v in terminals)]
            if len(pp)<2:continue
            if all(segment_box(a,c,*bc)>rad+.015 for a,c in zip(pp,pp[1:])):continue
            if ob.name not in cache:
                ev=ob.evaluated_get(deps);mesh=ev.to_mesh();cache[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons]) if mesh and len(mesh.vertices) else None;ev.to_mesh_clear()
            tree=cache[ob.name]
            if tree is None:continue
            gap=999.;tests+=1
            for a,c in zip(pp,pp[1:]):
                if segment_box(a,c,*bc)>rad+.015:continue
                length=(c-a).length
                if length<1e-7:continue
                n=max(1,math.ceil(length/.01))
                for i in range(n+1):
                    hit=tree.find_nearest(a.lerp(c,i/n))
                    if hit[0] is not None:gap=min(gap,hit[3]-rad-length/(2*n))
                if tree.ray_cast(a,(c-a).normalized(),length)[0] is not None:gap=-rad
            if gap<-.004:clashes.append((tag,ob.name,round(gap,4)))
    return dict(selected_route_obstacle_pairs=tests,clashes=clashes,scope='Selected spatial checks; deliberate terminals excluded; valve/instrument reservations are association markers')

def write_outputs(out,data):
    (out/'coolant-pid-coverage.json').write_text(json.dumps(data,indent=2,default=list)+'\n')
    with (out/'coolant-pid-coverage.csv').open('w') as stream:
        w=csv.writer(stream);w.writerow(['group','tag','representation','source status','Blender objects','note'])
        for r in data['coverage']:w.writerow([r[k] if k!='objects' else '; '.join(r[k]) for k in ('group','tag','representation','status','objects','note')])

def main():
    p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');p.add_argument('--build-only',action='store_true');p.add_argument('--views',nargs='*');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=ROOT/cfg.OUTPUT;out.mkdir(parents=True,exist_ok=True);source=ROOT/cfg.SOURCE
    bpy.ops.wm.open_mainfile(filepath=str(out/'geometry-checkpoint.blend' if args.resume else source))
    for c in bpy.data.collections:c.hide_viewport=False
    for o in bpy.data.objects:o.hide_viewport=False
    bpy.context.view_layer.update();b=builder()
    if args.resume:data=json.loads((out/'geometry-checkpoint.json').read_text())
    else:
        data=dict(model=model(),coverage=[],routes={},cold_suction={},original_main_signature=fingerprint())
        for name,color in [('pid_gas','#397D83'),('pid_proposed','#BA8834'),('pid_unresolved','#AA567B')]:b.material(name,color,metallic=.35,roughness=.36)
        data['air']=trim_air(b);lower_transfer(b,data);existing(b,data);gas_geometry(b,data);nitrogen_draft.build(b,data,cfg,F,route,bind,remove_prefix);symbols(b,data)
        bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out/'geometry-checkpoint.blend'));(out/'geometry-checkpoint.json').write_text(json.dumps(data,default=list))
    assert fingerprint()==data['original_main_signature'],'Main circulation geometry changed'
    data['source_hashes']={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p.relative_to(HUB)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (source,Path(__file__),ROOT/'models/wistr_coolant_pid_draft.py',ROOT/'scripts/nitrogen_draft.py',HUB/cfg.PID,HUB/'design/engineering/coolant-system.toml')}
    assert data['model']==model(),'P&ID changed since checkpoint; rebuild geometry'
    data['nitrogen_checks']=nitrogen_draft.check(data,F)
    data['topology_checks']=topology_check(data);data['route_pair_checks']=route_pair_check(data)
    data['coverage_checks']=coverage_check(data);data['geometry_checks']=clash_check(data)
    write_outputs(out,data)
    assert not data['geometry_checks']['clashes'],data['geometry_checks']['clashes'][:60]
    print('COOLANT_PID_CHECKS_OK',data['coverage_checks'],flush=True)
    cams={'nitrogen-exterior':camera(b,'CoolantPID.Nitrogen',(-32,66,25),(4,28,-5),49),
          'nitrogen-cutaway':camera(b,'CoolantPID.NitrogenInside',(42,55,35),(4,28,-5),48),
          'overview':camera(b,'CoolantPID.Overview',(55,67,48),(3,8,0),70),
          'sg-detail':camera(b,'CoolantPID.SG',(-6,-3,16),(6.3,10.5,9.4),11),
          'tank-detail':camera(b,'CoolantPID.Tank',(-6,40,21),(17,20,-.6),30),
          'drain-plan':camera(b,'CoolantPID.Drain',(15,16,65),(15,16,F),32)}
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    def show(key):
        viewtype='exterior' if key=='nitrogen-exterior' else 'cutaway'
        compact_view(b,{viewtype:cams[key]},viewtype)
        for name in ('Air distribution','Structure'):
            if name in b.collections:b.collections[name].hide_render=b.collections[name].hide_viewport=False
        for name in ('Coolant gas piping','Coolant gas vessels','Coolant PID reservations','Coolant pressure-control station','Unresolved coolant interfaces','Exterior nitrogen supply'):b.collections[name].hide_render=b.collections[name].hide_viewport=False
        if key in ('sg-detail','drain-plan'):
            for name in ('Air distribution','Structure'):
                if name in b.collections:b.collections[name].hide_render=b.collections[name].hide_viewport=key=='sg-detail' or name=='Air distribution'
        if key=='tank-detail':
            bpy.data.objects['site.combined_process.east'].hide_render=True
        if key=='drain-plan':
            for name in ('Steam generators','Coolant storage','Coolant pumps','Pipe insulation','Pressure pipe metal','Reactor vessel','Shared wall inspection','Coolant gas piping','Coolant gas vessels','Coolant PID reservations','Unresolved coolant interfaces'):
                if name in b.collections:b.collections[name].hide_render=b.collections[name].hide_viewport=True
            for ob in bpy.data.objects:
                if ob.get('silo_shell'):ob.hide_render=ob.hide_viewport=True
    show('overview');bpy.ops.wm.save_as_mainfile(filepath=str(out/'fast-salt-coolant-pid.blend'))
    if not args.build_only:
        for key in (args.views or cams):
            show(key);scene.render.filepath=str(out/(key+'.png'));bpy.ops.render.render(write_still=True)
    print('COOLANT_PID_DRAFT_OK',flush=True)

if __name__=='__main__':main()
