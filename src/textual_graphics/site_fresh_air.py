"""Relocate the draft fresh-air plenum inside the composed reactor building.

The source installation is retained. The composed site uses an internal header,
complete wall columns, three outdoor intakes and centered generator valve boxes.
"""
import math
import bpy
from mathutils import Vector
from .installation_air import polar
from .installation_piping import fillet_path
from .installation_clearance import bounds, gapbox, segment_box, segdist


def outer_radius(theta,cfg,recesses):
    value=cfg['outer_radius']
    for q in recesses:
        d=abs((theta-q['angle']+180)%360-180)
        if d>=3.5:continue
        blend=0 if d<=1.25 else (1-math.cos(math.pi*(d-1.25)/2.25))/2
        value=min(value,q['radius']+(cfg['outer_radius']-q['radius'])*blend)
    return value



def inner_radius(theta,cfg,recesses):
    # Keep the inner face clear of the insulated coolant tank at the 340° pier.
    # This local outer-wall pocket reduces area; it is recorded in the report.
    return outer_radius(theta,cfg,[q for q in recesses if round(q['angle'])!=340])-cfg['clear_width']-2*cfg['wall']


def complete_columns(b):
    shell=bpy.data.objects['building.shell']
    ref=bpy.data.objects['building.shell.pilaster0']
    for angle in range(200,360,20):
        ob=ref.copy();ob.data=ref.data.copy();ob.name='building.shell.pilaster'+str(angle)
        shell.users_collection[0].objects.link(ob)
        ob.location.x,ob.location.y,_=polar(math.hypot(ref.location.x,ref.location.y),angle,0)
        ob['role']='Full-circumference draft wall column; front wall cut away'
    col=b.collection('Building columns')
    for ob in list(bpy.data.objects):
        if ob.name.startswith('building.shell.pilaster'):
            for previous in list(ob.users_collection):previous.objects.unlink(ob)
            col.objects.link(ob)


