"""Compose a provisional Fast Salt site around the existing installation.

Run from this repository with Blender --background --python scripts/build_site.py.
The source installation and approved baselines are never overwritten.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
for p in ('src', 'models', 'scripts'):
    sys.path.insert(0, str(ROOT / p))
import wistr_site as site
import wistr_installation as installation
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.installation_piping import insulated_route
from build_wistr import palette, camera
from render_pms import text_on_camera


def wall(b, root, label, axis, constant, lo, hi, height, material, opening=None):
    """Partition a wall around one rectangular opening, without Boolean solids."""
    spans = [(lo, hi, 0, height)]
    if opening:
        a, c, bottom, top = opening
        assert lo <= a < c <= hi and 0 <= bottom < top <= height
        spans = [(lo, a, 0, height), (c, hi, 0, height),
                 (a, c, 0, bottom), (a, c, top, height)]
    for i, (a, c, bottom, top) in enumerate(spans):
        if top - bottom < .001 or c-a < .001:
            continue
        size = (site.WALL, c-a, top-bottom) if axis == 'x' else (c-a, site.WALL, top-bottom)
        loc = (constant, (a+c)/2, (bottom+top)/2) if axis == 'x' else ((a+c)/2, constant, (bottom+top)/2)
        b.box(f'{label}.{i}', root, size, loc, material, .025)


def envelope(b, key, p, material):
    x, y = p['centre']; length, width, height = p['size']
    root = b.assembly('site.'+key, 'Site buildings', (x, y, site.PAD_Z))
    root['scope'] = 'Provisional envelope; no process, structural, shielding or capacity sizing'
    root['dimensions_m'] = p['size']
    b.box('slab', root, (length, width, .35), (0, 0, -.175), 'floor')
    # Opposing service openings: turbine pipe bay on east, fuel receiving door on west.
    east = site.TURBINE_PIPE_BAY if key == 'turbine' else None
    west = (-5.0, 3.0, 0, 9.0) if key == 'turbine' else None
    north = (.5,6.5,0,4.2) if key=='fuel_preparation' else ((-2,2,0,4.0) if key=='off_gas' else None)
    south = None
    if key in ('fuel_preparation','off_gas'):
        cfg=site.PROCESS_ANNEX;link_x=cfg['shared_link_x']-x
        low=cfg['link_floor_z']-site.PAD_Z
        south=(max(-length/2,link_x-cfg['link_width']/2+.16),min(length/2,link_x+cfg['link_width']/2-.16),low,low+cfg['link_height'])
    wall(b, root, 'east', 'x', length/2-site.WALL/2, -width/2, width/2, height, material, east)
    wall(b, root, 'west', 'x', -length/2+site.WALL/2, -width/2, width/2, height, material, west)
    wall(b, root, 'north', 'y', width/2-site.WALL/2, -length/2, length/2, height, material, north)
    wall(b, root, 'south', 'y', -width/2+site.WALL/2, -length/2, length/2, height, material, south)
    roof = b.box('roof', root, (length+.5, width+.5, site.ROOF), (0, 0, height+site.ROOF/2), material, .04)
    roof['site_roof'] = True
    # Architectural panel seams only; the structural system is not selected.
    for i in range(1, int(length/5)):
        b.box(f'panel_joint{i}', root, (.055, .025, height-.2),
              (-length/2+i*5, -width/2-.014, height/2), 'rail')
    return root


def floor_label(b, name, text, position, size=1.2):
    curve = bpy.data.curves.new(name, 'FONT'); curve.body = text; curve.size = size
    curve.align_x = 'CENTER'; curve.align_y = 'CENTER'
    obj = bpy.data.objects.new(name, curve); b.collection('Site floor labels').objects.link(obj)
    obj.location = position; curve.materials.append(b.materials['dark'])
    return obj


def compose(b, source_report):
    palette(b)
    b.material('turbine_envelope', '#9BAFC0', roughness=.7)
    b.material('fuel_envelope', '#CDB896', roughness=.7)
    b.material('site_paving', '#DADDD8', roughness=.9)
    ground = b.assembly('site.ground', 'Site setting')
    b.box('backdrop', ground, (2000,2000,.1), (0,0,site.PAD_Z-.5), 'backdrop')
    b.box('common_pad', ground, (190,140,.16), (-14,5,site.PAD_Z-.1), 'site_paving', .08)
    yard = site.SERVICE_YARD
    b.box('service_yard', ground, (*yard['size'],.018), (*yard['centre'],site.PAD_Z-.01), 'floor')
    # Clear approach outside the existing 18-degree access apron; no fuel-transfer process is implied.
    for y in (-6, 18):
        b.box('yard_edge'+str(y), ground, (10,.08,.012), (30,y,site.PAD_Z+.005), 'crane')
    turbine = envelope(b, 'turbine', site.TURBINE, 'turbine_envelope')
    fuel = envelope(b, 'fuel_preparation', site.FUEL_PREPARATION, 'fuel_envelope')
    b.material('offgas_envelope','#9AB8B3',roughness=.7)
    envelope(b,'off_gas',site.OFF_GAS,'offgas_envelope')
    envelope(b,'converter',site.CONVERTER,'fuel_envelope')
    floor_label(b,'Converter label','SPENT-FUEL CONVERTER\n20 x 15 m / 8 m high',(11.5,55,site.PAD_Z+.03),.95)
    from textual_graphics.site_process_buildings import build_process_annexes
    b.process_annexes=build_process_annexes(b,site,installation,floor_label)
    from textual_graphics.site_salt_distribution import build_salt_distribution
    b.salt_distribution=build_salt_distribution(b,site,installation,b.process_annexes)
    from textual_graphics.site_fuel_pressure import build_fuel_pressure
    b.fuel_pressure=build_fuel_pressure(b,site,installation,b.process_annexes)
    from textual_graphics.site_fresh_air import build_fresh_air
    b.fresh_air=build_fresh_air(b,site,installation,source_report['services']['air'])
    from turbine_equipment import add_equipment
    add_equipment(b, ROOT, site)
    floor_label(b, 'Turbine reservation', 'TURBINE / GENERATOR', (site.TURBINE['centre'][0],site.TURBINE['centre'][1]-4,site.PAD_Z+.03), 1.1)
    floor_label(b, 'Yard label', 'SERVICE\nYARD', (30,0,site.PAD_Z+.03), .85)
    routes=[]
    root=b.assembly('site.secondary', 'Site connections')
    for network in source_report['services']['networks']:
        kind=network['service']; original_exit=Vector(network['exit']); spec=network['spec']
        radial=Vector((original_exit.x,original_exit.y,0)).normalized()
        approach=site.SECONDARY_APPROACH
        entry_y=site.TURBINE['centre'][1]-site.TURBINE['size'][1]/2+approach['local_terminal_y']
        # Adapt only this imported site copy: a shallow 20-degree outlet turn
        # makes the end runs parallel, allowing an exact two-45-degree offset.
        # The existing reactor wall penetration and upstream route are retained.
        start=Vector((approach['outlet_x'],original_exit.y,original_exit.z))
        connection_points=[Vector(q) for q in network['building_connection_points']]+[start]
        prefix='connections.secondary_headers.'+kind+'_building_connection'
        for suffix in ('','.metal','.insulation'):
            bpy.data.objects.remove(bpy.data.objects[prefix+suffix],do_unlink=True)
        source_root=bpy.data.objects['connections.secondary_headers']
        assert source_root.matrix_world.translation.length<1e-6
        stub=insulated_route(b,kind+'_building_connection',source_root,connection_points,spec,kind)
        stub_points=[Vector(q.co[:3]) for q in stub.data.splines[0].points]
        west=Vector((-1,0,0))
        assert (stub_points[-1]-start).length<1e-5
        assert (stub_points[-1]-stub_points[-2]).normalized().dot(west)>1-1e-5
        trim_angle=math.degrees(radial.angle(west))
        assert abs(trim_angle-20)<1e-4
        corner=Vector((approach['turn_x'],start.y,start.z))
        outer_turn=Vector((corner.x-abs(entry_y-start.y),entry_y,start.z))
        end=Vector((approach['terminal_x'],entry_y,start.z))
        control=[start,corner,outer_turn,end]
        directions=[(q-p).normalized() for p,q in zip(control,control[1:])]
        bend_angles=[math.degrees(u.angle(v)) for u,v in zip(directions,directions[1:])]
        assert len(bend_angles)==2 and all(abs(a-45)<1e-4 for a in bend_angles)
        guide=insulated_route(b,kind,root,control,spec,kind,rounded=True)
        guide['interface_status']='Two 45-degree offset bends; reactor-side connection adds a 20-degree alignment turn'
        points=[Vector(q.co[:3]) for q in guide.data.splines[0].points]
        assert (points[0]-start).length < 1e-5
        assert (points[1]-points[0]).normalized().dot(west)>1-1e-5
        assert abs((points[-1]-points[-2]).normalized().x+1)<1e-5
        at_wall=Vector((-36,entry_y,start.z))
        half=spec['jacket_od']/2
        local_y=at_wall.y-site.TURBINE['centre'][1]
        assert site.TURBINE_PIPE_BAY[0]+half < local_y < site.TURBINE_PIPE_BAY[1]-half
        assert site.PAD_Z+half < at_wall.z < site.PAD_Z+18-half
        routes.append(dict(service=kind,start=list(start),end=list(end),spec=spec,
                           control_points=[list(q) for q in control],centreline=[list(q) for q in points],
                           bend_deflections_deg=bend_angles,
                           reactor_outlet_adaptation=dict(original_exit=list(original_exit),alignment_turn_deg=trim_angle,
                               control_points=[list(q) for q in connection_points],centreline=[list(q) for q in stub_points],
                               minimum_bend_radius_m=stub['minimum_bend_radius_m']),
                           minimum_bend_radius_m=guide['minimum_bend_radius_m'],wall_entry_angle_to_plane_deg=90,
                           floor_clearance_m=start.z-half-site.PAD_Z))
    # Two illustrative portal frames under the straight interbuilding pipe run.
    for i,x in enumerate(site.SECONDARY_APPROACH['rack_x']):
        y=entry_y; frame=b.assembly(f'site.pipe_rack{i}','Site connections')
        for side in (-1,1):
            b.box(f'post{side}',frame,(.25,.25,15),(x,y+side*1.8,site.PAD_Z+7.5),'rail')
        for kind in routes:
            z=kind['start'][2]-kind['spec']['jacket_od']/2-.15
            b.box(kind['service']+'_beam',frame,(.3,3.85,.25),(x,y,z),'rail')
    return routes


def check_layout(routes):
    # Both air headers are internal; use the current building wall envelope.
    radius=installation.BUILDING['diameter']/2
    results=[]
    for p in (site.TURBINE,site.FUEL_PREPARATION,site.OFF_GAS,site.CONVERTER):
        x,y=p['centre']; length,width,height=p['size']
        dx=max(abs(x)-length/2,0); dy=max(abs(y)-width/2,0)
        gap=math.hypot(dx,dy)-radius
        assert gap>(10 if p is site.TURBINE else 1.5), (p['name'],gap)
        results.append(dict(building=p['name'],reactor_wall_to_building_gap_m=gap))
    # The existing straight access corridor ends at radius 27; the new envelope starts at x=36.
    a=math.radians(installation.ACCESS['angle'])
    end=(installation.ACCESS['outer_radius']*math.cos(a),installation.ACCESS['outer_radius']*math.sin(a))
    assert end[0]+installation.ACCESS['width']/2 < 36
    # Stack to the north and intake to the south remain between the two new footprints.
    stack_angle=math.radians(installation.STACKS['angles'][0])
    for x,y,r in ((installation.STACKS['radius']*math.cos(stack_angle),installation.STACKS['radius']*math.sin(stack_angle),1.901),(0,-28,2)):
        for p in (site.TURBINE,site.FUEL_PREPARATION,site.OFF_GAS,site.CONVERTER):
            cx,cy=p['centre'];lx,ly,_=p['size']
            assert math.hypot(max(abs(cx-x)-lx/2,0),max(abs(cy-y)-ly/2,0))>r+5
    water,steam=sorted(routes,key=lambda p:p['start'][2])
    gap=steam['start'][2]-water['start'][2]-(steam['spec']['jacket_od']+water['spec']['jacket_od'])/2
    assert gap>0 and min(r['floor_clearance_m'] for r in routes)>4
    # Curved approach stays outside the outer reactor ring and square through the wall.
    envelope_clearance=min(math.hypot(p[0],p[1])-r['spec']['jacket_od']/2-radius for r in routes for p in r['centreline'])
    assert envelope_clearance>.5,envelope_clearance
    assert abs(site.TURBINE['centre'][1])<1e-8
    for r in routes:
        assert r['minimum_bend_radius_m']>r['spec']['jacket_od']/2
        pts=r['centreline'];assert abs(pts[-1][1]-pts[-2][1])<1e-6
    return dict(aligned_building_centre_y_m=0,minimum_external_pipe_to_reactor_envelope_gap_m=envelope_clearance,building_clearances=results,secondary_jacket_separation_m=gap,
        checks=['Two 45-degree interbuilding bends per pipe; separate 20-degree reactor outlet alignment turn; sizes retained',
                'Building centres aligned; steam/feedwater enter east wall at 90 degrees',
                'Pipe jackets clear the turbine wall opening and common pad',
                'Building walls clear the reactor wall, stack and fresh-air intake',
                'Existing reactor doorway approach remains clear'],
        limitations='Selected envelope checks only; no full plant clash, vehicle swept-path, structure, shielding, turbine capacity or process validation')


def presentation(b):
    for name,loc,power in [('Key',(-45,-65,85),190000),('Fill',(65,-10,65),130000),('Rim',(-5,55,70),150000)]:
        data=bpy.data.lights.new('Site.'+name,'AREA'); data.energy=power;data.shape='DISK';data.size=65
        obj=bpy.data.objects.new('Site.'+name,data);b.collection('Site presentation').objects.link(obj)
        obj.location=loc;obj.rotation_euler=(Vector((-8,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
    cams={'overview':camera(b,'Site overview',(-14,-155,115),(-14,-5,0),205),
          'plan':camera(b,'Site plan',(-14,-5,140),(-14,-5,0),205)}
    cams['plan'].location=(-14,9,140)
    cams['plan'].rotation_euler=(0,0,0)
    cams['process']=camera(b,'Attached process buildings',(77,100,82),(6,33,-1),115)
    cams['process-plan']=camera(b,'Process buildings plan',(6,34,120),(6,34,0),120)
    cams['process-plan'].rotation_euler=(0,0,0)
    cams['alignment']=camera(b,'Aligned reactor and power plant',(-32,0,145),(-32,0,0),150)
    cams['alignment'].rotation_euler=(0,0,0)
    cams['turbine']=camera(b,'Turbine equipment draft',(-120,-100,75),(*site.TURBINE['centre'],3),105)
    for view,cam in cams.items():
        col=b.collection('Site annotations.'+view)
        if view in ('process','process-plan'):
            text_on_camera('Title.'+view,'WISTR | Converter, refiner and off-gas buildings',-43,25.0,1.15,cam,col)
            text_on_camera('Detail.'+view,'Duct: gold fuel IN / rose fuel OUT / teal coolant / purple off-gas / blue supply gas',-43,22.5,.65,cam,col,'#526575')
            text_on_camera('Footer.'+view,'Provisional envelopes and tie-ins; process duties, treatment performance and supports remain open',-43,-25,.60,cam,col,'#526575')
            continue
        if view=='alignment':
            text_on_camera('Title.alignment','REACTOR / TURBINE HALL | Aligned building centres',-69,40,1.4,cam,col)
            text_on_camera('Detail.alignment','Two 45-degree offset bends per pipe; shallow 20-degree outlet alignment turn',-69,37.5,.85,cam,col,'#526575')
            text_on_camera('Footer.alignment','60 x 40 m hall | Building centres Y = 0 | Preliminary routing; pipe stresses and supports remain to design',-69,-40,.8,cam,col,'#526575')
            continue
        if view=='turbine':
            text_on_camera('Title.turbine','MOTOR-BFP TURBINE HALL | Machinery detail',-48,28,1.25,cam,col)
            text_on_camera('Detail.turbine','Illustrative casings and service connections / existing 60 x 40 m layout',-48,25.5,.85,cam,col,'#526575')
            text_on_camera('Footer.turbine','Ground: condensers / reheaters / pumps / heaters | Upper: turbines / generators / storage',-48,-28,.72,cam,col,'#526575')
            continue
        text_on_camera('Title.'+view,'FAST SALT SYSTEM | Site arrangement',-81,46,2.0,cam,col)
        text_on_camera('Subtitle.'+view,'Provisional building / equipment envelopes / existing WISTR installation',-81,42.5,1.05,cam,col,'#526575')
        labels=[(-80,'TURBINE BUILDING','60 x 40 m / 28 m high'),(-20,'REACTOR BUILDING','42 m shell / attached process wings'),(44,'PROCESS BUILDINGS','Converter / refiner / off-gas')]
        for i,(x,title,detail) in enumerate(labels):
            text_on_camera(f'Label.{view}.{i}',title,x,-32,1.32,cam,col)
            text_on_camera(f'Detail.{view}.{i}',detail,x,-34.3,1.0,cam,col,'#526575')
        text_on_camera('Footer.'+view,'Purple: steam / Blue: feedwater     |     Shared pad datum is illustrative; equipment sizing and civil grade remain open.',
                       -81,-46,1.0,cam,col,'#526575')
    return cams


def select(b,cams,view):
    scene=bpy.context.scene;scene.camera=cams[view];scene['section_cutaway']=view=='overview'
    for key in cams:
        col=b.collections['Site annotations.'+key];col.hide_render=col.hide_viewport=key!=view
    for obj in bpy.data.objects:
        if obj.get('site_roof'):obj.hide_render=obj.hide_viewport=view in ('plan','alignment','turbine','process','process-plan')
    for obj in bpy.data.objects:
        if obj.get('turbine_upper'):obj.hide_render=obj.hide_viewport=view in ('plan','alignment','process','process-plan')
        if obj.name.startswith('site.turbine.') and any('.'+k in obj.name for k in ['south','west','panel_joint']):
            obj.hide_render=obj.hide_viewport=view=='turbine'
    for key in ('Shell','Crane'):
        col=bpy.data.collections.get(key)
        if col:col.hide_render=col.hide_viewport=view in ('plan','alignment','process','process-plan')
    for obj in bpy.data.objects:
        if obj.get('air_plenum_part'):
            hidden=(obj.get('air_plenum_lid',False) and view in ('plan','alignment','process','process-plan')) or (view=='overview' and obj.get('air_plenum_front',False) and obj.get('air_plenum_service')=='hot')
            obj.hide_render=obj.hide_viewport=hidden
    # Inspection views open the nearer process walls; plan keeps all perimeter walls.
    for ob in bpy.data.objects:
        if ob.name.startswith(('site.fuel_preparation.','site.off_gas.','site.converter.')) and any('.'+key in ob.name for key in ('north','east')):
            ob.hide_render=ob.hide_viewport=(view=='process')
    bpy.context.view_layer.update()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/site-study')
    parser.add_argument('--build-only',action='store_true')
    parser.add_argument('--with-piping',action='store_true',help='Add the checked provisional main-circuit routing')
    parser.add_argument('--view',choices=['overview','plan','alignment','turbine','process','process-plan'])
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    source=ROOT/site.SOURCE; report_source=ROOT/site.SOURCE_REPORT
    report=json.loads(report_source.read_text())
    bpy.ops.wm.open_mainfile(filepath=str(source))
    # Remove only presentation objects from this in-memory copy. Retain Boolean cutters and reactor assets.
    for obj in list(bpy.data.objects):
        if obj.name.startswith('presentation.') or obj.type in ('LIGHT','CAMERA','FONT'):
            bpy.data.objects.remove(obj,do_unlink=True)
    scene=bpy.context.scene
    b=SceneBuilder();routes=compose(b,report);checks=check_layout(routes)
    from textual_graphics.site_process_buildings import check_process_annexes
    b.process_annexes['checks']=check_process_annexes(b,site,installation,b.process_annexes)
    from textual_graphics.site_salt_distribution import check_salt_distribution
    b.salt_distribution['checks']=check_salt_distribution(b.salt_distribution,site,b.process_annexes)
    from textual_graphics.site_fuel_pressure import check_fuel_pressure
    b.fuel_pressure['checks']=check_fuel_pressure(b.fuel_pressure,site,b.process_annexes,b.salt_distribution)
    from textual_graphics.site_fresh_air import check_fresh_air
    b.fresh_air['checks']=check_fresh_air(b.fresh_air,site,installation,b.process_annexes,b.salt_distribution,b.fuel_pressure)
    piping=None
    if args.with_piping:
        from turbine_pipe_geometry import add_piping
        piping=add_piping(b,ROOT,site)
        ox=site.TURBINE['centre'][0]-site.TURBINE['size'][0]/2;oy=site.TURBINE['centre'][1]-site.TURBINE['size'][1]/2
        for service,name,index in [('steam','Main steam to HP',0),('water','HP4 feedwater to SG interface',-1)]:
            internal=next(q for q in piping['routes'] if q['name']==name)
            external=next(q for q in routes if q['service']==service)
            point=internal['render_points'][index]
            assert (Vector((point[0]+ox,point[1]+oy,point[2]+site.PAD_Z))-Vector(external['end'])).length<1e-5
            p0,p1=internal['render_points'][:2] if index==0 else internal['render_points'][-2:]
            assert abs(p0[1]-p1[1])<1e-6 and abs(p0[2]-p1[2])<1e-6
        checks['checks'].append('Internal steam and feedwater endpoints and wall-normal tangents match site routes')
    cams=presentation(b)
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=1800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.view_settings.exposure=.1
    scene['site_scope']='Motor-BFP turbine hall, reactor, rectangular process-building reservations and fuel supply/return duct'
    scene['site_source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    scene['site_pad_datum']='Common access pad at reactor sub-floor -9.1 m; actual civil grade unresolved'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.overlay.show_overlays=False
    args.output.mkdir(parents=True,exist_ok=True)
    data=dict(title='Fast Salt System provisional site',units='metres',source=site.SOURCE,
              source_sha256=scene['site_source_sha256'],source_report_sha256=hashlib.sha256(report_source.read_bytes()).hexdigest(),
              pad_z=site.PAD_Z,turbine=site.TURBINE,fuel_preparation=site.FUEL_PREPARATION,off_gas=site.OFF_GAS,converter=site.CONVERTER,process_annexes=b.process_annexes,turbine_layout=json.loads((ROOT/'models/turbine-layout.json').read_text()),turbine_equipment=b.turbine_equipment,
              secondary_connections=routes,validation=checks,internal_piping=piping,salt_distribution=b.salt_distribution,fuel_pressure=b.fuel_pressure,fresh_air=b.fresh_air,
              exclusions=['Salt-preparation chemistry/throughput and off-gas treatment performance/emission limits','Supplier equipment outlines, full piping and structures','Final heat sink and cooling-water pump layout','Civil grade and drainage','Equipment installation and transport qualification'])
    if piping:
        (args.output/'turbine-piping.json').write_text(json.dumps(piping,indent=2)+'\n')
    (args.output/'site-report.json').write_text(json.dumps(data,indent=2)+'\n')
    select(b,cams,'overview')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'fast-salt-site.blend'))
    for view in ([] if args.build_only else ([args.view] if args.view else cams)):
        select(b,cams,view);scene.render.filepath=str(args.output/f'site-{view}-draft.png')
        bpy.ops.render.render(write_still=True)
    select(b,cams,args.view or 'overview');bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'fast-salt-site.blend'))
    print('SITE_OK '+json.dumps(checks),flush=True)

if __name__=='__main__':main()
