"""Named static reactor geometry, derived from the owner's dimensional sketch."""
import math
import bpy
import bmesh
from mathutils import Vector
from .perforated import perforated_prism


def xy(r, angle):
    a=math.radians(angle)
    return r*math.cos(a),r*math.sin(a)


def stepped_shell(b,name,root,lower,upper,bottom,step,top,thickness,mat):
    """Revolve one closed profile; the shoulder and walls share one mesh."""
    profile=[(lower,bottom),(lower,step),(upper,step),(upper,top),
             (upper+thickness,top),(upper+thickness,step-thickness),
             (lower+thickness,step-thickness),(lower+thickness,bottom)]
    n=128; m=len(profile)
    vertices=[(*xy(r,i*360/n),z) for i in range(n) for r,z in profile]
    faces=[(i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m)
           for i in range(n) for j in range(m)]
    obj=b.mesh(name,root,vertices,faces,mat)
    # Flat faces prevent Boolean section caps inheriting cylindrical shading.
    # 128 radial segments keep the complete shells visually round.
    return obj


def sector_outline(inner,outer,gap):
    outline=[]
    for r,reverse in ((outer,False),(inner,True)):
        offset=math.asin(min(gap/r,.99))
        angles=[offset+(math.pi/3-2*offset)*i/40 for i in range(41)]
        if reverse: angles.reverse()
        outline.extend((r*math.cos(a),r*math.sin(a)) for a in angles)
    return outline


def sector(b, name, root, inner, outer, bottom, top, gap, mat):
    """60-degree annular sector, with constant-width space at its radial edges."""
    outline=sector_outline(inner,outer,gap)
    n=len(outline)
    verts=[(x,y,z) for z in (bottom,top) for x,y in outline]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return b.mesh(name,root,verts,faces,mat)


def palette(b):
    for name,color,metal,rough in [
        ('steel','#798992',.45,.35),('reflector','#ABB4B8',.35,.4),
        ('top_reflector','#C0C9CB',.35,.4),
        ('vessel','#4D7087',.4,.32),('cut_steel','#B0C2CB',.35,.35),
        ('core','#B98143',.12,.45),('absorber','#37656A',.25,.4),
        ('hot','#C99A32',.18,.38),('cold','#568C71',.18,.4),
        ('air','#477FAE',.12,.4),('baffle','#78A8B8',.5,.3),
        ('dark','#253C48',.2,.5),('concrete','#B7B4AB',0,.8),
        ('floor','#D7D4CB',0,.7),('background','#EEEFEA',0,.8),
        ('cap','#71828B',.45,.36),('links','#BAC4C9',.6,.28),
    ]:
        b.material(name,color,metallic=metal,roughness=rough,concrete=name=='concrete')


def build_core(b,layout,d):
    p=layout.PRESENTATION;l=layout.LAYERS
    gap=p['absorber_tank_width']/2+.008
    holes=[(x,y,p['tube_pattern_radius']) for x,y in layout.hole_centres()]
    for i in range(6):
        root=b.assembly(f'reactor.sector_{i+1}','Core sectors',angle=i*60)
        for name,radius,bottom,top,material in (
            ('core',d['core_radius'],d['core_z'],d['top_reflector_z'],'core'),
            ('bottom_reflector',d['reflector_radius'],d['bottom_reflector_z'],d['core_z'],'reflector'),
            ('top_reflector',d['core_radius'],d['top_reflector_z'],d['hot_plenum_z'],'top_reflector'),
        ):
            obj=perforated_prism(b,name,root,sector_outline(p['central_clearance_radius'],radius,gap),
                                holes,bottom,top,material)
            obj['hole_pattern']='triangular; rows parallel to sector edges'
        sector(b,'radial_reflector',root,d['core_radius'],d['reflector_radius'],
               d['core_z'],d['hot_plenum_z'],gap,'reflector')
        separator=sector(b,'separator',root,d['reflector_radius'],d['vessel_inner_radius'],
                         d['hot_plenum_z']-p['downcomer_roof_thickness'],d['hot_plenum_z'],.002,'reflector')
        separator['role']='sector_separator'
        tank=b.assembly(f'reactor.absorber_{i+1}','Absorber tanks',angle=i*60)
        start=.10; end=d['reflector_radius']; height=d['hot_plenum_z']-d['bottom_reflector_z']
        b.box('rectangular_tank',tank,(end-start,p['absorber_tank_width'],height),
              ((start+end)/2,0,(d['hot_plenum_z']+d['bottom_reflector_z'])/2),'absorber')


