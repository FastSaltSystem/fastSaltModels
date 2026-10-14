"""Accessible exterior nitrogen utility draft, using P&ID identities."""
import math
import bpy
from mathutils import Vector
from textual_graphics.installation_utilities import cut
from textual_graphics.installation_clearance import segdist

def build(b,data,cfg,F,route,bind,remove_prefix):
    n=cfg.NITROGEN;z=F+n['header_height'];root=b.assembly('site.nitrogen_distribution','Exterior nitrogen supply')
    b.material('nitrogen_supply','#326DA8',metallic=.4,roughness=.30)
    b.material('nitrogen_station','#6898B5',metallic=.3,roughness=.4)
    # Replace the old single-room feed; remove its obsolete wall opening.
    remove_prefix('site.fuel_pressure.nitrogen_to_offgas')
    remove_prefix('draft.attached_openings.nitrogen_entry')
    def line(tag,controls,od,group='lines'):
        ob=route(b,data,tag,controls,od,0,group=group)
        ob.data.materials.clear();ob.data.materials.append(b.materials['nitrogen_supply'])
        ob['clean_nitrogen_supply']=True;ob['coolant_only_gas']=False
        ob['process_gas_return']=False;ob['flow_direction']='from_to'
        return ob
    header=[(x,y,z) for x,y in n['header']]
    line('H-601',header,n['header_od'],'equipment')
    line('N-600',[(-13.15,21.95,F+3),(-14.2,21.95,F+3),(-14.2,21.95,F+1.25),(-14.2,21.5,F+1.25),(-14.6,21.5,F+1.25),(-14.6,21.5,z),(-7.4,21.5,z),header[0]],n['header_od'])
    bind(data,'boundaries','B-601',['equipment.nitrogen_supply'],'modeled','Existing bulk tank and vaporizer; outlet is gas phase')
    bind(data,'boundaries','B-602',['site.offgas_gas_supply'],'functional_envelope','Existing off-gas-area gas distribution; supply kept distinct from treatment train')
    fuel=b.assembly('site.nitrogen_fuel_station','Exterior nitrogen supply',(5.,30.3,F+1.6))
    b.box('envelope',fuel,(.65,.45,.8),(0,-.225,0),'nitrogen_station',.03)
    bind(data,'boundaries','B-603',[fuel.name],'functional_envelope','Fuel refining/recycling room distribution interface; users unresolved')
    controls={
      'N-601':[(*n['branches'][0],z),(-5.5,31.65,F+1.6),(-5.5,30.4,F+1.6),(-5.5,22.2,F+1.6),(-4.5,22.2,F+1.25),(-3.9,22.2,F+1.25)],
      'N-602':[(*n['branches'][1],z),(5.,31.65,F+1.6),(5.,30.3,F+1.6)],
      'N-603':[(*n['branches'][2],z),(14.4,37.15,F+1.6),(14.4,35.8,F+1.6),(14.4,26.8,F+1.6),(14.4,26.45,F+1.4)]}
    data['nitrogen_valve_positions']={}
    for i,(x,y) in enumerate(n['branches'],1):
        tag=f'N-60{i}';line(tag,controls[tag],n['branch_od'])
        # Side-mounted box leaves the vertical pipe and its valve inspectable.
        box=b.box(f'station_{i}',root,(.48,.28,.65),(x+.24,y,F+1.6),'nitrogen_station',.03)
        box['functions']='Branch pressure regulation and backflow prevention: functional reservation only'
        box['pid_line']=tag;box['hardware_selection']='Unresolved; no credited protection arrangement'
        for h in (.5,2.0):b.beam(f'station_bracket_{i}_{h}',root,(x+.24,y,F+h),(x+.24,y-.65,F+h),.04,'rail')
        data['nitrogen_valve_positions'][f'V-60{i}N']=(x,y,F+n['valve_height'])
        # Short wall sleeves/openings; the process runs continue within each room.
        walls=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('site.coolant_preparation.north' if i==3 else 'site.combined_process.north')]
        assert walls,(i,'no room-entry wall')
        cut(b,'nitrogen_room_'+str(i),bpy.data.objects['draft.pid_openings'],[(x,y-.1,F+1.6),(x,y-1.,F+1.6)],.045,walls)
    for i,(x,y) in enumerate([(-6.,31.65),(0.,31.65),(6.,31.65),(12.,31.65),(14.,37.15),(18.,37.15),(22.,37.15)]):
        b.beam(f'header_bracket_{i}',root,(x,y,z-.055),(x,y-.65,z-.055),.035,'rail')
    # Skid-to-wall rack, then wall brackets round the corner. These are
    # illustrative supports; member selection and expansion restraint are TBD.
    for i,y in enumerate((22.,24.5,27.,29.5)):
        b.beam(f'feed_wall_bracket_{i}',root,(-7.4,y,z-.055),(-7.,y,z-.055),.035,'rail')
    for i,y in enumerate((21.30,21.70)):
        b.beam(f'feed_rack_rail_{i}',root,(-14.6,y,z-.15),(-7.,y,z-.15),.045,'rail')
        b.beam(f'feed_rack_skid_post_{i}',root,(-14.6,y,F+.08),(-14.6,y,z-.15),.05,'rail')
    for i,x in enumerate((-14.6,-12.2,-9.8,-7.4)):
        b.beam(f'feed_rack_crossmember_{i}',root,(x,21.30,z-.075),(x,21.70,z-.075),.035,'rail')
    data['nitrogen']=dict(header_height_m=n['header_height'],visual_header_od_m=n['header_od'],visual_branch_od_m=n['branch_od'],
        feed_route='Skid riser, supported crossing to west wall, wall-supported run around front corner',branches=controls,scope='Spatial utility draft; flow, pressure, protection hardware, supports and penetration seals unresolved')

def check(data,F):
    routes=data['routes'];header=[Vector(q) for q in routes['H-601']['points']]
    for tag,end in [('N-600',-1),('N-601',0),('N-602',0),('N-603',0)]:
        q=Vector(routes[tag]['points'][end]);assert min(segdist(q,q,a,c)[0] for a,c in zip(header,header[1:]))<1e-5,(tag,'disconnected nitrogen header')
    assert min(p[2] for p in header)-F-4.2>.4,'Receiving door headroom lost'
    assert data['model']['lines']['N-603']['to']=='B-401.nitrogen_makeup'
    assert data['model']['lines']['G-400']['to']=='B-401.coolant_gas'
    assert all(data['model']['lines'][f'N-60{i}']['flow_direction']=='from_to' for i in range(4))
    assert 'site.fuel_pressure.nitrogen_to_offgas' not in bpy.data.objects
    assert 'site.nitrogen_distribution.riser_support' not in bpy.data.objects
    feed=routes['N-600']['controls']
    assert tuple(feed[-2])==(-7.4,21.5,F+4.65) and tuple(feed[-1])==(-7.4,31.65,F+4.65), 'Feed no longer follows west wall'
    assert abs(header[0].x+7.4)<1e-5, 'Old freestanding header extension remains'
    return dict(header_connections=4,independent_room_branches=3,header_clearance_above_tallest_door_m=round(min(p[2] for p in header)-F-4.2-data['routes']['H-601']['radius'],3),
                wall_supported_feed=True,supply_return_ports_distinct=True,old_single_room_feed_removed=True)
