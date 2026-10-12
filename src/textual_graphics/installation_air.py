"""Illustrative air duct envelopes and explicit connection topology, not airflow sizing."""
import json
import math
import bpy
from mathutils import Vector
from .air_insulation import insulated_air_route,materials,tag


def polar(radius,angle,z):
    t=math.radians(angle)
    return (radius*math.cos(t),radius*math.sin(t),z)


def air_networks(b,layout,repo):
    p=layout.AIR
    materials(b)
    spec=p['insulation'];ins=spec['thickness'];jacket=spec['cladding']
    root=b.assembly('connections.air','Air distribution')
    result={'scope':'Provisional cooling-air routing envelopes; no airflow or heat-removal validation',
            'branches':[], 'reactor_stub_ports':{},
            'fresh_header_arc':[p['fresh_start_angle'],p['fresh_end_angle']],
            'maintenance':'Side connections remain outside the cover footprint; disconnect spools for manifold maintenance. Full crane routes remain to check.'}
    result['construction']='Exterior hollow concrete rings; fresh ring interrupted at access door with sealed ends'
    result['ring_sections']={}
    inner=p['concrete_inner_radius'];outer=p['concrete_outer_radius'];skin=p['concrete_skin']
    rings={}
    liners={}
    half_gap=math.degrees(math.asin(layout.ACCESS['ring_gap_width']/2/inner))
    gap=(layout.ACCESS['angle']-half_gap,layout.ACCESS['angle']+half_gap)
    result['fresh_access_gap_degrees']=list(gap)
    for kind in ('hot','fresh'):
        ring_outer=outer+2*(ins+jacket) if kind=='hot' else outer
        ring_height=p['concrete_height']+4*(ins+jacket) if kind=='hot' else p['concrete_height']
        z=p[kind+'_z'];bottom=z-ring_height/2;top=z+ring_height/2
        result['ring_sections'][kind]={'inner_radius':inner,'outer_radius':ring_outer,
            'bottom':bottom,'top':top,'skin':skin,
            'clear_width':ring_outer-inner-2*skin,'clear_height':ring_height-2*skin}
        rings[kind]={part:[] for part in ('floor','roof','inner_web','outer_web')}
        segments=[(False,0,180),(True,180,360)] if kind=='hot' else [(False,0,gap[0]),(False,gap[1],180),(True,180,360)]
        for front,start,end in segments:
            for name,ri,ro,z0,z1 in [('floor',inner,ring_outer,bottom,bottom+skin),
                                    ('roof',inner,ring_outer,top-skin,top),
                                    ('inner_web',inner,inner+skin,bottom+skin,top-skin),
                                    ('outer_web',ring_outer-skin,ring_outer,bottom+skin,top-skin)]:
                obj=b.annulus(f'{kind}_plenum.{name}.{start}',root,ri,ro,z0,z1,
                              'concrete',start=start,end=end,steps=128)
                obj['air_plenum_part']=True;obj['air_plenum_service']=kind
                obj['air_plenum_front']=front;obj['air_plenum_lid']=name=='roof'
                rings[kind][name].append(obj)
            if kind=='hot':
                liners.setdefault(kind,{part:[] for part in ('floor','roof','inner_web','outer_web')})
                # Insulate the hot-air face of the concrete ring, preserving its clear width with a small outward/height allowance.
                ri=inner+skin;ro=ring_outer-skin;z0=bottom+skin;z1=top-skin
                layers=[('insulation',ins,0,'air_insulation'),('cladding',jacket,ins,'air_cladding')]
                for layer,t,offset,mat in layers:
                    for part,a,c,low,high in [
                        ('floor',ri,ro,z0+offset,z0+offset+t),
                        ('roof',ri,ro,z1-offset-t,z1-offset),
                        ('inner_web',ri+offset,ri+offset+t,z0+ins+jacket,z1-ins-jacket),
                        ('outer_web',ro-offset-t,ro-offset,z0+ins+jacket,z1-ins-jacket)]:
                        obj=tag(b.annulus(f'hot_plenum.{layer}.{part}.{start}',root,a,c,low,high,mat,start=start,end=end,steps=128),spec,layer)
                        obj['air_plenum_part']=True;obj['air_plenum_service']='hot';obj['air_plenum_front']=front;obj['air_plenum_lid']=part=='roof'
                        liners[kind][part].append(obj)
            # Thin colored floor finish identifies each air passage in the open-top views.
            obj=b.annulus(f'{kind}_plenum.color_key.{start}',root,inner+skin,ring_outer-skin,
                          bottom+skin+.005,bottom+skin+.015,
                          'exhaust_air' if kind=='hot' else 'fresh_air',start=start,end=end,steps=128)
            obj['air_plenum_part']=True;obj['air_plenum_service']=kind
            obj['air_plenum_front']=front

    # Seal both ends of the C-shaped fresh passage; no air opens into the driveway.
    cap_angle=math.degrees(skin/inner)
    for i,(start,end) in enumerate(((gap[0]-cap_angle,gap[0]),(gap[1],gap[1]+cap_angle))):
        cap=b.annulus(f'fresh_plenum.end_wall{i}',root,inner+skin,outer-skin,
                      p['fresh_z']-p['concrete_height']/2+skin,p['fresh_z']+p['concrete_height']/2-skin,
                      'concrete',start=start,end=end,steps=4)
        cap['air_plenum_part']=True;cap['air_plenum_service']='fresh';cap['air_plenum_front']=False

    def branch(component,kind,points,diameter):
        obj=(insulated_air_route(b,component+'.'+kind,root,points,diameter,spec) if kind=='hot'
             else b.rounded_pipe(component+'.'+kind,root,points,diameter/2,'fresh_air',bend=1.1))
        obj.data.use_fill_caps=False  # Open duct mouths inside the hollow plenum.
        obj['service']='Cooling exhaust air' if kind=='hot' else 'Fresh cooling air'
        obj['flow_direction']='equipment to header' if kind=='hot' else 'header to equipment'
        obj['scope']='Provisional external cooling connection; not a process-fluid nozzle'
        result['branches'].append({'component':component,'service':kind,'object':obj.name,
                                   'diameter':diameter,'outside_diameter':diameter+2*(ins+jacket) if kind=='hot' else diameter,'points':[list(q) for q in points]})
        return obj

    def equipment_branches(component,hot_port,fresh_port,hot_diameter,fresh_diameter,roof_outlet=False,fresh_lead=None):
        angle=math.degrees(math.atan2(hot_port[1],hot_port[0]))
        riser_radius=p['fuel_hot_riser_radius'] if component.startswith('fuel_tank_') else p['hot_inside_riser_radius']
        wall=polar(riser_radius,angle,hot_port[2])
        rise=polar(riser_radius,angle,p['hot_z'])
        if roof_outlet:
            hot_points=[hot_port,(hot_port[0],hot_port[1],p['hot_z']),rise,polar(p['hot_radius'],angle,p['hot_z'])]
        elif component in ('fuel_tank_5','fuel_tank_6'):
            lead=Vector(hot_port)+Vector(polar(.9,angle,0))
            cross=p['fuel_storage_cross_z']
            hot_points=[hot_port,tuple(lead),(lead.x,lead.y,cross),(wall[0],wall[1],cross),rise,polar(p['hot_radius'],angle,p['hot_z'])]
        else:
            hot_points=[hot_port,wall,rise,polar(p['hot_radius'],angle,p['hot_z'])]
        branch(component,'hot',hot_points,hot_diameter)
        lead=fresh_port if fresh_lead is None else fresh_lead
        angle=math.degrees(math.atan2(lead[1],lead[0]))
        low=polar(p['fresh_inside_riser_radius'],angle,fresh_port[2])
        rise=polar(p['fresh_inside_riser_radius'],angle,p['fresh_z'])
        approach=[fresh_port] if fresh_lead is None else [fresh_port,fresh_lead]
        branch(component,'fresh',approach+[low,rise,polar(p['fresh_radius'],angle,p['fresh_z'])],fresh_diameter)

    bpy.context.view_layer.update()
    for i in range(1,4):
        sg=b.assemblies[f'equipment.steam_generator_{i}']
        # Local -X face is 90 degrees from both process faces, away from pump.
        valve=bpy.data.objects[sg.name+'.air_butterfly_valve']
        hot=sg.matrix_world @ Vector(valve['top_port_local'])
        fresh=sg.matrix_world @ Vector((-layout.STEAM_GENERATORS['width']/2,1.0,
                                       p['low_branch_z']-layout.FLOOR_Z))
        lead=sg.matrix_world @ Vector((-layout.STEAM_GENERATORS['width']/2-1.2,1.0,
                                      p['low_branch_z']-layout.FLOOR_Z))
        equipment_branches(f'generator_{i}',hot,fresh,p['generator_hot_diameter'],p['generator_fresh_diameter'],roof_outlet=True,fresh_lead=lead)
    for i in range(1,7):
        tank=b.assemblies[f'equipment.fuel_storage_{i}']
        hot=tank.matrix_world @ Vector((layout.FUEL_STORAGE['length']/2,0,layout.FUEL_STORAGE['height']/2-.6))
        fresh=tank.matrix_world @ Vector((layout.FUEL_STORAGE['length']/2,0,
                                         p['low_branch_z']-tank.location.z))
        equipment_branches(f'fuel_tank_{i}',hot,fresh,p['fuel_hot_diameter'],p['fuel_fresh_diameter'])

    # Use source metadata, then verify against the imported physical stubs in check_air_networks.
    source=json.loads((repo/layout.REACTOR['baseline']/'reactor-study-report.json').read_text())
    q=source['air_system']['dimensions'];a=source['air_system']['parameters']
    rotation=math.radians(layout.REACTOR['rotation_degrees'])
    for kind,service in [('hot','hot'),('fresh','cold')]:
        port=q['ports'][service];x,y,z=port['point']
        start=(x*math.cos(rotation)-y*math.sin(rotation),x*math.sin(rotation)+y*math.cos(rotation),z+layout.REACTOR['origin_z'])
        dx,dy,_=port['direction'];direction=Vector((dx*math.cos(rotation)-dy*math.sin(rotation),dx*math.sin(rotation)+dy*math.cos(rotation),0))
        lead=Vector(start)+direction*1.2
        result['reactor_stub_ports'][kind]=list(start)
        angle=math.degrees(math.atan2(start[1],start[0]))
        if kind=='hot':
            points=[start,tuple(lead),(lead.x,lead.y,p['hot_z']),
                    polar(p['reactor_inside_riser_radius'],angle,p['hot_z']),polar(p['hot_radius'],angle,p['hot_z'])]
        else:
            # Direct low run from the fresh ring; only the reactor end rises.
            points=[start,tuple(lead),(lead.x,lead.y,p['fresh_z']),
                    polar(p['fresh_radius'],angle,p['fresh_z'])]
        obj=branch('reactor',kind,points,a['duct_diameter']);obj['removable_for_maintenance']=True
        flange=b.annulus('reactor.'+kind+'_disconnect',root,a['duct_diameter']/2,a['duct_diameter']/2+.10,0,.10,'rail',steps=48)
        flange.location=start;flange.rotation_euler=direction.to_track_quat('Z','Y').to_euler()

    stack_angle=layout.STACKS['angles'][0]
    exhaust=[polar(p['hot_radius'],stack_angle,p['hot_z']),
             polar(layout.STACKS['radius'],stack_angle,p['hot_z'])]
    insulated_air_route(b,'stack_connection',root,exhaust,p['hot_diameter'],spec,rounded=False)
    result['stack_connection']=[list(q) for q in exhaust]
    intake=[polar(p['fresh_radius'],p['intake_angle'],p['fresh_z']),
            polar(p['intake_radius'],p['intake_angle'],p['fresh_z'])]
    b.tube('outside_air_intake',root,intake,p['fresh_diameter']/2,'fresh_air').data.use_fill_caps=False
    # An intake box distinguishes the outdoor supply from the exhaust stack.
    intake_root=b.assembly('connections.fresh_air_intake','Air distribution',intake[-1],p['intake_angle'])
    b.box('louver_housing',intake_root,(.7,2.4,2.4),(0,0,0),'fresh_air',.05)
    b.box('dark_opening',intake_root,(.04,2.1,2.1),(.37,0,0),'dark')
    for j in range(9):
        b.box(f'louver{j}',intake_root,(.15,2.1,.08),(.42,0,-.88+j*.22),'rail')
    result['intake_connection']=[list(q) for q in intake]

    # Schematic ports connect the hollow ring interiors to their branches.
    shell=bpy.data.objects['building.shell.retained_wall']
    cuts=b.assembly('connections.air_wall_openings','Air opening tools')
    count=0
    def opening(targets,angle,z,diameter,radius,vertical=False):
        nonlocal count
        count+=1
        position=polar(radius,angle,z)
        cutter=b.cylinder(f'opening_{count}',cuts,diameter/2+.04,2.0,position,None,vertices=48,bevel=0)
        if not vertical:
            cutter.rotation_mode='QUATERNION'
            cutter.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector(polar(1,angle,0)))
        for target in targets:
            modifier=target.modifiers.new(f'Air opening {count}','BOOLEAN')
            modifier.operation='DIFFERENCE';modifier.object=cutter;modifier.solver='EXACT'
        cutter.hide_render=True;cutter.hide_set(True)
    for route in result['branches']:
        kind=route['service'];points=route['points'];diameter=route['diameter']
        angle=math.degrees(math.atan2(points[-1][1],points[-1][0]))%360
        targets=rings[kind]['inner_web']+([shell] if 0<angle<180 else [])
        if kind=='hot':targets+=liners[kind]['inner_web']
        opening(targets,angle,p[kind+'_z'],route['outside_diameter'],inner)
        route['wall_penetration']=list(polar(inner-layout.BUILDING['wall_thickness']/2,angle,p[kind+'_z']))
    opening(rings['hot']['outer_web']+liners['hot']['outer_web'],stack_angle,p['hot_z'],p['hot_diameter']+2*(ins+jacket),outer+2*(ins+jacket)-skin/2)
    opening(rings['fresh']['outer_web'],p['intake_angle'],p['fresh_z'],p['fresh_diameter'],outer-skin/2)
    result['hot_air_insulation']=dict(spec,insulated_branch_count=10,stack_connector=True,concrete_ring_internal_lining=True,ring_clear_width=outer-inner-2*skin,ring_clear_height=p['concrete_height']-2*skin+2*(ins+jacket))
    return result


