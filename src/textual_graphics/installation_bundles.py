"""Compact traced tubing bundles and lift-clear insulation channels (draft geometry)."""
import math,itertools,json
import bpy
from mathutils import Vector,Matrix
from .installation_piping import fillet_path,shell_mesh
from .installation_clearance import bounds,gapbox,segdist,segment_box
from .perforated import perforated_prism


def frames(points):
    result=[];side=None
    for i,p in enumerate(points):
        t=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        if side is None:
            side=Vector((-t.y,t.x,0))
            if side.length<1e-5:side=Vector((0,1,0))
        side=(side-t*side.dot(t)).normalized()
        result.append((side,t.cross(side).normalized()))
    return result


def fixed_frames(points,side):
    out=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        normal=(side-tangent*side.dot(tangent)).normalized()
        out.append((normal,tangent.cross(normal).normalized()))
    return out


def profile(w,h,r):
    r=min(r,w,h)
    return [(sx*(w-r)+r*math.cos(a),sy*(h-r)+r*math.sin(a))
        for sx,sy,start in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]
        for a in [math.radians(start+j*90/8) for j in range(9)]]


def jacket(b,name,root,points,halfwidth,halfheight,thickness=.05,sideframes=None):
    """Hollow rounded rectangular jacket; member tubes remain individually modeled."""
    pts=[Vector(p) for p in points];ff=sideframes or frames(pts)
    profiles=[profile(halfwidth+thickness,halfheight+thickness,.015+thickness),profile(halfwidth,halfheight,.015)]
    verts=[];faces=[];m=len(profiles[0]);n=len(pts)
    for p,(side,up) in zip(pts,ff):
        for pp in profiles:verts.extend(p+side*x+up*y for x,y in pp)
    for k in range(n-1):
        for layer in (0,1):
            for j in range(m):
                a=k*2*m+layer*m+j;c=k*2*m+layer*m+(j+1)%m
                q=(a,c,c+2*m,a+2*m);faces.append(q if layer==0 else tuple(reversed(q)))
    for k in (0,n-1):
        for j in range(m):
            a=k*2*m+j;c=k*2*m+(j+1)%m;faces.append((a,c,c+m,a+m))
    ob=b.mesh(name,root,verts,faces,'absorber_jacket')
    ob['role']='insulated_tube_bundle';ob['insulation_m']=thickness
    ob['scope']='Insulated envelope including compact electrical tape; heater wattage and insulation thickness provisional'
    for f in ob.data.polygons:f.use_smooth=True
    return ob,dict(name=ob.name,points=[list(p) for p in pts],radius=math.hypot(halfwidth+thickness,halfheight+thickness),
        halfwidth=halfwidth+thickness,halfheight=halfheight+thickness)


def route(b,root,name,controls,od,heated,**metadata):
    points,radii=fillet_path(controls,.09)
    o=shell_mesh(b,name,root,points,od/2,od/2-.002,'absorber_external_centre' if od==.025 else 'absorber_external_outer')
    o['electrical_resistance_tape']=heated;o['service']='salt' if heated else 'gas'
    return dict(points=[list(p) for p in points],outside_diameter_m=od,wall_thickness_m=.002,
        start=list(points[0]),end=list(points[-1]),minimum_bend_radius_m=min(radii) if radii else 1.,heated=heated,**metadata)


