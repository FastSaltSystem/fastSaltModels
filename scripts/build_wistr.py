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
        ('sector','#8E6440',.15,.5),('hot','#AA862B',.2,.4),
        ('cold','#3E7468',.25,.4),('air','#789DB3',.25,.4),
        ('crane','#D4A143',.25,.35),('black','#252B31',.15,.55),
        ('backdrop','#FAFAF7',0,.7),
    ]:
        b.material(name,color,metallic=metal,roughness=rough,concrete=name=='concrete')


def building(b):
    p=layout.BUILDING; r=p['diameter']/2; depth=p['lower_level_depth']
    wall_top=p['total_height']-depth-p['dome_rise']
    root=b.assembly('building.structure','Structure')
    b.cylinder('foundation',root,r+.55,.6,(0,0,-depth-.4),'cut_concrete',vertices=160)
    b.cylinder('lower_slab',root,r,.6,(0,0,-depth+.3),'floor',vertices=160)
    deck=b.cylinder('operating_deck',root,12.5,p['deck_thickness'],
                    (0,0,-p['deck_thickness']/2),'floor',vertices=160,bevel=0)
    cutter=b.cylinder('cut.central',root,3.5,3,(0,0,0),None,vertices=96,bevel=0)
    b.cut(deck,cutter)
    for index,angle in enumerate(layout.FUEL_STORAGE['pair_angles']):
        cx,cy=xy(layout.FUEL_STORAGE['radius'],angle)
        cutter=b.box(f'cut.storage{index}',root,(4.3,4.25,3),(cx,cy,0),None)
        cutter.rotation_euler.z=math.radians(angle)
        b.cut(deck,cutter)
    sx,sy,_=layout.SECTOR_STORAGE['position']
    cutter=b.box('cut.sector',root,(3.9,2.9,3),(sx,sy,0),None)
    b.cut(deck,cutter)
    # An open wedge exposes the vessel and the front pair of storage tanks.
    cutter=b.annulus('cut.front',root,.001,r+.5,-1,1,None,start=215,end=280,steps=32)
    b.cut(deck,cutter)

    shell=b.assembly('building.shell','Shell')
    b.annulus('retained_wall',shell,r-p['wall_thickness'],r,-depth,wall_top,
              'concrete',start=0,end=180,steps=112)
    b.dome('retained_dome',shell,r,p['dome_rise'],wall_top,p['wall_thickness'],'concrete')
    for angle in range(0,181,20):
        x,y=xy(r-.95,angle)
        b.box(f'pilaster{angle}',shell,(.45,.45,wall_top),(x,y,wall_top/2),'cut_concrete',.04)
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
    # Basement columns and short beam ends remain visible in the cutaway.
    for index,angle in enumerate((20,65,115,160,205,295,340)):
        x,y=xy(11.8,angle)
        b.box(f'basement_column{index}',root,(.48,.48,depth-.6),(x,y,-depth/2),'concrete',.04)
    for angle in (215,280):
        x,y=xy(8.0,angle)
        beam=b.box(f'cut_edge_beam{angle}',root,(10,.35,.6),(x,y,-.6),'concrete')
        beam.rotation_euler.z=math.radians(angle)
    # A thin perimeter deck band and rail give a readable edge to the floor.
    b.annulus('perimeter_walk',root,12.5,13.5,-.55,0,'floor',start=0,end=360)
    for angle in range(0,360,8):
        x,y=xy(13.05,angle)
        b.beam(f'perimeter_post{angle}',root,(x,y,0),(x,y,1.05),.025,'rail')
    b.ring('perimeter_rail',root,13.05,1.05,.025,'rail')
    b.ring('perimeter_midrail',root,13.05,.55,.022,'rail')
    # Generic architectural wall lights, without assigning functional systems.
    for angle in (25,65,110,155):
        x,y=xy(13.35,angle)
        b.box(f'wall_light{angle}',shell,(.35,.18,.6),(x,y,5.3),'panel',.04)
    return root


