"""Six removable thermal cassettes with captive vertical pickup stems."""
import math
import bpy
from mathutils import Vector
from .perforated import perforated_prism,inside_polygon
from .reactor_lifting import lifting_hook,build_two_bar_head,check_common_head
from .reactor_checks import closed_mesh


def materials(b):
    for n,c,m,r in [('stainless','#B8C7CF',.65,.3),('hot_frame','#AA7048',.6,.4),
                    ('cold_frame','#587D8D',.55,.35),('wool','#C8B782',0,.95),
                    ('wool_alt','#DDCDA0',0,.95),('links','#384D59',.65,.3),
                    ('indicator','#E5AD36',.4,.4),('seal','#716E62',0,.9),
                    ('zirconia','#F5EFE0',0,.3),('context','#8B969F',.15,.7),('background','#E8EEF1',0,.8),
                    ('steel','#7C919C',.55,.35),('handling_tool','#B29A54',.5,.35),
                    ('lock_gold','#DEA345',.5,.3),('dark','#253543',.3,.5)]:
        b.material(n,c,metallic=m,roughness=r)


def keyed_plate(b,name,parent,x,y,bottom,top,width,depth,slot,mat):
    obj=b.box(name,parent,(width,depth,top-bottom),(x,y,(bottom+top)/2),mat)
    cutter=b.box(name+'_slot',parent,(slot,slot,top-bottom+.04),(x,y,(bottom+top)/2),None)
    b.cut(obj,cutter)
    return obj


def pickup(b,cfg,parent,index,x,y,station,category='Sliding pickups'):
    c=cfg.COVER
    fixed=b.assembly(parent.name+f'.guide_{index}',category);fixed.parent=parent
    plate=keyed_plate(b,'guide',fixed,x,y,c['guide_bottom'],c['guide_top'],.12,.10,c['guide_slot'],'cold_frame')
    plate['role']='cool_side_keyed_guide'
    mover=b.assembly(parent.name+f'.slider_{index}',category);mover.parent=parent
    mover['role']='captive_vertical_pickup';mover['travel_m']=c['travel'];mover['station']=station
    top=c['frame_bottom']-c['travel'];bottom=top-c['shoulder_thickness']
    b.box('lifting_shoulder',mover,(c['shoulder_width'],c['shoulder_depth'],c['shoulder_thickness']),(x,y,(top+bottom)/2),'links')['role']='lifting_shoulder'
    b.box('square_stem',mover,(c['stem_width'],c['stem_width'],c['hook_foot']-top),(x,y,(c['hook_foot']+top)/2),'links')
    b.box('rest_collar',mover,(.074,.066,c['collar_thickness']),(x,y,c['guide_top']+c['collar_thickness']/2),'stainless')
    # A band emerges above the stationary guide as load is taken up.
    b.box('stroke_band',mover,(c['stem_width']+.002,c['stem_width']+.002,.022),(x,y,c['guide_top']-.012),'indicator')
    hook=lifting_hook(b,'external_hook',mover,(x,y,c['hook_foot']),'insulation_cover_pickup',cfg.reactor,station)
    hook.rotation_euler.z=math.pi if station else 0
    return mover,hook,fixed


def mesh_grid(b,root,poly,z,c,n):
    r=c['radius'];pitch=c['mesh_pitch'];shaft=.102
    def inside(x,y):
        return inside_polygon((x,y),poly) and all(math.hypot(x-a,y-d)>radius for a,d,radius in root['clearance_holes'])
    # Break wires around every travelling shoulder sleeve; no mesh/stem contact.
    for axis in (0,1):
        for i in range(-int(r/pitch),int(r/pitch)+1):
            fixed=i*pitch;run=[];part=0
            for j in range(401):
                v=-r+2*r*j/400;x,y=(v,fixed) if axis==0 else (fixed,v)
                if inside(x,y):run.append((x,y,z))
                elif run:
                    if len(run)>1:b.beam(f'grid{n}_{axis}_{i}_{part}',root,run[0],run[-1],c['mesh_wire_radius'],'stainless')
                    run=[];part+=1
            if len(run)>1:b.beam(f'grid{n}_{axis}_{i}_{part}',root,run[0],run[-1],c['mesh_wire_radius'],'stainless')