def connect_absorbers(b,layout,report):
    p=layout.CATWALK;cfg=layout.ABSORBER_RESERVOIRS
    root=b.assembly('connections.absorber_services','Absorber service piping')
    for label,color in [('centre','#368C9C'),('outer','#D9A14C')]:b.material('absorber_external_'+label,color,metallic=.6,roughness=.3)
    bpy.context.scene['section_cutaway']=False;bpy.context.scene.update_tag();bpy.context.view_layer.update()
    report['bundles']=[];report['routes']=[]
    for i in range(1,7):
        src=bpy.data.objects[f'reactor.absorber_tubes_{i}'];tr=src.matrix_world
        def world(x,y,z):
            q=tr@Vector((x,y,0));q.z=z;return q
        for s in [s for s in report['stations'] if s['absorber']==i]:
            pair=s['pair'];idx=s['index'];sign=-1 if pair=='centre' else 1
            tank=b.assemblies[s['tank']];mod=b.assemblies[s['module']]
            y=-.20 if sign<0 else .18
            bottom=tank.matrix_world@Vector((0,0,cfg['bottom_above_deck']))
            centre_end=world(5.4,y,-1.31)
            # Two salt drains and their gas partners split after the compact plug boot.
            own=[]
            for suffix in ('b','a'):
                old=bpy.data.objects[src.name+'.'+pair+'_'+suffix];start=old.matrix_world@Vector(old['termination']);large=suffix=='b';od=.05 if large else .025
                dy=0 if large else -.06
                controls=[start,world(3.53,old['termination'][1],-1.51),world(3.92,y+dy,-1.47),world(5.4,y+dy,-1.31)]
                if large:
                    controls += [Vector((bottom.x,bottom.y,-1.20)),bottom];end=bottom
                else:
                    end=mod.matrix_world@Vector((0,0,.12))
                    # Gas has no drain constraint; drop locally before crossing the salt leg.
                    controls += [world(5.58,y+dy,-1.52),Vector((end.x,end.y,-1.52)),end]
                rr=route(b,root,f'absorber_{i}.{pair}_{suffix}',controls,od,large,absorber=i,pair=pair,index=idx,source=old.name,
                    target=tank.name if large else mod.name,kind='tank_bottom_to_spider' if large else 'spider_small_to_module',service=pair+'_'+suffix)
                own.append(rr);report['routes'].append(rr)
                union=b.annulus(f'absorber_{i}.{pair}_{suffix}.disconnect',root,od/2,od/2+.008,-.016,.016,'rail',steps=20);union.location=start+Vector((0,0,.025))
            # Common pair insulation around the parallel portion, then separate tails.
            path,_=fillet_path([world(3.92,y-.03,-1.47),world(5.4,y-.03,-1.31)],.09)
            obj,envelope=jacket(b,f'absorber_{i}.{pair}_bundle',root,path,.058,.028)
            envelope.update(absorber=i,index=idx,kind='paired',members=[q['source'] for q in own]);report['bundles'].append(envelope)
            for rr in own:
                pts=[Vector(q) for q in rr['points']]
                # Include an interpolated join point, rather than leaving a gap on long segments.
                cut=[]
                for u,v in zip(pts,pts[1:]):
                    a=tr.inverted()@u;c=tr.inverted()@v
                    if a.x<5.4<=c.x:cut.append(u.lerp(v,(5.4-a.x)/(c.x-a.x)))
                    if c.x>=5.4:cut.append(v)
                if len(cut)>1:
                    od=rr['outside_diameter_m'];obj,en=jacket(b,f'absorber_{i}.{rr["service"]}_tail',root,cut,od/2+.003,od/2+.003)
                    en.update(absorber=i,index=idx,kind='tail',members=[rr['source']]);report['bundles'].append(en)
            top=tank.matrix_world@Vector((0,0,cfg['bottom_above_deck']+cfg['height']))
            end=mod.matrix_world@Vector((0,.405 if sign<0 else -.405,layout.ABSORBER_MODULES['tank_base_z']+layout.ABSORBER_MODULES['tank_height']+1.10))
            height=max(top.z,end.z)+.20
            rr=route(b,root,f'absorber_{i}.{pair}_tank_top',[top,(top.x,top.y,height),(end.x,end.y,height),end],.025,False,
                absorber=i,pair=pair,index=idx,source=tank.name,target=mod.name,kind='tank_top_to_module',service=pair+'_top')
            report['routes'].append(rr)
            obj,en=jacket(b,f'absorber_{i}.{pair}_top_insulation',root,rr['points'],.0155,.0155)
            en.update(absorber=i,index=idx,kind='gas_top',members=[tank.name]);report['bundles'].append(en)
        # Low-profile shared boot at the close-pitch four-tube plug, entirely under cover.
        path,_=fillet_path([world(3.53,0,-1.64),world(3.53,0,-1.51),world(3.92,-.01,-1.47)],.07)
        ff=[]
        for p0 in path:
            side=tr.to_3x3()@Vector((0,1,0));ff.append((side,Vector((0,0,1))))
        # A fork boot occupies the open-bottom channel; its removable jacket is schematic.
        obj,en=jacket(b,f'absorber_{i}.plug_boot',root,path,.275,.028,sideframes=fixed_frames(path,tr.to_3x3()@Vector((0,1,0))))
        en.update(absorber=i,kind='boot',members=[r['source'] for r in report['routes'] if r['absorber']==i and r['kind']!='tank_top_to_module']);report['bundles'].append(en)
        print('ABSORBER_BUNDLES',i,flush=True)
    merge_pair_jackets(report)
    report['checks']=check_absorbers(b,layout,report)
    return report