def reactor(b):
    p=layout.VESSEL; root=b.assembly('equipment.reactor_vessel','Reactor vessel')
    height=p['body_top']-p['bottom']
    b.cylinder('closed_shell',root,p['radius'],height,(0,0,(p['bottom']+p['body_top'])/2),'vessel',vertices=128,bevel=.1)
    # Shallow dished exterior heads; no internal core geometry.
    for name,z,scale in [('top_head',-.3,(p['radius'],p['radius'],.56)),
                          ('bottom_head',p['bottom'],(p['radius'],p['radius'],.45))]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=24,radius=1)
        obj=b.finish(bpy.context.object,name,root,'vessel_light',(0,0,z))
        obj.scale=scale
        for face in obj.data.polygons: face.use_smooth=True
    b.annulus('head_flange',root,p['radius']-.12,p['radius']+.2,-.42,-.2,'rail')
    for index in range(32):
        x,y=xy(p['radius']+.06,index*360/32)
        b.cylinder(f'head_bolt{index}',root,.055,.14,(x,y,-.17),'dark',vertices=6,bevel=.005)
    for z in (-2.5,-5.5): b.ring(f'exterior_band{z}',root,p['radius']+.025,z,.055,'vessel_light')
    b.cylinder('support_plinth',root,2.6,.6,(0,0,-8.9),'concrete',vertices=96)
    b.annulus('retained_well',root,3.0,3.35,-9.1,-.05,'concrete',start=0,end=180)
    b.annulus('well_rim',root,3.45,3.8,-.15,.05,'rail',start=0,end=215)
    rail_points=[(*xy(3.7,a),.05) for a in range(0,211,10)]
    b.rail('well_guard',root,rail_points)
    return root


def steam_generator(b,index,angle):
    p=layout.STEAM_GENERATORS
    root=b.assembly(f'equipment.steam_generator_{index}','Steam generators',(*xy(p['radius'],angle),0),angle)
    width,height=p['width'],p['height']
    root['casing_dimensions_m']=[width,width,height]
    b.box('pedestal',root,(4.5,4.5,.38),(0,0,.19),'concrete',.06)
    b.box('casing',root,(width,width,height),(0,0,.5+height/2),'equipment',.075)
    # Panel joints, corner posts and inspection covers on the exterior casing.
    for side in (-1,1):
        for level in range(5):
            b.box(f'side_panel{side}.{level}',root,(3.72,.045,1.82),(0,side*2.025,1.5+2*level),'panel',.025)
            b.box(f'front_panel{side}.{level}',root,(.045,3.72,1.82),(side*2.025,0,1.5+2*level),'panel',.025)
        for tangent in (-1,1):
            b.box(f'corner{side}.{tangent}',root,(.1,.1,10),(side*1.96,tangent*1.96,5.5),'rail',.01)
    b.box('inspection_cover',root,(1.05,.075,1.25),(-.25,-2.075,2.2),'equipment',.045)
    b.beam('door_handle',root,(-.65,-2.14,2.05),(-.65,-2.14,2.45),.035,'dark')
    # Access ladder and a top maintenance platform give visual scale.
    for x in (.8,1.45):
        b.beam(f'ladder_rail{x}',root,(x,-2.33,.5),(x,-2.33,11.2),.035,'rail')
    for index_rung in range(33):
        z=.65+index_rung*.31
        b.beam(f'ladder_rung{index_rung}',root,(.8,-2.33,z),(1.45,-2.33,z),.025,'rail')
    for x in (-2.22,2.22): b.box(f'catwalk_x{x}',root,(.44,4.85,.12),(x,0,10.45),'rail')
    for y in (-2.22,2.22): b.box(f'catwalk_y{y}',root,(4.0,.44,.12),(0,y,10.45),'rail')
    points=[(-2.4,-2.4,10.5),(0,-2.4,10.5),(2.4,-2.4,10.5),
            (2.4,0,10.5),(2.4,2.4,10.5),(0,2.4,10.5),
            (-2.4,2.4,10.5),(-2.4,0,10.5),(-2.4,-2.4,10.5)]
    b.rail('top_guard',root,points)
    b.box('top_cover',root,(3.7,3.7,.13),(0,0,10.57),'equipment',.04)
    # Identification plate remains geometry attached to the named assembly.
    plate=b.box('identification_plate',root,(1.15,.04,.42),(0,-2.07,8.7),'dark',.025)
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
            base_top=center-p['height']/2
            base_bottom=-9.1
            b.box('support_plinth',root,(p['length']+.15,p['width']+.2,base_top-base_bottom),
                  (0,0,(base_top+base_bottom)/2-center),'concrete',.04)
    return count


