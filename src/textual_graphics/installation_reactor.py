"""Place a manifest-verified detailed reactor in an installation without rebuilding it."""
import hashlib
import json
import math

import bpy
from mathutils import Vector
from .installation_piping import insulated_route


def reactor_placement(layout, repo):
    """Read connection metadata before constructing the large Blender scene."""
    config=layout.REACTOR
    folder=repo/config['baseline']
    report_path=folder/'reactor-study-report.json'
    manifest=json.loads((folder/'manifest.json').read_text())
    assert hashlib.sha256(report_path.read_bytes()).hexdigest()==manifest['files'][report_path.name]['sha256']
    report=json.loads(report_path.read_text())
    d=report['derived_dimensions'];p=report['presentation_dimensions']
    terminals=[]
    for kind,offset,z in [('cold_inlet',report['connections']['cold_angle_offset'],d['cold_inlet_z']),
                          ('hot_outlet',report['connections']['hot_angle_offset'],d['hot_outlet_z'])]:
        for i in range(3):
            angle=math.radians(config['rotation_degrees']+offset+i*120)
            end=d['pipe_end_radius']+(.35 if kind=='cold_inlet' else 0)
            terminals.append(dict(name=f'reactor.{kind}_{i+1}',kind=kind,
                point=[end*math.cos(angle),end*math.sin(angle),z+config['origin_z']],
                direction=[math.cos(angle),math.sin(angle),0],diameter=layout.PIPING['salt_pipe_diameter']))
    return dict(deck_opening_radius=d['hot_well_outer_radius']+config['deck_clearance'],
        well_outer_radius=d['hot_well_outer_radius'],
        well_floor_bottom=config['origin_z']+d['floor_z']-p['well_floor'],
        well_base_radius=d['well_outer_radius'],terminals=terminals,routes=[],deck_penetrations=[])


def import_reactor(b, layout, repo):
    config = layout.REACTOR
    folder = repo / config['baseline']
    manifest = json.loads((folder / 'manifest.json').read_text())
    source = folder / 'wistr-reactor-study.blend'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != manifest['files'][source.name]['sha256']:
        raise ValueError('Reactor source hash does not match its manifest')
    report_path=folder/'reactor-study-report.json'
    assert hashlib.sha256(report_path.read_bytes()).hexdigest()==manifest['files'][report_path.name]['sha256']
    report = json.loads(report_path.read_text())
    d = report['derived_dimensions']
    scene = bpy.context.scene
    with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
        loaded.scenes = available.scenes[:1]
    source_scene = loaded.scenes[0]
    for key, value in source_scene.items():
        scene[key] = value
    scene['maintenance_position'] = False
    scene['section_cutaway'] = True
    ignored = {'Presentation', 'Flow arrows', 'Air path arrows'}
    collections = [c for c in source_scene.collection.children
                   if c.name.split('.')[0] not in ignored and not c.name.startswith('Labels.')]
    objects = {o for c in collections for o in c.all_objects}
    excluded = set(source_scene.objects) - objects
    wrapper = b.assembly('equipment.reactor_vessel', 'Reactor vessel',
                         (0, 0, config['origin_z']), config['rotation_degrees'])
    wrapper['baseline_sha256'] = digest
    for c in collections:
        scene.collection.children.link(c)
    for o in objects:
        if o.parent is None:
            o.parent = wrapper
        if o.animation_data:
            for fcurve in o.animation_data.drivers:
                for variable in fcurve.driver.variables:
                    for target in variable.targets:
                        if target.id == source_scene:
                            target.id = scene
    # Keep the section plane parallel to the building's front opening.
    bpy.data.objects['study.section_tool'].rotation_euler.z = -math.radians(config['rotation_degrees'])
    bpy.data.scenes.remove(source_scene)
    for o in excluded:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.view_layer.update()
    # The source is a seated scene; retain its hidden tools and insulated-cover state.
    # The archived baseline stays untouched; adapt only the installation copy's sleeves.
    spec=layout.PIPE_SPECS['hot']
    for kind in ('cold_inlet','hot_outlet'):
        for i in range(1,4):
            nozzle=bpy.data.objects[f'reactor.{kind}_{i}']
            old=nozzle['diameter']/2
            for obj in nozzle.children:
                if obj.type!='MESH':continue
                for v in obj.data.vertices:
                    r=math.hypot(v.co.x,v.co.y)
                    if r<1e-7:continue
                    if obj.name.endswith('.pipe'):
                        nr=spec['bore']/2 if r<old-.01 else spec['bare_od']/2
                    elif '.opening_cutter' in obj.name:
                        nr=r*(spec['bare_od']/2+.005)/(old+.005)
                    elif obj.name.endswith('.end_flange'):
                        nr=spec['bore']/2 if r<old+.01 else spec['bare_od']/2+.11
                    else:continue
                    v.co.x*=nr/r;v.co.y*=nr/r
                obj.data.update()
            nozzle['source_diameter_m']=2*old;nozzle['diameter']=spec['bare_od']
            nozzle['bore_m']=spec['bore'];nozzle['wall_m']=spec['wall']
    bpy.context.view_layer.update()
    terminals = []
    for kind in ('cold_inlet', 'hot_outlet'):
        for i in range(1, 4):
            nozzle = bpy.data.objects[f'reactor.{kind}_{i}']
            point = nozzle.matrix_world @ Vector((nozzle['end_radius'], 0, nozzle['nozzle_z']))
            direction = nozzle.matrix_world.to_3x3() @ Vector((1, 0, 0))
            terminals.append(dict(name=nozzle.name, kind=kind, point=list(point),
                                  direction=list(direction), diameter=nozzle['diameter']))
    return dict(source=str(source.relative_to(repo)), sha256=digest,
                source_commit=config['source_commit'], origin_z=config['origin_z'],
                rotation_degrees=config['rotation_degrees'], scale=1.0,
                deck_opening_radius=d['hot_well_outer_radius']+config['deck_clearance'],
                well_outer_radius=d['hot_well_outer_radius'],
                well_floor_bottom=config['origin_z']+d['floor_z']-report['presentation_dimensions']['well_floor'],
                well_base_radius=d['well_outer_radius'],
                cap_top_world_z=config['origin_z']+d['top_z']+report['presentation_dimensions']['spider_beam_depth']+report['presentation_dimensions']['cap_thickness'],
                terminals=terminals, air_stubs='Side-manifold stubs connected to installation air headers',
                routes=[], deck_penetrations=[])


