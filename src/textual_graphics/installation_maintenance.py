"""Removable-item laydown and mobile sector transport envelopes, not rated hardware."""
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from .installation_stairs import grate, prism, swept_outline, offset_edge, prism_data
from .installation_clearance import bounds, gapbox, segment_box


def item_bounds(name):
    root=bpy.data.objects[name];inv=root.matrix_world.inverted()
    pts=[inv@ob.matrix_world@Vector(v) for ob in [root]+list(root.children_recursive)
         if ob.type in ('MESH','CURVE') and not ob.hide_render for v in ob.bound_box]
    return bounds(pts)


def build_maintenance(b,layout):
    p=layout.MAINTENANCE;z=layout.CATWALK['deck_z'];floor=layout.FLOOR_Z
    root=b.assembly('equipment.maintenance_laydown','Maintenance laydown')
    root['scope']=p['scope']
    x0,x1,y0,y1=p['platform_bounds']
    grate(b,'grating',root,x0,x1,y0,y1,z)
    # Conceptual independent frame: columns miss the tanks below; nothing bears on the vessel.
    for x in (x0+.2,x1-.2):
        for y in (y0+.2,y1-.2):
            b.box(f'column_{x}_{y}',root,(.25,.25,z-floor),(x,y,(floor+z)/2),'catwalk_frame')
            b.box(f'foot_{x}_{y}',root,(.5,.5,.04),(x,y,floor+.02),'catwalk_frame')
    for y in (y0+.2,y1-.2):
        b.box('main_girder_'+str(y),root,(x1-x0,.20,.40),((x0+x1)/2,y,z-.23),'catwalk_frame')
    for x in (x0+.2,10.5,12.6,14.7,x1-.2):
        b.box('cross_beam_'+str(x),root,(.12,y1-y0,.25),(x,(y0+y1)/2,z-.155),'catwalk_frame')
    # Marked solid receiving trays. Actual items are shown only in the inspection render.
    for key in ('cover','cap'):
        a,c,d,e=p[key+'_bay']
        b.box(key+'_receiving_tray',root,(c-a,e-d,.025),((a+c)/2,(d+e)/2,z+.0125),'panel')
        b.tube(key+'_bay_marking',root,[(a,d,z+.032),(c,d,z+.032),(c,e,z+.032),(a,e,z+.032),(a,d,z+.032)],.018,'crane')
        # Bearing runners are provisional and must be aligned to each item's frame.
        for yy in (d+.45,e-.45):
            b.box(key+'_bearing_'+str(yy),root,(c-a-.3,.10,.08),((a+c)/2,yy,z+.065),'dark')
    def rail(name,a,c):
        n=max(1,math.ceil(math.dist(a,c)/1.2))
        pts=[tuple(Vector(a).lerp(Vector(c),i/n))+(z,) for i in range(n+1)]
        b.rail(name,root,pts,mat='catwalk_rail',height=1.10)
        b.tube(name+'_toe',root,[(*a,z+.06),(*c,z+.06)],.045,'catwalk_frame')
    rail('south',(x0,y0),(x1,y0));rail('east',(x1,y0),(x1,y1))
    rail('north',(x1,y1),(x0,y1));rail('west',(x0,y0),(x0,.78))
    # 1.3 m bridge enters the clear northern aisle beside the two receiving bays.
    a=math.radians(p['entry_angle'])
    path=[Vector((r*math.cos(a),r*math.sin(a),z)) for r in (7.30,7.80)]
    path.append(Vector((8.4,1.48,z)))
    prism(b,'entry_bridge',root,swept_outline(path,.65),z-.035,z,'catwalk_mesh')
    for side in (-1,1):
        edge=offset_edge(path,side*.70)
        # End the bridge guard at the platform edge, leaving its aisle open.
        if edge[-1][0]>x0-.05:
            u,v=Vector(edge[-2]),Vector(edge[-1])
            edge[-1]=tuple(u+(v-u)*((x0-.05-u.x)/(v.x-u.x)))
        b.rail('bridge_'+str(side),root,[(*v,z) for v in edge],mat='catwalk_rail',height=1.10)
        b.tube('bridge_frame_'+str(side),root,[(*v,z-.12) for v in edge],.055,'catwalk_frame')
    # Preserve the existing stair opening and add an independent laydown entrance.
    cat=bpy.data.objects['equipment.reactor_catwalk'];rr=layout.CATWALK['outer_radius']
    half=math.degrees(math.asin(.65/rr));angles=sorted([p['entry_angle'],layout.CATWALK_STAIRS['entry_angle']])
    for ob in list(cat.children):
        if '.outer_rail_' in ob.name or '.outer_toeplate' in ob.name:
            bpy.data.objects.remove(ob,do_unlink=True)
        elif '.outer_post_' in ob.name:
            angle=math.degrees(math.atan2(ob.location.y,ob.location.x))%360
            if any(abs((angle-aa+180)%360-180)<half for aa in angles):bpy.data.objects.remove(ob,do_unlink=True)
    for i,aa in enumerate(angles):
        start=aa+half;end=angles[(i+1)%len(angles)]+(360 if i==len(angles)-1 else 0)-half
        for h in (.55,1.10):b.ring(f'outer_rail_{i}_{h}',cat,rr,h,.025,'catwalk_rail',start=start,end=end)
        b.annulus(f'outer_toeplate_{i}',cat,rr-.005,rr+.005,0,.10,'catwalk_frame',start=start,end=end)
    for aa in (p['entry_angle']-half,p['entry_angle']+half):
        q=Vector((rr*math.cos(math.radians(aa)),rr*math.sin(math.radians(aa)),0))
        b.beam('laydown_entry_jamb_'+str(aa),cat,q,q+Vector((0,0,1.1)),.025,'catwalk_rail')
    # A low-profile vehicle envelope outside the door, aligned for straight entry/exit.
    aa=math.radians(layout.ACCESS['angle']);r=p['cart_radius']
    cart=b.assembly('equipment.sector_canister_cart','Sector handling',(r*math.cos(aa),r*math.sin(aa),floor),layout.ACCESS['angle'])
    cart['scope']=p['scope'];cart['mobile_equipment']=True
    b.box('chassis',cart,(p['cart_length'],p['cart_width'],.10),(0,0,p['cart_deck']-.05),'crane',.025)
    for x in (-1.25,1.25):
        for y in (-1.37,1.37):
            wheel=b.cylinder('wheel_'+str(x)+'_'+str(y),cart,.10,.18,(x,y,.10),'dark',vertices=24,bevel=.008)
            wheel.rotation_euler.x=math.pi/2
    bot=p['cart_deck'];height=p['canister_clear_height'];ri=p['canister_inside_diameter']/2;ro=p['canister_outside_diameter']/2
    b.cylinder('base',cart,ro,p['canister_base'],(0,0,bot+p['canister_base']/2),'sector',bevel=0)
    b.annulus('canister_shell',cart,ri,ro,bot+p['canister_base'],bot+p['canister_base']+height,'equipment')
    top=bot+p['canister_base']+height
    b.cylinder('removable_lid',cart,ro,p['canister_lid'],(0,0,top+p['canister_lid']/2),'sector',bevel=.01)
    for zz in (bot+.30,top-.15):b.ring('shell_band_'+str(zz),cart,ro,zz,.035,'rail')
    for ob in cart.children_recursive:ob['maintenance_mobile']=True
    bpy.context.view_layer.update()
    return dict(parameters=p,deck_z=z,platform_area_m2=(x1-x0)*(y1-y0),bridge_points=[list(v) for v in path],
        cover_bounds=item_bounds('reactor.insulation_1'),cap_bounds=item_bounds('reactor.cap_1'),
        core_with_tubes_bounds=item_bounds('reactor.sector_1.core'),cart_total_height_m=top+p['canister_lid'],
        aisle_clear_width_m=y1-.025-p['cover_bay'][3],
        scope=p['scope'])


