"""Compose the divided shared-wall annex, cylindrical tank enclosure and coolant room."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/p) for p in ('src','models','scripts')]
import wistr_attached_services_draft as cfg
import wistr_installation as layout
import wistr_site as site
from build_tank_bay_draft import builder,remove_prefix
from build_wistr import camera
from textual_graphics.installation_stairs import prism
from textual_graphics.installation_piping import fillet_path
from textual_graphics.installation_utilities import cut,service_line,polar
from textual_graphics.site_salt_distribution import fuel_bundle
from textual_graphics.installation_clearance import bounds,gapbox,segdist,segment_box
FLOOR=layout.FLOOR_Z


def fingerprint():
    data=[]
    for o in bpy.data.objects:
        if o.type=='CURVE' and o.get('process_route'):
            data.append((o.name,[[list(o.matrix_world@Vector(p.co[:3])) for p in sp.points] for sp in o.data.splines]))
    return hashlib.sha256(json.dumps(sorted(data)).encode()).hexdigest()


def arced_footprint(x0,x1,north,cx,cy,r):
    # Floors/roofs terminate at the existing circular wall; no duplicate facade.
    arc=[(x,cy+math.sqrt(r*r-(x-cx)**2)) for x in [x0+(x1-x0)*i/120 for i in range(121)]]
    return [*arc,(x1,north),(x0,north)]


def curved_slab(b,name,root,poly,z0,z1,material):
    # Explicit quad strips avoid unstable tessellation of the long concave edge.
    arc=poly[:-2];north=poly[-1][1];verts=[];faces=[]
    for x,y in arc:verts.extend([(x,y,z0),(x,north,z0),(x,y,z1),(x,north,z1)])
    for i in range(len(arc)-1):
        k=4*i;j=k+4
        faces.extend([(k+2,j+2,j+3,k+3),(k,k+1,j+1,j),
                      (k,j,j+2,k+2),(k+1,k+3,j+3,j+1)])
    end=4*(len(arc)-1);faces.extend([(0,2,3,1),(end,end+1,end+3,end+2)])
    return b.mesh(name,root,verts,faces,material)


def wall_y(b,name,root,x0,x1,y,height,mat,door=None,t=.35):
    spans=[(x0,x1,0,height)]
    if door:
        a,c,h=door;spans=[(x0,a,0,height),(c,x1,0,height),(a,c,h,height)]
    objects=[]
    for i,(a,c,z0,z1) in enumerate(spans):
        if c-a<.001 or z1-z0<.001:continue
        ob=b.box(name+str(i),root,(c-a,t,z1-z0),((a+c)/2,y,FLOOR+(z0+z1)/2),mat)
        ob['annex_outer_wall']=True;objects.append(ob)
    return objects


def building(b,name,params,circle,material,doors):
    x0,x1=params['x_bounds'];north=params['north_y'];h=params['height'];t=params['wall'];cx,cy,r=circle
    root=b.assembly(name,'Attached service buildings');root['scope']=cfg.SCOPE
    poly=arced_footprint(x0,x1,north,cx,cy,r)
    curved_slab(b,'floor',root,poly,FLOOR-.35,FLOOR,'floor')
    roof=curved_slab(b,'roof',root,poly,FLOOR+h,FLOOR+h+.25,material);roof['site_roof']=True
    for key,x in [('west',x0+t/2),('east',x1-t/2)]:
        # At the outer boundary the side-wall nose meets the circular wall.
        start=cy+math.sqrt(r*r-((x0 if key=='west' else x1)-cx)**2)
        ob=b.box(key,root,(t,north-start,h),(x,(north+start)/2,FLOOR+h/2),material)
        ob['annex_outer_wall']=True
    # Divide the north wall around independent receiving/service doors.
    cursor=x0
    for i,(a,c,height) in enumerate(doors):
        wall_y(b,'north_'+str(i),root,cursor,c,north-t/2,h,material,(a,c,height),t);cursor=c
    if cursor<x1:wall_y(b,'north_end',root,cursor,x1,north-t/2,h,material,t=t)
    return root,poly


def labels(b):
    from build_site import floor_label
    floor_label(b,'Attached.OffgasLabel','OFF-GAS TREATMENT',(-1.5,30,FLOOR+.04),.48)
    floor_label(b,'Attached.FuelLabel','FUEL REFINING / RECYCLING',(8.5,30.4,FLOOR+.04),.35)
    floor_label(b,'Attached.CoolantLabel','COOLANT PREPARATION',(20.5,37,FLOOR+.04),.48)


def move_equipment():
    dy=cfg.COMBINED['equipment_shift_y'];cool=Vector(cfg.COOLANT_PREP['equipment_translation'])
    moved=[]
    for o in list(bpy.data.objects):
        if not o.name.startswith('site.process_services.'):continue
        key=o.name[len('site.process_services.'):]
        delta=cool if key.startswith('Coolant') else Vector((0,dy,0))
        o.matrix_world=Matrix.Translation(delta)@o.matrix_world
        if o.type=='MESH' and not o.hide_render:moved.append(dict(name=o.name,area='coolant' if key.startswith('Coolant') else 'fuel' if key.startswith('Fuel') else 'offgas'))
    for o in list(bpy.data.objects):
        if o.type!='FONT':continue
        if o.name in ('Offgas building label','Salt building label','Salt receiving label'):
            bpy.data.objects.remove(o,do_unlink=True);continue
        if o.name.startswith('Coolant'):o.location+=cool
        elif o.name.startswith(('Fuel','Inlet treatment','Further treatment','Release monitoring')):o.location.y+=dy
    bpy.data.objects['site.offgas_gas_supply'].location.y+=dy
    bpy.data.objects['site.offgas_release_stack'].location.x=cfg.RELEASE_STACK_XY[0]
    bpy.data.objects['site.offgas_release_stack'].location.y=cfg.RELEASE_STACK_XY[1]
    bpy.data.objects['equipment.nitrogen_supply'].location=(*cfg.NITROGEN_XY,FLOOR)
    bpy.context.view_layer.update()
    return moved


def replace_curve(b,name,controls,bend=.12):
    old=bpy.data.objects[name];parent=old.parent;mat=old.data.materials[0];props=dict(old.items());radius=old.data.bevel_depth
    material=mat.name;b.materials[material]=mat
    bpy.data.objects.remove(old,do_unlink=True)
    pts,radii=fillet_path(controls,bend)
    ob=b.tube(name[len(parent.name)+1:],parent,pts,radius,material)
    for key,value in props.items():ob[key]=value
    ob['attached_revision_route']=True
    return dict(name=ob.name,points=[list(p) for p in pts],controls=[list(p) for p in controls],radius=radius,
                minimum_bend_radius_m=min(radii) if radii else None)


def routes(b):
    out=[];z=FLOOR
    off=[(-1.95,10,z+.85),(-1.95,16.8,z+.85),(1.4,16.8,z+.85),(1.4,16.8,z+4.65),
         (1.4,18.6,z+4.65),(3.3,18.6,z+4.65),(3.3,21.3,z+4.65),(-1,21.3,z+4.65),(-1,21.3,z+2.6),(-1,21.75,z+2.6)]
    supply=[(-1.75,10,z+.65),(-1.75,17.1,z+.65),(1.05,17.1,z+.65),(1.05,17.1,z+4.4),
            (1.05,18.9,z+4.4),(2.95,18.9,z+4.4),(2.95,21.6,z+4.4),(-3.5,21.6,z+4.4),(-3.5,21.6,z+2.2),(-3.5,21.8,z+2.2)]
    out.append(replace_curve(b,'site.fuel_pressure.offgas_common',off))
    out.append(replace_curve(b,'site.fuel_pressure.supply_common',list(reversed(supply))))
    nitrogen=bpy.data.objects['equipment.nitrogen_supply']
    nw=lambda p:tuple(nitrogen.matrix_world@Vector(p))
    feed=[nw((-.65,-3.05,3)),nw((-1.7,-3.05,3)),nw((-1.7,-3.05,1.25)),nw((-1.7,-3.5,1.25)),nw((-2.1,-3.5,1.25)),
          (-14.6,22.6,z+1.25),(-4.3,22.6,z+1.25),(-4.3,22.2,z+1.25),(-3.9,22.2,z+1.25)]
    out.append(replace_curve(b,'site.fuel_pressure.nitrogen_to_offgas',feed))
    out.append(replace_curve(b,'site.process_services.monitored_release',[
        (-1,29,z+2.6),(-1,30.4,z+2.6),(-8.2,30.4,z+2.6),(-8.2,29.5,z+2.6)],.35))
    remove_prefix('site.salt_distribution.refiner_to_distributor')
    entry=fuel_bundle(b,bpy.data.objects['site.salt_distribution'],'refiner_to_distributor',[
        (7.5,21.225,z+.70),(7.5,20.7,z+.70),(7.5,20.7,-5.35),(4.55,20.7,-5.35),
        (4.55,20.7,FLOOR+4.55),(4.55,16.5,FLOOR+4.55),(4.55,16.5,z+.18),(0,16.5,z+.18),(0,10.6,z+.18)],site)
    out.append(dict(name=entry['name'],points=entry['points'],controls=entry['controls'],radius=entry['outside_envelope_m']/2,
                    members=entry['members'],minimum_bend_radius_m=entry['minimum_bend_radius_m']))
    old=bpy.data.objects['connections.coolant_transfer.preparation_to_tee'];spec=dict(old['pipe_spec'])
    remove_prefix('connections.coolant_transfer.preparation_to_tee')
    controls=[(20.5,27.725,z+.70),(20.5,27.2,z+.70),(20.5,27.2,z+.4),(20.5,20.5,z+.4)]
    ob=service_line(b,'preparation_to_tee',bpy.data.objects['connections.coolant_transfer'],controls,spec)
    ob['attached_revision_route']=True
    out.append(dict(name=ob.name,points=[list(p.co[:3]) for p in ob.data.splines[0].points],controls=controls,radius=spec['jacket_od']/2))
    return out


def move_intake():
    p=cfg.INTAKE;index=p['index'];R=Matrix.Rotation(math.radians(p['angle']-p['old_angle']),4,'Z')
    names=[f'connections.air.outside_air_intake_{index}',f'site.fresh_air_intake_{index}',
           f'site.fresh_air_openings.outdoor_intake_duct_{index}',f'site.fresh_air_openings.outdoor_intake_wall_{index}']
    for name in names:
        o=bpy.data.objects[name];o.matrix_world=R@o.matrix_world;o['draft_intake_angle']=p['angle']
    # Boolean cutters move with the inlet, closing the old openings automatically.
    bpy.context.view_layer.update()
    ob=bpy.data.objects[names[0]]
    return dict(angle=p['angle'],points=[list(ob.matrix_world@Vector(q.co[:3])) for q in ob.data.splines[0].points],
                diameter=2*ob.data.bevel_depth,housing=names[1])


def geometry(b):
    remove_prefix('site.off_gas');remove_prefix('site.fuel_preparation');remove_prefix('site.coolant_tank_bay')
    remove_prefix('site.salt_receiving_apron')
    for o in list(bpy.data.objects):
        if o.name.startswith('site.shared_service_link.') and not o.name.endswith('shell_opening_tool'):
            bpy.data.objects.remove(o,do_unlink=True)
    # Old bay wall sleeves are superseded by the circular wall penetrations.
    for name in ('draft_transfer_bay_wall','draft_preparation_wall','bay_wall_sleeve','prep_wall_sleeve'):
        remove_prefix('utilities.penetrations.'+name)
    tool=bpy.data.objects['site.shared_service_link.shell_opening_tool']
    tool.scale.z*=1.3;tool.location.z+=.15
    b=builder()
    b.material('attached_annex','#BBC4BA',roughness=.72)
    b.material('silo_enclosure','#B6C6CD',roughness=.7)
    b.material('coolant_annex','#AFC5C5',roughness=.7)
    combined,poly=building(b,'site.combined_process',cfg.COMBINED,(0,0,21),'attached_annex',[(-4,-1,3.5),(7,11,4.2)])
    p=cfg.COMBINED;x=p['divider_x'];start=math.sqrt(21**2-x*x)
    b.box('partition',combined,(p['divider_thickness'],p['north_y']-start,p['height']),
          (x,(p['north_y']+start)/2,FLOOR+p['height']/2),'attached_annex')
    # Inspection substitute for the corresponding slice of the existing reactor wall.
    # Original full-height wall is retained, hidden only for the architectural cutaway.
    viewroot=b.assembly('draft.shared_wall_display','Shared wall inspection')
    aa=math.degrees(math.acos(p['x_bounds'][1]/21));bb=math.degrees(math.acos(p['x_bounds'][0]/21))
    shared=b.annulus('existing_reactor_wall',viewroot,21-layout.BUILDING['wall_thickness'],21,FLOOR,FLOOR+5,'concrete',start=aa,end=bb,steps=96)
    shared['presentation_only']=True;shared['represents']='building.shell.retained_wall'
    # Copy only existing wall penetration modifiers into the displayed slice.
    original=bpy.data.objects['building.shell.retained_wall']
    for mod in original.modifiers:
        if mod.type=='BOOLEAN' and mod.object:
            new=shared.modifiers.new(mod.name,'BOOLEAN');new.operation=mod.operation;new.solver='EXACT';new.object=mod.object
    p=cfg.SILO;cx,cy=p['centre'];ri=p['inside_radius'];ro=ri+p['wall']
    silo=b.assembly('site.coolant_silo','Coolant silo',(cx,cy,FLOOR));silo['scope']=cfg.SCOPE
    b.cylinder('floor',silo,ro,.35,(0,0,-.175),'floor',vertices=128,bevel=0)
    # Separate rear/front shell pieces for an inspectable cutaway; full shell is retained.
    for label,a,c in [('rear',0,180),('front',180,360)]:
        wall=b.annulus('wall_'+label,silo,ri,ro,0,p['height'],'silo_enclosure',start=a,end=c,steps=96)
        wall['silo_shell']=label
    roof=b.cylinder('roof',silo,ro,.25,(0,0,p['height']+.125),'silo_enclosure',vertices=128,bevel=0);roof['site_roof']=True
    coolant,coolpoly=building(b,'site.coolant_preparation',cfg.COOLANT_PREP,(cx,cy,ro),'coolant_annex',[(18.5,22.5,4.2)])
    for name,x0,x1,y in [('combined',-7,13,31),('coolant',15.5,25.5,38)]:
        b.box(name+'_receiving_apron',combined,(x1-x0,4,.10),((x0+x1)/2,y+2,FLOOR-.05),'floor')
    moved=move_equipment();newroutes=routes(b);intake=move_intake()
    tools=b.assembly('draft.attached_openings','Attached service opening tools')
    # North liquid connection and south-west reactor transfer line through silo wall.
    walls=[bpy.data.objects['site.coolant_silo.wall_'+s] for s in ('rear','front')]
    cut(b,'coolant_preparation_entry',tools,[(cx,cy+ri-.2,FLOOR+.4),(cx,cy+ro+.2,FLOOR+.4)],.11,walls)
    cut(b,'reactor_transfer_entry',tools,[polar(22.5,45,FLOOR+.4),polar(24.0,45,FLOOR+.4)],.11,walls)
    # East access opening in the silo; tank installation/removal is still undefined.
    cutter=b.box('silo_access',tools,(1.,p['access_width'],p['access_height']),(cx+ro-.175,cy,FLOOR+p['access_height']/2),None)
    cutter.hide_render=True;cutter.hide_set(True);cutter['utility_opening_tool']=True
    for wall in walls:
        mod=wall.modifiers.new('Silo access','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    west=bpy.data.objects['site.combined_process.west']
    cut(b,'nitrogen_entry',tools,[(-7.3,22.6,FLOOR+1.25),(-6.3,22.6,FLOOR+1.25)],.05,[west])
    cut(b,'release_outlet',tools,[(-7.3,30.4,FLOOR+2.6),(-6.3,30.4,FLOOR+2.6)],.10,[west])
    cut(b,'stack_release_nozzle',tools,[(-8.2,29.5,FLOOR+2.6),(-8.2,30.2,FLOOR+2.6)],.10,[bpy.data.objects['site.offgas_release_stack.barrel']])
    labels(b);bpy.context.view_layer.update()
    return b,dict(combined_footprint=poly,coolant_footprint=coolpoly,moved_equipment=moved,routes=newroutes,intake=intake)


def merge_floor_surfaces(b):
    # The retained reactor sub-floor extends to R=24 m, beyond its R=21 m wall.
    # Reuse it inside that radius instead of drawing coplanar annex/skid slabs.
    root=b.assembly('draft.floor_join','Attached service opening tools')
    existing=bpy.data.objects['building.structure.lower_slab']
    radius=max(math.hypot(v.co.x,v.co.y) for v in existing.data.vertices)
    tool=b.cylinder('existing_slab_footprint',root,radius,4.,(0,0,FLOOR),None,vertices=160,bevel=0)
    tool.hide_render=True;tool.hide_set(True);tool['utility_opening_tool']=True
    for name in ('site.combined_process.floor','site.coolant_silo.floor','equipment.nitrogen_supply.pad'):
        ob=bpy.data.objects[name]
        mod=ob.modifiers.new('Use existing reactor sub-floor inside its footprint','BOOLEAN')
        mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
    bpy.context.view_layer.update()


def check(b,data):
    clashes=[];deps=bpy.context.evaluated_depsgraph_get();p=cfg.COMBINED
    # Existing equipment placeholders fit their assigned rooms after rigid translations.
    room_clear=[]
    for item in data['moved_equipment']:
        ob=bpy.data.objects[item['name']]
        if 'canister_lid' in ob.name or ob.get('utility_opening_tool'):continue
        points=[ob.matrix_world@Vector(v) for v in ob.bound_box]
        if item['area']=='coolant':
            room=cfg.COOLANT_PREP;cx,cy=cfg.SILO['centre'];radius=cfg.SILO['inside_radius']+cfg.SILO['wall'];limits=room['x_bounds']
        else:
            room=cfg.COMBINED;cx=cy=0.;radius=21.
            limits=(room['x_bounds'][0],room['divider_x']-room['divider_thickness']/2) if item['area']=='offgas' else (room['divider_x']+room['divider_thickness']/2,room['x_bounds'][1])
        for q in points:
            assert limits[0]+.05<q.x<limits[1]-.05,(ob.name,'side wall',q)
            assert q.y<room['north_y']-room['wall']-.05,(ob.name,'north wall',q)
            assert math.hypot(q.x-cx,q.y-cy)>radius+.05,(ob.name,'curved wall',q)
        room_clear.append(ob.name)
    # Pump enclosure, ladder and tank jacket fit inside the round building.
    cx,cy=cfg.SILO['centre'];ri=cfg.SILO['inside_radius'];inside=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render or not o.name.startswith(('equipment.coolant_storage.','equipment.coolant_transfer_pump.')) or o.get('utility_opening_tool'):continue
        # Actual vertices rather than cylinder bounding-box corners.
        points=[o.matrix_world@v.co for v in o.data.vertices]
        gap=min(ri-math.hypot(q.x-cx,q.y-cy) for q in points)
        assert gap>0,(o.name,'silo clearance',gap)
        inside.append((o.name,gap))
    # Air inlet clears the silo and the existing doorway's straight approach.
    inlet=bpy.data.objects[data['intake']['housing']];v=[o.matrix_world@Vector(q) for o in inlet.children_recursive if o.type=='MESH' for q in o.bound_box]
    ro=ri+cfg.SILO['wall'];silo_gap=min(math.hypot(q.x-cx,q.y-cy)-ro for q in v)
    assert silo_gap>.25,silo_gap
    a=math.radians(layout.ACCESS['angle']);door_side=[-q.x*math.sin(a)+q.y*math.cos(a) for q in v]
    door_gap=min(door_side)-layout.ACCESS['width']/2
    assert door_gap>.5,door_gap
    # Check changed routed capsules against evaluated nearby walls, equipment and existing routes.
    newnames={q['name'] for q in data['routes']};newprefixes=('site.salt_distribution.refiner_to_distributor','connections.coolant_transfer.preparation_to_tee')
    obstacles=[]
    for o in bpy.data.objects:
        if o.type not in ('MESH','CURVE') or o.hide_render or o.get('utility_opening_tool') or o.get('presentation_only'):continue
        if o.name in newnames or o.name.startswith(newprefixes) or o.name.startswith(('DraftLaydown.','draft.attached_openings.','utilities.penetrations.')):continue
        if not o.name.startswith(('site.','connections.','equipment.','building.shell.','reactor.')):continue
        if o.name.startswith(('site.ground.','site.converter.','site.turbine.','site.pipe_rack','site.secondary.','site.coolant_silo.floor')):continue
        obstacles.append((o,bounds([o.matrix_world@Vector(v) for v in o.bound_box])))
    pairs=0
    for route in data['routes']:
        pts=[Vector(q) for q in route['points']];rad=route['radius'];bb=bounds(pts)
        for ob,bc in obstacles:
            if gapbox(bb,bc)>rad+.02:continue
            pp=pts
            # Deliberate component terminals. Only trim the local terminal neighbourhood.
            terminals=[]
            if 'refiner_to_distributor' in route['name'] and ob.name in ('site.salt_distribution.cladding_saddle_7','site.salt_distribution.cladding_saddle_8'):continue  # Retained bearing contacts.
            if route['name'].endswith('offgas_common') and 'Inlet treatment' in ob.name:terminals=[pts[-1]]
            if route['name'].endswith('supply_common') and ob.name.startswith('site.offgas_gas_supply.'):terminals=[pts[0]]
            if route['name'].endswith('nitrogen_to_offgas') and ob.name.startswith('equipment.nitrogen_supply.'):continue
            if route['name'].endswith('nitrogen_to_offgas') and ob.name.startswith('site.offgas_gas_supply.'):terminals=[pts[-1]]
            if route['name'].endswith('monitored_release') and ('Release monitoring' in ob.name or ob.name.startswith('site.offgas_release_stack.')):terminals=[pts[0],pts[-1]]
            if 'refiner_to_distributor' in route['name'] and (ob.name=='site.process_services.Fuel transfer pump' or 'fuel_valve_box' in ob.name):terminals=[pts[0],pts[-1]]
            if route['name'].endswith('preparation_to_tee') and ob.name=='site.process_services.Coolant transfer pump':terminals=[pts[0]]
            if route['name'].endswith('preparation_to_tee') and ob.name.startswith(('connections.coolant_transfer.pump_to_storage','connections.coolant_transfer.tank_bottom_nozzle')):terminals=[pts[-1]]
            # Existing gas branches join the unchanged interior common headers at their tees.
            if ob.name.startswith('site.fuel_pressure.server_') and route['name'].endswith(('offgas_common','supply_common')):continue
            if terminals:pp=[q for q in pts if all((q-t).length>.25 for t in terminals)]
            if len(pp)<2:continue
            pairs+=1;gap=1000.
            ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
            if mesh and len(mesh.vertices):
                vs=[ob.matrix_world@v.co for v in mesh.vertices];tree=BVHTree.FromPolygons(vs,[tuple(f.vertices) for f in mesh.polygons])
                for u,w in zip(pp,pp[1:]):
                    if segment_box(u,w,*bc)>rad+.02:continue
                    length=(w-u).length
                    if length<1e-8:continue
                    n=max(1,math.ceil(length/.04))
                    for i in range(n+1):
                        hit=tree.find_nearest(u.lerp(w,i/n))
                        if hit[0] is not None:gap=min(gap,hit[3]-rad-length/(2*n))
                    hit=tree.ray_cast(u,(w-u).normalized(),length)
                    if hit[0] is not None:gap=-rad
            ev.to_mesh_clear()
            if gap<-.003:clashes.append((route['name'],ob.name,round(gap,4)))
    # Changed routes also clear each other (the only shared tee is with retained piping).
    for i,a in enumerate(data['routes']):
        for c in data['routes'][i+1:]:
            if gapbox(bounds(a['points']),bounds(c['points']))>a['radius']+c['radius']:continue
            gap=min(segdist(Vector(p),Vector(q),Vector(u),Vector(v))[0] for p,q in zip(a['points'],a['points'][1:]) for u,v in zip(c['points'],c['points'][1:]))-a['radius']-c['radius']
            if gap<-.003:clashes.append((a['name'],c['name'],gap))
    assert not clashes,clashes[:60]
    return dict(moved_equipment_inside_rooms=room_clear,new_route_pairs=pairs,route_clashes=clashes,
        minimum_silo_equipment_wall_gap_m=min(v for _,v in inside),intake_to_silo_gap_m=silo_gap,
        intake_to_door_corridor_gap_m=door_gap,shared_wall='Existing reactor wall, R=21 m; no separate southern facade',
        scope='Selected envelope/routing checks; no shielding, process, thermal, support, full crane or egress qualification')


def view(b,cams,key):
    for c in bpy.data.collections:
        if c.name.startswith(('Site annotations.','Annotations.','Draft labels.')):c.hide_render=c.hide_viewport=True
    for name in ('Shell','Crane'):
        col=bpy.data.collections.get(name)
        if col:col.hide_render=col.hide_viewport=True
    bpy.data.collections['Draft maintenance items'].hide_render=True;bpy.data.collections['Draft maintenance items'].hide_viewport=True
    bpy.data.collections['Shared wall inspection'].hide_render=bpy.data.collections['Shared wall inspection'].hide_viewport=False
    for ob in bpy.data.objects:
        if ob.get('site_roof'):ob.hide_render=ob.hide_viewport=key!='exterior'
        if ob.get('annex_outer_wall'):ob.hide_render=ob.hide_viewport=key=='cutaway'
        if ob.get('silo_shell'):ob.hide_render=ob.hide_viewport=key=='cutaway' and ob['silo_shell']=='rear'
    for c in ('Building columns','Stacks','Hot air insulation','Hot air duct metal'):
        if c in b.collections:b.collections[c].hide_render=b.collections[c].hide_viewport=key=='cutaway'
    bpy.context.scene.camera=cams[key]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
    bpy.context.view_layer.update()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build-only',action='store_true');parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=ROOT/cfg.OUTPUT;out.mkdir(parents=True,exist_ok=True)
    checkpoint=out/'geometry-checkpoint.blend';source=ROOT/cfg.SOURCE
    bpy.ops.wm.open_mainfile(filepath=str(checkpoint if args.resume else source))
    for c in bpy.data.collections:c.hide_viewport=False
    for o in bpy.data.objects:o.hide_viewport=False
    bpy.context.view_layer.update();original_signature=fingerprint()
    if not args.resume:
        b,data=geometry(builder())
        data['original_main_route_signature']=original_signature
        data['configuration_sha256']=hashlib.sha256((ROOT/'models/wistr_attached_services_draft.py').read_bytes()).hexdigest()
        bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint));(out/'geometry-checkpoint.json').write_text(json.dumps(data,default=list))
    else:
        b=builder();data=json.loads((out/'geometry-checkpoint.json').read_text())
        assert data['configuration_sha256']==hashlib.sha256((ROOT/'models/wistr_attached_services_draft.py').read_bytes()).hexdigest(),'Rebuild changed geometry without --resume'
    merge_floor_surfaces(b)
    assert fingerprint()==data['original_main_route_signature'],'Main circulation routes changed'
    data['checks']=check(b,data);print('ATTACHED_GEOMETRY_CHECKED',flush=True)
    data.update(source=cfg.SOURCE,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),combined=cfg.COMBINED,silo=cfg.SILO,coolant_preparation=cfg.COOLANT_PREP,scope=cfg.SCOPE)
    (out/'attached-services-report.json').write_text(json.dumps(data,indent=2,default=list)+'\n')
    cams={'cutaway':camera(b,'Attached.Cutaway',(52,70,49),(7,21,-1.8),57),
          'plan':camera(b,'Attached.Plan',(6,12,90),(6,12,-8),89),
          'exterior':camera(b,'Attached.Exterior',(70,-43,45),(7,14,-.5),74)}
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    view(b,cams,'cutaway');bpy.ops.wm.save_as_mainfile(filepath=str(out/'fast-salt-attached-services.blend'))
    if not args.build_only:
        for key in cams:
            view(b,cams,key);scene.render.filepath=str(out/(key+'-draft.png'));bpy.ops.render.render(write_still=True)
    print('ATTACHED_SERVICES_DRAFT_OK',flush=True)

if __name__=='__main__':main()
