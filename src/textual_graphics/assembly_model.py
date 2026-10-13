"""Python-authored static assemblies, resolved documents and TOML exchange.

No Blender or PMS dependency. This is a visual assembly schema, not a dynamics input.
Local transforms use metres and XYZ Euler angles in degrees (Rz @ Ry @ Rx).
"""
from copy import deepcopy
import json
import math
from pathlib import Path
import re
import tomllib

IDENTITY=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
def vec(v):
    if len(v)!=3 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in v):
        raise ValueError('Expected three finite coordinates')
    return list(map(float,v))
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mv(m,v):return [sum(a*b for a,b in zip(row,v)) for row in m]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def transpose(m):return list(map(list,zip(*m)))
def rotation(angles):
    x,y,z=map(math.radians,vec(angles));cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return mm(mm([[cz,-sz,0],[sz,cz,0],[0,0,1]],[[cy,0,sy],[0,1,0],[-sy,0,cy]]),[[1,0,0],[0,cx,-sx],[0,sx,cx]])
def point(frame,local):return add(frame['world_position_m'],mv(frame['world_rotation'],local))
def local_point(frame,world):return mv(transpose(frame['world_rotation']),sub(world,frame['world_position_m']))
def distance(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

class Model:
    def __init__(self,name):
        self.name=name;self.components={};self.ports={};self.connections={};self.metadata={}
    def component(self,name,kind='assembly',*,parent='',position=(0,0,0),rotation_deg=(0,0,0),parameters=None,**metadata):
        if name in self.components:raise ValueError(f'Duplicate component: {name}')
        if parent and parent not in self.components:raise ValueError(f'Unknown parent: {parent}')
        self.components[name]=dict(kind=kind,parent=parent,position_m=vec(position),rotation_deg=vec(rotation_deg),parameters=deepcopy(parameters or {}),**deepcopy(metadata))
        return name
    def port(self,owner,name,position,direction=(0,0,1)):
        key=owner+'.'+name
        if owner not in self.components:raise ValueError(f'Unknown port owner: {owner}')
        if key in self.ports:raise ValueError(f'Duplicate port: {key}')
        d=vec(direction);norm=distance(d,[0,0,0])
        if norm==0:raise ValueError('Port direction cannot be zero')
        self.ports[key]=dict(owner=owner,position_m=vec(position),direction=[x/norm for x in d])
        return key
    def connect(self,name,start,end,*,frame,via=(),reverse_flow=False,**metadata):
        if name in self.connections:raise ValueError(f'Duplicate connection: {name}')
        if start not in self.ports or end not in self.ports:raise ValueError('Unknown connection port')
        if frame not in self.components:raise ValueError('Unknown route frame')
        self.connections[name]=dict(start=start,end=end,frame=frame,via_m=[vec(p) for p in via],reverse_flow=bool(reverse_flow),**deepcopy(metadata))
        return name
    def place_port_at(self,owner,port,target):
        """Translate a component so its port meets target; preserve its orientation."""
        doc=document(self);key=owner+'.'+port
        if key not in doc['ports']:raise ValueError(f'Unknown port: {key}')
        ancestor=doc['ports'][target]['owner']
        while ancestor:
            if ancestor==owner:raise ValueError('Cannot mate a component to its own descendant')
            ancestor=self.components[ancestor]['parent']
        delta=sub(doc['ports'][target]['world_position_m'],doc['ports'][key]['world_position_m'])
        parent=self.components[owner]['parent']
        if parent:delta=mv(transpose(doc['components'][parent]['world_rotation']),delta)
        self.components[owner]['position_m']=add(self.components[owner]['position_m'],delta)

def document(model):
    """Resolve hierarchy and connections into a detached, literal-only document."""
    result=dict(schema_version=1,model=dict(name=model.name,units='m',up_axis='Z',scope='Static visual assembly; no solver constraints'),metadata=deepcopy(model.metadata),components=deepcopy(model.components),ports=deepcopy(model.ports),connections=deepcopy(model.connections))
    active=set();done=set()
    def resolve(name):
        if name in done:return
        if name in active:raise ValueError('Cyclic component hierarchy')
        active.add(name);c=result['components'][name];r=rotation(c['rotation_deg']);p=c['position_m']
        if c['parent']:
            resolve(c['parent']);parent=result['components'][c['parent']];p=point(parent,p);r=mm(parent['world_rotation'],r)
        c['world_position_m']=p;c['world_rotation']=r;active.remove(name);done.add(name)
    for name in result['components']:resolve(name)
    for port in result['ports'].values():
        frame=result['components'][port['owner']];port['world_position_m']=point(frame,port['position_m']);port['world_direction']=mv(frame['world_rotation'],port['direction'])
    for c in result['connections'].values():
        frame=result['components'][c['frame']]
        start=result['ports'][c['start']]['world_position_m'];end=result['ports'][c['end']]['world_position_m']
        c['points_m']=[local_point(frame,start),*c['via_m'],local_point(frame,end)]
        c['world_points_m']=[point(frame,p) for p in c['points_m']]
        c['flow_from']=c['end'] if c['reverse_flow'] else c['start'];c['flow_to']=c['start'] if c['reverse_flow'] else c['end']
    result=json.loads(json.dumps(result,allow_nan=False))
    validate(result)
    return result

def validate(doc):
    if doc.get('schema_version')!=1 or doc['model']['units']!='m' or doc['model']['up_axis']!='Z':raise ValueError('Unsupported assembly schema/units')
    for name in doc['components']:
        seen=set();node=name
        while node:
            if node in seen:raise ValueError('Cyclic component hierarchy')
            seen.add(node);node=doc['components'][node]['parent']
    for name,c in doc['components'].items():
        vec(c['world_position_m']);r=c['world_rotation'];expected=rotation(c['rotation_deg'])
        if c['parent']:
            parent=doc['components'][c['parent']];expected=mm(parent['world_rotation'],expected);p=point(parent,c['position_m'])
        else:p=c['position_m']
        if distance(p,c['world_position_m'])>1e-8 or any(distance(a,b)>1e-8 for a,b in zip(r,expected)):raise ValueError(f'Inconsistent resolved frame: {name}')
    for name,p in doc['ports'].items():
        frame=doc['components'][p['owner']]
        if distance(point(frame,p['position_m']),p['world_position_m'])>1e-8:raise ValueError(f'Inconsistent port: {name}')
        if abs(distance(p['direction'],[0,0,0])-1)>1e-8 or distance(mv(frame['world_rotation'],p['direction']),p['world_direction'])>1e-8:raise ValueError(f'Inconsistent port direction: {name}')
    for name,c in doc['connections'].items():
        f=doc['components'][c['frame']];pts=c['world_points_m']
        if len(pts)!=len(c['points_m']) or len(pts)<2:raise ValueError(f'Invalid route: {name}')
        if any(distance(point(f,a),b)>1e-8 for a,b in zip(c['points_m'],pts)):raise ValueError(f'Inconsistent route frame: {name}')
        for port,pt in [(c['start'],pts[0]),(c['end'],pts[-1])]:
            if distance(pt,doc['ports'][port]['world_position_m'])>1e-8:raise ValueError(f'Disconnected route: {name}')
        if any(distance(a,b)<1e-9 for a,b in zip(pts,pts[1:])):raise ValueError(f'Zero-length route segment: {name}')
        expected=(c['end'],c['start']) if c['reverse_flow'] else (c['start'],c['end'])
        if (c['flow_from'],c['flow_to'])!=expected:raise ValueError(f'Inconsistent flow direction: {name}')
    return doc

def dumps(doc):
    """Compact TOML for literal dictionaries/lists. Reject unresolved/nonfinite values."""
    def key(k):return k if re.fullmatch(r'[A-Za-z0-9_-]+',k) else json.dumps(k)
    def value(v):
        if isinstance(v,str):return json.dumps(v)
        if isinstance(v,bool):return str(v).lower()
        if isinstance(v,(int,float)) and math.isfinite(v):return repr(v)
        if isinstance(v,(list,tuple)):return '['+', '.join(value(x) for x in v)+']'
        raise ValueError(f'Non-literal TOML value: {v!r}')
    lines=['# Generated resolved assembly. Edit the Python authoring model, then regenerate.']
    def emit(d,path=()):
        scalars={k:v for k,v in d.items() if not isinstance(v,dict)}
        if path and (scalars or not d):lines.extend(['','['+'.'.join(map(key,path))+']'])
        lines.extend(key(k)+' = '+value(v) for k,v in scalars.items())
        for k,v in d.items():
            if isinstance(v,dict):emit(v,path+(k,))
    emit(doc)
    return '\n'.join(lines)+'\n'

def write(model_or_document,path):
    doc=document(model_or_document) if isinstance(model_or_document,Model) else deepcopy(model_or_document)
    validate(doc);text=dumps(doc)
    if tomllib.loads(text)!=doc:raise ValueError('TOML round trip changed model')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    return path

def read(path):return validate(tomllib.loads(Path(path).read_text()))