def check_air_networks(b,layout,air):
    p=layout.AIR
    assert len(layout.STACKS['angles'])==1
    expected={'reactor'}|{f'generator_{i}' for i in range(1,4)}|{f'fuel_tank_{i}' for i in range(1,7)}
    for kind in ('hot','fresh'):
        routes=[r for r in air['branches'] if r['service']==kind]
        assert {r['component'] for r in routes}==expected and len(routes)==10
        radius=p['hot_radius'] if kind=='hot' else p['fresh_radius']
        height=p['hot_z'] if kind=='hot' else p['fresh_z']
        for r in routes:
            endpoint=r['points'][-1]
            assert abs(math.hypot(*endpoint[:2])-radius)<1e-5
            assert abs(endpoint[2]-height)<1e-5
            if kind=='fresh':
                angle=math.degrees(math.atan2(endpoint[1],endpoint[0]))
                while angle<p['fresh_start_angle']:angle+=360
                assert angle<=p['fresh_end_angle']
            obj=bpy.data.objects[r['object']]
            actual=[obj.matrix_world @ Vector(v.co[:3]) for v in obj.data.splines[0].points]
            assert (actual[0]-Vector(r['points'][0])).length<1e-5
            assert (actual[-1]-Vector(endpoint)).length<1e-5
    for i in range(1,4):
        route=next(r for r in air['branches'] if r['component']==f'generator_{i}' and r['service']=='hot')
        sg=b.assemblies[f'equipment.steam_generator_{i}']
        valve=bpy.data.objects[sg.name+'.air_butterfly_valve']
        port=sg.matrix_world @ Vector(valve['top_port_local'])
        assert (Vector(route['points'][0])-port).length<1e-5
        direction=(Vector(route['points'][1])-Vector(route['points'][0])).normalized()
        assert direction.dot(Vector((0,0,1)))>.99999
        fresh=next(r for r in air['branches'] if r['component']==f'generator_{i}' and r['service']=='fresh')
        inverse=sg.matrix_world.inverted()
        port=inverse @ Vector(fresh['points'][0]);lead=inverse @ Vector(fresh['points'][1])
        assert abs(port.x+layout.STEAM_GENERATORS['width']/2)<1e-5
        assert abs(port.y)+fresh['diameter']/2<layout.STEAM_GENERATORS['width']/2
        assert (lead-port).normalized().dot(Vector((-1,0,0)))>.99999

    for kind,name in [('hot','hot_stub'),('fresh','cold_stub')]:
        obj=bpy.data.objects['reactor.air_ducts.'+name]
        # Section modifiers trim the bounds asymmetrically; terminal metadata identifies the side-facing end.
        top=obj.matrix_world @ Vector(obj['terminal_local'])
        assert (top-Vector(air['reactor_stub_ports'][kind])).length<1e-5, (kind,list(top),air['reactor_stub_ports'][kind])
        assert bpy.data.objects['connections.air.reactor.'+kind]['removable_for_maintenance']
    stack=air['stack_connection'];intake=air['intake_connection']
    assert (Vector(stack[0])-Vector(polar(p['hot_radius'],layout.STACKS['angles'][0],p['hot_z']))).length<1e-5
    assert (Vector(stack[-1])-Vector(polar(layout.STACKS['radius'],layout.STACKS['angles'][0],p['hot_z']))).length<1e-5
    assert (Vector(intake[0])-Vector(polar(p['fresh_radius'],p['intake_angle'],p['fresh_z']))).length<1e-5
    assert math.hypot(*intake[-1][:2])>p['fresh_radius']
    assert p['hot_z']<layout.STACKS['base_z']+layout.STACKS['base_height']+layout.STACKS['height']
    # External ring envelopes touch the building wall and have open internal chambers.
    for kind,section in air['ring_sections'].items():
        assert abs(section['inner_radius']-layout.BUILDING['diameter']/2)<1e-6
        assert section['clear_width']>2.0 and section['clear_height']>2.0
        assert section['outer_radius']<layout.STACKS['radius']-(layout.STACKS['tube_diameter']+.89)/2
    gap=air['fresh_access_gap_degrees']
    for route in air['branches']:
        if route['service']=='fresh':
            theta=math.degrees(math.atan2(route['points'][-1][1],route['points'][-1][0]))%360
            margin=math.degrees(math.asin((route['diameter']/2+p['concrete_skin'])/p['concrete_inner_radius']))
            assert theta<gap[0]-margin or theta>gap[1]+margin
    assert abs(air['ring_sections']['fresh']['bottom']-layout.FLOOR_Z)<1e-6
    crane_bottom=layout.CRANE['runway_height']-.3
    assert air['ring_sections']['hot']['top']<crane_bottom
    for route in air['branches']:
        points=route['points'];half=route['outside_diameter']/2;kind=route['service']
        inner_wall=layout.BUILDING['diameter']/2-layout.BUILDING['wall_thickness']
        assert all(math.hypot(*q[:2])+half<inner_wall for q in points[:-1]), route['component']
        assert abs(points[-2][2]-points[-1][2])<1e-6
        assert abs(route['wall_penetration'][2]-p[kind+'_z'])<1e-6
        section=air['ring_sections'][kind]
        lining=sum(p['insulation'][k] for k in ('thickness','cladding')) if kind=='hot' else 0
        assert section['bottom']+section['skin']+lining<points[-1][2]-half
        assert section['top']-section['skin']-lining>points[-1][2]+half
    assert p['reactor_hot_cross_z']-1.0>layout.GENERATOR_TOP_Z
    assert p['reactor_hot_cross_z']+1.0<layout.CRANE['runway_height']-.3
    assert p['fresh_inside_riser_radius']-.35>layout.SECONDARY['header_radius']+layout.SECONDARY['water_header_diameter']/2
    # The low equipment feeds cross beneath the water header, not through it.
    assert p['low_branch_z']+max(p['generator_fresh_diameter'],p['fuel_fresh_diameter'])/2 < layout.manifold_point('water')[2]-layout.SECONDARY['water_header_diameter']/2
    air['checked_vertical_clearances']={'hot_ring_below_crane_runway_m':crane_bottom-air['ring_sections']['hot']['top'],
                                      'reactor_hot_cross_above_generator_m':p['reactor_hot_cross_z']-1-layout.GENERATOR_TOP_Z,
                                      'reactor_hot_cross_below_crane_m':layout.CRANE['runway_height']-.3-p['reactor_hot_cross_z']-1}
    air['reactor_floor_supply_check']=check_floor_supply(layout)
    air['hot_air_insulation_check']=check_hot_insulation(layout)
    return ['Reactor fresh-air branch follows the floor with one rise at the reactor; equipment and air-route clearances checked',
            'Three fresh-air inlets on perpendicular side faces with normal approaches, away from pumps',
            'Three generator exhaust ducts start vertically from roof-mounted butterfly-valve boxes',
            'One exhaust stack; ten hot and ten fresh branches connect reactor, three generators and six fuel tanks',
            'Both reactor air routes meet actual imported side-manifold stub centres and have removable-spool markers',
            'Fresh C-shaped plenum has sealed access ends and all branch ports outside gap; hot ring remains below crane',
            'Rings clear stack base; reactor crossover clears generators and runway; small fresh feeds cross below water header',
            'All twenty equipment air routes stay inside wall until horizontal entry directly into their ring']