def build_supports(b,layout,d):
    p=layout.PRESENTATION;s=layout.SUPPORTS
    inner=s['central_clear_diameter']/2;outer=d['reflector_radius']
    for i in range(s['count']):
        angle=s['angle_offset']+i*360/s['count']
        for name,category,bottom,top,material in (
            ('core_support','Core supports',0,d['bottom_reflector_z'],'steel'),
            ('vessel_support','Vessel supports',d['floor_z'],-p['vessel_bottom'],'vessel'),
        ):
            root=b.assembly(f'reactor.{name}_{i+1}',category,angle=angle)
            root['azimuth_degrees']=angle;root['sector_number']=i//2+1
            root['support_kind']='pedestal'
            column=b.cylinder('pedestal',root,s['pedestal_diameter']/2,top-bottom,
                              ((d['core_radius']+outer)/2,0,(bottom+top)/2),material,vertices=48,bevel=0)
            column['diameter']=s['pedestal_diameter']
    for i in range(6):
        for name,category,bottom,top,material in (
            ('core_absorber_support','Core supports',0,d['bottom_reflector_z'],'steel'),
            ('vessel_absorber_support','Vessel supports',d['floor_z'],-p['vessel_bottom'],'vessel'),
        ):
            root=b.assembly(f'reactor.{name}_{i+1}',category,angle=i*60)
            root['support_kind']='absorber_sheet';root['azimuth_degrees']=i*60
            web_top=top-s['lip_thickness'];height=web_top-bottom
            xs=[inner+.20+j*s['stiffener_pitch'] for j in range(9)]
            holes=[(x,bottom+height*f,s['passage_diameter']/2) for x in xs for f in (1/3,2/3)]
            perforated_prism(b,'perforated_sheet',root,[(inner,bottom),(outer,bottom),(outer,web_top),(inner,web_top)],
                            holes,-s['wall_thickness']/2,s['wall_thickness']/2,material,axis='Y')
            b.box('bearing_lip',root,(outer-inner,s['lip_width'],s['lip_thickness']),
                  ((inner+outer)/2,0,top-s['lip_thickness']/2),material)
            half_tube_stiffeners(b,root,layout,inner,bottom,web_top,material)


def half_tube_stiffeners(b,root,layout,inner,bottom,top,mat):
    s=layout.SUPPORTS;radius=s['stiffener_diameter']/2
    vertices=[];faces=[]
    for side in (-1,1):
        for j in range(10):
            x=inner+.10+j*s['stiffener_pitch'];cy=side*s['wall_thickness']/2
            outline=[]
            for r,reverse in ((radius,False),(radius-s['stiffener_wall'],True)):
                angles=[i*math.pi/12 for i in range(13)]
                if reverse:angles.reverse()
                outline.extend((x+r*math.cos(a),cy+side*r*math.sin(a)) for a in angles)
            start=len(vertices);n=len(outline)
            vertices.extend((u,v,z) for z in (bottom,top) for u,v in outline)
            faces.extend([tuple(start+i for i in reversed(range(n))),tuple(start+n+i for i in range(n))])
            faces.extend((start+i,start+(i+1)%n,start+(i+1)%n+n,start+i+n) for i in range(n))
    ribs=b.mesh('welded_half_tube_stiffeners',root,vertices,faces,mat)
    ribs['outside_diameter']=s['stiffener_diameter'];ribs['pitch']=s['stiffener_pitch']
    ribs['count']=20;ribs['attachment']='split edges meet the sheet on both faces; welded'