def auxiliary_equipment(b):
    p=layout.COOLANT_STORAGE; root=b.assembly('equipment.coolant_storage','Coolant storage',p['position'])
    b.cylinder('plinth',root,p['radius']+.25,.3,(0,0,.15),'concrete')
    b.cylinder('closed_tank',root,p['radius'],p['height'],(0,0,.3+p['height']/2),'coolant',vertices=96,bevel=.08)
    b.cylinder('roof',root,p['radius']+.03,.13,(0,0,.3+p['height']),'coolant',vertices=96)
    for z in (1,3.5,6): b.ring(f'seam{z}',root,p['radius']+.025,z,.035,'rail')
    b.cylinder('access_cover',root,.38,.15,(.6,0,p['height']+.42),'rail')
    for y in (-.35,.35): b.beam(f'ladder{y}',root,(-2.12,y,.3),(-2.12,y,8.5),.032,'rail')
    for i in range(26): b.beam(f'rung{i}',root,(-2.12,-.35,.45+i*.3),(-2.12,.35,.45+i*.3),.022,'rail')
    p=layout.SECTOR_STORAGE; root=b.assembly('equipment.sector_storage','Sector storage',p['position'])
    b.box('closed_enclosure',root,p['size'],(0,0,0),'sector',.09)
    b.box('cover',root,(3.55,2.55,.18),(0,0,p['size'][2]/2+.08),'fuel_light',.06)
    for x in (-1,1): b.beam(f'lifting_bar{x}',root,(x,-.5,3.1),(x,.5,3.1),.06,'rail')
    b.box('plinth',root,(3.7,2.7,2.65),(0,0,-4.225),'concrete',.04)


def pipes_and_stacks(b):
    salt_radius=layout.PIPING['salt_pipe_diameter']/2
    for index,angle in enumerate(layout.STEAM_GENERATORS['angles'],1):
        root=b.assembly(f'connections.loop_{index}','Major piping',angle=angle)
        inlet=layout.STEAM_GENERATORS['radius']-2
        b.rounded_pipe('upper_connection',root,[(2.05,-.85,-1.2),(3,-.85,-1.2),
                       (3,-.85,8.7),(inlet,-.85,8.7)],salt_radius,'hot',bend=.65)
        b.rounded_pipe('lower_connection',root,[(2.05,.85,-5.8),(3,.85,-5.8),
                       (3,.85,1.25),(inlet,.85,1.25)],salt_radius,'cold',bend=.6)
        b.cylinder('pump_casing',root,.43,.7,(5.8,.85,1.25),'cold',vertices=48)
        b.cylinder('pump_motor',root,.35,.85,(5.8,.85,2.04),'equipment',vertices=48)
        b.box('pump_support',root,(1.05,.85,.3),(5.8,.85,.15),'concrete',.04)
        for x in (3.7,6.1):
            b.box(f'pipe_support{x}',root,(.12,.9,1.1),(x,.85,.55),'rail')
        # Upper and lower runs are visual connection cues, with no sizing model.
        b.rounded_pipe('air_connection',root,[(inlet+4,0,1.4),(15.5,0,1.4)],.34,'air')
    for index,angle in enumerate(layout.STACKS['angles'],1):
        p=layout.STACKS; root=b.assembly(f'building.stack_{index}','Stacks',(*xy(p['radius'],angle),0))
        tube_radius=p['tube_diameter']/2
        b.box('base',root,(p['tube_diameter']+.89,p['tube_diameter']+.89,1.0),(0,0,.0),'concrete',.06)
        b.cylinder('tube',root,tube_radius,p['height'],(0,0,p['height']/2),'air',vertices=64)
        b.annulus('open_rim',root,tube_radius-.055,tube_radius+.06,
                  p['height']-.12,p['height']+.05,'rail',steps=64)
        # A dark inset reads as an open stack mouth without an internal model.
        b.cylinder('mouth',root,tube_radius-.065,.02,(0,0,p['height']+.015),'dark',vertices=64,bevel=0)
        for z in range(3,p['height'],4): b.ring(f'band{z}',root,tube_radius+.035,z,.035,'rail')


