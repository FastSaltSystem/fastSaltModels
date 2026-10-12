"""Inspectable insulation shells around illustrative cooling-air ducts."""
import bpy
from mathutils import Vector
from .installation_piping import shell_mesh,fillet_path,move_collection


def materials(b):
    b.material('air_insulation','#D8C9A8',roughness=.9)
    b.material('air_cladding','#B4ABA3',metallic=.55,roughness=.35)


def insulated_air_route(b,name,root,points,diameter,spec,rounded=True):
    materials(b)
    radius=diameter/2;outside=radius+spec['thickness']+spec['cladding']
    path,radii=fillet_path(points,max(1.5,2*outside)) if rounded else ([Vector(p) for p in points],[])
    assert not radii or min(radii)>outside,(name,'insulated bend too tight',min(radii),outside)
    guide=b.tube(name,root,path,outside,'air_cladding');guide.data.use_fill_caps=False
    guide.hide_render=True;guide.hide_set(True)
    guide['air_insulated']=True;guide['bare_diameter_m']=diameter
    guide['insulation_m']=spec['thickness'];guide['cladding_m']=spec['cladding']
    guide['minimum_bend_radius_m']=min(radii) if radii else 1e6
    for suffix,ro,ri,material in [('metal',radius,radius-spec['branch_wall'],'rail'),
            ('insulation',radius+spec['thickness'],radius,'air_insulation'),
            ('cladding',outside,radius+spec['thickness'],'air_cladding')]:
        obj=shell_mesh(b,name+'.'+suffix,root,path,ro,ri,material)
        obj['air_route_object']=guide.name;obj['service']='hot cooling air'
        move_collection(b,obj,'Hot air insulation' if suffix!='metal' else 'Hot air duct metal')
    return guide


def tag(obj,spec,kind):
    obj['air_insulation_part']=kind;obj['insulation_allowance_m']=spec['thickness']
    obj['scope']=spec['scope']
    return obj