def build_well(b,layout,d):
    p=layout.PRESENTATION
    root=b.assembly('reactor.well','Concrete well')
    stepped_shell(b,'wall',root,d['well_inner_radius'],d['hot_well_inner_radius'],
                  d['floor_z'],d['well_step_z'],d['top_z']+.12,p['well_wall'],'concrete')
    b.cylinder('floor',root,d['well_outer_radius'],p['well_floor'],
               (0,0,d['floor_z']-p['well_floor']/2),'concrete',vertices=128,bevel=0)
    root=b.assembly('reactor.baffle','Cooling air baffle')
    stepped_shell(b,'vertical_sheet',root,d['baffle_inner_radius'],d['hot_baffle_inner_radius'],
                  p['baffle_bottom_z'],d['baffle_step_z'],d['top_z']+.08,p['baffle_thickness'],'baffle')
    plate=b.annulus('floor_sheet',root,p['baffle_turn_opening_radius'],d['baffle_inner_radius'],
                    p['baffle_bottom_z'],p['baffle_bottom_z']+p['baffle_thickness'],'baffle')
    inner=layout.SUPPORTS['central_clear_diameter']/2;outer=d['reflector_radius']
    for i in range(layout.SUPPORTS['count']):
        angle=layout.SUPPORTS['angle_offset']+i*360/layout.SUPPORTS['count']
        x,y=xy((inner+outer)/2,angle)
        x,y=xy((d['core_radius']+outer)/2,angle)
        cutter=b.cylinder(f'pedestal_clearance_{i}',root,layout.SUPPORTS['pedestal_diameter']/2+.003,.2,
                          (x,y,p['baffle_bottom_z']),None,vertices=48,bevel=0)
        b.cut(plate,cutter)
    for i in range(6):
        x,y=xy((inner+outer)/2,i*60)
        width=layout.SUPPORTS['wall_thickness']+layout.SUPPORTS['stiffener_diameter']+.004
        cutter=b.box(f'sheet_clearance_{i}',root,(outer-inner+.01,width,.2),(x,y,p['baffle_bottom_z']),None)
        cutter.rotation_euler.z=math.radians(i*60);b.cut(plate,cutter)


def horizontal_pipe(b,name,root,radius,x1,x2,z,mat):
    # Open mouths keep the pipe envelope visibly different from a solid rod.
    pipe=b.annulus(name,root,radius-.035,radius,0,abs(x2-x1),mat,steps=64)
    pipe.location=(x1,0,z)
    pipe.rotation_euler.y=math.pi/2 if x2>x1 else -math.pi/2
    return pipe


def build_vessel(b,layout,d):
    p=layout.PRESENTATION
    root=b.assembly('reactor.vessel','Vessel')
    wall=stepped_shell(b,'wall',root,d['vessel_inner_radius'],d['hot_inner_radius'],
                       0,d['hot_plenum_z'],d['top_z'],p['vessel_wall'],'vessel')
    b.cylinder('bottom_plate',root,d['vessel_outer_radius'],p['vessel_bottom'],
               (0,0,-p['vessel_bottom']/2),'vessel',vertices=128,bevel=0)
    b.annulus('top_flange',root,d['hot_outer_radius'],d['hot_outer_radius']+.12,
              d['top_z']-.10,d['top_z'],'cut_steel')
    pipe_radius=layout.CONNECTIONS['pipe_diameter']/2
    for name,z,mat,radius,offset in [
            ('cold_inlet',d['cold_inlet_z'],'cold',d['vessel_inner_radius'],layout.CONNECTIONS['cold_angle_offset']),
            ('hot_outlet',d['hot_outlet_z'],'hot',d['hot_inner_radius'],layout.CONNECTIONS['hot_angle_offset'])]:
        for i in range(layout.CONNECTIONS['count_per_level']):
            angle=offset+i*360/layout.CONNECTIONS['count_per_level']
            root=b.assembly(f'reactor.{name}_{i+1}','Side connections',angle=angle)
            root['connection_type']=name;root['diameter']=layout.CONNECTIONS['pipe_diameter']
            root['azimuth_degrees']=angle;root['nozzle_z']=z
            end=d['pipe_end_radius']+(.35 if name=='cold_inlet' else 0)
            root['end_radius']=end
            horizontal_pipe(b,'pipe',root,pipe_radius,radius-.01,end,z,mat)
            for target in (wall,bpy.data.objects['reactor.baffle.vertical_sheet'],bpy.data.objects['reactor.well.wall']):
                centre=(radius+end)/2
                cutter=b.cylinder('opening_cutter',root,pipe_radius+.005,end-radius+.4,
                                  (centre,0,z),None,vertices=64,bevel=0)
                cutter.rotation_euler.y=math.pi/2
                b.cut(target,cutter)
            flange=b.annulus('end_flange',root,pipe_radius,pipe_radius+.11,0,.09,'steel',steps=64)
            flange.location=(end-.10,0,z);flange.rotation_euler.y=math.pi/2


