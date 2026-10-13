"""Blender consumer of literal resolved coolant documents; no authoring rules."""
import json
import math
from .assembly_model import validate,point
from .installation_piping import insulated_route
from .installation_services import steel_frame


def yaw(component):
    r=component['world_rotation']
    if max(abs(r[2][0]),abs(r[2][1]),abs(r[0][2]),abs(r[1][2]),abs(r[2][2]-1))>1e-8:
        raise ValueError('Current equipment renderer supports Z-axis placement rotations only')
    return math.degrees(math.atan2(r[1][0],r[0][0]))


def build_coolant(b,doc,integration):
    validate(doc);integration['routes']=[];integration['cold_suction_routes']=[];integration['pumps']=[]
    frames={}
    for name,c in doc['components'].items():
        if c['kind']=='assembly' and 'blender_name' in c:
            root=b.assembly(c['blender_name'],'Major piping',c['world_position_m'],yaw(c))
            root['model_component']=name;root['model_parent']=c['parent'];frames[name]=root
    for name,c in doc['connections'].items():
        root=frames[c['frame']];spec=c['spec'];obj=insulated_route(b,c['blender_name'],root,c['points_m'],spec,c['service'])
        obj['model_connection']=name;obj['pid_line']=c['pid_line'];obj['flow_from']=c['flow_from'];obj['flow_to']=c['flow_to'];obj['flow_direction']=c['flow_description']
        if 'reactor_terminal' in c:
            obj['reactor_terminal']=c['reactor_terminal'];obj['centreline_points_local']=json.dumps(c['points_m'])
            integration['routes'].append(dict(object=obj.name,terminal=c['reactor_terminal'],points=c['world_points_m'],diameter=spec['bare_od'],jacket_diameter=spec['jacket_od'],generator=c['index'],target=c['target'],flow_direction=c['flow_description']))
        else:integration['cold_suction_routes'].append(dict(object=obj.name,generator=c['index'],points=c['world_points_m']))
    for name,c in doc['components'].items():
        if c['kind']!='pump':continue
        p=c['parameters'];pz=c['position_m'][2];pr=p['casing_diameter']/2;duty=c['duty'];bottom=pz-p['casing_height']/2
        pump=b.assembly(c['blender_name'],'Coolant pumps',c['world_position_m'],yaw(c))
        pump['model_component']=name;pump['model_parent']=c['parent'];pump['pid_tag']=c['pid_tag']
        for k in ('motor_rating_kw','flow_m3_s','pressure_rise_pa'):pump[k]=duty[k]
        pump['shaft_demand_kw']=duty['shaft_kw'];pump['scope']='Provisional vertical centrifugal pump with bottom suction'
        parent=doc['components'][c['parent']]
        pump['support_bottom_z']=point(parent,[0,0,c['floor_z']])[2];pump['support_top_z']=point(parent,[0,0,bottom])[2]
        b.cylinder('volute_envelope',pump,pr,p['casing_height'],(0,0,0),'cold',vertices=48)
        b.cylinder('bearing_pedestal',pump,.45,p['motor_bottom']-(pz+p['casing_height']/2),(0,0,(pz+p['casing_height']/2+p['motor_bottom'])/2-pz),'rail',vertices=32)
        b.box('motor_envelope',pump,(p['motor_width'],p['motor_depth'],p['motor_height']),(0,0,p['motor_bottom']+p['motor_height']/2-pz),'equipment',.08)
        b.cylinder('motor_top',pump,.85,.18,(0,0,p['motor_bottom']+p['motor_height']-pz),'dark',vertices=32)
        steel_frame(b,pump,'support',3.2,3.2,c['floor_z']-pz,-p['casing_height']/2)
        for y in (-1.0,1.0):b.box(f'casing_bearer{y}',pump,(3.2,.20,.25),(0,y,-p['casing_height']/2-.125),'rail')
        integration['pumps'].append(dict(name=pump.name,centre=c['world_position_m'],suction=doc['ports'][name+'.suction']['world_position_m'],discharge=doc['ports'][name+'.discharge']['world_position_m'],**{k:duty[k] for k in ('hydraulic_kw','shaft_kw','electrical_kw','motor_rating_kw','flow_m3_s')}))
    return integration
