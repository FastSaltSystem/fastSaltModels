"""Attached process-building envelopes and illustrative service interfaces.

No salt chemistry, treatment performance, throughput or equipment duty is selected.
"""
import math
import bpy
from mathutils import Vector, Matrix
from .installation_piping import fillet_path
from .installation_clearance import bounds,gapbox,segment_box,segdist


def build_process_annexes(b,site,installation,label):
    p=site.PROCESS_ANNEX;floor=site.PAD_Z;routes=[];equipment=[]
    def compact(q):return (.5*q[0]+.5,.5*q[1]+13,q[2])
    original_label=label
    def label(b,name,text,position,size):return original_label(b,name,text,compact(position),size*.65)
    for name,color in [('process_gas','#946FA8'),('fuel_supply','#BE9140'),('fuel_return','#BB556C'),('coolant_supply','#348E83'),('process_unit','#A6B7BF'),('canister','#788F9D')]:
        b.material(name,color,metallic=.2,roughness=.4)
    root=b.assembly('site.process_services','Process connections')
    def pipe(name,pts,diameter,material,service):
        if name not in ('reactor_offgas','Fuel_liquid_return') and not name.endswith('_liquid_supply'):pts=[compact(q) for q in pts]
        path,radii=fillet_path(pts,.35)
        ob=b.tube(name,root,path,diameter/2,material);ob['process_annex_route']=True
        ob['scope']='Illustrative interface route; diameter, pressure, heat tracing and supports unqualified'
        ob['service']=service
        routes.append(dict(name=ob.name,service=service,points=[list(v) for v in path],outside_envelope_m=diameter,
            minimum_bend_radius_m=min(radii) if radii else None))
        return ob
    def unit(name,xy,size,mat='process_unit'):
        dx,dy,dz=size;ob=b.box(name,root,size,(*xy,floor+dz/2),mat,.10)
        ob['process_placeholder']=True;equipment.append(dict(name=name,centre=xy,size=size))
        return ob
    # One shared enclosed duct carries four independent lines above the fresh-air ring.
    links=[]
    for key,x in [('shared',p['shared_link_x'])]:
        inside_y=math.sqrt((installation.BUILDING['diameter']/2-installation.BUILDING['wall_thickness']-.3)**2-x*x)
        width=p['link_width'];y1=26.2;z=p['link_floor_z'];height=p['link_height']
        link=b.assembly('site.'+key+'_service_link','Process service links')
        b.box('floor',link,(width,y1-inside_y,.20),(x,(y1+inside_y)/2,z-.10),'rail')
        for side in (-1,1):b.box('wall'+str(side),link,(.16,y1-inside_y,height),(x+side*(width/2-.08),(y1+inside_y)/2,z+height/2),'panel')
        roof=b.box('roof',link,(width,y1-inside_y,.16),(x,(y1+inside_y)/2,z+height+.08),'panel');roof['site_roof']=True
        # Only the site copy gets a real shell opening. No change to the isolated reactor.
        cutter=b.box('shell_opening_tool',link,(width-.32,4.0,height),(x,math.sqrt(21**2-x*x),z+height/2),None)
        cutter.hide_render=True;cutter.hide_set(True)
        for ob in list(bpy.data.objects):
            if ob.name=='building.shell.retained_wall' or ob.name.startswith('building.shell.pilaster'):
                mod=ob.modifiers.new(key+' service opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;mod.solver='EXACT'
        links.append(dict(name=key,x=x,y0=inside_y,y1=y1,width=width,floor_z=z,roof_z=z+height+.16,
            scope='Enclosed service connection; provisional cantilever/support and penetration design'))
    # Off-gas equipment reservations: treatment/filtering, further treatment allowance, monitored outlet.
    for name,y,size in [('Inlet treatment and filtration',31,(4,3,4)),('Further treatment reservation',37,(4,3,4)),('Release monitoring',43,(3,2,3))]:
        unit(name,(-3,y),size)
        label(b,name+' label',name.upper().replace(' AND ',' / '),(-3,y-2.2,floor+.025),.42)
    unit('Service and replacement space',(3.5,36),(2,5,.12),'floor')
    # The reactor gas source is an explicitly reserved collection terminal above the vessel.
    source=(-3,4.7,3.2);pipe('reactor_offgas',[source,(-3,18,3.2),(3.3,18,3.2),(3.3,18,floor+4.2),(3.3,27,floor+4.2),(-1,27,floor+4.2),(-1,27,floor+2.6),(-1,27.75,floor+2.6)],p['gas_pipe_od'],'process_gas','Reactor gas to treatment')
    b.cylinder('reserved_offgas_tie_in',root,.22,.10,source,'process_gas',vertices=32)
    pipe('gas_between_treatment',[(-3,32.5,floor+2.6),(-3,35.5,floor+2.6)],p['gas_pipe_od'],'process_gas','Treatment interconnection')
    pipe('gas_to_monitor',[(-3,38.5,floor+2.6),(-3,42,floor+2.6)],p['gas_pipe_od'],'process_gas','Treated gas to monitoring')
    sx,sy=p['release_stack_xy'];r=p['release_stack_diameter']/2
    pipe('monitored_release',[(-3,44,floor+2.6),(-3,46,floor+2.6),((sx-.5)*2,46,floor+2.6),((sx-.5)*2,(sy-13)*2,floor+2.6)],p['gas_pipe_od'],'process_gas','Monitored gas to separate release stack')
    # Dedicated off-gas stack is independent of the reactor cooling-air exhaust stack.
    stack=b.assembly('site.offgas_release_stack','Off-gas release',(sx,sy,floor))
    b.box('footing',stack,(2,2,.35),(0,0,.175),'concrete')
    b.annulus('barrel',stack,r-.025,r,0,p['release_stack_height'],'process_gas')
    b.ring('open_rim',stack,r,p['release_stack_height'],.035,'rail')
    label(b,'Offgas building label','OFF-GAS TREATMENT',(-3,47,floor+.03),.78)
    # Separate fuel and coolant trains: incoming canisters, purification and melt/supply reservations.
    for service,x,mat,pipex,height in [('Fuel',14,'fuel_supply',4.6,4.0),('Coolant',28,'coolant_supply',5.3,4.2)]:
        unit(service+' purification',(x,39),(5,4,4.5),mat)
        label(b,service+' purification label',service.upper()+' PURIFICATION',(x,41.5,floor+.03),.52)
        for i in range(3):
            xx=x-1.5+i*1.5;ob=b.cylinder(service+'_incoming_canister'+str(i),root,.5,2.2,(xx,45.2,floor+1.1),'canister',vertices=32)
            b.cylinder(service+'_canister_lid'+str(i),root,.53,.10,(xx,45.2,floor+2.25),'rail',vertices=32)
        # Vessel envelope represents a melting/holding station, not selected technology.
        vessel=b.cylinder(service+'_melt_and_supply',root,1.55,4,(x,32.5,floor+2.35),mat,vertices=64)
        for yy in (-.8,.8):b.box(service+'_melt_support'+str(yy),root,(2.5,.20,.35),(x,32.5+yy,floor+.175),'rail')
        b.cylinder(service+'_insulated_roof',root,1.55,.12,(x,32.5,floor+4.41),'panel',vertices=64)
        label(b,service+' melter label',service.upper()+' MELT / SUPPLY',(x,35,floor+.03),.54)
        unit(service+' transfer pump',(x,29),(1.2,1.1,1.0),mat)
        # Conceptual connection from purification to melter: equipment sequence only.
        pipe(service+'_process_link',[(x,37,floor+2.8),(x,34.05,floor+2.8)],.15,mat,service+' purification to melting (interface allowance)')
        pipe(service+'_pump_suction',[(x,30.95,floor+.70),(x,29.55,floor+.70)],.15,mat,service+' melt to supply pump')
        cx=.5*x+.5
        pts=[(cx,27.225,floor+.70),(cx,26.7,floor+.70),(cx,26.7,floor+height),(pipex,26.7,floor+height),(pipex,18.5,floor+height)]
        # Parallel insulated/heated liquid supply runs terminate at reserved reactor-side tie-ins.
        pipe(service+'_liquid_supply',pts,p['liquid_pipe_od']+2*p['liquid_insulation'],mat,service+' liquid supply; heat traced and insulated')
        ob=b.cylinder(service+'_reactor_side_tie_in',root,.18,.08,pts[-1],mat,vertices=32);ob.rotation_euler.x=math.pi/2
    # The return is an illustrative building-to-building connection, ending at
    # reserved terminals. It does not specify a reactor extraction or refining circuit.
    return_pts=[(4.95,18.5,floor+4.35),(4.95,27.05,floor+4.35),
                (6.6,27.05,floor+4.35),(6.6,28.4,floor+4.35)]
    ret=pipe('Fuel_liquid_return',return_pts,p['liquid_pipe_od']+2*p['liquid_insulation'],
             'fuel_return','Used fuel: reactor to refining/recycling; illustrative insulated line')
    ret['flow_direction']='reactor_to_refiner'
    supply=next(o for o in root.children if o.name.endswith('Fuel_liquid_supply'))
    supply['flow_direction']='refiner_to_reactor'
    for name,point in [('Fuel_return_reactor_tie_in',return_pts[0]),('Fuel_return_refiner_tie_in',return_pts[-1])]:
        ob=b.cylinder(name,root,.18,.08,point,'fuel_return',vertices=32)
        ob.rotation_euler.x=math.pi/2;ob['keep_site_coordinates']=True
    # Paired arrows make in/out unambiguous in the duct inspection view.
    for x,z,direction,mat in [(4.6,floor+4.,-1,'fuel_supply'),(4.95,floor+4.35,1,'fuel_return')]:
        for y in (22.,24.5):
            b.tube('fuel_direction_'+mat+str(y),root,
                [(x-.16,y-direction*.25,z+.10),(x,y+direction*.25,z+.10),(x+.16,y-direction*.25,z+.10)],.025,mat)
    label(b,'Salt building label','FUEL REFINING / RECYCLING',(22,48.6,floor+.03),.73)
    label(b,'Salt receiving label','CANISTER RECEIVING',(22,44.2,floor+.03),.63)
    # Compact receiving apron retains the 6 m-wide canister door.
    yard=b.assembly('site.salt_receiving_apron','Site setting')
    b.box('apron',yard,(15,8,.20),(11.5,42,floor-.10),'floor')
    for x in (12,18):b.box('receiving_lane'+str(x),yard,(.07,8,.012),(x,42,floor+.01),'crane')
    # Compact only the unsized equipment placeholders in plan, preserving heights
    # and the line diameters. Pipe routes and reactor terminals already use new coordinates.
    bpy.context.view_layer.update()
    transform=Matrix.Translation(Vector((.5,13,0)))@Matrix.Diagonal((.5,.5,1,1))
    for ob in root.children:
        if ob.type=='MESH' and not ob.get('keep_site_coordinates') and not ob.name.endswith(('reserved_offgas_tie_in','Fuel_reactor_side_tie_in','Coolant_reactor_side_tie_in')):
            ob.matrix_world=transform@ob.matrix_world
    for item in equipment:
        item['centre']=[.5*item['centre'][0]+.5,.5*item['centre'][1]+13]
        item['size']=[item['size'][0]/2,item['size'][1]/2,item['size'][2]]
    return dict(parameters=p,links=links,routes=routes,equipment=equipment,
        tie_ins={'offgas_collection':list(source),'fuel_liquid':[4.6,18.5,floor+4.0],'fuel_return_reactor':list(return_pts[0]),'fuel_return_refiner':list(return_pts[-1]),'coolant_liquid':[5.3,18.5,floor+4.2]},
        scope='Process placeholders and proposed interfaces only; salt storage distribution is recorded separately; actual off-gas collection manifold remains to design')


def check_process_annexes(b,site,installation,result):
    """Selected building, opening, route and receiving-lane screens."""
    visibility=[(c,c.hide_viewport) for c in bpy.data.collections]+[(o,o.hide_viewport) for o in bpy.data.objects]
    for ob,_ in visibility:ob.hide_viewport=False
    bpy.context.view_layer.update()
    p=site.PROCESS_ANNEX
    assert site.OFF_GAS['centre'][0]+site.OFF_GAS['size'][0]/2==site.FUEL_PREPARATION['centre'][0]-site.FUEL_PREPARATION['size'][0]/2
    ring_top=site.PAD_Z+site.FRESH_AIR['base_height']+site.FRESH_AIR['clear_height']+2*site.FRESH_AIR['wall']
    assert len(result['links'])==1
    assert site.OFF_GAS['size']==(10.0,11.0,5.0) and site.FUEL_PREPARATION['size']==(15.0,12.0,5.0)
    gap=min(q['floor_z']-.20-ring_top for q in result['links']);assert gap>.25
    assert result['links'][0]['roof_z']<site.PAD_Z+5
    # Pipe envelopes fit both elevated service galleries and their building portals.
    for route in result['routes']:
        if route['name'].endswith(('reactor_offgas','Fuel_liquid_supply','Fuel_liquid_return','Coolant_liquid_supply')):
            link=result['links'][0];radius=route['outside_envelope_m']/2
            for x,y,z in route['points']:
                if link['y0']+.1<y<26.2:
                    assert abs(x-link['x'])+radius<link['width']/2-.16
                    assert link['floor_z']+radius<z<link['roof_z']-.16-radius
    # Existing pipes and selected equipment boxes inside the reactor, independent of view settings.
    existing=[];boxes=[]
    for ob in bpy.data.objects:
        if ob.type=='CURVE' and (ob.get('process_route') or ob.get('air_insulated') or ob.get('utility_route')):
            for sp in ob.data.splines:
                pts=[ob.matrix_world@Vector(v.co[:3]) for v in sp.points];existing.append((ob.name,pts,ob.data.bevel_depth,bounds(pts)))
        if ob.type=='MESH' and ob.name.startswith('equipment.') and any(ob.name.endswith('.'+q) for q in ('casing','closed_tank','closed_enclosure','motor_envelope')):
            boxes.append(ob)
    collisions=[];pairs=0
    for route in result['routes']:
        pts=[Vector(v) for v in route['points']];radius=route['outside_envelope_m']/2;bb=bounds(pts)
        for name,other,rad,bc in existing:
            if gapbox(bb,bc)>radius+rad:continue
            pairs+=1;best=1e9
            for a,c in zip(pts,pts[1:]):
                for d,e in zip(other,other[1:]):
                    if gapbox(bounds([a,c]),bounds([d,e]))>radius+rad:continue
                    best=min(best,segdist(a,c,d,e)[0]-radius-rad)
            if best<-.001:collisions.append((route['name'],name,best))
        for ob in boxes:
            inv=ob.matrix_world.inverted();local=[inv@v for v in pts];lo,hi=bounds([Vector(v) for v in ob.bound_box])
            if min(segment_box(a,c,lo,hi) for a,c in zip(local,local[1:]))<radius-.001:collisions.append((route['name'],ob.name))
    # The two fuel members now share a continuous jacket owned and checked by
    # salt_distribution. There is no separate exposed return-envelope route here.
    assert not collisions,collisions
    # Equipment doorway remains south of the annex footprints. Nitrogen is relocated by the site gas-service builder.
    assert min(q['centre'][1]-q['size'][1]/2 for q in (site.OFF_GAS,site.FUEL_PREPARATION))>=26
    assert installation.ACCESS['outer_radius']*math.sin(math.radians(installation.ACCESS['angle']))+installation.ACCESS['width']/2<26
    for ob,value in visibility:ob.hide_viewport=value
    bpy.context.view_layer.update()
    return dict(fresh_air_ring_to_service_link_underside_m=gap,selected_route_pairs=pairs,collisions=collisions,fuel_bundle_checks="salt_distribution",
        checks=['Building footprints quartered; both buildings 5 m tall','Adjacent process buildings share one attached service duct','Internal fresh-air duct below shared service connection; duct roof below building roofs','Fuel, coolant and off-gas routes fit shared duct; paired supply gas is checked separately','Selected new routes clear existing process/air/service routes and equipment boxes','Existing reactor entrance remains south of new building footprints'],
        limitations='Selected geometry only; building penetrations, full crane/vehicle access, ventilation, process capacity and performance require further design')