def build_separator_supports(b,layout,d):
    root=b.assembly('reactor.separator_supports','Separator supports')
    seat=d['separator_seat_z']
    ring=b.annulus('wall_ledge',root,d['ledge_inner_radius'],d['vessel_inner_radius'],
                   seat-d['ledge_height'],seat,'steel')
    ring['radial_projection']=d['ledge_width'];ring['height']=d['ledge_height']
    ring['attachment']='fixed to vessel; separator bears on upper face'
    # Embed 10 mm into the wall so rectangular ends meet the curved shell.
    start=d['reflector_radius'];end=d['vessel_inner_radius']+.01
    for i in range(6):
        for level,z in zip(('bottom','middle','top'),d['absorber_brace_centres']):
            x,y=xy((start+end)/2,i*60)
            brace=b.box(f'absorber_{i+1}_{level}',root,
                        (end-start,d['absorber_brace_width'],layout.SEPARATOR_SUPPORTS['radial_height']),
                        (x,y,z),'steel')
            brace.rotation_euler.z=math.radians(i*60)
            brace['level']=level;brace['absorber_number']=i+1
            brace['attachment']='fixed between absorber outer end and vessel wall'


def build_cap(b,layout,d):
    p=layout.PRESENTATION
    root=b.assembly('reactor.spider','Spider')
    b.annulus('outer_ring',root,d['cap_opening_radius'],d['hot_outer_radius']+.12,
              d['top_z'],d['top_z']+.15,'steel')
    hub=[(*xy(d['spider_hub_radius'],30+i*60),z) for z in (d['top_z'],d['top_z']+.15) for i in range(6)]
    b.mesh('hub',root,hub,[tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)],'steel')
    for i in range(6):
        a=i*60;start=d['spider_hub_radius']*math.cos(math.pi/6);end=d['cap_opening_radius']
        x,y=xy((start+end)/2,a)
        beam=b.box(f'arm_{i+1}',root,(end-start,d['spider_beam_width'],p['spider_beam_depth']),
                   (x,y,d['top_z']+p['spider_beam_depth']/2),'steel',.012)
        beam.rotation_euler.z=math.radians(a)
        web=b.box(f'underside_web_{i+1}',root,(end-start,p['spider_web_thickness'],p['spider_web_height']),
                  (x,y,d['top_z']-p['spider_web_height']/2),'steel')
        web.rotation_euler.z=math.radians(a)
        web['attachment']='welded vertically to the underside centre line of spider arm'
        cap=b.assembly(f'reactor.cap_{i+1}','Cap pieces',angle=a)
        sector(b,'plate',cap,.22,d['cap_opening_radius']+.015,
               d['top_z']+.15,d['top_z']+.15+p['cap_thickness'],.02,'cap')
        for r in (d['cap_opening_radius']*.3,d['cap_opening_radius']*.72):
            x,y=xy(r,30)
            b.box(f'lifting_lug_{r}',cap,(.12,.22,.14),(x,y,d['top_z']+.15+p['cap_thickness']+.07),'links',.01)
    for i in range(6):
        root=b.assembly(f'reactor.fourbar_{i+1}','Four-bar hardware',angle=30+i*60)
        owner=b.assemblies[f'reactor.sector_{i+1}']
        half_spacing=p['link_pair_spacing']/2
        # The upright link's depth lies radially. Allow its inner corner to
        # clear the curved reflector, while retaining parallel hinge axes.
        moving=layout.linkage_dimensions()['moving'];fixed=layout.linkage_dimensions()['fixed']
        root['link_length']=fixed-moving
        root['wall_pin_setback']=p['link_depth']
        def in_sector(x,y,z):
            return (x*math.cos(math.pi/6)-y*.5,x*.5+y*math.cos(math.pi/6),z)
        for level in ('lower','upper'):
            z=d['core_z']+p[f'link_{level}_above_core_base']
            for side,y in (('a',-half_spacing),('b',half_spacing)):
                name=level+'_'+side
                length=fixed-moving;end_radius=p['link_depth']/2
                outline=[(length/2+end_radius*math.cos(-math.pi/2+j*math.pi/16),end_radius*math.sin(-math.pi/2+j*math.pi/16)) for j in range(17)]
                outline.extend((-length/2+end_radius*math.cos(math.pi/2+j*math.pi/16),end_radius*math.sin(math.pi/2+j*math.pi/16)) for j in range(17))
                holes=[(x,0,p['pin_radius']+p['pin_hole_clearance']) for x in (-length/2,length/2)]
                bar=perforated_prism(b,name+'_link',root,outline,holes,-p['link_width']/2,p['link_width']/2,
                                    'links',axis='Y',segments=32,position=((moving+fixed)/2,y,z))
                bar['pin_overhang']=end_radius
                bar['role']='fourbar_link';bar['level']=level;bar['side']=side
                bar['moving_pivot']=(moving,y,z);bar['fixed_pivot']=(fixed,y,z)
                pin_half=p['link_width']/2+.09
                b.beam(name+'_wall_pin',root,(fixed,y-pin_half,z),(fixed,y+pin_half,z),.075,'dark')
                # Paired cheeks leave room for the link to rotate between them.
                cheek_width=.045; cheek_offset=p['link_width']/2+.01+cheek_width/2
                for cheek,sign in (('a',-1),('b',1)):
                    cy=y+sign*cheek_offset
                    end=math.sqrt((d['vessel_inner_radius']+.025)**2-(abs(cy)+cheek_width/2)**2)
                    start=fixed-.11
                    b.box(name+'_wall_cheek_'+cheek,root,(end-start,cheek_width,p['link_depth']+.02),
                          ((start+end)/2,cy,z),'steel',.008)
                a1=math.degrees(math.asin((y-.24)/d['vessel_inner_radius']))
                a2=math.degrees(math.asin((y+.24)/d['vessel_inner_radius']))
                b.annulus(name+'_wall_backplate',root,d['vessel_inner_radius']-.05,d['vessel_inner_radius']+.025,
                          z-.26,z+.26,'steel',start=a1,end=a2,steps=12)
                b.beam(name+'_moving_pin',owner,in_sector(moving,y-pin_half,z),in_sector(moving,y+pin_half,z),.075,'dark')
                for cheek,sign in (('a',-1),('b',1)):
                    cy=y+sign*cheek_offset
                    start=math.sqrt(d['reflector_radius']**2-cy**2)-.03
                    end=moving+.11
                    lug=b.box(name+'_moving_cheek_'+cheek,owner,(end-start,cheek_width,p['link_depth']),
                              in_sector((start+end)/2,cy,z),'steel',.008)
                    lug.rotation_euler.z=math.pi/6