def crane(b):
    p=layout.CRANE; root=b.assembly('building.circular_crane','Crane')
    radius=12.9; height=p['runway_height']; y=p['bridge_y']
    b.annulus('runway',root,radius-.16,radius+.16,height-.3,height+.1,'crane',steps=160)
    b.ring('rail',root,radius,height+.17,.06,'rail')
    span=2*math.sqrt(radius**2-y**2)
    for offset in (-.5,.5):
        b.box(f'bridge_web{offset}',root,(span,.22,.78),(0,y+offset,height+.55),'crane',.025)
        for z in (height+.16,height+.94):
            b.box(f'bridge_flange{offset}.{z}',root,(span,.56,.09),(0,y+offset,z),'crane',.02)
    for end in (-1,1): b.box(f'end_truck{end}',root,(1.3,2.1,.45),(end*span/2,y,height+.4),'crane',.06)
    x=p['trolley_x']
    b.box('trolley',root,(1.8,1.8,.55),(x,y,height+1.3),'dark',.09)
    b.cylinder('hoist_motor',root,.32,1.15,(x+.2,y,height+1.8),'crane')
    for offset in (-.17,.17): b.beam(f'cable{offset}',root,(x+offset,y,height+1),(x+offset,y,10.8),.018,'dark')
    b.box('hook_block',root,(.65,.35,.5),(x,y,10.65),'crane',.06)
    points=[(x+.25*math.cos(t),y,10.12+.25*math.sin(t)) for t in [math.radians(a) for a in range(-210,41,8)]]
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
    b.cylinder('site_disc',root,17.1,.18,(0,0,-10.15),'cut_concrete',vertices=160,bevel=.08)
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
        'cutaway':camera(b,'View.Cutaway',(-8,-65,42),(0,0,8),68,.10),
        'plan':camera(b,'View.Plan',(0,0,70),(0,0,0),42),
        'equipment':camera(b,'View.Equipment',(-10,-48,34),(0,0,0),47,.07),
    }
    # Direct overhead camera keeps +Y at the top of the drawing.
    cameras['plan'].rotation_euler=(0,0,0)
    return cameras


def annotations(b,cam,view):
    name='Annotations.'+view
    collection=b.collection(name)
    if view=='cutaway':
        text_on_camera('WISTR.Title','WISTR | Installation concept',-29.0,22.7,1.3,cam,collection)
        text_on_camera('WISTR.Subtitle','Static cutaway  /  equipment arrangement',-28.9,21.1,.57,cam,collection,'#4C5C68')
        labels=[('Reactor vessel','#648AA3'),('Steam generators (3)','#9DA6AC'),
                ('Fuel storage (6)','#C98B41'),('Coolant storage','#839778'),
                ('Sector storage','#A88158'),('Circular crane','#C8993C')]
        for index,(label,color) in enumerate(labels):
            y=10-index*2.2
            text_on_camera(f'Legend.swatch{index}','●',16.0,y,.64,cam,collection,color)
            text_on_camera(f'Legend{index}',label,17.1,y,.58,cam,collection,'#334858')
        text_on_camera('Legend.detail','Closed equipment envelopes',16.0,-5.1,.43,cam,collection,'#4C5C68')
        text_on_camera('Legend.detail2','Front shell and floor opened',16.0,-6.0,.43,cam,collection,'#4C5C68')
        text_on_camera('WISTR.Note','Based on the supplied plan and section. Unspecified dimensions are illustrative.',
                       -28.9,-23.0,.47,cam,collection,'#4C5C68')
    elif view=='equipment':
        text_on_camera('Equipment.Title','WISTR | Equipment and lower level',-20.5,15.4,1.0,cam,collection)
        text_on_camera('Equipment.Note','Building shell and crane hidden for visibility',-20.5,14.15,.47,cam,collection,'#66717A')
        text_on_camera('Equipment.Footer','Blue: reactor vessel    Amber: storage    Silver: steam generators    Green: coolant storage',
                       -20.5,-15.4,.39,cam,collection,'#66717A')
    else:
        text_on_camera('Plan.Title','WISTR | Plan arrangement',-18.4,18.3,.82,cam,collection)
        text_on_camera('Plan.Note','Roof, crane and upper shell hidden',-18.4,17.15,.42,cam,collection,'#66717A')
        text_on_camera('Plan.Footer','Three steam generators  /  six storage tanks in three pairs',-18.4,-18.3,.44,cam,collection,'#66717A')
    return collection