def build_fresh_air(b,site,installation,source):
    visibility=[(o,o.hide_viewport) for o in [*bpy.data.collections,*bpy.data.objects]]
    for o,_ in visibility:o.hide_viewport=False
    bpy.context.view_layer.update()
    complete_columns(b)
    cfg=site.FRESH_AIR;floor=site.PAD_Z;wall=cfg['wall'];width=cfg['clear_width']+2*wall
    low=floor+cfg['base_height'];high=low+cfg['clear_height']+2*wall
    old=[o for o in bpy.data.objects if o.name.startswith('connections.air.fresh_plenum.')]
    cutters={m.object for o in old for m in o.modifiers if m.type=='BOOLEAN' and m.object}
    for o in bpy.data.objects:
        for m in list(o.modifiers):
            if m.type=='BOOLEAN' and m.object in cutters:o.modifiers.remove(m)
    for o in old+list(cutters):bpy.data.objects.remove(o,do_unlink=True)
    root=b.assembly('site.fresh_air','Internal fresh-air duct')
    b.material('fresh_duct','#789FAA',metallic=.45,roughness=.38)
    bpy.context.view_layer.update()
    recesses=[]
    for o in bpy.data.objects:
        if not o.name.startswith('building.shell.pilaster') or o.type!='MESH':continue
        pts=[o.matrix_world@Vector(v.co) for v in o.data.vertices]
        centre=sum(pts,Vector())/len(pts)
        recesses.append(dict(column=o.name,angle=math.degrees(math.atan2(centre.y,centre.x))%360,
            radius=min(math.hypot(p.x,p.y) for p in pts)-.06))
    # The inherited hot header also occupied the wall-column envelopes.
    # Recess its sealed outer edge, retaining the existing layer thicknesses
    # and branch connections; the unobstructed inner edge stays fixed.
    spec=installation.AIR['insulation']
    hot_outer=(installation.AIR['hot_radius']+installation.AIR['hot_clear_width']/2
        +spec['branch_wall']+spec['thickness']+spec['cladding'])
    hot_cfg=dict(cfg,outer_radius=hot_outer)
    hot_vertices=0
    for ob in bpy.data.objects:
        if ob.type!='MESH' or not ob.get('hot_header_part'):continue
        inv=ob.matrix_world.inverted()
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co;r=math.hypot(p.x,p.y)
            if r<installation.AIR['hot_radius']+.9:continue
            theta=math.degrees(math.atan2(p.y,p.x))%360
            delta=hot_outer-outer_radius(theta,hot_cfg,recesses)
            if delta>0:
                v.co=inv@Vector((p.x*(r-delta)/r,p.y*(r-delta)/r,p.z));hot_vertices+=1
        ob.data.update()
    inner_min=min(q['radius'] for q in recesses)-width
    half_gap=math.degrees(math.asin(installation.ACCESS['ring_gap_width']/2/inner_min))
    gap=(installation.ACCESS['angle']-half_gap,installation.ACCESS['angle']+half_gap)
    parts=[]
    def strip(name,start,end,part):
        n=max(2,math.ceil((end-start)/.4));verts=[];faces=[]
        for i in range(n+1):
            angle=start+(end-start)*i/n;ro=outer_radius(angle,cfg,recesses);ri=inner_radius(angle,cfg,recesses)
            if part=='floor':a,c,z0,z1=ri,ro,low,low+wall
            elif part=='roof':a,c,z0,z1=ri,ro,high-wall,high
            elif part=='inner':a,c,z0,z1=ri,ri+wall,low+wall,high-wall
            else:a,c,z0,z1=ro-wall,ro,low+wall,high-wall
            verts.extend(polar(r,angle,z) for r,z in [(a,z0),(c,z0),(c,z1),(a,z1)])
        for i in range(n):
            a=i*4
            for j in range(4):faces.append((a+j,a+(j+1)%4,a+(j+1)%4+4,a+j+4))
        faces.extend([(3,2,1,0),tuple(4*n+j for j in range(4))])
        ob=b.mesh(name,root,verts,faces,'fresh_duct');ob['air_plenum_part']=True;ob['air_plenum_service']='fresh'
        ob['air_plenum_lid']=part=='roof';ob['fresh_header_part']=part
        parts.append(ob);return ob
    # Two sealed ends flank the unchanged equipment-door approach.
    for start,end in [(0,gap[0]),(gap[1],180),(180,360)]:
        for part in ('floor','roof','inner','outer'):strip(f'{part}.{start}',start,end,part)
    for index,a in enumerate(gap):
        ro=outer_radius(a,cfg,recesses);ri=inner_radius(a,cfg,recesses)
        ob=b.box(f'door_end_{index}',root,(ro-ri,wall,high-low),polar((ri+ro)/2,a,(low+high)/2),'fresh_duct')
        ob.rotation_euler.z=math.radians(a);ob['fresh_header_part']='end';parts.append(ob)
    # Simple bearing strips, a visual support allowance rather than load sizing.
    for angle in range(0,360,15):
        if gap[0]-1<angle<gap[1]+1:continue
        ro=outer_radius(angle,cfg,recesses);ri=inner_radius(angle,cfg,recesses);ob=b.box('bearing_'+str(angle),root,(ro-ri,.12,cfg['base_height']),
            polar((ro+ri)/2,angle,floor+cfg['base_height']/2),'rail')
        ob.rotation_euler.z=math.radians(angle)
    air_root=bpy.data.objects['connections.air'];branches=[]
    opening_root=b.assembly('site.fresh_air_openings','Fresh-air opening tools')
    def opening(name,targets,angle,z,diameter,radius,depth=.6):
        tool=b.cylinder(name,opening_root,diameter/2+.005,depth,polar(radius,angle,z),None,vertices=64,bevel=0)
        tool.rotation_euler=Vector(polar(1,angle,0)).to_track_quat('Z','Y').to_euler()
        tool.hide_render=True;tool.hide_set(True);tool['fresh_air_opening_tool']=True
        for ob in targets:
            m=ob.modifiers.new('Internal fresh air '+name,'BOOLEAN');m.operation='DIFFERENCE';m.object=tool;m.solver='EXACT'
        return tool
    inner_parts=[o for o in parts if o.get('fresh_header_part')=='inner']
    exhaust_bore=installation.AIR['generator_hot_diameter']-2*cfg['branch_wall']
    inlet_bore=exhaust_bore*math.sqrt(cfg['generator_area_ratio'])
    inlet_od=inlet_bore+2*cfg['branch_wall'];valves=[]
    # Retain reactor/tank paths up to the new ring. Generator branches get
    # larger bores and centered valve ports. All ten enter the inner duct wall.
    for route in source['branches']:
        if route['service']!='fresh':continue
        old=bpy.data.objects[route['object']]
        path=[old.matrix_world@Vector(q.co[:3]) for q in old.data.splines[0].points]
        theta=math.degrees(math.atan2(route['points'][-1][1],route['points'][-1][0]))%360
        ri=inner_radius(theta,cfg,recesses);end_radius=ri+wall+.20
        clipped=[path[0]]
        for a,c in zip(path,path[1:]):
            if math.hypot(c.x,c.y)>=end_radius:
                lo_t,hi_t=0.,1.
                for _ in range(35):
                    t=(lo_t+hi_t)/2;q=a.lerp(c,t)
                    if math.hypot(q.x,q.y)<end_radius:lo_t=t
                    else:hi_t=t
                clipped.append(a.lerp(c,(lo_t+hi_t)/2));break
            clipped.append(c)
        diameter=route['diameter']
        if route['component'].startswith('generator_'):
            index=int(route['component'].split('_')[-1]);sg=bpy.data.objects[f'equipment.steam_generator_{index}']
            half=installation.STEAM_GENERATORS['width']/2;z=cfg['generator_inlet_height']
            box=b.box('fresh_air_butterfly_valve',sg,(.65,inlet_od+.40,inlet_od+.40),(-half-.325,0,z),'fresh_duct',.04)
            box['role']='Butterfly-valve envelope; centred on generator side'
            port=sg.matrix_world@Vector((-half-.65,0,z));lead=sg.matrix_world@Vector((-cfg['generator_lead_offsets'][index-1],0,z))
            approach=[port,lead]
            theta=math.degrees(math.atan2(lead.y,lead.x))%360
            entry=Vector(polar(inner_radius(theta,cfg,recesses)+wall+.20,theta,floor+1.35))
            controls=approach+[Vector((lead.x,lead.y,entry.z)),entry]
            clipped,bend_radii=fillet_path(controls,1.0);diameter=inlet_od
            valves.append(dict(name=box.name,generator=index,centre=list(sg.matrix_world@Vector((-half,0,z))),
                inlet=list(port),minimum_bend_radius_m=min(bend_radii)))
        name=old.name[len(air_root.name)+1:];props=dict(old.items());bpy.data.objects.remove(old,do_unlink=True)
        ob=b.tube(name,air_root,clipped,diameter/2,'fresh_air');ob.data.use_fill_caps=False
        for k,v in props.items():ob[k]=v
        ob['fresh_internal_branch']=True
        end=clipped[-1];theta=math.degrees(math.atan2(end.y,end.x))%360
        opening(route['component'],inner_parts,theta,end.z,diameter,inner_radius(theta,cfg,recesses))
        branches.append(dict(component=route['component'],name=ob.name,diameter=diameter,
            points=[list(q) for q in clipped],start=list(clipped[0]),header_entry='inner duct wall; no building-wall penetration'))
    for ob in list(bpy.data.objects):
        if ob.name=='connections.air.outside_air_intake' or ob.name.startswith('connections.fresh_air_intake'):
            bpy.data.objects.remove(ob,do_unlink=True)
    intakes=[]
    for index,angle in enumerate(cfg['intake_angles'],1):
        radius=outer_radius(angle,cfg,recesses);ri=inner_radius(angle,cfg,recesses);zz=floor+1.35
        intake_points=[polar((radius+ri)/2,angle,zz),polar(cfg['intake_radius'],angle,zz)]
        ob=b.tube('outside_air_intake_'+str(index),air_root,intake_points,inlet_od/2,'fresh_air');ob.data.use_fill_caps=False
        intake_root=b.assembly('site.fresh_air_intake_'+str(index),'Internal fresh-air duct',intake_points[-1],angle)
        b.box('louver_housing',intake_root,(.45,inlet_od+.30,inlet_od+.30),(0,0,0),'fresh_duct',.04)
        for i in range(7):
            b.box('louver_'+str(i),intake_root,(.08,inlet_od+.15,.06),(.24,0,(i-3)*(inlet_od/7)),'rail')
        opening('outdoor_intake_duct_'+str(index),[o for o in parts if o.get('fresh_header_part')=='outer'],angle,zz,inlet_od,radius)
        opening('outdoor_intake_wall_'+str(index),[bpy.data.objects['building.shell.retained_wall']],angle,zz,inlet_od,
            installation.BUILDING['diameter']/2-installation.BUILDING['wall_thickness']/2,1.5)
        intakes.append(dict(name=ob.name,points=intake_points,diameter=inlet_od,angle=angle))
    for o,value in visibility:
        try:o.hide_viewport=value
        except ReferenceError:pass  # Exterior plenum pieces were deliberately removed.
    bpy.context.view_layer.update()
    return dict(parameters=cfg,branches=branches,intakes=intakes,valves=valves,exhaust_bore_m=exhaust_bore,inlet_bore_m=inlet_bore,inlet_od_m=inlet_od,area_ratio=(inlet_bore/exhaust_bore)**2,
        minimum_clear_section_m2=min((outer_radius(a/10,cfg,recesses)-inner_radius(a/10,cfg,recesses)-2*wall)*cfg['clear_height'] for a in range(3600)),
        column_recesses=recesses,hot_header_column_recess_vertices=hot_vertices,door_gap_degrees=gap,bottom=low,top=high,inner_radius=cfg['outer_radius']-width,
        nominal_clear_area_m2=cfg['clear_width']*cfg['clear_height'],building_inside_radius=installation.BUILDING['diameter']/2-installation.BUILDING['wall_thickness'],
        scope='Draft steel duct with sealed inward offsets around columns; nominal area retained between columns; narrowed outer-wall pocket at 340 degrees clears coolant tank; local effective area, airflow, supports and access qualification pending')