def build_sector(b,cfg,number,with_grid=True):
    c=cfg.COVER;poly=cfg.outline();pts=cfg.points();a=30+(number-1)*60
    root=b.assembly(f'cover.sector_{number}','Cassette assemblies',angle=a)
    root['role']='removable_insulation_cassette';root['sector_number']=number
    shell=b.assembly(root.name+'.shell','Stainless skins');shell.parent=root
    body=b.assembly(root.name+'.insulation','Stone wool layers');body.parent=root
    inner=b.assembly(root.name+'.inner_frame','Internal carrying frames');inner.parent=root
    outer=b.assembly(root.name+'.outer_frame','Outer skin supports');outer.parent=root
    grid=b.assembly(root.name+'.grids','Intermediate wire grids');grid.parent=root;grid['clearance_holes']=[list(p) for p in cfg.wool_holes()]
    holes=cfg.wool_holes()
    for n in range(c['layers']):
        perforated_prism(b,f'wool_layer_{n+1}',body,poly,holes,n*.1+.002,(n+1)*.1+.002,'wool' if n%2==0 else 'wool_alt')
        if with_grid and n<c['layers']-1:mesh_grid(b,grid,poly,(n+1)*.1+.003,c,n)
    perforated_prism(b,'top_sheet',shell,poly,[(x,y,.030) for x,y,_ in pts],.520,.522,'stainless')
    perforated_prism(b,'hot_face_liner',shell,poly,[(x,y,.033) for x,y in cfg.post_points()],0,c['liner'],'stainless')
    # Cool outer skirt stops above the independent lower hot-face edge.
    b.annulus('outer_skirt',shell,c['radius']+.001,c['radius']+.003,.075,.522,'stainless',start=-30+math.degrees(math.asin(c['seam_half_gap']/c['radius'])),end=30-math.degrees(math.asin(c['seam_half_gap']/c['radius'])),steps=64)
    for sign in (-1,1):
        x1,y1=poly[0];x2,y2=poly[1 if sign<0 else -1]
        obj=b.box(f'side_skirt_{sign}',shell,(math.hypot(x2-x1,y2-y1),.002,.447),((x1+x2)/2,(y1+y2)/2,.2985),'stainless')
        obj.rotation_euler.z=math.atan2(y2-y1,x2-x1)
    # Upper rails receive pickup loads; separate hollow posts carry resting loads.
    xs=sorted(set(x for x,y,st in pts));maxy=max(abs(y) for x,y,st in pts)
    rail_z=c['frame_bottom']+c['frame_height']/2
    for sign in (-1,1):
        b.box(f'load_rail_{sign}',inner,(xs[1]-xs[0]+.38,.045,.06),((xs[0]+xs[1])/2+.05,sign*(maxy+.15),rail_z),'hot_frame')
    hanger_x=[x+.100 for x in xs];hanger_y=.950
    # Each grid and the bottom liner have their own edge frame and crossmembers.
    # Rods pass through collars at each level; wool is not part of the load path.
    levels=[-.0125]+[(n+1)*.1+.003-.0125 for n in range(4)]
    for n,z in enumerate(levels):
        b.annulus(f'tray_{n}_rim',inner,c['radius']-.050,c['radius']-.034,z-.0125,z+.0125,'hot_frame',start=-30,end=30,steps=64)
        for sign in (-1,1):
            p1=(.10,sign*.018,z);p2=((c['radius']-.042)*math.cos(math.pi/6),sign*(c['radius']-.042)*.5,z)
            dx=p2[0]-p1[0];dy=p2[1]-p1[1]
            edge=b.box(f'tray_{n}_edge_{sign}',inner,(math.hypot(dx,dy),.016,.025),((p1[0]+p2[0])/2,(p1[1]+p2[1])/2,z),'hot_frame')
            edge.rotation_euler.z=math.atan2(dy,dx)
        for x in hanger_x:
            span=x*math.tan(math.pi/6)-.030
            b.box(f'tray_{n}_cross_{x}',inner,(.016,2*span,.025),(x,0,z),'hot_frame')
            for sign in (-1,1):
                b.cylinder(f'tray_{n}_collar_{x}_{sign}',inner,.014,.008,(x,sign*hanger_y,z-.0165),'hot_frame',bevel=0)
    for x in hanger_x:
        b.box(f'hanger_bridge_{x}',inner,(.035,2*hanger_y+.05,.025),(x,0,c['frame_bottom']+.0275),'hot_frame')
        for sign in (-1,1):
            b.beam(f'tension_hanger_{x}_{sign}',inner,(x,sign*hanger_y,-.035),(x,sign*hanger_y,c['frame_bottom']+.055),c['hanger_diameter']/2,'links')['role']='tension_hanger'
            b.cylinder(f'hanger_top_nut_{x}_{sign}',inner,.012,.012,(x,sign*hanger_y,c['frame_bottom']+.046),'links',vertices=6,bevel=0)
    # Crossed wire bracing connects tray/frame nodes, not the outer shell.
    for sign in (-1,1):
        for a,d in ((0,1),(1,0)):
            b.beam(f'diagonal_wire_{sign}_{a}',inner,(hanger_x[a],sign*hanger_y,.010),(hanger_x[d],sign*hanger_y,c['frame_bottom']),.002,'links')
    for i,(x,y) in enumerate(cfg.post_points(),1):
        bottom=c['zirconia_top']+.010;top=rail_z-.030
        post=b.box(f'compression_post_{i}',inner,(c['post_width'],c['post_width'],top-bottom),(x,y,(top+bottom)/2),'hot_frame')
        void=b.box(f'post_void_{i}',inner,(c['post_width']-2*c['post_wall'],c['post_width']-2*c['post_wall'],top-bottom+.02),(x,y,(top+bottom)/2),None);b.cut(post,void)
        post['role']='resting_compression_post'
        b.box(f'ceramic_bearing_foot_{i}',inner,(.070,.070,.010),(x,y,c['zirconia_top']+.005),'hot_frame')['role']='removable_upper_ceramic_bearing'
    movers=[];hooks=[]
    for i,(x,y,station) in enumerate(pts,1):
        keyed_plate(b,f'bearing_{i}',inner,x,y,c['frame_bottom'],c['frame_bottom']+c['frame_height'],.18,.16,c['frame_slot'],'hot_frame')
        # Rail-to-bearing arms meet the bearing pad without crossing its slot.
        end=math.copysign(maxy+.15,y);start=y+math.copysign(.08,y)
        b.box(f'bearing_arm_{i}',inner,(.10,abs(end-start),.03),(x,(start+end)/2,rail_z),'hot_frame')
        moving,hook,fixed=pickup(b,cfg,root,i,x,y,station)
        movers.append(moving);hooks.append(hook)
        b.box(f'upper_rail_{i}',outer,(.16,.07,.022),(x,y+math.copysign(.10,y),.531),'cold_frame')
        # Two slender stand-offs connect guide plate edges to its outer rail.
        for dx in (-.045,.045):
            b.box(f'guide_tab_{i}_{dx}',outer,(.015,.075,.015),(x+dx,y+math.copysign(.0675,y),.5425),'cold_frame')
        # Provisional long-path ties carry skin/grid loads. They remain heat paths.
        y0=end; y1=end+math.copysign(.10,y)
        b.tube(f'skin_tie_{i}',outer,[(x,y0,rail_z),(x+.16,y0,rail_z),(x+.16,y1,.49),(x,y1,.52),(x,y+.10*math.copysign(1,y),.52)],.004,'cold_frame')
    b.box('upper_crossrail',outer,(xs[1]-xs[0]+.20,.04,.02),((xs[0]+xs[1])/2,0,.532),'cold_frame')
    for x in xs:b.box(f'upper_transverse_{x}',outer,(.035,2*maxy+.32,.02),(x,0,.532),'cold_frame')
    # Flexible butt joint strip: compressible filler, not a rigid overlap.
    seam=b.box('compressible_seam',body,(c['radius']-.10,.010,.49),(c['radius']*.5*math.cos(math.pi/6),c['radius']*.5*.5,.255),'seal')
    seam.rotation_euler.z=math.pi/6
    return {'root':root,'sliders':movers,'hooks':hooks,'shell':shell,'body':body,'grid':grid}