def pose_driver(obj,path,index,expression):
    curve=obj.driver_add(path) if index is None else obj.driver_add(path,index)
    driver=curve.driver
    variable=driver.variables.new();variable.name='raised';variable.type='SINGLE_PROP'
    variable.targets[0].id_type='SCENE';variable.targets[0].id=bpy.context.scene
    variable.targets[0].data_path='["maintenance_position"]'
    if path in ('hide_render','hide_viewport'):
        variable=driver.variables.new();variable.name='detail';variable.type='SINGLE_PROP'
        variable.targets[0].id_type='SCENE';variable.targets[0].id=bpy.context.scene
        variable.targets[0].data_path='["core_tube_detail_view"]'
        expression='('+expression+') or detail'
    driver.expression=expression


def build_maintenance_pose(b,layout):
    scene=bpy.context.scene;scene['maintenance_position']=layout.MAINTENANCE['enabled']
    scene.id_properties_ui('maintenance_position').update(description='Raise sector 3, stand its four links vertical and remove its cap; turn off to reseat it.')
    number=layout.MAINTENANCE['sector']
    sector_root=b.assemblies[f'reactor.sector_{number}']
    hardware=b.assemblies[f'reactor.fourbar_{number}']
    length=hardware['link_length'];angle=hardware.rotation_euler.z
    for axis,delta in enumerate((length*math.cos(angle),length*math.sin(angle),length)):
        pose_driver(sector_root,'location',axis,f'raised*{delta!r}')
    for bar in hardware.children:
        if bar.get('role')!='fourbar_link':continue
        moving=Vector(bar['moving_pivot']);fixed=Vector(bar['fixed_pivot'])
        pose_driver(bar,'location',0,f'{(moving.x+fixed.x)/2!r}+raised*{length/2!r}')
        pose_driver(bar,'location',2,f'{fixed.z!r}+raised*{length/2!r}')
        pose_driver(bar,'rotation_euler',1,f'raised*{math.pi/2!r}')
    cap=b.assemblies[f'reactor.cap_{number}']
    for obj in (cap,*cap.children_recursive):
        pose_driver(obj,'hide_render',None,'raised')
        pose_driver(obj,'hide_viewport',None,'raised')
    scene.update_tag();bpy.context.view_layer.update()