def check_generator_connections(result,annex,salt,gas):
    def prep(name,pts,radius):
        pts=[Vector(p) for p in pts]
        return dict(name=name,pts=pts,r=radius,bb=bounds(pts),segments=[(a,c,bounds([a,c])) for a,c in zip(pts,pts[1:])])
    routes=[];tests=0;clashes=[];nearest=1000.
    for ob in bpy.data.objects:
        if ob.type=='CURVE' and (ob.get('process_route') or ob.get('air_insulated') or ob.get('utility_route') or ob.name.startswith('connections.air.')):
            for sp in ob.data.splines:routes.append(prep(ob.name,[ob.matrix_world@Vector(v.co[:3]) for v in sp.points],ob.data.bevel_depth))
    for q in annex['routes']+salt['routes']+gas['routes']:
        routes.append(prep(q['name'],q['points'],q['outside_envelope_m']/2))
    boxes=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('equipment.') or o.name.startswith('building.shell.pilaster')) and not o.get('utility_opening_tool')]
    for q in [r for r in result['branches'] if r['component'].startswith('generator_')]+result['intakes']:
        a=prep(q['name'],q['points'],q['diameter']/2)
        for c in routes:
            if a['name']==c['name'] or gapbox(a['bb'],c['bb'])>a['r']+c['r']+.10:continue
            tests+=1;best=1e6
            for u,v,bb in a['segments']:
                for w,x,bc in c['segments']:
                    if gapbox(bb,bc)>a['r']+c['r']+.10:continue
                    best=min(best,segdist(u,v,w,x)[0]-a['r']-c['r'])
            nearest=min(nearest,best)
            if best<-.001:clashes.append((a['name'],c['name'],best))
        for ob in boxes:
            if q.get('component') and ob.name.startswith('equipment.steam_'+q['component']+'.'):
                # The valve mouth is only 0.65 m from the casing, less than
                # the duct radius. A spherical endpoint falsely intersects it.
                # Check the actual swept-circle extent toward the casing plane;
                # the flat mouth has no axial extension beyond its end plane.
                if not ob.name.endswith('.casing'):continue
                inv=ob.matrix_world.inverted();pp=[inv@p for p in a['pts']]
                face=min(v[0] for v in ob.bound_box)
                extent=max(p.x+a['r']*math.sqrt(max(0,1-(pp[min(i+1,len(pp)-1)]-pp[max(i-1,0)]).normalized().x**2))
                    for i,p in enumerate(pp))
                tests+=1
                if extent>face+.001:clashes.append((a['name'],ob.name,face-extent))
                continue
            else:pts=a['pts']
            bb=bounds([ob.matrix_world@Vector(v) for v in ob.bound_box])
            if gapbox(bounds(pts),bb)>a['r']+.10:continue
            inv=ob.matrix_world.inverted();pp=[inv@p for p in pts];lo,hi=bounds(ob.bound_box)
            g=min(segment_box(u,v,lo,hi) for u,v in zip(pp,pp[1:]))-a['r'];tests+=1
            if g<-.001:clashes.append((a['name'],ob.name,g))
    for v in result['valves']:
        assert v['minimum_bend_radius_m']>result['inlet_od_m']/2
        sg=bpy.data.objects[f'equipment.steam_generator_{v["generator"]}'];p=sg.matrix_world.inverted()@Vector(v['centre'])
        assert abs(p.y)<1e-5 and abs(p.z-result['parameters']['generator_inlet_height'])<1e-5
        assert p.z-(result['inlet_od_m']+.40)/2>0
    assert not clashes,clashes
    return dict(selected_pairs=tests,nearest_pipe_gap_m=nearest,unresolved_clashes=clashes)


