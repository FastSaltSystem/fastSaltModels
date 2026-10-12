"""Provisional coolant transfer and nitrogen supply geometry, not equipment sizing."""
import json,math
import bpy
from mathutils import Vector
from .installation_piping import fillet_path,shell_mesh,move_collection
from .installation_clearance import bounds,segment_box,segdist


def polar(r,a,z):
    t=math.radians(a);return (r*math.cos(t),r*math.sin(t),z)


def cut(b,name,root,points,radius,targets):
    assert len(points)==2
    a,c=map(Vector,points);axis=c-a
    tool=b.cylinder(name,root,radius,axis.length,tuple((a+c)/2),None,vertices=48,bevel=0)
    tool.rotation_mode='QUATERNION';tool.rotation_quaternion=Vector((0,0,1)).rotation_difference(axis.normalized())
    tool['utility_opening_tool']=True;tool.hide_render=True;tool.hide_set(True)
    for target in targets:
        mod=target.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
    return tool


def build_coolant_tank(b,layout):
    from .air_insulation import materials
    materials(b)
    p=layout.COOLANT_STORAGE;r=p['radius'];h=p['height'];t=p['insulation'];j=p['cladding']
    root=b.assembly('equipment.coolant_storage','Coolant storage',p['position'])
    b.material('tank_jacket','#ABB6B4',metallic=.65,roughness=.32)
    b.cylinder('closed_tank',root,r,h,(0,0,h/2),'coolant',vertices=96,bevel=.05)
    b.cylinder('roof',root,r+.03,.13,(0,0,h),'coolant',vertices=96)
    for layer,ri,ro,mat in [('insulation',r,r+t,'air_insulation'),('cladding',r+t,r+t+j,'tank_jacket')]:
        ob=b.annulus(layer,root,ri,ro,0 if layer=='insulation' else -t-j,h+.065 if layer=='insulation' else h+.065+t+j,mat,steps=128)
        ob['insulation_allowance_m']=t;ob['scope']='350 mm geometric allowance borrowed from return-salt piping; tank heat loss not calculated'
    bottom=b.annulus('bottom_insulation',root,.09,r+t,-t,0,'air_insulation',steps=96)
    jacket=b.annulus('bottom_cladding',root,.09,r+t+j,-t-j,-t,'tank_jacket',steps=96)
    b.cylinder('top_insulation',root,r+t,t,(0,0,h+.065+t/2),'air_insulation',vertices=96,bevel=0)
    b.cylinder('top_cladding',root,r+t+j,j,(0,0,h+.065+t+j/2),'tank_jacket',vertices=96,bevel=0)
    for z in (1,3.5,6):b.ring(f'jacket_band{z}',root,r+t+j+.009,z,.014,'rail')
    b.cylinder('access_neck',root,.38,.60,(.6,0,h+.30),'rail')
    b.cylinder('access_cover',root,.43,.07,(.6,0,h+.635),'rail')
    lx=-r-t-.20
    for y in (-.35,.35):b.beam(f'ladder{y}',root,(lx,y,-p['support_height']+.25),(lx,y,h+.7),.032,'rail')
    count=math.ceil((h+p['support_height']+.4)/.3)
    for i in range(count):b.beam(f'rung{i}',root,(lx,-.35,-p['support_height']+.45+i*.3),(lx,.35,-p['support_height']+.45+i*.3),.022,'rail')
    for x in (-1.25,1.25):
        for y in (-1.25,1.25):
            b.box(f'support_{x}_{y}',root,(.22,.22,p['support_height']),(x,y,-p['support_height']/2),'rail')
            b.box(f'foot_{x}_{y}',root,(.40,.40,.05),(x,y,-p['support_height']+.025),'rail')
            cutter=b.box(f'insulation_support_opening_{x}_{y}',root,(.24,.24,t+.06),(x,y,-t/2),None)
            cutter['utility_opening_tool']=True;cutter.hide_render=True;cutter.hide_set(True)
            for ob in (bottom,jacket):
                mod=ob.modifiers.new('Support penetration','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    root['bare_bottom_z']=p['position'][2];root['bottom_jacket_z']=p['position'][2]-t-j
    return root


def service_line(b,name,root,points,spec):
    path,radii=fillet_path(points,.12)
    ob=b.tube(name,root,path,spec['jacket_od']/2,'cold')
    ob.hide_render=True;ob.hide_set(True);ob['pipe_spec']=dict(spec)
    ob['minimum_bend_radius_m']=min(radii) if radii else 1e6
    ob['utility_route']=True;ob['service']='heated coolant transfer';ob['heat_traced']=True
    metal=shell_mesh(b,name+'.metal',root,path,spec['bare_od']/2,spec['bore']/2,'rail')
    ins_path=[q.copy() for q in path]
    if name=='reactor_to_pump':ins_path[0].z=points[0][2]-.085
    insulation=shell_mesh(b,name+'.insulation',root,ins_path,spec['jacket_od']/2,spec['bare_od']/2,'cold')
    for o in (metal,insulation):o['route_object']=ob.name;o['service']='heated coolant transfer'
    for o in (ob,metal,insulation):move_collection(b,o,'Utility piping')
    return ob


def build_transfer(b,layout):
    p=layout.COOLANT_TRANSFER;c=layout.COOLANT_STORAGE;tx,ty,tz=c['position']
    angle=math.degrees(math.atan2(ty,tx));direction=Vector(polar(1,angle,0));tank_r=math.hypot(tx,ty)
    z=p['pipe_z'];root=b.assembly('connections.coolant_transfer','Utility piping')
    pump=b.assembly('equipment.coolant_transfer_pump','Coolant transfer',polar(p['pump_radius'],angle,z),angle)
    pump['scope']='Small motor-driven transfer pump envelope; flow, head, NPSH and materials not selected'
    b.box('base',pump,(1.05,.65,.10),(0,0,layout.FLOOR_Z-z+.05),'rail',.02)
    for yy in (-.20,.20):b.box(f'foot{yy}',pump,(.50,.10,.22),(0,yy,-.20),'rail')
    casing=b.cylinder('casing',pump,.18,.45,(0,0,0),'cold',vertices=48)
    casing.rotation_euler.y=math.pi/2
    b.cylinder('motor_envelope',pump,.17,.48,(0,0,.40),'equipment',vertices=48)
    for sign in (-1,1):
        f=b.cylinder(f'flange{sign}',pump,.075,.035,(sign*.23,0,0),'rail',vertices=32)
        f.rotation_euler.y=math.pi/2
    plate=bpy.data.objects['reactor.vessel.bottom_plate'];bpy.context.view_layer.update()
    top=max((plate.matrix_world@Vector(v)).z for v in plate.bound_box)
    tap=Vector(polar(p['vessel_tap_radius'],angle,top))
    inlet=Vector(polar(p['pump_radius']-.225,angle,z));outlet=Vector(polar(p['pump_radius']+.225,angle,z))
    suction=[tuple(tap),(tap.x,tap.y,z),tuple(inlet)]
    discharge=[tuple(outlet),(tx,ty,z),(tx,ty,tz)]
    spec={'bare_od':p['outside_diameter'],'bore':p['outside_diameter']-2*p['wall'],'wall':p['wall'],
          'insulation':p['insulation'],'jacket_od':p['outside_diameter']+2*p['insulation']}
    routes=[]
    for name,points in [('reactor_to_pump',suction),('pump_to_storage',discharge)]:
        o=service_line(b,name,root,points,spec)
        routes.append({'name':o.name,'points':points,'diameter':p['outside_diameter'],'jacket_diameter':spec['jacket_od']})
    # Separate actual vessel/baffle/well openings in this installation copy only.
    tools=b.assembly('utilities.penetrations','Utility tools')
    cut(b,'vessel_bottom',tools,[(tap.x,tap.y,top+.10),(tap.x,tap.y,top-.18)],p['outside_diameter']/2+.002,[plate])
    cut(b,'baffle_floor',tools,[(tap.x,tap.y,top-.1),(tap.x,tap.y,z-.05)],spec['jacket_od']/2+.015,[bpy.data.objects['reactor.baffle.floor_sheet']])
    # Below the baffle floor, the line crosses only the concrete well wall.
    cut(b,'well_service_sleeve',tools,[polar(3.55,angle,z),polar(4.35,angle,z)],spec['jacket_od']/2+.015,[bpy.data.objects['reactor.well.wall']])
    tank=bpy.data.objects['equipment.coolant_storage.closed_tank']
    cut(b,'storage_bottom',tools,[(tx,ty,tz-.10),(tx,ty,tz+.10)],p['outside_diameter']/2+.002,[tank])
    # Low cylinder is a visual envelope: do not imply it is a fully hollow pressure vessel.
    return {'routes':routes,'pump':pump.name,'reactor_port':list(tap),'pump_inlet':list(inlet),'pump_outlet':list(outlet),
        'storage_port':[tx,ty,tz],'tank_insulation_m':c['insulation'],'tank_support_height_m':c['support_height'],
        'scope':p['scope']+'; openings/sleeves shown, seals and thermal movement not detailed'}


def build_nitrogen(b,layout):
    p=layout.NITROGEN;root=b.assembly('equipment.nitrogen_supply','Nitrogen supply',polar(p['radius'],p['angle'],layout.FLOOR_Z),p['angle'])
    b.material('nitrogen','#8FADB9',metallic=.35,roughness=.36)
    b.material('nitrogen_tank','#DAE2E2',metallic=.22,roughness=.32)
    b.box('pad',root,(5.3,6.3,1.2),(-.55,-1.55,-.60),'concrete',.04)
    r=p['tank_diameter']/2
    b.cylinder('vacuum_jacket',root,r,5.0,(0,0,3.5),'nitrogen_tank',vertices=64)
    for label,z in [('bottom_head',1.0),('top_head',6.0)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1)
        ob=b.finish(bpy.context.object,label,root,'nitrogen_tank',(0,0,z));ob.scale=(r,r,.5)
    for x,y in [(-.75,-.75),(.75,-.75),(-.75,.75),(.75,.75)]:b.box(f'leg{x}_{y}',root,(.14,.14,.75),(x,y,.375),'rail')
    b.ring('lower_seam',root,r+.006,1.05,.014,'rail');b.ring('upper_seam',root,r+.006,5.95,.014,'rail')
    b.box('vaporizer_base',root,(2.0,1.8,.12),(0,-3.5,.06),'rail',.02)
    for x in (-.55,0,.55):
        for y in (-3.95,-3.05):
            b.cylinder(f'vaporizer_tube{x}_{y}',root,.035,2.8,(x,y,1.65),'nitrogen',vertices=16)
            for axis in (0,1):
                b.box(f'fin{x}_{y}_{axis}',root,((.45,.012,2.8) if axis==0 else (.012,.45,2.8)),(x,y,1.65),'rail')
    b.tube('vaporizer_lower_header',root,[(-.65,-3.95,.30),(.65,-3.95,.30),(.65,-3.05,.30),(-.65,-3.05,.30)],.04,'nitrogen')
    b.tube('vaporizer_upper_header',root,[(-.65,-3.95,3.0),(.65,-3.95,3.0),(.65,-3.05,3.0),(-.65,-3.05,3.0)],.04,'nitrogen')
    liquid=[(0,-r,.80),(0,-2.25,.80),(-.65,-2.25,.80),(-.65,-3.95,.80),(-.65,-3.95,.30)]
    ln=b.rounded_pipe('liquid_to_vaporizer',root,liquid,.04,'nitrogen',bend=.15)
    ln['bare_od_m']=p['liquid_diameter'];ln['scope']='Vacuum-jacket envelope; provisionally 80 mm OD'
    b.box('regulator_panel',root,(.50,.20,.60),(-1.7,-3.5,1.25),'equipment',.03)
    b.box('regulator_stand',root,(.12,.12,1.0),(-1.7,-3.5,.5),'rail')
    b.rounded_pipe('relief_vent',root,[(.55,0,6.3),(.55,0,7.1),(.8,0,7.1)],.025,'nitrogen',bend=.1)
    b.rounded_pipe('fill_connection',root,[(r,0,.85),(1.65,0,.85),(1.65,0,.50)],.025,'nitrogen',bend=.1)
    for x in (-2.8,2.5):b.cylinder(f'bollard{x}',root,.065,1.0,(x,-4.7,.50),'crane',vertices=24)
    bpy.context.view_layer.update()
    header_z=p['header_z'];local_z=header_z-layout.FLOOR_Z
    local=[(-.65,-3.05,3.0),(-1.7,-3.05,3.0),(-1.7,-3.05,1.25),(-1.7,-3.5,1.25),(-2.1,-3.5,1.25),(-2.1,-3.5,local_z),(-2.1,0,local_z),(p['header_radius']-p['radius'],0,local_z)]
    world=[tuple(root.matrix_world@Vector(q)) for q in local]
    pipes=b.assembly('connections.nitrogen','Utility piping')
    ob=b.rounded_pipe('gas_supply',pipes,world,p['gas_diameter']/2,'nitrogen',bend=.15);ob['utility_gas']=True
    arc=[polar(p['header_radius'],a,header_z) for a in range(int(p['header_angles'][0]),int(p['header_angles'][1])+1)]
    head=b.tube('common_header',pipes,arc,p['gas_diameter']/2,'nitrogen');head['utility_gas']=True
    stubs=[]
    for a in (315,330,345):
        pts=[polar(p['header_radius'],a,header_z),polar(p['header_radius']-.40,a,header_z)]
        ob=b.tube(f'future_takeoff{a}',pipes,pts,p['gas_diameter']/2,'nitrogen');ob['utility_gas']=True
        end=pts[-1];cap=b.cylinder(f'capped_takeoff{a}',pipes,.034,.025,end,'rail',vertices=24)
        cap.rotation_mode='QUATERNION';cap.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector(polar(1,a,0)))
        stubs.append(end)
    tools=b.assemblies['utilities.penetrations'];wall_r=layout.BUILDING['diameter']/2
    cut(b,'nitrogen_wall_sleeve',tools,[polar(wall_r-1,p['angle'],header_z),polar(wall_r+1,p['angle'],header_z)],.055,[bpy.data.objects['building.shell.retained_wall']])
    root['scope']=p['scope'];root['stored_fluid']='Liquid nitrogen';root['distributed_fluid']='Nitrogen gas after vaporizer'
    return {'tank':root.name,'location':list(root.location),'envelope_diameter_m':p['tank_diameter'],'tank_envelope_height_m':p['tank_height'],
        'gas_header_od_m':p['gas_diameter'],'wall_entry':list(polar(wall_r,p['angle'],header_z)),
        'gas_supply':world,'header_points':arc,'capped_future_takeoffs':stubs,'scope':p['scope']}