def check_absorbers(b,layout,report):
    routes=report['routes'];assert len(routes)==36 and len(report['stations'])==12
    drains=[]
    for r in routes:
        if r['kind']=='tank_top_to_module':assert not r['heated'];continue
        src=bpy.data.objects[r['source']]
        assert (src.matrix_world@Vector(src['termination'])-Vector(r['start'])).length<1e-5
        assert r['heated']==(r['kind']=='tank_bottom_to_spider')
        if r['heated']:
            p=list(reversed(r['points']));rise=max(v[2]-u[2] for u,v in zip(p,p[1:]));assert rise<1e-5,(r['source'],rise)
            internal=[src.matrix_world@Vector(q) for q in reversed(src['centreline'])]
            assert max(v.z-u.z for u,v in zip(internal,internal[1:]))<1e-5
            drains.append(dict(source=r['source'],fall_m=p[0][2]-p[-1][2],maximum_uphill_step_m=max(0,rise)))
    report['drain_checks']=drains;assert len(drains)==12
    report['deck_change_from_D037_m']=layout.CATWALK['deck_z']-.5
    report['clear_inner_walking_band_m']=layout.CATWALK['module_radius']-.56-layout.CATWALK['inner_radius']
    return ['12 independent salt/gas pairs; only 50 mm absorber salt tubes are heat traced',
        '12 insulated tank-top gas lines are unheated','12 external salt drains and inherited internal paths have no upward segment']


def build_fuel_services(b,layout,services):
    cfg=layout.FUEL_SERVICES;root=b.assembly('connections.fuel_services','Fuel service piping')
    result=dict(parameters=cfg,routes=[],bundles=[],assignments=[],scope='Individual heated fuel tubes in six shared jackets; visual geometry, not transfer or thermal qualification',
        limitations=['Heater duty, drainability, structural and pressure checks remain open','Lift insulation before disconnecting and removing cap-side jumpers'])
    for i,target in enumerate(cfg['sector_to_tank'],1):
        tank=b.assemblies[f'equipment.fuel_storage_{target}'];src=bpy.data.objects[f'reactor.core_tubes_{i}'];tr=src.matrix_world
        def world(x,y,z):
            q=tr@Vector((x,y,0));q.z=z;return q
        lid=bpy.data.objects[tank.name+'.lid'];roof=lid.matrix_world@Vector((-1.41,0,.075));end=roof+Vector((0,0,.50))
        start=world(2.60,.50,-1.455);out=world(4.23,.50,-1.455);drop=world(math.sqrt(4.70**2-.50**2),.50,-1.85)
        a0=math.atan2(drop.y,drop.x);a1=math.atan2(end.y,end.x);delta=(a1-a0+math.pi)%math.tau-math.pi
        steps=max(3,math.ceil(abs(delta)/math.radians(10)));arc=[Vector((4.70*math.cos(a0+delta*j/steps),4.70*math.sin(a0+delta*j/steps),-1.85)) for j in range(steps+1)]
        approach_z=-1.40 if delta<0 else -1.85
        controls=[start,out,drop,*arc,(5.10*math.cos(a1),5.10*math.sin(a1),approach_z),(end.x,end.y,approach_z),end]
        if delta>=0:controls=[start,out,world(5.05,.5,-1.85),(end.x,end.y,-1.85),end]
        pts,radii=fillet_path(controls,.25);ff=frames(pts)
        envelope,en=jacket(b,f'sector_{i}.heated_bundle',root,pts,.12,.083)
        en.update(sector=i,members=[]);result['bundles'].append(en)
        holes=[];starts=[]
        for rank in range(3):
            for connection,od,dz in [('top',.025,.055),('bottom',.05,-.055)]:
                label=f'pair_{rank+1}_{connection}_{int(od*1000)}mm';old=bpy.data.objects[src.name+'.'+label]
                source=old.matrix_world@Vector(old['termination']);starts.append(source)
                members=[p+side*((rank-1)*.09)+up*dz for p,(side,up) in zip(pts,ff)]
                # Source stubs rise into the low-profile common bundle under the cover.
                join=[source,Vector((source.x,source.y,members[0].z)),members[0]]
                head,hr=fillet_path(join,.09)
                orientation=1 if ff[-1][0].dot(tank.matrix_world.to_3x3()@Vector((0,1,0)))>0 else -1
                tx=-1.41+orientation*(.07 if connection=='top' else -.07);ty=(rank-1)*.18*orientation
                port=lid.matrix_world@Vector((tx,ty,.075));terminus=port+Vector((0,0,.15))
                tail,tradii=fillet_path([members[-2],members[-1],terminus],.09)
                full=[*head[:-1],*members[:-2],*tail]
                shell_mesh(b,f'sector_{i}.{label}',root,full,od/2,od/2-.002,'absorber_external_centre' if od==.025 else 'absorber_external_outer')['electrical_resistance_tape']=True
                shell_mesh(b,f'tank_{target}.{label}.nozzle',root,[port,terminus],od/2,od/2-.002,'rail')
                holes.append((tx,ty,od/2+.003));en['members'].append(old.name)
                rr=dict(sector=i,tank=target,source=old.name,connection_type=connection,pair=rank+1,outside_diameter_m=od,heated=True,
                    start=list(source),end=list(terminus),points=[list(p) for p in full],minimum_bend_radius_m=min([*hr,*tradii,*radii]),tank_roof_port=list(port))
                result['routes'].append(rr)
                u=b.annulus(f'sector_{i}.{label}.cap_disconnect',root,od/2,od/2+.008,-.016,.016,'rail',steps=20);u.location=source+Vector((0,0,.025))
        # Short connector boots finish each six-tube bundle at plug and tank roof.
        p0=world(2.16,.5,-1.64);p1=world(2.16,.5,-1.455)
        boot,_=fillet_path([p0,p1,start],.075)
        ob,ee=jacket(b,f'sector_{i}.plug_boot',root,boot,.14,.083,sideframes=fixed_frames(boot,tr.to_3x3()@Vector((0,1,0))));ee.update(sector=i,members=en['members']);result['bundles'].append(ee)
        ob,ee=jacket(b,f'sector_{i}.tank_boot',root,[pts[-1],roof+Vector((0,0,.12))],.24,.105);ee.update(sector=i,members=en['members']);result['bundles'].append(ee)
        mat=lid.data.materials[0];hw=(layout.FUEL_STORAGE['length']+.12)/2;hd=(layout.FUEL_STORAGE['width']+.12)/2
        temp=perforated_prism(b,f'tank_lid_{target}',root,[(-hw,-hd),(hw,-hd),(hw,hd),(-hw,hd)],holes,-.075,.075,'rail',segments=24)
        lid.data=temp.data;lid.data.materials.clear();lid.data.materials.append(mat);lid['through_hole_count']=6;bpy.data.objects.remove(temp,do_unlink=True)
        result['assignments'].append(dict(sector=i,tank=target))
        print('FUEL_BUNDLE',i,flush=True)
    result['verification']=check_bundles(b,layout,services,result)
    return result


