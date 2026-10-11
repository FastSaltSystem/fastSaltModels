"""Separate pressure-pipe and insulation meshes with inspectable route guides."""
import math
import bpy
from mathutils import Vector, Quaternion


def move_collection(b,obj,name):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    b.collection(name).objects.link(obj)


def fillet_path(points,desired):
    pts=[Vector(q) for q in points]
    pts=[q for i,q in enumerate(pts) if not i or (q-pts[i-1]).length>1e-6]
    result=[pts[0]];radii=[]
    for i,(a,p,c) in enumerate(zip(pts,pts[1:],pts[2:]),1):
        u=(a-p).normalized();v=(c-p).normalized()
        theta=math.acos(max(-1,min(1,u.dot(v))))
        if abs(theta-math.pi)<1e-5:result.append(p);continue
        assert theta>1e-4, 'Reversing pipe route'
        trim=min(desired/math.tan(theta/2),(a-p).length*(.95 if i==1 else .49),
                 (c-p).length*(.95 if i==len(pts)-2 else .49))
        radius=trim*math.tan(theta/2);radii.append(radius)
        centre=p+(u+v).normalized()*(radius/math.sin(theta/2))
        start=p+u*trim;end=p+v*trim
        axis=(start-centre).cross(end-centre).normalized()
        sweep=(start-centre).angle(end-centre)
        result.extend(centre+Quaternion(axis,sweep*j/20) @ (start-centre) for j in range(21))
    result.append(pts[-1])
    return result,radii


def shell_mesh(b,name,root,points,outer,inner,material):
    verts=[];faces=[];sides=48;normal=None;n=len(points)
    for i,p in enumerate(points):
        tangent=(points[min(n-1,i+1)]-points[max(0,i-1)]).normalized()
        if normal is None:
            ref=min((Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))),key=lambda q:abs(tangent.dot(q)))
            normal=tangent.cross(ref).normalized()
        else:normal=(normal-tangent*normal.dot(tangent)).normalized()
        binormal=tangent.cross(normal).normalized()
        for radius in (outer,inner):
            verts.extend(p+radius*(normal*math.cos(j*2*math.pi/sides)+binormal*math.sin(j*2*math.pi/sides)) for j in range(sides))
    for i in range(n-1):
        for layer in (0,1):
            for j in range(sides):
                a=i*2*sides+layer*sides+j;c=i*2*sides+layer*sides+(j+1)%sides
                face=(a,c,c+2*sides,a+2*sides)
                faces.append(face if layer==0 else tuple(reversed(face)))
    for i in (0,n-1):
        for j in range(sides):
            a=i*2*sides+j;c=i*2*sides+(j+1)%sides
            face=(a,c,c+sides,a+sides);faces.append(tuple(reversed(face)) if i==0 else face)
    obj=b.mesh(name,root,verts,faces,material)
    for poly in obj.data.polygons:poly.use_smooth=poly.index<(n-1)*2*sides
    obj['bore_diameter_m']=inner*2;obj['outside_diameter_m']=outer*2
    obj['radial_thickness_m']=outer-inner
    return obj


def insulated_route(b,name,root,points,spec,material,rounded=True):
    path,radii=fillet_path(points,max(1.5,spec['jacket_od'])) if rounded else ([Vector(q) for q in points],[])
    guide=b.tube(name,root,path,spec['jacket_od']/2,material)
    guide['pipe_spec']=dict(spec);guide['process_route']=True
    guide['minimum_bend_radius_m']=min(radii) if radii else 1e6
    guide['service']=material
    move_collection(b,guide,'Pipe route guides');guide.hide_render=True;guide.hide_set(True)
    metal=shell_mesh(b,name+'.metal',root,path,spec['bare_od']/2,spec['bore']/2,'rail')
    move_collection(b,metal,'Pressure pipe metal')
    insulation=shell_mesh(b,name+'.insulation',root,path,spec['jacket_od']/2,spec['bare_od']/2,material)
    move_collection(b,insulation,'Pipe insulation')
    for obj in (metal,insulation):obj['route_object']=guide.name;obj['service']=material
    return guide


def check_piping(b,layout,services):
    bpy.context.view_layer.update()
    routes=[o for o in bpy.context.scene.objects if o.get('process_route')]
    summary=[]
    for obj in routes:
        spec=obj['pipe_spec'];radius=spec['jacket_od']/2
        metal=bpy.data.objects[obj.name+'.metal'];ins=bpy.data.objects[obj.name+'.insulation']
        assert abs(metal['bore_diameter_m']-spec['bore'])<1e-8
        assert abs(metal['radial_thickness_m']-spec['wall'])<1e-8
        assert abs(ins['radial_thickness_m']-spec['insulation'])<1e-8
        assert obj['minimum_bend_radius_m']>radius, (obj.name,'bend too tight',obj['minimum_bend_radius_m'],radius)
        pts=[obj.matrix_world @ Vector(q.co[:3]) for q in obj.data.splines[0].points]
        floor=min(q.z for q in pts)-radius-layout.FLOOR_Z
        assert floor>0,(obj.name,'insulation at floor',floor)
        summary.append({'object':obj.name,'service':obj['service'],'spec':dict(spec),
                        'minimum_bend_radius_m':obj['minimum_bend_radius_m'] if obj['minimum_bend_radius_m']<1e5 else None,
                        'floor_clearance_m':floor})
    assert len(routes)==19, len(routes)
    # Plan radius applies to complete circular header envelopes, beyond sampled extrema.
    wall_clearance=(layout.BUILDING['diameter']/2-layout.BUILDING['wall_thickness']
                    -layout.SECONDARY['header_radius']-layout.PIPE_SPECS['steam_header']['jacket_od']/2)
    assert wall_clearance>=.8
    services['steam_header_wall_clearance_m']=wall_clearance
    # Side-discharge end planes and bottom-suction cylinders are disjoint outside the volute.
    pump_mouth_clearance=layout.PUMPS['casing_diameter']/2-layout.PIPE_SPECS['cold']['jacket_od']/2
    assert pump_mouth_clearance>.25
    services['pump_nozzle_envelope_clearance_m']=pump_mouth_clearance
    services['insulated_piping']={'routes':summary,'insulation_collection':'Pipe insulation',
        'metal_collection':'Pressure pipe metal','scope':'Hollow metal and insulation geometry; conditional worksheet inputs; no pipe support or stress validation'}
    return ['All 19 process routes have separate hollow metal and insulation meshes matching Hurmet dimensions',
            'Insulated pipe envelopes clear floor; circular elbow centreline radii exceed insulation outer radius']