def route_coolant(b, layout, integration):
    from .installation_services import steel_frame
    integration['cold_suction_routes']=[];integration['pumps']=[]
    p=layout.PUMPS
    flow=p['mass_flow_kg_s']/p['density_kg_m3']
    hydraulic=flow*p['sg_pressure_drop_pa']*p['allowance_factor']/1000
    shaft=hydraulic/p['pump_efficiency']
    for index, angle in enumerate(layout.STEAM_GENERATORS['angles'], 1):
        root=b.assembly(f'connections.loop_{index}', 'Major piping', angle=angle)
        bpy.context.view_layer.update();inverse=root.matrix_world.inverted()
        px,py,pz=p['local_position'];pr=p['casing_diameter']/2
        hot=layout.manifold_point('hot',-1);cold=layout.manifold_point('cold',1)
        bottom=pz-p['casing_height']/2
        for kind,material in [('hot_outlet','hot'),('cold_inlet','cold')]:
            def difference(t):
                az=math.degrees(math.atan2(t['point'][1],t['point'][0]))
                return abs((az-angle+180)%360-180)
            terminal=min((t for t in integration['terminals'] if t['kind']==kind),key=difference)
            start=inverse @ Vector(terminal['point'])
            direction=root.matrix_world.to_3x3().inverted() @ Vector(terminal['direction'])
            turn=start+direction*((layout.PIPING['riser_x']-start.x)/direction.x)
            if kind=='hot_outlet':
                points=[tuple(start),tuple(turn),(hot[0],3.8,start.z),(hot[0],3.8,hot[2]),hot]
                target='generator.hot_manifold'
            else:
                # Discharge heads inward to the vessel; generator return goes to bottom suction.
                cx=layout.PIPING['cold_riser_x']
                turn=start+direction*((cx-start.x)/direction.x)
                points=[tuple(start),tuple(turn),(cx,py,start.z),(px-pr,py,pz)]
                target=f'equipment.coolant_pump_{index}.discharge'
            spec=layout.PIPE_SPECS[material]
            obj=insulated_route(b,kind,root,points,spec,material)
            obj['reactor_terminal']=terminal['name'];obj['centreline_points_local']=json.dumps(points)
            obj['flow_direction']=('Reactor hot outlet to generator hot manifold' if kind=='hot_outlet'
                                   else 'Pump side discharge to reactor cold inlet')
            world=[list(root.matrix_world @ Vector(q)) for q in points]
            integration['routes'].append(dict(object=obj.name,terminal=terminal['name'],points=world,
                diameter=spec['bare_od'],jacket_diameter=spec['jacket_od'],generator=index,target=target,flow_direction=obj['flow_direction']))
        run=p['suction_run_z']
        # The floor-mounted generator outlet feeds a level run with two bends.
        assert abs(cold[2]-run)<1e-6
        suction=[cold,(cold[0],py,run),(px,py,run),(px,py,bottom)]
        obj=insulated_route(b,'cold_suction',root,suction,layout.PIPE_SPECS['cold'],'cold')
        obj['flow_direction']='Generator cold manifold to pump bottom; final direction vertically upward'
        integration['cold_suction_routes'].append(dict(object=obj.name,generator=index,
            points=[list(root.matrix_world @ Vector(q)) for q in suction]))
        centre=root.matrix_world @ Vector(p['local_position'])
        pump=b.assembly(f'equipment.coolant_pump_{index}','Coolant pumps',tuple(centre),angle)
        pump['motor_rating_kw']=p['motor_rating_kw'];pump['shaft_demand_kw']=shaft
        pump['flow_m3_s']=flow;pump['pressure_rise_pa']=p['sg_pressure_drop_pa']*p['allowance_factor']
        pump['scope']='Provisional vertical centrifugal pump with bottom suction'
        pump['support_bottom_z']=layout.FLOOR_Z;pump['support_top_z']=bottom
        b.cylinder('volute_envelope',pump,pr,p['casing_height'],(0,0,0),'cold',vertices=48)
        b.cylinder('bearing_pedestal',pump,.45,p['motor_bottom']-(pz+p['casing_height']/2),
                   (0,0,(pz+p['casing_height']/2+p['motor_bottom'])/2-pz),'rail',vertices=32)
        b.box('motor_envelope',pump,(p['motor_width'],p['motor_depth'],p['motor_height']),
              (0,0,p['motor_bottom']+p['motor_height']/2-pz),'equipment',.08)
        b.cylinder('motor_top',pump,.85,.18,(0,0,p['motor_bottom']+p['motor_height']-pz),'dark',vertices=32)
        steel_frame(b,pump,'support',3.2,3.2,layout.FLOOR_Z-pz,-p['casing_height']/2)
        for y in (-1.0,1.0):
            b.box(f'casing_bearer{y}',pump,(3.2,.20,.25),(0,y,-p['casing_height']/2-.125),'rail')
        integration['pumps'].append(dict(name=pump.name,centre=list(centre),
            suction=list(root.matrix_world @ Vector((px,py,bottom))),
            discharge=list(root.matrix_world @ Vector((px-pr,py,pz))),
            hydraulic_kw=hydraulic,shaft_kw=shaft,electrical_kw=shaft/p['motor_efficiency'],
            motor_rating_kw=p['motor_rating_kw'],flow_m3_s=flow))



