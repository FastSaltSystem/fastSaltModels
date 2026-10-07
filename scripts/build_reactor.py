"""Build the isolated WISTR reactor visual study, without modifying the installation."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models'),str(ROOT/'scripts')]
import wistr_reactor as layout
from textual_graphics.static_scene import SceneBuilder
from textual_graphics.reactor_geometry import build_reactor
from textual_graphics.reactor_checks import check_supports, check_bores, check_spider_passage
from textual_graphics.reactor_air import check_air_system
from render_pms import text_on_camera


def camera(b,name,position,target,scale,shift=0):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data)
    b.collection('Presentation').objects.link(obj)
    obj.location=position;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    obj.location+=obj.rotation_euler.to_quaternion() @ Vector((shift,0,0))
    data.type='ORTHO';data.ortho_scale=scale;data.clip_end=500
    return obj


def presentation(b,d):
    root=b.assembly('study.stage','Presentation')
    b.box('ground',root,(1000,1000,.10),(0,0,d['floor_z']-layout.PRESENTATION['well_floor']-.06),'background')
    for name,position,power,size in [('Key',(-7,-10,15),2200,10),('Fill',(9,-3,9),1300,9),('Rim',(0,8,12),1800,8)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
        obj=bpy.data.objects.new(name,data);b.collection('Presentation').objects.link(obj)
        obj.location=position;obj.rotation_euler=(Vector((0,0,3))-obj.location).to_track_quat('-Z','Y').to_euler()
    scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Studio')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.85,.9,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    cameras={
        'air-system':camera(b,'View.AirCollectors',(-13,-25,18),(0,0,4.2),20),
        'air-section':camera(b,'View.AirCircuit',(0,-30,4.3),(0,0,4.3),18.5),
        'cutaway':camera(b,'View.ReactorCutaway',(-10,-19,12.225),(0,0,3.025),19,1.8),
        'section':camera(b,'View.ReactorSection',(0,-25,2.925),(0,0,2.925),18,1.7),
        'plan':camera(b,'View.ReactorPlan',(0,0,25),(0,0,0),16),
        'cap':camera(b,'View.CapAndSpider',(-9,-14,17.7),(0,0,d['top_z']+.35),13),
        'linkage':camera(b,'View.SectorAndLinks',(11,-12,6.7),(1.4,.7,2.8),9),
        'supports':camera(b,'View.RadialSupports',(6,-8,7),(0,0,.35),8.5),
        'support-detail':camera(b,'View.SupportDetail',(5,-6,3.5),(1.0,.45,.32),4.7),
        'spider':camera(b,'View.SpiderUnderside',(-8,-11,d['top_z']-4.5),(0,0,d['top_z']),11.5),
        'pattern':camera(b,'View.TriangularBores',(4,-5,8),(1.0,.6,2.9),10),
    }
    number=layout.MAINTENANCE['sector'];turn=math.radians((number-1)*60)
    length=b.assemblies[f'reactor.fourbar_{number}']['link_length']
    def raised_point(point):
        x,y,z=point;x+=length*math.cos(math.pi/6);y+=length*.5;z+=length
        return (x*math.cos(turn)-y*math.sin(turn),x*math.sin(turn)+y*math.cos(turn),z)
    cameras['maintenance']=camera(b,'View.MaintenanceSector',raised_point((11,-12,6.7)),raised_point((1.4,.7,2.8)),9)
    cameras['plan'].rotation_euler=(0,0,0)
    return cameras


def annotations(b,cameras,d):
    for view,cam in cameras.items():
        col=b.collection('Labels.'+view)
        def text(name,value,x,y,size=.19,color='#314553'):
            scale={'cutaway':19/15,'section':18/14,'plan':16/11.5,'cap':13/10,'linkage':1,'supports':8.5/7.5,'maintenance':1,
                   'support-detail':4.7/7.5,'spider':11.5/10,'pattern':10/9,'air-system':20/23,'air-section':18.5/23}[view]
            return text_on_camera(view+'.'+name,value,x*scale,y*scale,size*scale,cam,col,color)
        if view in ('air-system','air-section'):
            text('title','WISTR | Vessel air cooling',-10.4,7.65,.46)
            text('subtitle','Cold-air hood encloses the insulated hot hood; two short central duct connections',-10.4,7.0,.24)
            text('cold','COLD AIR IN',-6.7,6.2,.25,'#477FAE')
            text('hot','HOT AIR OUT',3.9,6.2,.25,'#A76432')
            text('foot','Wider cold ring: 0.56 m clear. Outer hood covers most of the concrete wall width.',-10.4,-7.05,.24)
            text('assumptions','Short Ø2 m stubs for later connection. Hood clearances and stub dimensions remain provisional.',-10.4,-7.65,.21)
        elif view=='cutaway':
            text('title','WISTR | Reactor, vessel & well',-6.8,4.88,.38)
            text('subtitle','Sector 3 raised for maintenance  /  its cap removed  /  front half opened',-6.8,4.4,.17)
            items=[('Core sectors (6)','#B98143'),('Steel reflectors','#7C8A91'),
                   ('Absorber tanks (6)','#37656A'),('Cold inlet / downcomer','#568C71'),
                   ('Hot plenum / outlet','#B78725'),('Cooling-air baffle','#59899D')]
            for i,(name,color) in enumerate(items):
                text('swatch'+str(i),'●',4.1,2.5-i*.47,.20,color)
                text('legend'+str(i),name,4.43,2.5-i*.47,.18)
            text('core_dimension','Core: Ø3.6 m × 3.4 m',4.1,-.65,.20)
            text('body_dimension',f'Lower vessel: Ø{2*d["vessel_inner_radius"]:.1f} m',4.1,-1.03,.18)
            text('height',f'Internal stack: {d["top_z"]:.2f} m',4.1,-1.39,.18)
            text('plenum',f'Hot plenum: Ø{2*d["hot_inner_radius"]:.2f} m × 1.6 m',4.1,-1.94,.16)
            text('pipe','6 hot + 6 cold pipes: Ø1.4 m',4.1,-2.25,.16)
            text('downcomer','Downcomer: 1.0 m radially',4.1,-2.57,.16)
            text('supports','12 pedestals + 6 absorber supports',4.1,-2.89,.15)
            text('mounts','Wall pins: 0.30 m from inner wall',4.1,-3.25,.16)
            text('foot','Dimensions from owner; unspecified hardware and air clearances remain illustrative.',-6.8,-5.0,.16)
        elif view=='section':
            text('title','WISTR | Flow paths & vertical stack',-6.35,4.5,.34)
            text('subtitle','Seated reference; cold-inlet section with hot outlets staggered 30°.',-6.35,4.08,.17)
            rows=[('Hot plenum   1.60 m',(d['hot_plenum_z']+d['top_z'])/2,'#A8791C'),
                  ('Top reflector   0.25 m',(d['top_reflector_z']+d['hot_plenum_z'])/2,'#586B78'),
                  ('Core   3.40 m',(d['core_z']+d['top_reflector_z'])/2,'#8C5B29'),
                  ('Bottom reflector   0.30 m',(d['bottom_reflector_z']+d['core_z'])/2,'#586B78'),
                  ('Bottom plenum   0.75 m',d['bottom_reflector_z']/2,'#47755F')]
            for i,(value,z,color) in enumerate(rows):
                y=z-cam.location.z
                text('layer'+str(i),value,3.85,y/(18/14),.19,color)
            text('inlet','FROM PUMP',2.4,(d['cold_inlet_z']-cam.location.z+.9)/(18/14),.15,'#47755F')
            text('outlet','TO STEAM GENERATORS',-5.45,(d['hot_outlet_z']-cam.location.z+.9)/(18/14),.15,'#A8791C')
            text('air','AIR: down by wall, under vessel, up to return',-6.35,-3.83,.17,'#477FAE')
            text('foot','Pedestals and perforated absorber supports inside and below the vessel. Flow arrows are schematic.',-6.35,-4.55,.145)
        elif view=='plan':
            text('title','WISTR | Six-sector arrangement',-5.15,5.02,.32)
            text('subtitle','Sector 3 moved outward; cap and spider hidden',-5.15,4.56,.17)
            text('size',f'Lower vessel Ø6.2 m  /  upper vessel Ø{2*d["hot_inner_radius"]:.2f} m  /  downcomer 1.0 m',-5.15,-4.38,.18)
            text('tanks','6 hot outlets + 6 cold inlets, staggered by 30°.',-5.15,-4.75,.18)
            text('foot','Triangular through-bores; rows parallel to sector edges. Pitch and bore diameter remain illustrative.',-5.15,-5.15,.135)
        elif view=='cap':
            text('title','WISTR | Segmented cap & spider',-4.5,3.25,.29)
            text('subtitle','Sector 3 cap removed; five remaining pieces lifted for inspection',-4.5,2.85,.16)
            text('foot',f'Spider legs {d["spider_beam_width"]:.3f} m wide; underside webs 15 mm thick × 50 mm high.',-4.5,-3.25,.15)
        elif view=='linkage':
            text('title','WISTR | Sector-mounted separator & paired links',-4.05,2.9,.25)
            text('subtitle','Rounded link ends extend beyond pins; pin holes pass through each link',-4.05,2.52,.14)
            text('foot','Seated reference. Enlarged clevis mounts; wall pins set 0.30 m inward from the wall.',-4.05,-2.95,.13)
        elif view=='maintenance':
            length=b.assemblies[f'reactor.fourbar_{layout.MAINTENANCE["sector"]}']['link_length']
            text('title','WISTR | Sector 3 in maintenance position',-4.05,2.9,.27)
            text('subtitle','Four vertical links; wall mounts fixed; sector, reflectors and separator raised together',-4.05,2.52,.135)
            text('travel',f'Lift and outward travel: {length:.3f} m  /  wall-pin setback: 0.30 m',-4.05,-2.62,.14)
            text('foot','Adjacent vessel wall and other sectors hidden for inspection. Sector 3 cap removed.',-4.05,-2.95,.13)
        elif view=='supports':
            text('title','WISTR | Pedestals & absorber supports',-3.38,2.35,.25)
            text('subtitle','12 columns + 6 perforated, lipped sheets at each level',-3.38,1.98,.15)
            text('upper','Steel: internal supports, 0.75 m high',-3.38,-1.70,.14)
            text('lower','Blue: matching external supports, 0.40 m high',-3.38,-1.96,.14)
            text('clear','Pedestals Ø0.30 m; two beneath each peripheral reflector.',-3.38,-2.25,.14)
            text('foot','Vessel plate, reflector, baffle and well hidden to expose the matching arrangement.',-3.38,-2.52,.115)
        elif view=='support-detail':
            text('title','WISTR | Support detail — one sector',-3.38,2.35,.25)
            text('subtitle','Two Ø0.30 m pedestals and the bordering absorber-support sheets',-3.38,1.98,.14)
            text('rib','Half-tubes: Ø20 mm, at 200 mm pitch on both faces',-3.38,-1.80,.14)
            text('lip','Provisional bearing lips: 200 mm wide × 20 mm thick',-3.38,-2.10,.14)
            text('hole','Provisional passages: Ø100 mm; sheet thickness: 20 mm',-3.38,-2.40,.14)
        elif view=='spider':
            text('title','WISTR | Spider underside',-4.5,3.25,.29)
            text('subtitle',f'Legs {d["spider_beam_width"]:.3f} m wide, sized to clear the raised sector',-4.5,2.85,.16)
            text('web','Welded vertical webs: 15 mm thick × 50 mm high',-4.5,-2.85,.16)
            text('foot','Nominal 30 mm passage clearance at the legs and outer ring; cap hidden.',-4.5,-3.25,.145)
        elif view=='pattern':
            text('title','WISTR | Triangular through-hole pattern',-4.05,2.9,.27)
            text('subtitle','Top reflector, core and bottom reflector share the same hole centres',-4.05,2.52,.15)
            text('pitch','Rows parallel to sector edges; illustrative pitch 85 mm, bore Ø48 mm',-4.05,-2.62,.14)
            text('foot','Reflectors offset for inspection; peripheral reflector and separator hidden.',-4.05,-2.95,.13)


def select_view(b,cameras,cut_objects,view):
    scene=bpy.context.scene;scene.camera=cameras[view]
    visible={
        'air-system':set(b.collections)-{'Flow arrows','Air path arrows'},
        'air-section':set(b.collections)-{'Flow arrows'},
        'cutaway':set(b.collections)-{'Flow arrows'},
        'section':set(b.collections)-{'Cap pieces','Four-bar hardware'},
        'plan':set(b.collections)-{'Cap pieces','Spider','Flow arrows'},
        'cap':{'Cap pieces','Spider','Presentation'},
        'linkage':{'Core sectors','Four-bar hardware','Presentation'},
        'supports':{'Core supports','Vessel supports','Presentation'},
        'maintenance':{'Core sectors','Four-bar hardware','Presentation'},
        'support-detail':{'Core supports','Presentation'},
        'spider':{'Spider','Presentation'},
        'pattern':{'Core sectors','Presentation'},
    }[view]
    if view not in ('air-system','air-section'):
        visible-= {'Air collectors','Air ducts','Air path arrows'}
    for name,col in b.collections.items():
        show=(name in visible and not name.startswith('Labels.')) or name=='Labels.'+view
        # The cutter must stay evaluable even when hidden as an object.
        if name=='Presentation tools':show=True
        col.hide_render=not show;col.hide_viewport=not show
    scene['section_cutaway']=view in ('cutaway','section','air-section')
    scene['maintenance_position']=view not in ('section','linkage','pattern','air-system','air-section')
    bpy.data.objects['study.stage.ground'].hide_render=view=='spider'
    bpy.data.objects['study.stage.ground'].hide_set(view=='spider')
    scene.update_tag()
    scene.frame_set(scene.frame_current)
    for i in range(6):
        obj=b.assemblies[f'reactor.cap_{i+1}']
        a=math.radians(30+i*60)
        obj.location=(.18*math.cos(a),.18*math.sin(a),1.05) if view=='cap' else (0,0,0)
        for category in ('sector','fourbar'):
            root=b.assemblies[f'reactor.{category}_{i+1}']
            isolated=0 if view in ('linkage','pattern') else layout.MAINTENANCE['sector']-1
            hide=view in ('linkage','maintenance','pattern') and i!=isolated
            for child in [root,*root.children_recursive]:
                child.hide_render=hide
                child.hide_set(hide)
                if view=='pattern' and category=='sector' and child.type=='MESH':
                    part=child.name.rsplit('.',1)[-1]
                    child.hide_render=hide or part not in ('core','top_reflector','bottom_reflector')
                    child.hide_set(child.hide_render)
        for part,offset in (('top_reflector',(.45,.60,.45)),('bottom_reflector',(-.55,-.3,-.3))):
            obj=bpy.data.objects[f'reactor.sector_{i+1}.{part}']
            obj.location=offset if view=='pattern' and i==0 else (0,0,0)
    for root in b.assemblies.values():
        if root.get('category')!='Core supports':continue
        keep=root.name in ('reactor.core_support_1','reactor.core_support_2','reactor.core_absorber_support_1','reactor.core_absorber_support_2')
        for obj in (root,*root.children_recursive):
            obj.hide_render=view=='support-detail' and not keep;obj.hide_set(obj.hide_render)
    scene.render.resolution_x,scene.render.resolution_y=(1800,1800) if view=='plan' else (2400,1800)
    bpy.context.view_layer.update()


def check_maintenance(b,d):
    scene=bpy.context.scene;number=layout.MAINTENANCE['sector']
    owner=b.assemblies[f'reactor.sector_{number}']
    hardware=b.assemblies[f'reactor.fourbar_{number}'];length=hardware['link_length']
    links=[o for o in hardware.children if o.get('role')=='fourbar_link']
    fixed_before={o.name:o.matrix_world.translation.copy() for o in hardware.children if o.name.endswith('_wall_pin')}
    for i in range(1,7):
        root=b.assemblies[f'reactor.fourbar_{i}']
        for obj in root.children:
            if obj.name.endswith('_wall_pin'):
                centre=obj.matrix_world.translation
                assert math.isclose(d['vessel_inner_radius']-math.hypot(centre.x,centre.y),layout.PRESENTATION['link_depth'],abs_tol=1e-6)
            if '_wall_cheek_' in obj.name:
                radii=[math.hypot(*(obj.matrix_world @ v.co)[:2]) for v in obj.data.vertices]
                assert max(radii)>d['vessel_inner_radius']
    for raised in (False,True,False,True):
        scene['maintenance_position']=raised;scene.update_tag();bpy.context.view_layer.update()
        assert math.isclose(owner.location.z,length if raised else 0,abs_tol=1e-6)
        assert math.isclose(math.hypot(owner.location.x,owner.location.y),length if raised else 0,abs_tol=1e-6)
        for bar in links:
            name=bar['level']+'_'+bar['side']
            moving=bpy.data.objects[f'reactor.sector_{number}.{name}_moving_pin'].matrix_world.translation
            fixed=bpy.data.objects[f'reactor.fourbar_{number}.{name}_wall_pin'].matrix_world.translation
            actual_moving=bar.matrix_world @ Vector((-length/2,0,0))
            actual_fixed=bar.matrix_world @ Vector((length/2,0,0))
            assert (moving-actual_moving).length<2e-6,(bar.name,'moving',moving,actual_moving)
            assert (fixed-actual_fixed).length<2e-6,(bar.name,'fixed')
            assert math.isclose((moving-fixed).length,length,abs_tol=2e-6)
            if raised:
                assert (Vector((moving.x-fixed.x,moving.y-fixed.y,0))).length<2e-6
                assert moving.z>fixed.z
                # Every corner on the inner face remains outside the reflector.
                inverse=owner.matrix_world.inverted()
                points=[inverse @ (bar.matrix_world @ v.co) for v in bar.data.vertices]
                assert min(math.hypot(v.x,v.y) for v in points)>d['reflector_radius']+.01
        for name,position in fixed_before.items():
            assert (bpy.data.objects[name].matrix_world.translation-position).length<1e-6
        for i in range(1,7):
            cap=bpy.data.objects[f'reactor.cap_{i}.plate']
            assert cap.hide_render==(raised and i==number)
            if i!=number:
                assert b.assemblies[f'reactor.sector_{i}'].location.length<1e-6
    return {'sector':number,'lift_metres':length,'outward_travel_metres':length,
            'wall_pin_setback_metres':layout.PRESENTATION['link_depth'],
            'link_angle_degrees':90,'visible_cap_pieces':5,
            'pose_toggle_checked':True,'full_collision_sweep_performed':False}


def report(b,d,output):
    # Validate the complete physical envelopes, not the presentation section.
    scene=bpy.context.scene
    scene['section_cutaway']=False
    scene['maintenance_position']=False
    scene.update_tag()
    bpy.context.view_layer.update()
    assert math.isclose(d['vessel_inner_radius']*2,6.2)
    assert d['hot_inner_radius']*2<8.2
    assert d['hot_inner_radius']>d['raised_separator_radius']
    assert math.isclose(d['top_z'],6.30)
    assert math.isclose(d['top_reflector_z']-d['core_z'],3.4)
    expected_counts={'Core sectors':6,'Absorber tanks':6,'Cap pieces':6,'Four-bar hardware':6,
                     'Core supports':18,'Vessel supports':18}
    counts={category:sum(obj['category']==category for obj in b.assemblies.values())
            for category in expected_counts}
    assert counts==expected_counts,counts
    for i in range(1,7):
        vertices=bpy.data.objects[f'reactor.sector_{i}.core'].data.vertices
        assert math.isclose(max(math.hypot(v.co.x,v.co.y) for v in vertices),1.8,abs_tol=1e-6)
        assert math.isclose(max(v.co.z for v in vertices)-min(v.co.z for v in vertices),3.4,abs_tol=1e-6)
        top=bpy.data.objects[f'reactor.sector_{i}.top_reflector'].data.vertices
        radial=bpy.data.objects[f'reactor.sector_{i}.radial_reflector'].data.vertices
        assert math.isclose(max(math.hypot(v.co.x,v.co.y) for v in top),d['core_radius'],abs_tol=1e-6)
        assert math.isclose(min(v.co.z for v in top),d['top_reflector_z'],abs_tol=1e-6)
        assert math.isclose(max(v.co.z for v in radial),d['hot_plenum_z'],abs_tol=1e-6)
    separator_count=0
    link_count=0
    for i in range(1,7):
        root=b.assemblies[f'reactor.sector_{i}']
        separator=bpy.data.objects[f'reactor.sector_{i}.separator']
        assert separator.parent==root
        r=(d['reflector_radius']+d['vessel_inner_radius'])/2
        # Object.ray_cast uses object-local coordinates.
        assert separator.ray_cast(Vector((r*math.cos(math.pi/6),r*.5,d['hot_plenum_z']+.2)),Vector((0,0,-1)))[0]
        separator_count+=1
        links=[o for o in b.assemblies[f'reactor.fourbar_{i}'].children if o.get('role')=='fourbar_link']
        assert len(links)==4
        for link in links:
            for axis,value in ((1,.26),(2,.30)):
                extent=max(v.co[axis] for v in link.data.vertices)-min(v.co[axis] for v in link.data.vertices)
                assert math.isclose(extent,value,abs_tol=1e-6),(link.name,axis,extent)
        directions=[Vector(o['fixed_pivot'])-Vector(o['moving_pivot']) for o in links]
        assert all(v.cross(directions[0]).length<1e-6 and math.isclose(v.length,directions[0].length,abs_tol=1e-6) for v in directions)
        for level in ('upper','lower'):
            pair=[o for o in links if o['level']==level]
            assert len(pair)==2
            assert math.isclose(abs(pair[0]['moving_pivot'][1]-pair[1]['moving_pivot'][1]),layout.PRESENTATION['link_pair_spacing'],abs_tol=1e-6)
        link_count+=len(links)
    support_checks=check_supports(b,d,layout)
    air_checks=check_air_system(b,layout,d)
    bore_checks=check_bores(b,d,layout)
    # A translation of the sector must carry its separator and reflector with it.
    root=b.assemblies['reactor.sector_1'];separator=bpy.data.objects['reactor.sector_1.separator']
    reflector=bpy.data.objects['reactor.sector_1.radial_reflector']
    before=[o.matrix_world.translation.copy() for o in (separator,reflector)]
    shift=Vector((.2,.1,.3));root.location+=shift;bpy.context.view_layer.update()
    assert all((o.matrix_world.translation-p-shift).length<1e-6 for o,p in zip((separator,reflector),before))
    root.location-=shift;bpy.context.view_layer.update()
    connections=[o for o in b.assemblies.values() if o.get('connection_type')]
    connection_counts={name:sum(o['connection_type']==name for o in connections) for name in ('hot_outlet','cold_inlet')}
    assert connection_counts=={'hot_outlet':6,'cold_inlet':6}
    # Verify actual shell perforations with local-space ray tests.
    for name in ('reactor.vessel.wall','reactor.baffle.vertical_sheet','reactor.well.wall'):
        obj=bpy.data.objects[name]
        for connection in connections:
            a=math.radians(connection['azimuth_degrees']);direction=Vector((math.cos(a),math.sin(a),0))
            origin=direction*(connection['end_radius']+.3);origin.z=connection['nozzle_z']
            hit=obj.ray_cast(origin,-direction)[0:2]
            # The ray may reach the opposite wall, but must clear the near wall.
            assert not hit[0] or hit[1].dot(direction)<0,(name,connection.name,hit)
    sources={name:hashlib.sha256((ROOT/'references'/name).read_bytes()).hexdigest()
             for name in ('wistr-reactor-1.svg','fourbar-retract.svg','sectors-with-regions.jpg')}
    maintenance=check_maintenance(b,d)
    spider_checks=check_spider_passage(b,d,layout)
    summary={'units':'metres; Z up','core':layout.CORE,'layers':layout.LAYERS,
             'connections':layout.CONNECTIONS,'supports':layout.SUPPORTS,'derived_dimensions':d,
             'presentation_dimensions':layout.PRESENTATION,'counts':counts,
             'connection_counts':connection_counts,'separator_count':separator_count,'link_bar_count':link_count,
             'maintenance':maintenance,'bore_pattern':bore_checks,'spider_passage':spider_checks,'air_system':air_checks,
             'source_sha256':sources,'assumptions':layout.ASSUMPTIONS,
             'checks':['Six sectors, tanks, cap pieces and four-bar assemblies; twelve pedestals and six sheets per level',
                       'Core mesh radii and heights checked against supplied dimensions',
                       f'6.2 m lower and {2*d["hot_inner_radius"]:.3f} m upper inside diameters; 6.30 m internal height',
                       'Top reflector seats directly on the core inside the peripheral reflector',
                       'Six separator pieces are attached to their sectors and move with the reflectors',
                       'Four equal-length parallel bars per sector, each 0.26 by 0.30 m in cross-section',
                       'Wall-pin centres 0.30 m inward from vessel inner surface; paired clevis mounts reach the wall',
                       'Maintenance sector translates upward and outward; all four link holes remain concentric with their pins',
                       'Four links stand vertical; reflector clears the links; wall pins stay fixed; selected cap is hidden',
                       'Triangular bores align through the core and both reflectors; all perforated meshes are closed',
                       'Links extend past each pin and contain clear through-holes for the pins',
                       'Raised sector and attached lugs fit vertically between spider legs, hub and ring with 30 mm nominal clearance',
                       'Each spider leg has an attached 15 mm by 50 mm underside web',
                       'Six hot and six cold nozzle ray checks pass through vessel, baffle and well',
                       'Stepped vessel, baffle and well remain closed meshes after the viewing cut']+support_checks,
             'installation_modified':False}
    scene['section_cutaway']=True
    scene.update_tag()
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    for name in ('reactor.well.wall','reactor.vessel.wall','reactor.baffle.vertical_sheet'):
        bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].evaluated_get(dg).data)
        open_edges=sum(not edge.is_manifold for edge in bm.edges)
        bm.free()
        assert open_edges==0,(name,open_edges)
    (output/'reactor-study-report.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft',action='store_true')
    views=['air-system','air-section','cutaway','section','plan','cap','linkage','supports','maintenance','support-detail','spider','pattern']
    parser.add_argument('--views',nargs='+',choices=views,default=views)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output=ROOT/'outputs/reactor-study';output.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    b=SceneBuilder();d,cut_objects=build_reactor(b,layout)
    cameras=presentation(b,d);annotations(b,cameras,d)
    summary=report(b,d,output)
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16 if args.draft else 48
    scene.cycles.use_denoising=True;scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0
    scene.render.resolution_percentage=50 if args.draft else 100
    select_view(b,cameras,cut_objects,'air-section')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.color_type='MATERIAL'
    if not args.draft:bpy.ops.wm.save_as_mainfile(filepath=str(output/'wistr-reactor-study.blend'))
    for view in args.views:
        select_view(b,cameras,cut_objects,view)
        scene.render.filepath=str(output/f'reactor-{view}{"-draft" if args.draft else ""}.png')
        bpy.ops.render.render(write_still=True)
    select_view(b,cameras,cut_objects,'air-section')
    if not args.draft:bpy.ops.wm.save_as_mainfile(filepath=str(output/'wistr-reactor-study.blend'))
    print('REACTOR_STUDY_OK '+json.dumps(summary['counts']))


if __name__=='__main__':main()