def check_maintenance(b,layout,result):
    """Selected actual-solid, aisle, pipe, component-fit and straight transport checks."""
    saved=[(c,c.hide_viewport) for c in bpy.data.collections]+[(o,o.hide_viewport) for o in bpy.data.objects]
    for ob,_ in saved:ob.hide_viewport=False
    bpy.context.view_layer.update()
    p=layout.MAINTENANCE;z=layout.CATWALK['deck_z'];own=[];obstacles=[];pipes=[]
    for ob in bpy.data.objects:
        if ob.hide_render or ob.get('maintenance_mobile'):continue
        if ob.type=='MESH' and ob.name.startswith(('equipment.','connections.','reactor.')):
            pts=[ob.matrix_world@v.co for v in ob.data.vertices]
            if not pts:continue
            data=(ob.name,pts,bounds(pts),BVHTree.FromPolygons(pts,[tuple(f.vertices) for f in ob.data.polygons]))
            (own if ob.name.startswith('equipment.maintenance_laydown.') else obstacles).append(data)
        elif ob.type=='CURVE' and (ob.get('process_route') or ob.get('air_insulated') or ob.get('utility_route') or ob.name.startswith('connections.')):
            for spline in ob.data.splines:
                pipes.append((ob.name,[ob.matrix_world@Vector(v.co[:3]) for v in spline.points],ob.data.bevel_depth))
    collisions=[];pairs=0
    for name,pts,bb,tree in own:
        for other,vs,bc,ot in obstacles:
            if other.startswith('equipment.reactor_catwalk.') and any(t in other for t in ('expanded_panel_','ring_beam_','radial_joist_','outer_','laydown_entry_jamb_')):continue
            if gapbox(bb,bc)>.001:continue
            pairs+=1
            if tree.overlap(ot):collisions.append((name,other))
        for other,pts,rad in pipes:
            if gapbox(bb,bounds(pts))>rad:continue
            if min(segment_box(a,c,*bb) for a,c in zip(pts,pts[1:]))<rad-.001:collisions.append((name,other))
    # Box envelope of clear aisle, plus a bridge headroom prism.
    x0,x1,y0,y1=p['platform_bounds']
    zones=[('aisle',[(x0+.04,.94),(x1-.06,.94),(x1-.06,y1-.06),(x0+.04,y1-.06)])]
    zones.append(('bridge',swept_outline([Vector(q) for q in result['bridge_points']],.59)))
    for name,poly in zones:
        vs,fs=prism_data(poly,z+.12,z+2.1);tree=BVHTree.FromPolygons(vs,fs);bb=bounds(vs)
        for other,pts,bc,ot in own+obstacles:
            if gapbox(bb,bc)>.001:continue
            if tree.overlap(ot):collisions.append((name,other))
    assert not collisions,collisions[:40]
    for key in ('cover','cap'):
        lo,hi=result[key+'_bounds'];a,c,d,e=p[key+'_bay']
        assert hi[0]-lo[0]<c-a-.10 and hi[1]-lo[1]<e-d-.10,(key,lo,hi)
    lo,hi=result['core_with_tubes_bounds']
    # A cylinder circumscribing the whole local bounding rectangle is conservative.
    diameter=math.hypot(hi[0]-lo[0],hi[1]-lo[1])
    assert diameter<p['canister_inside_diameter'] and hi[2]-lo[2]<p['canister_clear_height']
    width_gap=layout.ACCESS['width']-p['cart_width'];height_gap=layout.ACCESS['height']-result['cart_total_height_m']
    assert width_gap>.1 and height_gap>.1,(width_gap,height_gap)
    # Straight swept box includes the loading station, cart chassis and canister.
    inverse=bpy.data.objects['building.equipment_access'].matrix_world.inverted()
    lo=(p['loading_radius']-p['cart_length']/2,-p['cart_width']/2,.015)
    hi=(p['cart_radius']+p['cart_length']/2,p['cart_width']/2,result['cart_total_height_m'])
    path_clashes=[]
    vs,fs=prism_data([(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])],lo[2],hi[2])
    path_tree=BVHTree.FromPolygons([inverse.inverted()@Vector(v) for v in vs],fs)
    for name,pts,bb,tree in obstacles+own:
        local_pts=[inverse@q for q in pts];local=bounds(local_pts)
        if not all(local[1][i]>lo[i] and local[0][i]<hi[i] for i in range(3)):continue
        # Rings and routed jackets have broad boxes; check their actual surfaces.
        if path_tree.overlap(tree) or any(all(lo[i]<q[i]<hi[i] for i in range(3)) for q in local_pts):path_clashes.append(name)
    for name,pts,rad in pipes:
        pts=[inverse@q for q in pts]
        if min(segment_box(a,c,lo,hi) for a,c in zip(pts,pts[1:]))<rad:path_clashes.append(name)
    assert not path_clashes,path_clashes[:40]
    for ob,value in saved:ob.hide_viewport=value
    bpy.context.view_layer.update()
    return dict(platform_solid_pairs=pairs,collisions=collisions,straight_path_clashes=path_clashes,
        door_total_width_clearance_m=width_gap,door_height_clearance_m=height_gap,
        conservative_core_bundle_diameter_m=diameter,core_bundle_height_m=result['core_with_tubes_bounds'][1][2]-result['core_with_tubes_bounds'][0][2],
        scope='Selected geometry and straight envelope only; loaded crane sweep, structural loads, shielding/cooling and vehicle dynamics not qualified')