def ceramic_seat(b,root,c,x,y,index):
    top=c['zirconia_top'];bottom=top-c['zirconia_height'];r=c['zirconia_diameter']/2
    puck=b.cylinder(f'zirconia_{index}',root,r,c['zirconia_height'],(x,y,(top+bottom)/2),'zirconia',vertices=64,bevel=0)
    puck['role']='fixed_zirconia_compression_break'
    puck['scope']='Provisional geometry; grade and hot-service qualification required'
    b.cylinder(f'lower_seat_{index}',root,.040,.010,(x,y,bottom-.005),'context',vertices=64,bevel=0)
    cup=b.annulus(f'seat_cup_{index}',root,r+.001,r+.008,bottom,bottom+.010,'context');cup.location.x=x;cup.location.y=y
    b.box(f'interface_pedestal_{index}',root,(.070,.070,.10),(x,y,bottom-.060),'context')['scope']='Attachment to reactor support structure reserved, not designed'


def support_detail(b,cfg):
    c=cfg.COVER;root=b.assembly('support_detail','Support section')
    ceramic_seat(b,root,c,0,0,1)
    b.box('upper_foot',root,(.070,.070,.010),(0,0,c['zirconia_top']+.005),'hot_frame')
    top=c['frame_bottom']+.020-.030;bottom=c['zirconia_top']+.010
    post=b.box('hollow_post',root,(.040,.040,top-bottom),(0,0,(top+bottom)/2),'hot_frame')
    cut=b.box('post_void',root,(.036,.036,top-bottom+.02),(0,0,(top+bottom)/2),None);b.cut(post,cut)
    b.box('upper_frame',root,(.24,.045,.060),(0,0,c['frame_bottom']+.020),'hot_frame')
    # A nearby suspended tray illustrates the separate wool support path.
    b.beam('tension_rod',root,(.10,0,-.03),(.10,0,.465),.003,'links')
    for n,z in enumerate((0,.10,.20,.30,.40)):
        b.box(f'tray_{n}',root,(.14,.06,.016),(.14,0,z-.008),'stainless')
        b.cylinder(f'collar_{n}',root,.012,.008,(.10,0,z-.020),'links',bevel=0)
        b.box(f'wool_{n}',root,(.09,.05,.083),(.16,.006,z+.0415),'wool' if n%2==0 else 'wool_alt')
    return root