def arrow(b,name,root,points,mat,radius=.035):
    b.tube(name,root,points,radius,mat)
    end=Vector(points[-1]);direction=(end-Vector(points[-2])).normalized()
    bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=radius*2.7,radius2=0,depth=radius*6,
                                   location=end-direction*radius*3)
    obj=b.finish(bpy.context.object,name+'.head',root,mat,tuple(end-direction*radius*3))
    obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(direction)


def build_flow(b,layout,d):
    root=b.assembly('reactor.flow','Flow arrows');y=-.10
    down=(d['reflector_radius']+d['vessel_inner_radius'])/2
    end=d['pipe_end_radius']-.15
    # Foreground paths are diagrammatic, and sit just forward of the section plane.
    arrow(b,'cold_entry',root,[(end,y,d['cold_inlet_z']),(down,y,d['cold_inlet_z'])],'cold',.045)
    bottom_mid=layout.LAYERS['bottom_plenum']/2
    arrow(b,'downcomer',root,[(down,y,d['cold_inlet_z']-.3),(down,y,bottom_mid+.2)],'cold',.042)
    arrow(b,'bottom_turn',root,[(down,y,bottom_mid),(.9,y,bottom_mid),(.5,y,bottom_mid),
                               (.5,y,d['bottom_reflector_z']+.15)],'cold',.035)
    for i,x in enumerate((-.8,.8)):
        arrow(b,f'core_up_{i}',root,[(x,y,d['core_z']+.15),(x,y,d['top_reflector_z']-.25)],'hot',.035)
    arrow(b,'to_hot_plenum',root,[(-.8,y,d['top_reflector_z']+.03),(-.8,y,d['hot_plenum_z']+.4)],'hot',.045)
    # Follow the second hot outlet; its azimuth derives from the connection layout.
    hot_angle=layout.CONNECTIONS['hot_angle_offset']+360/layout.CONNECTIONS['count_per_level']
    hx,hy=xy(end,hot_angle)
    arrow(b,'hot_exit',root,[(0,0,d['hot_outlet_z']),(hx,hy,d['hot_outlet_z'])],'hot',.045)
    outer=(d['baffle_outer_radius']+d['well_inner_radius'])/2
    inner=(d['vessel_outer_radius']+d['baffle_inner_radius'])/2
    outer_upper=(d['hot_baffle_outer_radius']+d['hot_well_inner_radius'])/2
    inner_upper=(d['hot_outer_radius']+d['hot_baffle_inner_radius'])/2
    outer_step=(d['baffle_step_z']-layout.PRESENTATION['baffle_thickness']+d['well_step_z'])/2
    inner_step=(d['hot_plenum_z']-layout.PRESENTATION['vessel_wall']+d['baffle_step_z'])/2
    arrow(b,'air_down',root,[(-outer_upper,y,d['top_z']-.25),(-outer_upper,y,outer_step),(-outer,y,outer_step),
                           (-outer,y,-.38),(-.5,y,-.38),(-.5,y,-.16)],'air',.027)
    arrow(b,'air_return',root,[(-.75,y,-.15),(-inner,y,-.15),(-inner,y,inner_step),
                             (-inner_upper,y,inner_step),(-inner_upper,y,d['top_z']-.25)],'air',.027)


