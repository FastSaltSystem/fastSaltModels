"""Author the current three coolant legs in Python; Blender is only a consumer.

Common engineering data comes from the hub; view geometry comes from
wistr_installation.py and the verified reactor interface.
"""
import hashlib
import json
import math
from pathlib import Path
from textual_graphics.shared_coolant import coolant as shared_coolant
from textual_graphics.assembly_model import Model, document, local_point, mv, transpose


def reactor_interface(layout,repo):
    folder=Path(repo)/layout.REACTOR['baseline'];path=folder/'reactor-study-report.json'
    manifest=json.loads((folder/'manifest.json').read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest()!=manifest['files'][path.name]['sha256']:
        raise ValueError('Reactor report does not match manifest')
    report=json.loads(path.read_text());d=report['derived_dimensions'];p=report['presentation_dimensions'];cfg=layout.REACTOR
    terminals=[]
    for kind,offset,z in [('cold_inlet',report['connections']['cold_angle_offset'],d['cold_inlet_z']),('hot_outlet',report['connections']['hot_angle_offset'],d['hot_outlet_z'])]:
        for i in range(3):
            angle=math.radians(cfg['rotation_degrees']+offset+i*120);end=d['pipe_end_radius']+(.35 if kind=='cold_inlet' else 0)
            terminals.append(dict(name=f'reactor.{kind}_{i+1}',kind=kind,point=[end*math.cos(angle),end*math.sin(angle),z+cfg['origin_z']],direction=[math.cos(angle),math.sin(angle),0],diameter=layout.PIPING['salt_pipe_diameter']))
    return dict(deck_opening_radius=d['hot_well_outer_radius']+cfg['deck_clearance'],well_outer_radius=d['hot_well_outer_radius'],well_floor_bottom=cfg['origin_z']+d['floor_z']-p['well_floor'],well_base_radius=d['well_outer_radius'],terminals=terminals,routes=[],deck_penetrations=[])


def build_model(layout,integration,repo=None):
    engineering=layout.ENGINEERING
    by_tag={leg['generator']:leg for leg in shared_coolant.graphics_legs(engineering)}
    if set(layout.COOLANT_LEG_TAGS)!=set(by_tag) or len(layout.COOLANT_LEG_TAGS)!=len(by_tag):
        raise ValueError('Graphics placement tags differ from shared generators')
    legs=[by_tag[tag] for tag in layout.COOLANT_LEG_TAGS]
    model=Model('WISTR three-leg coolant assembly')
    model.metadata['shared_engineering']=engineering['_provenance']
    model.metadata.update(status='Current visual geometry; conditional dimensions; no new engineering sizing',authoring='models/coolant_assembly.py',scope='Three main circulation legs, pump envelopes and generator geometry. Storage/transfer and other systems remain in existing builders.')
    if repo:
        root=Path(repo)
        paths=[root/'models/wistr_installation.py',root/'models/coolant_assembly.py',root/'src/textual_graphics/assembly_model.py',root/layout.REACTOR['baseline']/'reactor-study-report.json']
        model.metadata['sources']={str(p.relative_to(root)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths if p.exists()}
    model.component('coolant')
    model.component('reactor','interface',parent='coolant',pid_tag=legs[0]['reactor'])
    for t in integration['terminals']:
        model.port('reactor',t['name'].split('.',1)[1],t['point'],t['direction'])
    p=layout.PUMPS;flow=p['mass_flow_kg_s']/p['density_kg_m3'];hydraulic=flow*p['sg_pressure_drop_pa']*p['allowance_factor']/1000
    if layout.STEAM_GENERATORS['count']!=len(layout.STEAM_GENERATORS['angles']) or p['count']!=len(layout.STEAM_GENERATORS['angles']):raise ValueError('Equipment count disagrees with leg layout')
    chosen=[]
    if len(legs)!=len(layout.STEAM_GENERATORS['angles']):raise ValueError('Shared leg count differs from graphics layout')
    for i,angle in enumerate(layout.STEAM_GENERATORS['angles'],1):
        shared=legs[i-1]
        leg=model.component(f'leg_{i}',parent='coolant',rotation_deg=(0,0,angle),blender_name=f'connections.loop_{i}',index=i)
        px,py,pz=p['local_position'];pr=p['casing_diameter']/2;bottom=pz-p['casing_height']/2
        pump=model.component(f'leg_{i}.pump','pump',parent=leg,position=p['local_position'],parameters=dict(p),pid_tag=shared['pump'],blender_name=f'equipment.coolant_pump_{i}',floor_z=layout.FLOOR_Z,
            duty=dict(flow_m3_s=flow,pressure_rise_pa=p['sg_pressure_drop_pa']*p['allowance_factor'],hydraulic_kw=hydraulic,shaft_kw=hydraulic/p['pump_efficiency'],electrical_kw=hydraulic/p['pump_efficiency']/p['motor_efficiency'],motor_rating_kw=p['motor_rating_kw']))
        suction=model.port(pump,'suction',(0,0,-p['casing_height']/2),(0,0,-1));discharge=model.port(pump,'discharge',(-pr,0,0),(-1,0,0))
        sg=layout.STEAM_GENERATORS
        gen=model.component(f'leg_{i}.generator','steam_generator',parent=leg,position=(sg['radius'],0,sg['casing_bottom']),rotation_deg=(0,0,sg['rotation_offset']),pid_tag=shared['generator'],blender_name=f'equipment.steam_generator_{i}',
            parameters=dict(generator=dict(sg),manifolds=dict(layout.MANIFOLDS),pipe_specs=dict(layout.PIPE_SPECS),floor_z=layout.FLOOR_Z))
        m=layout.MANIFOLDS
        hot=model.port(gen,'salt_inlet',(-m['half_length'],-m['side_offset'],m['hot_z']),(-1,0,0))
        cold=model.port(gen,'salt_outlet',(m['half_length'],-m['side_offset'],m['cold_z']),(1,0,0))
        doc=document(model);frame=doc['components'][leg]
        hot_point=local_point(frame,doc['ports'][hot]['world_position_m']);cold_point=local_point(frame,doc['ports'][cold]['world_position_m'])
        for kind,material,end in [('hot_outlet','hot',hot),('cold_inlet','cold',discharge)]:
            def difference(t):return abs((math.degrees(math.atan2(t['point'][1],t['point'][0]))-angle+180)%360-180)
            t=min((t for t in integration['terminals'] if t['kind']==kind),key=difference);chosen.append(t['name'])
            model.ports[t['name']]['pid_port']=shared['hot_port' if kind=='hot_outlet' else 'cold_port']
            start=local_point(frame,t['point']);direction=mv(transpose(frame['world_rotation']),t['direction'])
            x=layout.PIPING['riser_x' if kind=='hot_outlet' else 'cold_riser_x']
            if abs(direction[0])<1e-8:raise ValueError('Reactor nozzle cannot intersect the chosen riser plane')
            step=(x-start[0])/direction[0]
            if step<=0:raise ValueError('Coolant riser would reverse the nozzle direction')
            turn=[a+step*b for a,b in zip(start,direction)]
            via=[turn,(hot_point[0],3.8,start[2]),(hot_point[0],3.8,hot_point[2])] if kind=='hot_outlet' else [turn,(x,py,start[2])]
            model.connect(f'leg_{i}.{kind}',t['name'],end,frame=leg,via=via,reverse_flow=kind=='cold_inlet',service=material,spec=dict(layout.PIPE_SPECS[material]),blender_name=kind,index=i,
                pid_line=shared['hot_line' if kind=='hot_outlet' else 'cold_line'],reactor_terminal=t['name'],target='generator.hot_manifold' if kind=='hot_outlet' else f'equipment.coolant_pump_{i}.discharge',
                flow_description='Reactor hot outlet to generator hot manifold' if kind=='hot_outlet' else 'Pump side discharge to reactor cold inlet')
        run=p['suction_run_z']
        if abs(cold_point[2]-run)>1e-6:raise ValueError('Generator outlet and pump suction run elevations disagree')
        model.connect(f'leg_{i}.cold_suction',cold,suction,frame=leg,via=[(cold_point[0],py,run),(px,py,run)],service='cold',spec=dict(layout.PIPE_SPECS['cold']),blender_name='cold_suction',index=i,pid_line=shared['cold_line'],
            flow_description='Generator cold manifold to pump bottom; final direction vertically upward')
    if len(set(chosen))!=len(chosen):raise ValueError('A reactor nozzle is assigned to more than one leg')
    return model


def check_pid_links(doc, path):
    """Check that both consumers resolve the same common data and flow endpoints."""
    import tomllib
    path=Path(path)
    pid=tomllib.loads(path.read_text())
    if 'shared_engineering' in pid:
        pid=shared_coolant.merge_pid(pid,shared_coolant.read(path.parent/pid['shared_engineering']['model']))
    tags=[]
    for c in doc['components'].values():
        if 'pid_tag' in c:
            tag=c['pid_tag']
            if tag not in pid['equipment']:raise ValueError(f'P&ID lacks equipment {tag}')
            tags.append(tag)
    aliases={name:p['pid_port'] for name,p in doc['ports'].items() if 'pid_port' in p}
    for name,p in doc['ports'].items():
        c=doc['components'][p['owner']]
        if c['kind'] in ('pump','steam_generator'):aliases[name]=c['pid_tag']+'.'+name.rsplit('.',1)[1]
    checked=set()
    for route in doc['connections'].values():
        tag=route['pid_line'];line=pid['lines'][tag];spec=route['spec']
        for key,field in [('bore','bore_mm'),('wall','wall_mm'),('bare_od','od_mm'),('insulation','radial_insulation_mm')]:
            if abs(spec[key]*1000-line[field])>1e-6:raise ValueError(f'{tag}: {field} differs between graphics and P&ID')
        endpoints=(aliases[route['flow_from']],aliases[route['flow_to']])
        expected=[];start=line['from']
        for pump in line.get('via',[]):
            expected.append((start,pump+'.suction'));start=pump+'.discharge'
        expected.append((start,line['to']))
        if endpoints not in expected:raise ValueError(f'{tag}: flow connections differ between graphics and P&ID')
        checked.add(tag)
    return {'equipment_tags':sorted(tags),'line_tags':sorted(checked),'reactor_port_aliases':{p['pid_port']:name for name,p in doc['ports'].items() if 'pid_port' in p},'pid_source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}
