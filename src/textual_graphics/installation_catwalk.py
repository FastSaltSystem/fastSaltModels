"""Provisional reactor catwalk, absorber equipment and dedicated service routes."""
import math
import bpy
from mathutils import Vector
from .installation_piping import fillet_path, shell_mesh
from .perforated import perforated_prism
from .installation_clearance import segdist, segment_box, bounds, gapbox


def xy(r,a,z=0):
    return (r*math.cos(math.radians(a)),r*math.sin(math.radians(a)),z)


def cut_many(b,objects,cutter):
    for obj in objects:
        copy=cutter.copy();cutter.users_collection[0].objects.link(copy)
        b.cut(obj,copy)
    bpy.data.objects.remove(cutter,do_unlink=True)


def expanded_panel(b,root,name,ri,ro,a0,a1,z,openings=()):
    """Open diamond lattice with physical rectangular strands, one mesh per panel."""
    verts=[];faces=[];nr=28;nt=18
    def point(i,j):
        return Vector(xy(ri+(ro-ri)*i/nr,a0+(a1-a0)*j/nt,z))
    def strand(p,q):
        for center,radius in openings:
            c=Vector(center);v=q-p;t=max(0,min(1,(c-p).dot(v)/v.length_squared))
            if (p+t*v-c).length<radius+.004:return
        direction=(q-p).normalized();side=Vector((-direction.y,direction.x,0))*.003
        k=len(verts)
        verts.extend(p0+off+Vector((0,0,h)) for h in (-.006,0) for p0,off in [(p,-side),(p,side),(q,side),(q,-side)])
        faces.extend(tuple(k+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    for i in range(nr):
        for j in range(nt):
            if (i+j)%2==0:strand(point(i,j),point(i+1,j+1))
            else:strand(point(i,j+1),point(i+1,j))
    return b.mesh(name,root,verts,faces,'catwalk_mesh')


def build_catwalk(b,layout):
    p=layout.CATWALK;z=p['deck_z'];ri=p['inner_radius'];ro=p['outer_radius']
    b.material('catwalk_mesh','#8F9EA6',metallic=.65,roughness=.45)
    b.material('catwalk_frame','#536774',metallic=.5,roughness=.4)
    b.material('catwalk_rail','#D8AD4F',metallic=.3,roughness=.4)
    root=b.assembly('equipment.reactor_catwalk','Reactor catwalk',(0,0,z))
    root['scope']='Provisional expanded-metal walkway and shared equipment frame; structural sizing and access design pending'
    root['deck_z']=z;root['inner_radius']=ri;root['outer_radius']=ro
    cfg=layout.ABSORBER_RESERVOIRS
    openings=[(xy(p['module_radius'],layout.REACTOR['rotation_degrees']+i*60+sign*offset,0),radius)
        for i in range(6) for sign in (-1,1) for offset,radius in [(cfg['module_angle_offset'],.18),(cfg['tank_angle_offset'],.21)]]
    for i in range(24):
        a=7.5+i*15
        expanded_panel(b,root,f'expanded_panel_{i+1}',ri+.015,ro-.015,a+.1,a+14.9,0,openings)
        beam=b.box(f'radial_joist_{i+1}',root,(ro-ri,.06,.20),xy((ri+ro)/2,a,-.13),'catwalk_frame')
        beam.rotation_euler.z=math.radians(a)
        # Inner/outer edge and an intermediate bearer support the mesh panels.
    for j,r in enumerate((ri,(ri+ro)/2,ro)):
        b.annulus(f'ring_beam_{j}',root,r-.045,r+.045,-.23,-.03,'catwalk_frame',steps=192)
    for i,a in enumerate(p['column_angles'],1):
        r=ro-.20;h=z-.23-layout.FLOOR_Z
        col=b.box(f'column_{i}',root,(.18,.18,h),xy(r,a,-.23-h/2),'catwalk_frame')
        col['catwalk_structure']=True
        b.box(f'baseplate_{i}',root,(.40,.40,.025),xy(r,a,layout.FLOOR_Z-z+.0125),'catwalk_frame')
        # Knee braces carry the deck without fastening to the pressure vessel.
        b.beam(f'knee_{i}',root,xy(r,a,-1.20),xy((ri+ro)/2,a,-.23),.045,'catwalk_frame')
    for ring,r in [('inner',ri),('outer',ro)]:
        for h in (.55,1.10):
            b.tube(f'{ring}_rail_{h}',root,[xy(r,a,h) for a in range(361)],.025,'catwalk_rail')
        b.annulus(f'{ring}_toeplate',root,r-.005,r+.005,0,.10,'catwalk_frame',steps=192)
        for i in range(24):b.beam(f'{ring}_post_{i}',root,xy(r,i*15,0),xy(r,i*15,1.10),.025,'catwalk_rail')
    modules=[];stations=[];cfg=layout.ABSORBER_RESERVOIRS
    b.material('absorber_jacket','#BBC4C8',metallic=.6,roughness=.35)
    b.material('absorber_insulation','#D4CBB3',roughness=.85)
    b.material('absorber_heater','#B86135',metallic=.4,roughness=.4)
    for i in range(1,7):
        a=layout.REACTOR['rotation_degrees']+(i-1)*60
        for pair,sign in [('centre',-1),('outer',1)]:
            index=(i-1)*2+(1 if sign<0 else 2)
            ma=a+sign*cfg['module_angle_offset'];ta=a+sign*cfg['tank_angle_offset']
            m=b.assembly(f'equipment.absorber_module_{index}','Absorber modules',xy(p['module_radius'],ma,z),ma)
            m['absorber_number']=i;m['pair']=pair;m['shared_support']=root.name
            module=layout.ABSORBER_MODULES;w,d,h=module['size']
            diameter=module['tank_diameter'];height=module['tank_height'];base=module['tank_base_z']
            for side in (-1,1):b.box(f'foot_{side}',m,(.12,.65,.12),(side*.30,0,.06),'catwalk_frame')
            v=b.cylinder('salt_vessel_envelope',m,diameter/2,height,(0,0,base+height/2),'absorber_module',vertices=40,bevel=.02*module['tank_linear_scale'])
            v['nominal_cylindrical_volume_m3']=math.pi*(diameter/2)**2*height
            b.box('control_enclosure',m,(w*.9,d*.9,module['control_height']),(0,0,base+height+module['control_height']/2),'absorber_module',.025)
            b.box('front_panel',m,(.03,d*.65,.45),(-w*.46,0,base+height+.80),'panel')
            t=b.assembly(f'equipment.absorber_reservoir_{index}','Absorber reservoirs',xy(p['module_radius'],ta,z),ta)
            t['absorber_number']=i;t['pair']=pair;t['scope']='Provisional heated reservoir envelope; capacity and heater duty unverified'
            rad=cfg['diameter']/2;ht=cfg['height'];bottom=cfg['bottom_above_deck'];ins=cfg['insulation'];clad=cfg['cladding']
            b.cylinder('salt_vessel_envelope',t,rad,ht,(0,0,bottom+ht/2),'absorber_module',vertices=48)
            b.annulus('insulation',t,rad,rad+ins,bottom-ins,bottom+ht+ins,'absorber_insulation',steps=48)
            b.annulus('jacket',t,rad+ins,rad+ins+clad,bottom-ins,bottom+ht+ins,'absorber_jacket',steps=48)
            # Insulated end covers have actual centred nozzle passages.
            for end,lev,port in [('bottom',bottom-ins,.025),('top',bottom+ht,.0125)]:
                b.annulus(end+'_insulation',t,port+.006,rad,lev,lev+ins,'absorber_insulation',steps=48)
                at=lev if end=='bottom' else lev+ins
                b.annulus(end+'_cladding',t,port+.006,rad+ins+clad,at,at+clad,'absorber_jacket',steps=48)
            for n in range(4):
                zz=bottom+.12+n*(ht-.24)/3
                heater=b.annulus(f'heater_band_{n}',t,rad,rad+.004,zz,zz+.035,'absorber_heater',steps=48)
                heater['scope']='Electric heating allowance only; no selected power or element specification'
            b.box('heater_terminal',t,(.12,.15,.18),(-rad-ins-.06,0,bottom+.22),'absorber_heater',.01)
            for xx in (-.30,.30):
                for yy in (-.30,.30):
                    b.box(f'support_{xx}_{yy}',t,(.055,.055,bottom-ins),(xx,yy,(bottom-ins)/2),'catwalk_frame')
            # Shared structural seats, with central service openings through deck mesh.
            for label,angle,width,depth,hole in [('module',ma,.97,1.02,.18),('reservoir',ta,1.12,1.12,.21)]:
                seat=perforated_prism(b,f'{label}_seat_{index}',root,
                    [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)],
                    [(0,0,hole)],-.06,0,'catwalk_frame',segments=32)
                seat.location=xy(p['module_radius'],angle,0);seat.rotation_euler.z=math.radians(angle)
                for side in (-1,1):
                    bearer=b.box(f'{label}_bearer_{index}_{side}',root,(ro-(ri+ro)/2+.10,.06,.20),
                        Vector(xy((ro+(ri+ro)/2)/2,angle,-.13))+Vector(xy(side*.43,angle+90,0)),'catwalk_frame')
                    bearer.rotation_euler.z=math.radians(angle)
            modules.append(m.name)
            stations.append(dict(index=index,absorber=i,pair=pair,module=m.name,tank=t.name,module_angle=ma,tank_angle=ta))
    return dict(parameters=p,absorber_module_parameters=layout.ABSORBER_MODULES,reservoir_parameters=cfg,module_objects=modules,stations=stations,routes=[],
        scope='Draft geometry; no structural, thermal, pressure, drainage-rate or storage qualification',
        limitations=['Reservoir capacity, heater duty and insulation thickness are provisional',
            'Frame load rating and complete access/egress assessment remain open',
            'Lift channelled insulation before disconnecting cap-side services; full crane sweep not checked',
            'Geometric fall does not establish hydraulic drainage or gas/pressure management'])


def connect_absorbers(b,layout,report):
    from .installation_bundles import connect_absorbers as build
    return build(b,layout,report)