def check_floor_supply(layout):
    """Screen the revised low reactor duct against equipment and other air routes."""
    from .installation_clearance import bounds,segment_box,segdist
    obj=bpy.data.objects['connections.air.reactor.fresh']
    pts=[obj.matrix_world@Vector(p.co[:3]) for p in obj.data.splines[0].points]
    radius=obj.data.bevel_depth
    floor_gap=min(v.z for v in pts)-radius-layout.FLOOR_Z
    assert floor_gap>=.49
    assert all(a.z>=b.z-1e-6 for a,b in zip(pts,pts[1:])), 'Unexpected high crossover'
    clearances=[]
    for other in bpy.context.scene.objects:
        if other.type=='MESH' and other.name.startswith('equipment.'):
            inv=other.matrix_world.inverted();lo,hi=bounds(other.bound_box)
            local=[inv@p for p in pts]
            gap=min(segment_box(a,b,lo,hi) for a,b in zip(local,local[1:]))-radius
            clearances.append((gap,other.name))
        elif other.type=='CURVE' and other.name.startswith('connections.air.') and other!=obj:
            op=[other.matrix_world@Vector(p.co[:3]) for p in other.data.splines[0].points]
            gap=min(segdist(a,b,c,d)[0] for a,b in zip(pts,pts[1:]) for c,d in zip(op,op[1:]))-radius-other.data.bevel_depth
            clearances.append((gap,other.name))
    assert all(gap>=-.001 for gap,name in clearances),sorted(clearances)[:8]
    return {'floor_clearance_m':floor_gap,'nearest_envelopes':[{'clearance_m':gap,'object':name} for gap,name in sorted(clearances)[:5]],
            'scope':'Duct centreline capsules versus oriented equipment boxes and other air routes; process routes screened separately; supports and airflow not sized'}