def select_view(b,cameras,view):
    scene=bpy.context.scene;scene.camera=cameras[view]
    for key in cameras:
        b.collections['Annotations.'+key].hide_render=key!=view
        b.collections['Annotations.'+key].hide_viewport=key!=view
    for key in ('Shell','Crane'):
        b.collections[key].hide_render=view!='cutaway'
        b.collections[key].hide_viewport=view!='cutaway'
    b.collections['Stacks'].hide_render=view=='equipment'
    b.collections['Stacks'].hide_viewport=view=='equipment'
    if view=='plan': scene.render.resolution_x,scene.render.resolution_y=1800,1800
    else: scene.render.resolution_x,scene.render.resolution_y=2400,1800
    bpy.context.view_layer.update()


def report(b,output):
    counts={name:sum(1 for obj in b.assemblies.values() if obj['category']==name)
            for name in ('Steam generators','Fuel storage','Reactor vessel','Coolant storage','Sector storage','Stacks')}
    expected={'Steam generators':3,'Fuel storage':6,'Reactor vessel':1,'Coolant storage':1,'Sector storage':1,'Stacks':3}
    if counts!=expected: raise AssertionError(f'Assembly counts differ: {counts}')
    if bpy.context.scene.unit_settings.scale_length!=1: raise AssertionError('Expected metres')
    deck=bpy.data.objects['building.structure.operating_deck']
    # Check the resulting mesh, not just the cutter parameters: a reversed
    # Boolean cutter can otherwise silently leave an apparently solid deck.
    probes=[((0,0),False),((0,-7),False),((0,5),True)]
    probes.extend((xy(layout.FUEL_STORAGE['radius'],a),False)
                  for a in layout.FUEL_STORAGE['pair_angles'])
    for (x,y),expected_hit in probes:
        origin=deck.matrix_world.inverted() @ Vector((x,y,5))
        actual_hit=deck.ray_cast(origin,Vector((0,0,-1)))[0]
        if actual_hit!=expected_hit:
            raise AssertionError(f'Deck opening check failed at {(x,y)}: hit={actual_hit}')
    for obj in bpy.data.objects:
        if obj.type=='MESH' and not all(math.isfinite(v) for row in obj.matrix_world for v in row):
            raise AssertionError('Non-finite object transform: '+obj.name)
    source=ROOT/'references/reactor-building-v1.svg'
    document={
        'title':'WISTR static installation concept','units':'metres; Z up',
        'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'assembly_counts':counts,'mesh_objects':sum(o.type=='MESH' for o in bpy.data.objects),
        'assemblies':{name:{'category':obj['category'],'position':list(obj.location),
                            'rotation_z_deg':math.degrees(obj.rotation_euler.z)} for name,obj in b.assemblies.items()},
        'building':layout.BUILDING,'steam_generators':layout.STEAM_GENERATORS,
        'piping':layout.PIPING,'stacks':layout.STACKS,
        'assumptions':layout.ASSUMPTIONS,
        'checks':['Expected equipment counts verified','Metric units and finite transforms verified',
                  'Ray checks verify central opening, three storage bays, front cutaway and retained deck'],
    }
    (output/'wistr-model-report.json').write_text(json.dumps(document,indent=2)+'\n')
    return document


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft',action='store_true')
    parser.add_argument('--views',nargs='+',choices=['cutaway','plan','equipment'],default=['cutaway','plan','equipment'])
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output=ROOT/'outputs/wistr';output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    b=SceneBuilder();palette(b);building(b);reactor(b)
    for i,angle in enumerate(layout.STEAM_GENERATORS['angles'],1): steam_generator(b,i,angle)
    fuel_storage(b);auxiliary_equipment(b);pipes_and_stacks(b);crane(b)
    cameras=presentation(b)
    for view,cam in cameras.items(): annotations(b,cam,view)
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
    summary=report(b,output)
    if not args.draft: bpy.ops.wm.save_as_mainfile(filepath=str(output/'wistr-installation.blend'))
    for view in args.views:
        select_view(b,cameras,view)
        scene.render.filepath=str(output/f'wistr-{view}{"-draft" if args.draft else ""}.png')
        bpy.ops.render.render(write_still=True)
    select_view(b,cameras,'cutaway')
    if not args.draft: bpy.ops.wm.save_as_mainfile(filepath=str(output/'wistr-installation.blend'))
    print('WISTR_OK '+json.dumps({'counts':summary['assembly_counts'],'meshes':summary['mesh_objects']}))


if __name__=='__main__': main()
