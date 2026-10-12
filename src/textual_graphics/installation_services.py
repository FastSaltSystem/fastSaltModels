"""Basic generator manifolds, common secondary headers and absorber module envelopes."""
import math
import bpy
from mathutils import Vector
from .installation_piping import insulated_route, move_collection


def half_pipe_collector(b,root,name,side,wall,half_length,z,radius,port_offset,connected_end,material,collector_scale=1.5, collector_radius=None):
    """Casing-mounted D collector, smoothly lofted to a matching round pipe.

    Secondary terminals turn outward; salt terminals remain axial. Shapes are
    visual envelopes, not pressure-boundary or hydraulic designs.
    """
    n=64;neck=1.2;collar=.08;steps=32
    cr=collector_radius if collector_radius is not None else radius*collector_scale
    outward=side>0
    start=connected_end*(half_length-neck)
    def section(t):
        blend=t*t*t*(10+t*(-15+6*t))
        if outward:
            # Cubic centreline has axial entry and radial exit tangents.
            p0=Vector((start,wall));p1=p0+Vector((.7,0))
            p3=Vector((half_length,port_offset-collar));p2=p3-Vector((0,.55))
            c=(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3
            tangent=3*(1-t)**2*(p1-p0)+6*(1-t)*t*(p2-p1)+3*t*t*(p3-p2)
            tangent.normalize();normal=Vector((-tangent.y,tangent.x))
        else:
            c=Vector((start+connected_end*(neck-collar)*t,wall+(port_offset-wall)*blend))
            normal=Vector((0,1))
        out=[]
        for i in range(n):
            a=2*math.pi*i/n
            lateral=(1-blend)*cr*max(0,math.cos(a))+blend*radius*math.cos(a)
            rr=(1-blend)*cr+blend*radius
            out.append((c.x+normal.x*lateral,side*(c.y+normal.y*lateral),z+rr*math.sin(a)))
        return out
    body=[(-connected_end*half_length,side*(wall+cr*max(0,math.cos(2*math.pi*i/n))),z+cr*math.sin(2*math.pi*i/n)) for i in range(n)]
    rings=[body]+[section(j/steps) for j in range(steps+1)]
    end=[(half_length-radius*math.cos(2*math.pi*i/n),side*port_offset,z+radius*math.sin(2*math.pi*i/n)) if outward else
         (connected_end*half_length,side*(port_offset+radius*math.cos(2*math.pi*i/n)),z+radius*math.sin(2*math.pi*i/n)) for i in range(n)]
    rings.append(end)
    if connected_end==-1:rings.reverse()
    verts=[v for ring in rings for v in ring];faces=[]
    for j in range(len(rings)-1):
        for i in range(n):
            k=(i+1)%n;faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
    if connected_end==-1:faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    else:faces.append(tuple(reversed(range(n))))
    if side==-1:faces=[tuple(reversed(f)) for f in faces]
    obj=b.mesh(name,root,verts,faces,material)
    for poly in obj.data.polygons:poly.use_smooth=len(poly.vertices)==4
    obj['shape']='Half-pipe collector with flat side attached directly to generator casing'
    obj['port_minus_local']=[-half_length,side*port_offset,z]
    obj['port_plus_local']=[half_length,side*port_offset,z]
    obj['connected_end']=connected_end;obj['mating_wall_y']=side*wall
    obj['collector_radius']=cr;obj['pipe_radius']=radius;obj['transition_length']=neck
    obj['terminal_axis_local']=[0,1,0] if outward else [connected_end,0,0]
    obj['ring_vertex_count']=n
    return obj


def steel_frame(b,root,name,width,depth,bottom,top,section=.20):
    """Open support frame: no solid plate across the pump's axial suction."""
    root[name+'_bottom_local']=bottom;root[name+'_top_local']=top
    assert top>bottom
    x=width/2-section/2;y=depth/2-section/2
    beam_depth=.25
    for i in (-1,1):
        for j in (-1,1):
            b.box(f'{name}.column{i}.{j}',root,(section,section,top-bottom-beam_depth),
                  (i*x,j*y,(bottom+top-beam_depth)/2),'rail')
            b.box(f'{name}.foot{i}.{j}',root,(section+.10,section+.10,.08),
                  (i*x,j*y,bottom+.04),'rail')
        b.box(f'{name}.beam_x{i}',root,(width,section,beam_depth),(0,i*y,top-beam_depth/2),'rail')
        b.box(f'{name}.beam_y{i}',root,(section,depth,beam_depth),(i*x,0,top-beam_depth/2),'rail')


def secondary_headers(b,layout):
    m=layout.MANIFOLDS;p=layout.SECONDARY
    radius=p['header_radius'];sg=layout.STEAM_GENERATORS['radius']
    # The three branch tees lie on the same open C-shaped header at each elevation.
    y=-m['half_length']; x=math.sqrt(radius**2-y*y)
    offset=math.degrees(math.atan2(y,x))
    angles=sorted(a+offset for a in layout.STEAM_GENERATORS['angles'])
    root=b.assembly('connections.secondary_headers','Secondary piping')
    result={'convention':'Salt manifolds face inward; water and steam manifolds face the building wall',
            'networks':[], 'manifold_ports':[]}
    for kind,z,diameter in [('water',layout.manifold_point('water')[2],p['water_header_diameter']),
                           ('steam',layout.manifold_point('steam')[2],p['steam_header_diameter'])]:
        spec=layout.PIPE_SPECS[kind+'_header']
        arc=[(radius*math.cos(math.radians(a)),radius*math.sin(math.radians(a)),z) for a in [angles[0]+(angles[-1]-angles[0])*j/180 for j in range(181)]]
        insulated_route(b,kind+'_common_header',root,arc,spec,kind,rounded=False)
        exit_angle=math.radians(p['exit_angle'])
        exit_points=[(rr*math.cos(exit_angle),rr*math.sin(exit_angle),z)
                     for rr in (radius,p['exit_radius'])]
        if kind=='water':
            ring_top=layout.AIR['fresh_z']+layout.AIR['concrete_height']/2
            high=ring_top+p['water_above_air_ring_clearance']+diameter/2
            rr=p['water_exit_riser_radius']
            exit_points=[exit_points[0],(rr*math.cos(exit_angle),rr*math.sin(exit_angle),z),
                         (rr*math.cos(exit_angle),rr*math.sin(exit_angle),high),
                         (p['exit_radius']*math.cos(exit_angle),p['exit_radius']*math.sin(exit_angle),high)]
        insulated_route(b,kind+'_building_connection',root,exit_points,spec,kind)
        network={'service':kind,'header_radius':radius,'z':z,'diameter':diameter,'spec':spec,
                 'start_angle':angles[0],'end_angle':angles[-1],'exit':exit_points[-1],
                 'building_connection_points':exit_points,'branches':[]}
        for i,angle in enumerate(layout.STEAM_GENERATORS['angles'],1):
            a=math.radians(angle)
            def world(q):
                xx,yy,zz=q
                return [xx*math.cos(a)-yy*math.sin(a),xx*math.sin(a)+yy*math.cos(a),zz]
            local=[layout.manifold_point(kind,1),(x,y,z)]
            points=[world(q) for q in local]
            insulated_route(b,f'{kind}_branch_{i}',root,points,layout.PIPE_SPECS[kind+'_branch'],kind,rounded=False)
            network['branches'].append({'generator':i,'points':points,'spec':layout.PIPE_SPECS[kind+'_branch']})
            result['manifold_ports'].append({'generator':i,'service':kind,
                'point':points[0],'local_side':y})
        result['networks'].append(network)
    return result


def check_services(b,layout,services):
    m=layout.MANIFOLDS
    for net in services['networks']:
        assert len(net['branches'])==3
        assert math.hypot(*net['exit'][:2])>layout.BUILDING['diameter']/2
        for a in layout.STACKS['angles']:
            t=math.radians(a);x=layout.STACKS['radius']*math.cos(t);y=layout.STACKS['radius']*math.sin(t)
            # Stack-to-outlet segment clearance in plan.
            e=Vector(net['exit'][:2]);s=e.normalized()*net['header_radius'];v=e-s;q=Vector((x,y))
            u=max(0,min(1,(q-s).dot(v)/v.length_squared))
            assert (q-(s+u*v)).length>layout.STACKS['tube_diameter']/2+net['diameter']/2
        for branch in net['branches']:
            end=branch['points'][-1]
            assert abs(math.hypot(*end[:2])-net['header_radius'])<1e-6
            assert abs(end[2]-net['z'])<1e-6
            angle=math.degrees(math.atan2(end[1],end[0]))%360
            assert net['start_angle']-1e-6<=angle<=net['end_angle']+1e-6
    water=next(net for net in services['networks'] if net['service']=='water')
    path=water['building_connection_points'];half=water['diameter']/2
    ring_top=layout.AIR['fresh_z']+layout.AIR['concrete_height']/2
    assert len(path)==4 and path[1][2]==path[0][2] and path[2][2]==path[3][2]
    assert math.hypot(*path[1][:2])+half<layout.BUILDING['diameter']/2-layout.BUILDING['wall_thickness']
    assert path[-1][2]-half-ring_top>=layout.SECONDARY['water_above_air_ring_clearance']-1e-6
    pipe=bpy.data.objects['connections.secondary_headers.water_building_connection']
    samples=[pipe.matrix_world @ Vector(v.co[:3]) for v in pipe.data.splines[0].points]
    for v in samples:
        if math.hypot(v.x,v.y)+half>=layout.AIR['concrete_inner_radius']:
            assert v.z-half>ring_top
    services['feedwater_wall_crossing']={'z':path[-1][2],'clearance_above_fresh_ring_m':path[-1][2]-half-ring_top}
    assert not any('perimeter_rail' in o.name or 'perimeter_post' in o.name or 'perimeter_midrail' in o.name for o in bpy.context.scene.objects)
    for i in range(1,4):
        gen=b.assemblies[f'equipment.steam_generator_{i}']
        assert abs(gen['casing_dimensions_m'][2]-17)<1e-6
        for kind in ('hot','cold','steam','water'):
            obj=bpy.data.objects[gen.name+'.'+kind+'_manifold']
            expected='inward' if kind in ('hot','cold') else 'outward'
            assert obj['side_as_seen_from_reactor']==expected
            assert obj.type=='MESH' and obj['shape'].startswith('Half-pipe')
            pts=[obj.matrix_world @ Vector(obj[key]) for key in ('port_minus_local','port_plus_local')]
            # The straight collector portion has a flat back exactly on the casing.
            wall=obj['mating_wall_y']
            assert sum(abs(v.co.y-wall)<1e-5 for v in obj.data.vertices)>=32
            assert not any(o.name.startswith(gen.name+'.'+kind+'_branch') for o in gen.children)
            spec=layout.PIPE_SPECS[kind if kind in ('hot','cold') else kind+'_branch']
            assert abs(obj['pipe_radius']-spec['jacket_od']/2)<1e-6
            assert abs(obj['collector_radius']-(m['collector_bare_diameters'][kind]/2+spec['insulation']))<1e-6
            assert min(v.co.z for v in obj.data.vertices)>0
            n=obj['ring_vertex_count'];vertices=obj.data.vertices
            terminal=range(n) if obj['connected_end']==-1 else range(len(vertices)-n,len(vertices))
            delta=n if obj['connected_end']==-1 else -n
            axis=Vector(obj['terminal_axis_local']);centre=Vector(obj['port_minus_local'] if obj['connected_end']==-1 else obj['port_plus_local'])
            for k in terminal:
                radial=vertices[k].co-centre
                assert abs(radial.dot(axis))<1e-5
                assert abs(radial.length-obj['pipe_radius'])<1e-5
                assert (vertices[k].co-vertices[k+delta].co).normalized().dot(axis)>.99999

            loop=b.assemblies[f'connections.loop_{i}']
            if kind=='hot':
                pipe=bpy.data.objects[loop.name+'.hot_outlet'];end=pipe.data.splines[0].points[-1]
                assert ((pipe.matrix_world @ Vector(end.co[:3]))-pts[0]).length<1e-5
            elif kind=='cold':
                pipe=bpy.data.objects[loop.name+'.cold_suction'];end=pipe.data.splines[0].points[0]
                assert ((pipe.matrix_world @ Vector(end.co[:3]))-pts[-1]).length<1e-5
            else:
                branch=next(n for n in services['networks'] if n['service']==kind)['branches'][i-1]
                assert (Vector(branch['points'][0])-pts[-1]).length<1e-5

    # Measure the clearance from actual world-space mesh bounds, including the new valve boxes.
    def bounds_z(name):
        obj=bpy.data.objects[name]
        zs=[(obj.matrix_world @ Vector(q)).z for q in obj.bound_box]
        return min(zs),max(zs)
    generator_top=max(bounds_z(f'equipment.steam_generator_{i}.air_butterfly_valve')[1] for i in range(1,4))
    for i in range(1,4):
        assert abs(bounds_z(f'equipment.steam_generator_{i}.air_butterfly_valve')[0]-bounds_z(f'equipment.steam_generator_{i}.top_cover')[1])<1e-5
    hoist_bottom=min(bounds_z('building.circular_crane.'+part)[0] for part in ('trolley','hoist_motor'))
    assert abs(hoist_bottom-generator_top-layout.CRANE['generator_clearance'])<1e-5
    services['hoist_clearance']={'generator_top_z':generator_top,'body_underside_z':hoist_bottom,
                                'clearance_m':hoist_bottom-generator_top,'reference':'underside of hoist body'}
    for i in range(1,len(layout.STACKS['angles'])+1):
        assert abs(bounds_z(f'building.stack_{i}.base')[0]-layout.FLOOR_Z)<1e-5
    assert layout.PUMPS['motor_bottom']+layout.PUMPS['motor_height']<layout.manifold_point('hot')[2]-.7
    assert abs(layout.PUMPS['suction_run_z']-layout.manifold_point('cold')[2])<1e-6
    # Separating-axis checks for pump bases versus storage tanks and generators.
    def rectangle(x,y,w,d,angle):
        t=math.radians(angle)
        return [(x+u*math.cos(t)-v*math.sin(t),y+u*math.sin(t)+v*math.cos(t))
                for u,v in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
    def intersects(a,b):
        for poly in (a,b):
            for p,q in zip(poly,poly[1:]+poly[:1]):
                axis=(p[1]-q[1],q[0]-p[0])
                aa=[v[0]*axis[0]+v[1]*axis[1] for v in a]
                bb=[v[0]*axis[0]+v[1]*axis[1] for v in b]
                if max(aa)<=min(bb) or max(bb)<=min(aa):return False
        return True
    obstacles=[]
    f=layout.FUEL_STORAGE
    for a in f['pair_angles']:
        t=math.radians(a)
        obstacles.append(rectangle(f['radius']*math.cos(t),f['radius']*math.sin(t),4.3,4.25,a))
    x,y,_=layout.SECTOR_STORAGE['position']
    obstacles.append(rectangle(x,y,3.55,2.55,layout.SECTOR_STORAGE['angle']))
    for a in layout.STEAM_GENERATORS['angles']:
        t=math.radians(a);r=layout.STEAM_GENERATORS['radius']
        obstacles.append(rectangle(r*math.cos(t),r*math.sin(t),4.1,4.1,a))
    for i,a in enumerate(layout.STEAM_GENERATORS['angles'],1):
        pump=b.assemblies[f'equipment.coolant_pump_{i}']
        base=rectangle(pump.location.x,pump.location.y,3.2,3.2,a)
        assert not any(intersects(base,o) for o in obstacles), f'Pump {i} overlaps a storage opening or generator base'
        assert all(math.hypot(*q)<layout.BUILDING['diameter']/2-layout.BUILDING['wall_thickness'] for q in base)
    # Check actual world-space support contacts and inward/outward manifold placement.
    def mesh_bottom(obj):
        return min((obj.matrix_world @ Vector(q)).z for q in obj.bound_box)
    for root in b.assemblies.values():
        category=root['category']
        if category=='Fuel storage':
            assert abs(mesh_bottom(bpy.data.objects[root.name+'.closed_tank'])-layout.FLOOR_Z)<1e-5
        if category=='Coolant storage':
            assert abs(mesh_bottom(bpy.data.objects[root.name+'.closed_tank'])-layout.FLOOR_Z)<1e-5
        if category=='Steam generators':
            assert abs(mesh_bottom(bpy.data.objects[root.name+'.casing'])-layout.FLOOR_Z)<1e-5
            assert not any('.support.' in o.name for o in root.children)
        if category=='Coolant pumps':
            assert abs(root['support_bottom_z']-layout.FLOOR_Z)<1e-6
            legs=[o for o in root.children if '.support.column' in o.name]
            assert len(legs)==4
            assert all(abs(mesh_bottom(o)-layout.FLOOR_Z)<1e-5 for o in legs)
    for i in range(1,4):
        root=b.assemblies[f'equipment.steam_generator_{i}']
        a=math.radians(layout.STEAM_GENERATORS['angles'][i-1]);radial=Vector((math.cos(a),math.sin(a),0))
        for kind in ('hot','cold','steam','water'):
            obj=bpy.data.objects[root.name+'.'+kind+'_manifold']
            point=obj.matrix_world @ Vector(obj['port_minus_local'])
            displacement=(point-root.location).dot(radial)
            assert displacement<0 if kind in ('hot','cold') else displacement>0
    assert all(v.z-layout.PIPE_SPECS['cold']['jacket_od']/2>layout.FLOOR_Z
               for i in range(1,4)
               for o in [bpy.data.objects[f'connections.loop_{i}.cold_suction']]
               for v in [o.matrix_world @ Vector(p.co[:3]) for p in o.data.splines[0].points])
    if 'catwalk' in services:
        assert not any(o['category']=='Absorber supports' for o in b.assemblies.values())
        modules=[o for o in b.assemblies.values() if o['category']=='Absorber modules']
        assert len(modules)==12
        assert all(o['shared_support']=='equipment.reactor_catwalk' for o in modules)
        assert all(abs(o.location.z-layout.CATWALK['deck_z'])<1e-5 for o in modules)
    assert 'building.reactor_foundation.well_support' not in bpy.data.objects
    return ['Fuel and coolant tank bottoms and support column feet meet the sub-floor',
            'Generator casings meet floor; cold manifolds align with two-bend suction runs; absorber modules share the reactor catwalk',
            'Pump foundations clear storage tanks, generator bases and outer wall',
            'Three 17 m generator casings; valve boxes seated on roofs; measured 5 m from valve tops to hoist body underside',
            'The single stack base meets the equipment floor elevation',
            'Twelve insulated half-pipe collectors; round collars match calculated branch jacket diameters and axes',
            'Salt manifolds face reactor; steam/water manifolds face wall',
            'Both common headers connect all three generators and terminate outside building',
            'Feedwater rises inside and crosses the wall at the configured insulated clearance above the fresh-air ring',
            'Twelve absorber modules on shared catwalk; old paired stands absent; catwalk guardrails are local to reactor']