def check_bundles(b,layout,services,fuel):
    bpy.context.view_layer.update();routes=fuel['routes'];absorber=services['catwalk']['routes']
    assert len(routes)==36 and all(r['heated'] for r in routes)
    for r in routes:
        src=bpy.data.objects[r['source']];assert (src.matrix_world@Vector(src['termination'])-Vector(r['start'])).length<1e-5
        assert r['minimum_bend_radius_m']>r['outside_diameter_m']/2
    allroutes=routes+absorber;clashes=[];minimum=1e6
    # Screen individual lines; shared insulation contains its own member tubes intentionally.
    for a,c in itertools.combinations(allroutes,2):
        rad=(a['outside_diameter_m']+c['outside_diameter_m'])/2
        if gapbox(bounds(a['points']),bounds(c['points']))>rad+.01:continue
        gap=1e6
        for u,v in zip(a['points'],a['points'][1:]):
            bb=bounds([u,v])
            for x,y in zip(c['points'],c['points'][1:]):
                if gapbox(bb,bounds([x,y]))>rad+.01:continue
                gap=min(gap,segdist(u,v,x,y)[0]-rad)
        minimum=min(minimum,gap)
        if gap<-.0005:clashes.append((a['source'],c['source'],gap))
    assert not clashes,clashes
    return dict(route_count=36,assignment_count=6,bundle_count=6,unresolved_clashes=clashes,minimum_screened_bare_tube_gap_m=minimum,
        checks=['36 individually connected and heated maintenance tubes in six sector bundles','All actual cap stub endpoints retained','Bare service tubes screened against each other'],
        limitations='Insulation/structure envelope and vertical cover checks are recorded separately')

def merge_pair_jackets(report):
    """One physical split insulation jacket where the paired gas/salt tubes diverge."""
    for index in range(1,13):
        entries=[e for e in report['bundles'] if e.get('index')==index and e['kind']=='tail']
        if len(entries)!=2:continue
        first,second=entries;a=bpy.data.objects[first['name']];c=bpy.data.objects[second['name']]
        bpy.context.view_layer.update();mod=a.modifiers.new('Shared split insulation','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=c
        bpy.context.view_layer.objects.active=a;bpy.ops.object.modifier_apply(modifier=mod.name)
        a.name=a.name.replace('_b_tail','_split_jacket');bpy.data.objects.remove(c,do_unlink=True)
        first.update(name=a.name,members=first['members']+second['members'],kind='split',branch_points=[first['points'],second['points']])
        report['bundles'].remove(second)