def build(b,cfg):
    materials(b);c=cfg.COVER
    sectors=[build_sector(b,cfg,n,with_grid=n==c['lift_sector']) for n in range(1,7)]
    context=b.assembly('reference.spider','Reactor interface reference')
    d=cfg.reactor.dimensions();z=-.75
    b.annulus('outer_ring',context,d['cap_opening_radius'],d['hot_outer_radius']+.12,z-.15,z,'context')
    b.cylinder('hub',context,d['spider_hub_radius'],.15,(0,0,z-.075),'context',vertices=6,bevel=0)
    for i in range(6):
        a=math.radians(i*60);length=d['cap_opening_radius']-d['spider_hub_radius']*.866
        centre=d['spider_hub_radius']*.866+length/2
        leg=b.box(f'leg_{i+1}',context,(length,d['spider_beam_width'],.15),(centre*math.cos(a),centre*math.sin(a),z-.075),'context')
        leg.rotation_euler.z=a
        # Fixed seats and ceramic pucks remain behind when a cassette is removed.
        support=b.assembly(f'reference.seats_{i+1}','Zirconia seating interfaces',angle=30+i*60)
        for j,(x,y) in enumerate(cfg.post_points(),1):
            ceramic_seat(b,support,c,x,y,j)
    # Common head is reused with its 750 mm pitch; translate to the cover centroid.
    owner=b.assembly('cover.tool_reference','Remote lifting tools')
    owner.rotation_euler.z=0
    head=build_two_bar_head(b,cfg.reactor,{},owner,'cover.common_head','cap',c['hook_foot']+c['travel'])
    shift=2*c['radius']/math.pi-sum(cfg.reactor.LIFTING_INTERFACE['stations'])/2
    head.location.x=shift*math.cos(math.pi/6);head.location.y=shift*.5
    return sectors,head