def check_hot_insulation(layout):
    p=layout.AIR;spec=p['insulation']
    routes=[o for o in bpy.context.scene.objects if o.get('air_insulated')]
    assert len(routes)==11,len(routes)
    for guide in routes:
        radius=guide['bare_diameter_m']/2
        assert abs(guide.data.bevel_depth-radius-spec['thickness']-spec['cladding'])<1e-6
        assert guide['minimum_bend_radius_m']>guide.data.bevel_depth
        for name,thickness in [('metal',spec['branch_wall']),('insulation',spec['thickness']),('cladding',spec['cladding'])]:
            obj=bpy.data.objects[guide.name+'.'+name]
            assert abs(obj['radial_thickness_m']-thickness)<1e-7
    assert bpy.data.objects.get('reactor.hot_air_insulation.plenum_insulation')
    assert bpy.data.objects.get('reactor.hot_air_insulation.stub_insulation')
    assert bpy.data.objects.get('building.stack_1.insulation')
    for part in ('floor','roof','inner_web','outer_web'):
        assert bpy.data.objects.get('connections.air.hot_plenum.insulation.'+part+'.0')
    return {'insulated_routes':len(routes),'radial_insulation_m':spec['thickness'],'cladding_m':spec['cladding'],
            'reactor_hot_collector':True,'hot_concrete_ring_lined':True,'stack_barrel_wrapped':True,
            'scope':'Geometric layer thicknesses, bend envelopes and coverage; no thermal qualification'}