def check_fresh_air(result,site,installation,annex,salt,gas):
    cfg=result['parameters'];width=cfg['clear_width']+2*cfg['wall'];recesses=result['column_recesses'];gap=result['door_gap_degrees']
    floor=site.PAD_Z;bottom=result['bottom'];top=result['top'];clashes=[];tests=0
    assert len(result['branches'])==10
    assert len(result['intakes'])==3 and len(result['valves'])==3 and len(recesses)==18
    assert abs(result['area_ratio']-.75)<1e-9
    assert result['minimum_clear_section_m2']>4.5
    assert abs(result['nominal_clear_area_m2']-6.25)<1e-6
    assert cfg['outer_radius']<result['building_inside_radius']
    assert not any(o.name.startswith('connections.air.fresh_plenum.') for o in bpy.data.objects)
    def in_header(p,margin=0):
        theta=math.degrees(math.atan2(p[1],p[0]))%360;r=math.hypot(p[0],p[1])
        if gap[0]<theta<gap[1]:return False
        ro=outer_radius(theta,cfg,recesses)
        return inner_radius(theta,cfg,recesses)-margin<r<ro+margin and bottom-margin<p[2]<top+margin
    # All branch mouths are inside the hollow passage; preserve each equipment port.
    for route in result['branches']:
        pts=route['points'];rad=route['diameter']/2
        assert (Vector(pts[0])-Vector(route['start'])).length<1e-5
        assert in_header(pts[-1])
        assert bottom+cfg['wall']<pts[-1][2]-rad and pts[-1][2]+rad<top-cfg['wall']
    # Verify every built header vertex stays out of the specified level access lane.
    angle=math.radians(installation.ACCESS['angle']);side=Vector((-math.sin(angle),math.cos(angle),0))
    for o in bpy.data.objects:
        if o.type=='MESH' and o.name.startswith('site.fresh_air.'):
            for v in o.data.vertices:
                p=o.matrix_world@v.co
                if p.x*math.cos(angle)+p.y*math.sin(angle)>16.5:
                    assert abs(p.dot(side))>=installation.ACCESS['ring_gap_width']/2-.01,(o.name,list(p))
    # Check column clearance against the sealed, inward-offset outer wall.
    for q in recesses:
        o=bpy.data.objects[q['column']]
        for v in o.data.vertices:
            p=o.matrix_world@v.co;t=math.degrees(math.atan2(p.y,p.x))%360
            if gap[0]<t<gap[1]:continue
            assert math.hypot(p.x,p.y)-outer_radius(t,cfg,recesses)>.025
    # Screen equipment surfaces and their edges against the entire reserved air volume.
    for o in bpy.data.objects:
        if o.type!='MESH' or not o.name.startswith('equipment.') or o.get('utility_opening_tool'):continue
        pts=[o.matrix_world@Vector(v.co) for v in o.data.vertices]
        if not pts or min(p.z for p in pts)>top or max(p.z for p in pts)<bottom:continue
        if max(math.hypot(p.x,p.y) for p in pts)<min(q['radius'] for q in recesses)-width:continue
        tests+=1
        hit=any(in_header(p) for p in pts)
        if not hit:
            for edge in o.data.edges:
                a,c=(pts[i] for i in edge.vertices)
                if min(a.z,c.z)>top or max(a.z,c.z)<bottom:continue
                n=max(1,math.ceil((c-a).length/.10))
                if any(in_header(a.lerp(c,i/n)) for i in range(n+1)):hit=True;break
        if hit:clashes.append((o.name,'equipment in fresh-air volume'))
    selected=[]
    for o in bpy.data.objects:
        if o.type=='CURVE' and (o.get('process_route') or o.get('utility_route') or o.get('air_insulated')):
            for sp in o.data.splines:selected.append((o.name,[o.matrix_world@Vector(p.co[:3]) for p in sp.points],o.data.bevel_depth))
    for r in annex['routes']+salt['routes']+gas['routes']:
        selected.append((r['name'],[Vector(p) for p in r['points']],r['outside_envelope_m']/2))
    for name,pts,radius in selected:
        if min(p.z for p in pts)-radius>top or max(p.z for p in pts)+radius<bottom:continue
        hit=False
        for a,c in zip(pts,pts[1:]):
            n=max(1,math.ceil((c-a).length/.06));allow=(c-a).length/(2*n)
            if any(in_header(a.lerp(c,i/n),radius+allow) for i in range(n+1)):hit=True;break
        tests+=1
        if hit:clashes.append((name,'pipe envelope in fresh-air volume'))
    assert not clashes,clashes
    branch_checks=check_generator_connections(result,annex,salt,gas)
    return dict(generator_connections=branch_checks,branch_count=10,nominal_area_m2=result['nominal_clear_area_m2'],selected_envelopes=tests,unresolved_clashes=clashes,
        nominal_wall_gap_m=result['building_inside_radius']-cfg['outer_radius'],door_clear_width_m=installation.ACCESS['ring_gap_width'],
        checks=['Exterior concrete fresh-air ring and former branch wall holes removed','Ten equipment branches terminate inside internal fresh-air passage','Three outdoor inlets and three centered generator-side butterfly-valve boxes; clear inlet area 75% of exhaust','All 18 wall-column positions modeled; nominal passage retained between columns with local coolant-tank pocket','Selected equipment and pipe volumes clear internal duct','Level equipment-door gap preserved'],
        limitations='Selected visual envelope checks; local effective flow area, pressure loss, draft, thermal and structural/support performance not qualified')