def build_utilities(b,layout,repo):
    result={'coolant_transfer':build_transfer(b,layout),'nitrogen':build_nitrogen(b,layout)}
    bpy.context.view_layer.update()
    return result


def check_utilities(layout,services):
    """Screen auxiliary capsules against pipe routes and equipment, with port exclusions."""
    bpy.context.view_layer.update();clashes=[];pairs=0
    auxiliary=[o for o in bpy.context.scene.objects if o.type=='CURVE' and (o.get('utility_route') or o.get('utility_gas'))]
    routes=[o for o in bpy.context.scene.objects if o.type=='CURVE' and (o.get('process_route') or o.get('air_insulated') or o.name.startswith('connections.air.'))]
    boxes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('equipment.') and o.name.endswith(('.casing','.closed_tank','.closed_enclosure','.motor_envelope','.vacuum_jacket'))]
    def points(o):return [o.matrix_world@Vector(p.co[:3]) for p in o.data.splines[0].points]
    for ob in auxiliary:
        pts=points(ob);r=ob.data.bevel_depth
        for other in routes:
            op=points(other);gap=min(segdist(a,b,c,d)[0] for a,b in zip(pts,pts[1:]) for c,d in zip(op,op[1:]))-r-other.data.bevel_depth
            pairs+=1
            if gap<-.001:clashes.append((ob.name,other.name,gap))
        for other in boxes:
            if ob.get('utility_route') and other.name.startswith('equipment.coolant_transfer_pump.'):continue
            if ob.name.endswith('.pump_to_storage') and other.name=='equipment.coolant_storage.closed_tank':continue
            inv=other.matrix_world.inverted();lo,hi=bounds(other.bound_box);pp=[inv@q for q in pts]
            gap=min(segment_box(a,b,lo,hi) for a,b in zip(pp,pp[1:]))-r;pairs+=1
            if gap<-.001:clashes.append((ob.name,other.name,gap))
        if ob.get('utility_route'):
            assert abs(ob['pipe_spec']['bare_od']-.050)<1e-8 and ob['heat_traced']
            assert ob['minimum_bend_radius_m']>r
            assert min(q.z for q in pts)-r>layout.FLOOR_Z
    # Include the new full tank insulation envelope, not just its original steel body.
    cp=layout.COOLANT_STORAGE;cx,cy,cz=cp['position'];outside=cp['radius']+cp['insulation']+cp['cladding']
    bottom=cz-cp['insulation']-cp['cladding'];top=cz+cp['height']+.065+cp['insulation']+cp['cladding']
    tank_gaps=[]
    for ob in routes+auxiliary:
        if ob.name.endswith('.pump_to_storage'):continue  # Intended bottom connection, checked below.
        pp=points(ob);best=1e9
        for a,c in zip(pp,pp[1:]):
            n=max(1,math.ceil((c-a).length/.10));allowance=(c-a).length/(2*n)
            for i in range(n+1):
                q=a.lerp(c,i/n)
                dr=max(0,math.hypot(q.x-cx,q.y-cy)-outside);dz=max(0,bottom-q.z,q.z-top)
                best=min(best,math.hypot(dr,dz)-ob.data.bevel_depth-allowance)
        tank_gaps.append((best,ob.name));pairs+=1
        if best<-.001:clashes.append(('coolant tank insulation',ob.name,best))
    for ob in bpy.context.scene.objects:
        if ob.get('utility_opening_tool') and ob.name.startswith('utilities.penetrations.'):
            assert ob.type=='MESH' and ob.hide_render,ob.name
    assert not clashes,clashes[:20]
    t=services['coolant_transfer'];n=services['nitrogen']
    assert (Vector(t['routes'][0]['points'][-1])-Vector(t['pump_inlet'])).length<1e-8
    assert (Vector(t['routes'][1]['points'][0])-Vector(t['pump_outlet'])).length<1e-8
    assert t['storage_port'][2]==layout.COOLANT_STORAGE['position'][2]
    assert t['reactor_port'][2]<layout.REACTOR['origin_z']+.001
    assert layout.COOLANT_STORAGE['position'][2]-layout.COOLANT_STORAGE['insulation']-layout.COOLANT_STORAGE['cladding']>layout.COOLANT_TRANSFER['pipe_z']+.075
    assert math.hypot(*n['location'][:2])-n['envelope_diameter_m']/2>layout.AIR['concrete_outer_radius']
    assert n['wall_entry'][2]-.025>layout.AIR['fresh_z']+layout.AIR['concrete_height']/2
    return {'capsule_equipment_pairs':pairs,'tank_nearest_routes':[{'clearance_m':d,'route':name} for d,name in sorted(tank_gaps)[:5]],'collisions':clashes,'checks':['50 mm OD heated insulated line: vessel bottom to pump to storage bottom','Storage raised for insulated bottom connection; side/top/bottom insulation represented','Outdoor liquid nitrogen tank feeds vaporizer then a common gas header with three capped future takeoffs'],
        'scope':'Selected capsule/equipment and terminal geometry only; hydraulic, thermal, pressure, cryogenic, ventilation and support design pending'}
