"""Build and render the static WISTR installation presentation model in Blender."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'models'))
sys.path.insert(0,str(ROOT/'scripts'))
import wistr_installation as layout
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.installation_reactor import reactor_placement, import_reactor, route_coolant, check_integration
from textual_graphics.installation_services import secondary_headers, check_services, steel_frame, half_pipe_collector
from textual_graphics.installation_air import air_networks, check_air_networks
from textual_graphics.air_insulation import materials as air_materials, tag as insulation_tag
from textual_graphics.installation_access import equipment_access, check_access
from textual_graphics.installation_piping import move_collection, check_piping
from textual_graphics.installation_clearance import check_interference
from render_pms import text_on_camera


def xy(radius,angle):
    angle=math.radians(angle)
    return radius*math.cos(angle),radius*math.sin(angle)


def palette(b):
    for name,color,metal,rough in [
        ('concrete','#BBB9B1',0,.8),('cut_concrete','#D4D1C6',0,.8),
        ('floor','#D6D8D4',0,.65),('dark','#354755',.35,.42),
        ('rail','#768895',.5,.28),('vessel','#436E8C',.28,.32),
        ('vessel_light','#7394AC',.35,.3),('equipment','#A5AFB8',.25,.35),
        ('panel','#BDC5C9',.2,.4),('fuel','#B47630',.15,.4),
        ('fuel_light','#D8A457',.2,.4),('coolant','#71876A',.15,.4),
        ('absorber_module','#517F85',.2,.4),('steam','#ADB4E4',.2,.4),('water','#4D8CBC',.2,.4),
        ('sector','#8E6440',.15,.5),('hot','#AA862B',.2,.4),
        ('cold','#3E7468',.25,.4),('air','#789DB3',.25,.4),('exhaust_air','#BD7954',.18,.4),('fresh_air','#56B6C4',.15,.4),
        ('crane','#D4A143',.25,.35),('black','#252B31',.15,.55),
        ('backdrop','#FAFAF7',0,.7),
    ]:
        b.material(name,color,metallic=metal,roughness=rough,concrete=name=='concrete')


def building(b,integration):
    p=layout.BUILDING; r=p['diameter']/2; depth=p['lower_level_depth']
    wall_top=p['total_height']-depth-p['dome_rise']
    root=b.assembly('building.structure','Structure')
    b.cylinder('foundation',root,layout.AIR['concrete_outer_radius']+.55,.6,(0,0,-depth-.4),'cut_concrete',vertices=160)
    b.cylinder('lower_slab',root,layout.AIR['concrete_outer_radius'],.6,(0,0,-depth+.3),'floor',vertices=160)
    shell=b.assembly('building.shell','Shell')
    b.annulus('retained_wall',shell,r-p['wall_thickness'],r,-depth,wall_top,
              'concrete',start=0,end=180,steps=112)
    b.dome('retained_dome',shell,r,p['dome_rise'],wall_top,p['wall_thickness'],'concrete')
    for angle in range(0,181,20):
        x,y=xy(r-.95,angle)
        b.box(f'pilaster{angle}',shell,(.45,.45,wall_top-layout.FLOOR_Z),(x,y,(wall_top+layout.FLOOR_Z)/2),'cut_concrete',.04)
        # Quiet seams make the scale of the retained concrete shell visible.
        for z in (4,8,12):
            b.ring(f'panel_joint{angle}.{z}',shell,r-p['wall_thickness']-.015,z,.012,
                   'rail',start=angle,end=min(angle+20,180),steps=12)
    for angle in range(20,180,20):
        a=math.radians(angle)
        points=[((r-.7)*math.cos(t)*math.cos(a),(r-.7)*math.cos(t)*math.sin(a),
                 wall_top+(p['dome_rise']-.68)*math.sin(t))
                for t in [i*(math.pi/2-.035)/32 for i in range(33)]]
        b.tube(f'dome_rib{angle}',shell,points,.065,'cut_concrete')
    # Generic architectural wall lights, without assigning functional systems.
    for angle in (25,65,110,155):
        x,y=xy(r-.85,angle)
        b.box(f'wall_light{angle}',shell,(.35,.18,.6),(x,y,5.3),'panel',.04)
    return root


def reactor_foundation(b,integration):
    # The imported concrete well now bears directly on the existing sub-floor.
    bottom=-layout.BUILDING['lower_level_depth']+.6
    assert abs(integration['well_floor_bottom']-bottom)<1e-6


def steam_generator(b,index,angle):
    p=layout.STEAM_GENERATORS
    root=b.assembly(f'equipment.steam_generator_{index}','Steam generators',(*xy(p['radius'],angle),p['casing_bottom']),angle+p['rotation_offset'])
    width,height=p['width'],p['height']
    root['casing_dimensions_m']=[width,width,height]
    if p['frame_height']>0:
        steel_frame(b,root,'support',4.0,4.0,layout.FLOOR_Z-p['casing_bottom'],0)
    root['support_bottom_z']=layout.FLOOR_Z;root['support_top_z']=p['casing_bottom']
    b.box('casing',root,(width,width,height),(0,0,height/2),'equipment',.075)
    # Keep this iteration a simple equipment envelope with visible side manifolds.
    for side in (-1,1):
        for tangent in (-1,1):
            b.box(f'corner{side}.{tangent}',root,(.1,.1,height),
                  (side*(width/2-.04),tangent*(width/2-.04),height/2),'rail')
    cover=p['cover_thickness']
    b.box('top_cover',root,(width,width,cover),(0,0,height+cover/2),'equipment')
    m=layout.MANIFOLDS
    for kind,side,z,diameter,material in [
        ('hot',-1,m['hot_z'],m['salt_diameter'],'hot'),
        ('cold',-1,m['cold_z'],m['salt_diameter'],'cold'),
        ('water',1,m['water_z'],m['water_diameter'],'water'),
        ('steam',1,m['steam_z'],m['steam_diameter'],'steam')]:
        y=side*m['side_offset']; h=m['half_length']
        spec=layout.PIPE_SPECS[kind if kind in ('hot','cold') else kind+'_branch']
        cr=m['collector_bare_diameters'][kind]/2
        metal=half_pipe_collector(b,root,kind+'_manifold_metal',side,width/2,h,z,spec['bare_od']/2,
                                 m['side_offset'],-1 if kind=='hot' else 1,'rail',collector_radius=cr)
        move_collection(b,metal,'Pressure pipe metal')
        obj=half_pipe_collector(b,root,kind+'_manifold',side,width/2,h,z,spec['jacket_od']/2,
                               m['side_offset'],-1 if kind=='hot' else 1,material,collector_radius=cr+spec['insulation'])
        move_collection(b,obj,'Pipe insulation')
        obj['service']=kind;obj['side_as_seen_from_reactor']='inward' if side<0 else 'outward'
        obj['insulation_m']=spec['insulation'];obj['pressure_boundary']='Collector envelope only; pressure wall not sized'
    valve_size=p['air_valve_box_size'];vx,vy=p['air_valve_box_xy']
    valve_bottom=height+cover
    valve=b.box('air_butterfly_valve',root,valve_size,
                (vx,vy,valve_bottom+valve_size[2]/2),'exhaust_air',.035)
    valve['represents']='Butterfly valve housing; visual box only, no internal mechanism'
    valve['top_port_local']=[vx,vy,valve_bottom+valve_size[2]]

    return root


def fuel_storage(b):
    p=layout.FUEL_STORAGE; count=0
    for pair,angle in enumerate(p['pair_angles'],1):
        cx,cy=xy(p['radius'],angle); theta=math.radians(angle)
        for sign in (-1,1):
            count+=1; offset=sign*p['pair_spacing']/2
            x=cx-math.sin(theta)*offset; y=cy+math.cos(theta)*offset
            center=p['top']-p['height']/2
            root=b.assembly(f'equipment.fuel_storage_{count}','Fuel storage',(x,y,center),angle)
            root['pair']=pair
            b.box('closed_tank',root,(p['length'],p['width'],p['height']),(0,0,0),'fuel',.08)
            b.box('lid',root,(p['length']+.12,p['width']+.12,.15),(0,0,p['height']/2+.06),'fuel_light',.035)
            for z in (-1.8,0,1.8):
                for side in (-1,1):
                    b.box(f'stiffener{z}.{side}',root,(p['length']+.04,.045,.1),(0,side*(p['width']/2+.02),z),'fuel_light')
            for end in (-1,1):
                b.beam(f'lifting_lug{end}',root,(end*1.15,-.25,p['height']/2+.18),
                       (end*1.15,.25,p['height']/2+.18),.055,'rail')
            root['floor_contact_z']=layout.FLOOR_Z
    return count


def auxiliary_equipment(b):
    from textual_graphics.installation_utilities import build_coolant_tank
    build_coolant_tank(b,layout)



def stacks(b):
    air_materials(b)
    spec=layout.AIR['insulation']
    for index,angle in enumerate(layout.STACKS['angles'],1):
        p=layout.STACKS; root=b.assembly(f'building.stack_{index}','Stacks',(*xy(p['radius'],angle),p['base_z']))
        tube_radius=p['tube_diameter']/2; base=p['base_height']
        b.box('base',root,(p['tube_diameter']+.89,p['tube_diameter']+.89,base),(0,0,base/2),'concrete',.06)
        b.cylinder('tube',root,tube_radius,p['height'],(0,0,base+p['height']/2),'exhaust_air',vertices=64)
        b.annulus('open_rim',root,tube_radius-.055,tube_radius+.06,
                  base+p['height']-.12,base+p['height']+.05,'rail',steps=64)
        # A dark inset reads as an open stack mouth without an internal model.
        b.cylinder('mouth',root,tube_radius-.065,.02,(0,0,base+p['height']+.015),'dark',vertices=64,bevel=0)
        for layer,ri,ro,mat in [('insulation',tube_radius,tube_radius+spec['thickness'],'air_insulation'),
                ('cladding',tube_radius+spec['thickness'],tube_radius+spec['thickness']+spec['cladding'],'air_cladding')]:
            insulation_tag(b.annulus(layer,root,ri,ro,base,base+p['height'],mat,steps=96),spec,layer)
        for z in range(3,p['height'],4): b.ring(f'band{z}',root,tube_radius+spec['thickness']+spec['cladding']+.008,base+z,.012,'rail')


def crane(b):
    p=layout.CRANE; root=b.assembly('building.circular_crane','Crane')
    radius=layout.BUILDING['diameter']/2-1.3; height=p['runway_height']; y=p['bridge_y']
    b.annulus('runway',root,radius-.16,radius+.16,height-.3,height+.1,'crane',steps=160)
    b.ring('rail',root,radius,height+.17,.06,'rail')
    span=2*math.sqrt(radius**2-y**2)
    for offset in (-.5,.5):
        b.box(f'bridge_web{offset}',root,(span,.22,.78),(0,y+offset,height+.55),'crane',.025)
        for z in (height+.16,height+.94):
            b.box(f'bridge_flange{offset}.{z}',root,(span,.56,.09),(0,y+offset,z),'crane',.02)
    for end in (-1,1): b.box(f'end_truck{end}',root,(1.3,2.1,.45),(end*span/2,y,height+.4),'crane',.06)
    x=p['trolley_x']
    b.box('trolley',root,(1.8,1.8,p['trolley_height']),(x,y,height+p['trolley_centre_offset']),'dark',.09)
    b.cylinder('hoist_motor',root,.32,1.15,(x+.2,y,height+1.8),'crane')
    lift=p['displayed_hook_raise']
    for offset in (-.17,.17): b.beam(f'cable{offset}',root,(x+offset,y,height+1),(x+offset,y,height-3.5+lift),.018,'dark')
    b.box('hook_block',root,(.65,.35,.5),(x,y,height-3.65+lift),'crane',.06)
    points=[(x+.25*math.cos(t),y,height-4.18+lift+.25*math.sin(t)) for t in [math.radians(a) for a in range(-210,41,8)]]
    b.tube('hook',root,points,.065,'dark')


def camera(b,name,location,target,scale,shift=0):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data)
    b.collection('Presentation').objects.link(obj)
    obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'; data.ortho_scale=scale
    # Offset the camera itself so camera-parented typography stays centered in
    # the image while the installation moves left to leave room for the legend.
    obj.location+=obj.rotation_euler.to_quaternion() @ Vector((scale*shift,0,0))
    data.clip_end=1000
    return obj


def presentation(b):
    root=b.assembly('presentation.stage','Presentation')
    b.cylinder('site_disc',root,30.0,.18,(0,0,-10.15),'cut_concrete',vertices=160,bevel=.08)
    b.box('ground',root,(2000,2000,.1),(0,0,-10.35),'backdrop')
    for name,location,power,size in [('Key',(-20,-28,52),38000,32),('Fill',(32,-8,34),25000,25),
                                      ('Rim',(-4,28,40),30000,22)]:
        data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK';data.size=size
        obj=bpy.data.objects.new(name,data); b.collection('Presentation').objects.link(obj)
        obj.location=location;obj.rotation_euler=(Vector((0,0,6))-obj.location).to_track_quat('-Z','Y').to_euler()
    scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Studio')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.83,.87,.93,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
    cameras={
        'cutaway':camera(b,'View.Cutaway',(-8,-65,36),(0,0,8),94,.10),
        'plan':camera(b,'View.Plan',(0,0,70),(0,0,0),62),
        'equipment':camera(b,'View.Equipment',(-10,-48,34),(0,0,8),84,.04),
        'stairs':camera(b,'View.Stairs',(-27,-30,17),(-3,-2,-3),36),
        'catwalk':camera(b,'View.Catwalk',(18,-24,18),(0,0,-.3),25),
        'fuel-services':camera(b,'View.FuelServices',(22,-30,26),(0,0,-2),39),
    }
    # Direct overhead camera keeps +Y at the top of the drawing.
    cameras['plan'].rotation_euler=(0,0,0)
    return cameras


def annotations(b,cam,view):
    name='Annotations.'+view
    collection=b.collection(name)
    if view=='fuel-services':
        text_on_camera('FuelServices.Title','WISTR | Sector / maintenance-tank connections',-17.5,13,.57,cam,collection)
        text_on_camera('FuelServices.Note','Six heated maintenance bundles / three independent tube pairs per sector',-17.5,12.05,.29,cam,collection,'#4C5C68')
        text_on_camera('FuelServices.Footer','Insulated jackets shown / lift insulation before disconnecting cap-side jumpers',-17.5,-13.1,.26,cam,collection,'#4C5C68')
    elif view=='stairs':
        text_on_camera('Stairs.Title','WISTR | Stair access to reactor catwalk',-12.7,10.0,.45,cam,collection)
        text_on_camera('Stairs.Note','Three flights / 1.2 m clear width / 8.2 m bridge to catwalk',-12.7,9.3,.23,cam,collection,'#4C5C68')
        text_on_camera('Stairs.Footer','8.5 m rise / two intermediate landings / structural and egress design provisional',-12.7,-10.2,.21,cam,collection,'#4C5C68')
    elif view=='catwalk':
        text_on_camera('Catwalk.Title','WISTR | Absorber service catwalk',-10.2,7.7,.42,cam,collection)
        text_on_camera('Catwalk.Note','12 reservoir/module stations / compact salt-gas bundles / lowered deck',-10.2,7.05,.22,cam,collection,'#4C5C68')
        text_on_camera('Catwalk.Footer','Open-bottom cover channels / local insulation strips / sizes and supports provisional',-10.2,-7.8,.20,cam,collection,'#4C5C68')
    elif view=='cutaway':
        text_on_camera('WISTR.Title','WISTR | Installation concept',-36.0,29.0,1.3,cam,collection)
        text_on_camera('WISTR.Subtitle','Detailed WISTR reactor  /  provisional installation',-35.9,27.4,.57,cam,collection,'#4C5C68')
        labels=[('WISTR reactor and well','#648AA3'),('Steam generators (3)','#9DA6AC'),
                ('Fuel storage (6)','#C98B41'),('Coolant storage','#839778'),
                ('Mobile sector canister','#A88158'),('Circular crane','#C8993C'),
                ('Cold-leg pumps (3)','#3E7468'),('Absorber modules (12)','#517F85'),('Insulated hot air / stack','#B4ABA3'),('Fresh-air supply','#56B6C4')]
        for index,(label,color) in enumerate(labels):
            y=14-index*2.2
            text_on_camera(f'Legend.swatch{index}','●',14.0,y,.64,cam,collection,color)
            text_on_camera(f'Legend{index}',label,15.1,y,.58,cam,collection,'#334858')
        text_on_camera('Legend.detail','17 m generators; 2 MW pump motors',14.0,-9.0,.43,cam,collection,'#4C5C68')
        text_on_camera('Legend.detail2','Purple: steam / Blue: feedwater',14.0,-10.0,.43,cam,collection,'#4C5C68')
        text_on_camera('WISTR.Note','Based on the supplied plan and section. Unspecified dimensions are illustrative.',
                       -35.9,-29.0,.47,cam,collection,'#4C5C68')
    elif view=='equipment':
        text_on_camera('Equipment.Title','WISTR | Internal exhaust manifold',-10.0,24.0,1.0,cam,collection)
        text_on_camera('Equipment.Note','Draft: internal insulated header / direct reactor exhaust / shell hidden',-10.0,22.7,.47,cam,collection,'#66717A')
        text_on_camera('Equipment.Footer','Silver: insulated exhaust   Cyan: fresh air   Gold/green: salt',
                       -31,-24,.42,cam,collection,'#66717A')
    else:
        text_on_camera('Plan.Title','WISTR | Plan arrangement',-24,23.5,.82,cam,collection)
        text_on_camera('Plan.Note','Internal exhaust header; external fresh-air ring; direct reactor exhaust at 135 degrees',-24,22.35,.42,cam,collection,'#66717A')
        text_on_camera('Plan.Footer','Three steam generators  /  six storage tanks in three pairs',-24,-23.5,.44,cam,collection,'#66717A')
    return collection


def select_view(b,cameras,view):
    scene=bpy.context.scene;scene.camera=cameras[view]
    scene['section_cutaway']=view=='cutaway'
    scene.update_tag()
    for key in cameras:
        b.collections['Annotations.'+key].hide_render=key!=view
        b.collections['Annotations.'+key].hide_viewport=key!=view
    for key in ('Shell','Crane'):
        b.collections[key].hide_render=view!='cutaway'
        b.collections[key].hide_viewport=view!='cutaway'
    b.collections['Stacks'].hide_render=False
    b.collections['Stacks'].hide_viewport=False
    for obj in bpy.context.scene.objects:
        if obj.name.endswith('.sg_air_connection'):
            obj.hide_render=view!='cutaway';obj.hide_viewport=view!='cutaway'
    # Show the full hollow rings in equipment/plan; cut the upper front half with the shell.
    for obj in bpy.context.scene.objects:
        if obj.get('air_plenum_part'):
            hidden=(obj.get('air_plenum_lid',False) and view!='cutaway') or (view=='cutaway' and obj.get('air_plenum_front',False) and obj.get('air_plenum_service')=='hot')
            obj.hide_render=hidden;obj.hide_viewport=hidden
    # Close-up omits remote equipment but retains the real reactor/catwalk geometry.
    for category in ('Steam generators','Fuel storage','Coolant storage','Sector handling','Coolant pumps','Secondary piping','Air distribution','Major piping','Stacks','Pressure pipe metal','Pipe insulation','Hot air insulation','Hot air duct metal','Coolant transfer','Nitrogen supply','Utility piping','Maintenance laydown'):
        if category in b.collections:
            b.collections[category].hide_render=b.collections[category].hide_viewport=(view in ('catwalk','stairs') or (view=='fuel-services' and category!='Fuel storage'))
    if view=='plan': scene.render.resolution_x,scene.render.resolution_y=1800,1800
    else: scene.render.resolution_x,scene.render.resolution_y=2400,1800
    bpy.context.view_layer.update()


def report(b,output,integration,services):
    counts={name:sum(1 for obj in b.assemblies.values() if obj['category']==name)
            for name in ('Steam generators','Fuel storage','Reactor vessel','Coolant storage','Sector handling','Stacks','Coolant pumps','Absorber modules','Absorber reservoirs','Coolant transfer','Nitrogen supply')}
    expected={'Steam generators':3,'Fuel storage':6,'Reactor vessel':1,'Coolant storage':1,'Sector handling':1,'Stacks':1,'Coolant pumps':3,'Absorber modules':12,'Absorber reservoirs':12,'Coolant transfer':1,'Nitrogen supply':1}
    if counts!=expected: raise AssertionError(f'Assembly counts differ: {counts}')
    if bpy.context.scene.unit_settings.scale_length!=1: raise AssertionError('Expected metres')
    assert 'building.structure.operating_deck' not in bpy.data.objects
    assert 'building.structure.perimeter_walk' not in bpy.data.objects
    assert not any('building.structure.basement_column' in o.name for o in bpy.data.objects)
    for obj in bpy.data.objects:
        if obj.type=='MESH' and not all(math.isfinite(v) for row in obj.matrix_world for v in row):
            raise AssertionError('Non-finite object transform: '+obj.name)
    from textual_graphics.installation_utilities import check_utilities
    services['utilities']['checks']=check_utilities(layout,services['utilities'])
    from textual_graphics.installation_maintenance import check_maintenance
    services['maintenance']['checks']=check_maintenance(b,layout,services['maintenance'])
    source=ROOT/'references/reactor-building-v1.svg'
    document={
        'title':'WISTR static installation concept','units':'metres; Z up',
        'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'assembly_counts':counts,'mesh_objects':sum(o.type=='MESH' for o in bpy.data.objects),
        'assemblies':{name:{'category':obj['category'],'position':list(obj.location),
                            'rotation_z_deg':math.degrees(obj.rotation_euler.z)} for name,obj in b.assemblies.items()},
        'building':layout.BUILDING,'steam_generators':layout.STEAM_GENERATORS,
        'calculation_sources':{name: {'path':str(Path('../fastSalt/calculations/steam-generator')/name),
            'sha256':hashlib.sha256((ROOT.parent/'fastSalt/calculations/steam-generator'/name).read_bytes()).hexdigest()
            if (ROOT.parent/'fastSalt/calculations/steam-generator'/name).exists() else None}
            for name in ('Steam and feedwater pipe sizing - Hurmet.md','Steam and feedwater insulation - Hurmet.md',
                         'Molten-salt coolant pipe wall - Hurmet.md','Molten-salt coolant insulation - Hurmet.md')},
        'piping':layout.PIPING,'stacks':layout.STACKS,'crane':layout.CRANE,
        'generator_top_z':layout.GENERATOR_TOP_Z,'reactor_integration':integration,
        'services':services,'air_parameters':layout.AIR,'pump_estimate':layout.PUMPS,'assumptions':layout.ASSUMPTIONS,
        'checks':check_piping(b,layout,services)+check_interference(layout,services)+['Expected equipment counts verified','Metric units and finite transforms verified',
                  'Intermediate floor, perimeter walkway and former deck columns absent']+check_integration(integration)+check_services(b,layout,services)+check_air_networks(b,layout,services['air'])+check_access(b,layout,services),
    }
    (output/'wistr-model-report.json').write_text(json.dumps(document,indent=2)+'\n')
    return document


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft',action='store_true')
    parser.add_argument('--build-only',action='store_true',help='Save the scene and report without rendering')
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/wistr',help='Output directory')
    parser.add_argument('--views',nargs='+',choices=['cutaway','plan','equipment','catwalk','fuel-services','stairs'],default=['cutaway','plan','equipment'])
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output=args.output;output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    b=SceneBuilder();palette(b)
    integration=reactor_placement(layout,ROOT)
    route_coolant(b,layout,integration)
    building(b,integration);reactor_foundation(b,integration)
    for i,angle in enumerate(layout.STEAM_GENERATORS['angles'],1): steam_generator(b,i,angle)
    fuel_storage(b);auxiliary_equipment(b);stacks(b);crane(b)
    from textual_graphics.installation_catwalk import build_catwalk, connect_absorbers
    services=secondary_headers(b,layout)
    services['catwalk']=build_catwalk(b,layout)
    services['air']=air_networks(b,layout,ROOT)
    services['access']=equipment_access(b,layout)
    cameras=presentation(b)
    for view,cam in cameras.items(): annotations(b,cam,view)
    print('INSTALLATION_GEOMETRY_READY; importing reactor',flush=True)
    actual=import_reactor(b,layout,ROOT)
    expected={t['name']:t for t in integration['terminals']}
    for terminal in actual['terminals']:
        assert (Vector(terminal['point'])-Vector(expected[terminal['name']]['point'])).length<1e-5
    actual['routes']=integration['routes'];actual['deck_penetrations']=integration['deck_penetrations']
    actual['cold_suction_routes']=integration['cold_suction_routes'];actual['pumps']=integration['pumps']
    integration=actual
    print('REACTOR_IMPORTED',flush=True)
    connect_absorbers(b,layout,services['catwalk'])
    print('CATWALK_CONNECTED',flush=True)
    from textual_graphics.installation_fuel_services import build_fuel_services
    services['fuel_services']=build_fuel_services(b,layout,services)
    from textual_graphics.installation_channels import build_channels
    from textual_graphics.installation_bundle_checks import check_bundle_envelopes
    build_channels(b,layout,services)
    services['bundle_envelopes']=check_bundle_envelopes(services)
    from textual_graphics.installation_utilities import build_utilities
    services['utilities']=build_utilities(b,layout,ROOT)
    from textual_graphics.installation_stairs import build_stairs
    build_stairs(b,layout,services)
    from textual_graphics.installation_maintenance import build_maintenance
    services['maintenance']=build_maintenance(b,layout)
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16 if args.draft else 48
    scene.cycles.use_denoising=True;scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'
    scene.view_settings.exposure=.25
    scene.render.resolution_percentage=50 if args.draft else 100
    select_view(b,cameras,'cutaway')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.color_type='MATERIAL'
                area.spaces.active.overlay.show_relationship_lines=False
                area.spaces.active.overlay.show_overlays=False
    summary=report(b,output,integration,services)
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'wistr-installation.blend'))
    for view in ([] if args.build_only else args.views):
        select_view(b,cameras,view)
        scene.render.filepath=str(output/f'wistr-{view}{"-draft" if args.draft else ""}.png')
        bpy.ops.render.render(write_still=True)
    select_view(b,cameras,'stairs' if 'stairs' in args.views else ('catwalk' if 'catwalk' in args.views else ('fuel-services' if 'fuel-services' in args.views else ('equipment' if 'equipment' in args.views else 'cutaway'))))
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'wistr-installation.blend'))
    print('WISTR_OK '+json.dumps({'counts':summary['assembly_counts'],'meshes':summary['mesh_objects']}))


if __name__=='__main__': main()