def set_pose(sectors,head,cfg,stroke=0,lift=0):
    for sector in sectors:
        selected=sector['root']['sector_number']==cfg.COVER['lift_sector']
        sector['root'].location.z=lift if selected else 0
        for slider in sector['sliders']:slider.location.z=cfg.COVER['travel']*stroke if selected else 0
    # Lift-tool z driver otherwise controls unloaded 88 mm docking motion.
    head.location.z=lift+cfg.COVER['travel']*(stroke-1)
    bpy.context.view_layer.update()


def detail(b,cfg):
    """Two explanatory sections from the same pickup dimensions, at true scale."""
    states=[];c=cfg.COVER
    for n,stroke in enumerate((0,1)):
        root=b.assembly(f'detail.{"resting" if n==0 else "carrying"}','Catch sections',position=(n*.70,0,0))
        keyed_plate(b,'frame_bearing',root,0,0,c['frame_bottom'],c['frame_bottom']+c['frame_height'],.24,.16,c['frame_slot'],'hot_frame')
        # Cutaway halves expose the stem and shoulder rather than hiding them.
        obj=bpy.data.objects[root.name+'.frame_bearing'];cut=b.box('section_cut',root,(.6,.3,1),(0,-.15,.3),None);b.cut(obj,cut)
        b.box('top_skin',root,(.30,.04,.002),(0,.10,.521),'stainless')
        b.box('wool_left',root,(.07,.07,.50),(-.115,.075,.252),'wool')
        b.box('wool_right',root,(.07,.07,.50),(.115,.075,.252),'wool')
        mover,hook,fixed=pickup(b,cfg,root,1,0,0,0,'Catch sections')
        mover.location.z=stroke*c['travel']
        guide=bpy.data.objects[fixed.name+'.guide'];cut=b.box('guide_section_cut',root,(.6,.30,1),(0,-.15,.3),None);b.cut(guide,cut)
        b.beam('travel_line',root,(.20,-.02,c['frame_bottom']-c['travel']),( .20,-.02,c['frame_bottom']),.002,'indicator')
        for z in (c['frame_bottom']-c['travel'],c['frame_bottom']):b.beam(f'tick_{z}',root,(.18,-.02,z),(.22,-.02,z),.002,'indicator')
        states.append(root)
    return states


