"""Open-bottom service channels in installation copies of the six thermal cassettes."""
import math,json
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from .perforated import perforated_prism
from .installation_clearance import bounds,gapbox


def clip_poly(subject,clip):
    result=list(subject)
    for a,b in zip(clip,clip[1:]+clip[:1]):
        old=result;result=[]
        if not old:break
        def f(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
        for u,v in zip(old,old[1:]+old[:1]):
            fu,fv=f(u),f(v)
            if fu>=-1e-9:result.append(u)
            if (fu>=0)!=(fv>=0):
                t=fu/(fu-fv);result.append((u[0]+t*(v[0]-u[0]),u[1]+t*(v[1]-u[1])))
    return result


def subtract_prism_surface(ob,polygon,roof):
    """Clip merged steel surfaces independently; avoids Boolean self-intersections."""
    planes=[lambda q:q.z+.12,lambda q:roof-q.z]
    for a,c in zip(polygon,polygon[1:]+polygon[:1]):
        planes.append(lambda q,a=a,c=c:(c[0]-a[0])*(q.y-a[1])-(c[1]-a[1])*(q.x-a[0]))
    def cut(poly,f,inside):
        result=[]
        for u,v in zip(poly,poly[1:]+poly[:1]):
            fu,fv=f(u),f(v);iu=fu>=-1e-9 if inside else fu<=1e-9
            if iu:result.append(u)
            if (fu>1e-9 and fv< -1e-9) or (fu< -1e-9 and fv>1e-9):result.append(u.lerp(v,fu/(fu-fv)))
        return result
    verts=[];faces=[];inverse=ob.matrix_local.inverted()
    for face in ob.data.polygons:
        remainder=[ob.matrix_local@ob.data.vertices[v].co for v in face.vertices]
        for f in planes:
            if len(remainder)<3:break
            outside=cut(remainder,f,False)
            if len(outside)>=3:
                start=len(verts);verts.extend(inverse@v for v in outside);faces.append(tuple(range(start,len(verts))))
            remainder=cut(remainder,f,True)
    mesh=bpy.data.meshes.new(ob.data.name+'.channel');mesh.from_pydata(verts,[],faces)
    for m in ob.data.materials:mesh.materials.append(m)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();ob.data=mesh


def build_channels(b,layout,services):
    import wistr_tgrid_cover as cfg
    first=bpy.data.objects['reactor.insulation_1'];rot=Matrix.Rotation(-math.pi/6,3,'Z')
    outline=cfg.outline();channels=[]
    # All coordinates below are in the first cassette's local frame.
    for name,angle,x0,x1,y,w in [('fuel',0,1.90,4.60,.50,.48),('absorber_low',0,3.20,4.60,0,.72),('absorber_high',60,3.20,4.60,0,.72)]:
        turn=rot@Matrix.Rotation(math.radians(angle),3,'Z')
        poly=[tuple((turn@Vector((x,yy,0)))[:2]) for x,yy in [(x0,y-w/2),(x1,y-w/2),(x1,y+w/2),(x0,y+w/2)]]
        channels.append(dict(name=name,polygon=poly,roof=.48,turn=turn,x0=x0,x1=x1,y=y,width=w))
    # Thermal well plugs become parts of the liftable cassettes; no tube passes
    # through a closed hole that would lock the cover onto the connected bundle.
    for ob in list(bpy.data.objects):
        if ob.name.startswith('reactor.thermal_service_inserts.'):
            bpy.data.objects.remove(ob,do_unlink=True)
    for n,(x,y) in enumerate([(2.16,.50),(3.53,0),(3.53*.5,3.53*math.sin(math.pi/3))]):
        q=rot@Vector((x,y,0));circle=[(q.x+.249*math.cos(j*math.tau/64),q.y+.249*math.sin(j*math.tau/64)) for j in range(64)]
        pp=clip_poly(circle,outline)
        ob=perforated_prism(b,f'channel_well_fill_{n}',first,pp,[],.18,.512,'absorber_insulation');ob['component']='blocks'
        ob=perforated_prism(b,f'channel_well_lid_{n}',first,pp,[],.710,.716,'absorber_jacket');ob['component']='shell'
    # Cut only the first sector, then share its revised meshes with the other five.
    # Pressure caps, plugs and vessel objects are not touched.
    parts=[o for o in first.children if o.type=='MESH'];cuts=0
    for ob in parts:
        verts=[ob.matrix_local@v.co for v in ob.data.vertices]
        if not verts or min(v.z for v in verts)>.481:continue
        ob.data=ob.data.copy()
        for c in channels:
            cb=bounds([(*p,z) for p in c['polygon'] for z in (-.10,c['roof'])])
            if gapbox(bounds(verts),cb)>.001:continue
            if ob.get('component')=='grid':subtract_prism_surface(ob,c['polygon'],c['roof'])
            else:
                cutter=perforated_prism(b,'channel_cut',first,c['polygon'],[],-.12,c['roof'],None)
                b.cut(ob,cutter)
            cuts+=1
        ob['open_bottom_channel_revision']='D-038'
    print('CHANNEL_CUTS',cuts,flush=True)
    # Upper bridge straps support cut grid regions from the existing upper frame.
    # Their sections and connections are provisional; standalone mass/load results
    # do not qualify this new cassette revision.
    for c in channels:
        pp=clip_poly(c['polygon'],outline)
        if len(pp)<3:continue
        top=perforated_prism(b,'channel_topup_'+c['name'],first,pp,[],.714,.714+c['roof'],'absorber_insulation')
        top['component']='channel_topup';top['restored_nominal_insulation_m']=.512
        # Separate thin top plate and side jacket; the cap remains liftable as one unit.
        skin=perforated_prism(b,'channel_skin_'+c['name'],first,pp,[],.714+c['roof'],.716+c['roof'],'absorber_jacket');skin['component']='channel_skin'
        for j,(u,v) in enumerate(zip(pp,pp[1:]+pp[:1])):
            length=math.dist(u,v)
            skin=b.box(f'channel_side_{c["name"]}_{j}',first,(length,.001,c['roof']),((u[0]+v[0])/2,(u[1]+v[1])/2,.714+c['roof']/2),'absorber_jacket')
            skin.rotation_euler.z=math.atan2(v[1]-u[1],v[0]-u[0]);skin['component']='channel_skin'
        # Bridge beams sit above channel ceiling; no lower tie crosses a tube path.
        for xx in (c['x0']+.15,(c['x0']+min(c['x1'],4.1))/2,min(c['x1'],4.1)-.10):
            raw=[(xx-.025,c['y']-c['width']/2-.06),(xx+.025,c['y']-c['width']/2-.06),
                 (xx+.025,c['y']+c['width']/2+.06),(xx-.025,c['y']+c['width']/2+.06)]
            pp2=clip_poly([tuple((c['turn']@Vector((*q,0)))[:2]) for q in raw],outline)
            if len(pp2)>2:
                beam=perforated_prism(b,f'channel_header_{c["name"]}_{xx}',first,pp2,[],.483,.515,'catwalk_frame');beam['component']='channel_frame'
    # Edge webs connect the interrupted lower grid ends to the upper headers.
    # Trim webs at intersecting channels so they cannot close a lifting slot.
    for c in channels:
        for side in (-1,1):
            yy=c['y']+side*(c['width']/2+.004)
            raw=[(c['x0'],yy-.004),(c['x1'],yy-.004),(c['x1'],yy+.004),(c['x0'],yy+.004)]
            pp=clip_poly([tuple((c['turn']@Vector((*q,0)))[:2]) for q in raw],outline)
            if len(pp)<3:continue
            web=perforated_prism(b,f'channel_edge_web_{c["name"]}_{side}',first,pp,[],.015,.510,'catwalk_frame')
            for crossing in channels:
                cutter=perforated_prism(b,'web_channel_cut',first,crossing['polygon'],[],-.12,crossing['roof'],None)
                b.cut(web,cutter)
            web['component']='channel_frame'
    # Raise the external pickup heads/guides clear of the local insulation ridges.
    # The lower catch shoulders stay at their original frame engagement elevation.
    extension=.55
    for ob in list(first.children):
        if ob.name.endswith('.other_links'):
            ob.data=ob.data.copy()
            for v in ob.data.vertices:
                if v.co.z>.70:v.co.z+=extension
            ob['pickup_stem_extension_m']=extension
        elif ob.name.endswith(('.other_cold_frame','.other_indicator','.other_stainless','.shell_cold_frame')):
            ob.data=ob.data.copy()
            for v in ob.data.vertices:v.co.z+=extension
    for index,(x,y,_) in enumerate(cfg.points()):
        for side in (-1,1):
            post=b.box(f'raised_guide_support_{index}_{side}',first,(.025,.025,extension),(x+side*.065,y,.70+extension/2),'catwalk_frame')
            post['component']='channel_frame'
    # New header/skin elements as well as altered lower members move with each cassette.
    revised=[o for o in first.children if o.type=='MESH']
    for i in range(2,7):
        parent=bpy.data.objects[f'reactor.insulation_{i}']
        for ob in revised:
            name=ob.name.replace('insulation_1','insulation_'+str(i))
            existing=bpy.data.objects.get(name)
            if existing:
                existing.data=ob.data
                if ob.get('open_bottom_channel_revision'):existing['open_bottom_channel_revision']='D-038'
            else:
                child=ob.copy();child.data=ob.data;child.name=name
                for col in ob.users_collection:col.objects.link(child)
                child.parent=parent
    bpy.context.view_layer.update()
    result=dict(channel_roof_above_cap_m=.48,remaining_original_block_m=.032,additional_local_insulation_m=.48,
        nominal_block_thickness_over_channels_m=.512,channel_cuts=cuts,cover_count=6,
        channels=[dict(name=c['name'],polygon=c['polygon'],roof=c['roof']) for c in channels],
        scope='Installation cassette revision; open-bottom channels and local insulation topups; no revised structural or thermal qualification',
        limitations=['Upper grid/header load paths require engineering assessment','Local raised strips retain nominal insulation depth; heat bridges and area losses need recalculation','Whole crane handling/plant operating sequence is not validated'])
    services['cover_channels']=result
    result['pickup_extension_m']=extension
    result['checks']=['Six linked cassette revisions; pressure parts unchanged','Closed service holes replaced by liftable channel-well inserts','Headers lie above the channel roof; external pickup heads raised to clear insulation ridges']
    result['lift_checks']=check_lift_clearance(first)
    return result


def check_lift_clearance(first):
    def tree(ob,dz=0):
        return BVHTree.FromPolygons([ob.matrix_world@v.co+Vector((0,0,dz)) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
    parts=[o for o in first.children if o.type=='MESH']
    obstacles=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('connections.absorber_services.','connections.fuel_services.'))]
    cache={};clashes=[];tested=0
    for height in (0,.05,.20,.50,1.0):
        for ob in parts:
            bb=bounds([ob.matrix_world@Vector(q)+Vector((0,0,height)) for q in ob.bound_box]);ot=None
            for other in obstacles:
                if other.name not in cache:cache[other.name]=(bounds([other.matrix_world@Vector(q) for q in other.bound_box]),None)
                cb,ct=cache[other.name]
                if gapbox(bb,cb)>.001:continue
                if ct is None:ct=tree(other);cache[other.name]=(cb,ct)
                if ot is None:ot=tree(ob,height)
                tested+=1
                if ot.overlap(ct):clashes.append((ob.name,other.name,height))
    assert not clashes,clashes[:30]
    return dict(cassette=first.name,heights_m=[0,.05,.20,.50,1.0],surface_pairs_tested=tested,collisions=clashes,
        scope='Five positions of representative vertical lift against connected tubing and bundle jackets; other sectors use linked geometry')