def add_cutaway(b):
    scene=bpy.context.scene
    scene['section_cutaway']=True
    scene.id_properties_ui('section_cutaway').update(description='Turn off to restore the complete reactor and well geometry.')
    root=b.assembly('study.section_tool','Presentation tools')
    # Place the section just behind the two absorber tanks that lie on Y=0,
    # so they do not conceal the core's section face. Full geometry is retained.
    cutter=b.box('front_half',root,(30,15,30),(0,-7.44,5),None)
    cutter.hide_render=True;cutter.display_type='WIRE';cutter.hide_set(True)
    cut_objects=[]
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or obj==cutter or obj.users_collection[0].name in ('Flow arrows','Air path arrows','Presentation','Presentation tools'):
            continue
        if obj.name in ('reactor.well.wall','reactor.vessel.wall','reactor.baffle.vertical_sheet'):
            # Triangulated closed profiles support the Manifold Boolean solver.
            bm=bmesh.new();bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm,faces=list(bm.faces))
            bm.to_mesh(obj.data);bm.free();obj.data.update()
        mod=obj.modifiers.new('Study cutaway — disable for complete object','BOOLEAN')
        mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        if obj.name in ('reactor.well.wall','reactor.vessel.wall','reactor.baffle.vertical_sheet'):
            mod.solver='MANIFOLD'
        for prop in ('show_viewport','show_render'):
            driver=mod.driver_add(prop).driver
            variable=driver.variables.new();variable.name='enabled';variable.type='SINGLE_PROP'
            variable.targets[0].id_type='SCENE';variable.targets[0].id=scene
            variable.targets[0].data_path='["section_cutaway"]'
            driver.expression='enabled'
        cut_objects.append(obj)
    return cut_objects


def build_reactor(b,layout):
    from .reactor_air import build_air_system
    from .reactor_tubing import build_absorber_tubing, build_core_tubing
    d=layout.dimensions()
    palette(b);build_core(b,layout,d);build_supports(b,layout,d);build_well(b,layout,d)
    build_vessel(b,layout,d);build_separator_supports(b,layout,d);build_cap(b,layout,d);build_flow(b,layout,d)
    build_core_tubing(b,layout,d)
    build_maintenance_pose(b,layout)
    build_absorber_tubing(b,layout,d)
    build_air_system(b,layout,d)
    return d,add_cutaway(b)