def checks(b,sectors,head,cfg):
    c=cfg.COVER;report=cfg.summary();pts=cfg.points();checks=[]
    def check(name,condition):
        assert condition,name
        checks.append(name)
    check('Six cassettes; four captive sliders per cassette',len(sectors)==6 and all(len(s['sliders'])==4 for s in sectors))
    check('Shoulders cannot pull through frame slots',c['shoulder_width']>c['frame_slot'] and c['shoulder_depth']>c['frame_slot'])
    check('Square stem clears both guides and frame',c['stem_width']<min(c['guide_slot'],c['frame_slot']))
    check('Hook foot clears stop collar at rest',c['hook_foot']>c['guide_top']+c['collar_thickness'])
    for step in range(21):
        stroke=step/20;set_pose(sectors,head,cfg,stroke,0)
        for slider in sectors[0]['sliders']:
            shoulder=bpy.data.objects[slider.name+'.lifting_shoulder']
            top=max(v.co.z for v in shoulder.data.vertices)+shoulder.location.z+slider.location.z
            check(f'Slider {slider.name.rsplit("_",1)[-1]} stroke {step}: nonnegative bearing gap',c['frame_bottom']-top>=-1e-7)
            if step==20:check('Loaded shoulder contacts bearing '+slider.name,abs(top-c['frame_bottom'])<1e-7)
    # The perimeter and every hook remain within the assigned wedge at all lift heights.
    for x,y,st in pts:
        check(f'Pickup {x:.3f},{y:.3f} lies within sector',inside_polygon((x,y),cfg.outline()))
        check(f'Pickup {x:.3f},{y:.3f} within existing bar length',abs(y)+cfg.reactor.LIFTING_INTERFACE['hook_thickness']/2<cfg.reactor.LIFTING_INTERFACE['bar_half_lengths'][st]-.008)
    set_pose(sectors,head,cfg,1,0)
    bars=sorted([o for o in head.children if o.get('role')=='common_pickup_bar'],key=lambda o:o['station_index'])
    for hook in sectors[0]['hooks']:
        bar=bars[hook['station_index']]
        hc=hook.matrix_world @ Vector((0,0,cfg.reactor.LIFTING_INTERFACE['loaded_bar_height']))
        bc=bar.matrix_world @ Vector(bar['closed_local_centre']);axis=bar.matrix_world.to_3x3() @ Vector((0,1,0));v=hc-bc
        check('Loaded common-tool alignment '+hook.name,(v-axis*v.dot(axis)).length<2e-5)
    obstacles=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('cover.sector_1.shell.','cover.sector_1.outer_frame.','cover.sector_1.guide_'))]
    for stroke in (0,1):
        set_pose(sectors,head,cfg,stroke,0)
        check_common_head(head,sectors[0]['hooks'],cfg.reactor,obstacles)
        checks.append(f'Existing head sampled docking/release and lip capture, stroke={stroke}; {len(obstacles)} external obstacles')
    check('Four compression breaks per cassette',len([o for o in bpy.data.objects if o.get('role')=='fixed_zirconia_compression_break' and o.name.startswith('reference.')])==24)
    check('Shallow metal cups do not reach upper bearing plates',c['zirconia_height']-.010>0)
    check('Post clearances exceed square post diagonal',.033>c['post_width']/math.sqrt(2))
    check('Upper frame remains below wool top',c['frame_bottom']+c['frame_height']<c['insulation'])
    check('Four tension hangers per cassette',len([o for o in bpy.data.objects if o.get('role')=='tension_hanger'])==24)
    # Check closed manifold meshes, including every keyed bearing and guide.
    count=0
    for obj in bpy.data.objects:
        if obj.type=='MESH':closed_mesh(obj);count+=1
    checks.append(f'{count} closed manifold meshes')
    set_pose(sectors,head,cfg,0,0)
    report['passed_checks']=checks
    report['not_checked']=['Rated lifting loads, uneven sharing, welds and fatigue','Thermal bridges, radiation heating and actual hook temperature','Gravity return, binding, wear, contamination and material compatibility','External service tube routing, seating attachment and whole-reactor extraction','Full installed reactor/service and crane swept-volume checks','Structural capacity of suspended grid trays, bracing, posts and ceramic contacts; staggered wool joints']
    return report