def check_integration(integration):
    scene=bpy.context.scene
    assert not scene['maintenance_position']
    assert abs(integration['well_floor_bottom']+9.1) < 1e-6
    assert len(integration['routes']) == 6
    names=[route['terminal'] for route in integration['routes']]
    assert len(set(names)) == 6
    terminals={t['name']:t for t in integration['terminals']}
    for route in integration['routes']:
        terminal=terminals[route['terminal']]
        points=[Vector(p) for p in route['points']]
        assert (points[0]-Vector(terminal['point'])).length < 1e-5
        assert (points[1]-points[0]).normalized().dot(Vector(terminal['direction'])) > .99999
        assert abs(route['diameter']-terminal['diameter']) < 1e-6
        assert math.hypot(*points[1][:2])-route['jacket_diameter']/2 > integration['well_outer_radius']
    assert len(integration['pumps'])==3 and len(integration['cold_suction_routes'])==3
    for pump,suction in zip(integration['pumps'],integration['cold_suction_routes']):
        assert len(suction['points'])==4
        assert max(q[2] for q in suction['points'][:3])-min(q[2] for q in suction['points'][:3])<1e-6
        assert (Vector(suction['points'][-1])-Vector(pump['suction'])).length<1e-5
        cold=next(r for r in integration['routes'] if r['generator']==suction['generator'] and 'discharge' in r['target'])
        assert (Vector(cold['points'][-1])-Vector(pump['discharge'])).length<1e-5
        assert pump['motor_rating_kw']>pump['shaft_kw']
        last=Vector(suction['points'][-1])-Vector(suction['points'][-2])
        assert last.normalized().dot(Vector((0,0,1)))>.99999
        assert abs(pump['suction'][0]-pump['centre'][0])<1e-6
        assert abs(pump['suction'][1]-pump['centre'][1])<1e-6
        assert pump['suction'][2]<pump['discharge'][2]
    assert 'equipment.reactor_vessel.closed_shell'  not in bpy.data.objects
    assert not any(o.name.startswith('building.structure.cut_edge_beam') for o in scene.objects)
    invalid=[]
    for obj in scene.objects:
        if obj.animation_data:
            invalid.extend(obj.name+':'+f.data_path for f in obj.animation_data.drivers if not f.driver.is_valid)
    assert not invalid, invalid[:5]
    return ['Working reactor source verified against its SHA-256 manifest',
            'Full-scale reactor concrete well rests on sub-floor at Z=-9.1 m',
            'Six installed nozzle bores/walls resized to Hurmet case; endpoints and tangents match six bare pipe routes',
            'Coolant risers clear the outside of the concrete well',
            'Three cold legs pass through bottom suction and side discharge; upward suction tangents and motor ratings verified',
            'No superseded placeholder reactor and no invalid object drivers',
            'Current side-air plenums and insulation covers imported from the working source']
