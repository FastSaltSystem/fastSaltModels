"""Draw checked equipment bounding boxes; no detailed machinery geometry."""
import json,hashlib
import bpy

def add_equipment(b, root, site):
    file=root/'models/turbine-layout.json';data=json.loads(file.read_text());layout=data['building']
    assert tuple(site.TURBINE['size'])==(layout['length'],layout['width'],layout['height'])
    assert list(site.TURBINE['centre'])==layout['centre']
    origin=(site.TURBINE['centre'][0]-layout['length']/2,site.TURBINE['centre'][1]-layout['width']/2,site.PAD_Z)
    colors={'condenser':'#90BCCD','reheater':'#EAB284','heater':'#DCC778','pump':'#91BAA4','turbine':'#BCC8DB','generator':'#C4B3D1','storage':'#A4CBBB','electrical':'#DBBC9C'}
    for k,c in colors.items():b.material('turbine_'+k,c,roughness=.55)
    assembly=b.assembly('turbine.equipment','Turbine equipment',origin)
    assembly['source_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
    for q in data['items']:
        x,y,z=q['min'];dx,dy,dz=q['size']
        obj=b.box(q['name'],assembly,(dx,dy,dz),(x+dx/2,y+dy/2,z+dz/2),'turbine_'+q['kind'],.10)
        obj['layout_allowance_only']=True;obj['service']=q['name'];obj['turbine_upper']=z>=12
        if q['name'] in ('HP turbine','IP turbine'):
            curve=bpy.data.curves.new(q['name']+'.label','FONT');curve.body=q['name'].split()[0]
            curve.size=1.3;curve.align_x='CENTER';curve.align_y='CENTER'
            label=bpy.data.objects.new(q['name']+'.label',curve);b.collection('Turbine equipment labels').objects.link(label)
            label.parent=assembly;label.location=(x+dx/2,y+1.1,z+dz+.025)
            curve.materials.append(b.materials['dark']);label['turbine_upper']=True

    # Exterior tube-withdrawal aprons are empty; the building wall requires removable panels.
    for q in data['aprons']:
        label=q['name'];x,y=q['min'];dx,dy=q['size']
        b.box(label,assembly,(dx,dy,.10),(x+dx/2,y+dy/2,-.05),'floor')
    # Floor marks indicate service space only; not actual supports or barriers.
    for i,q in enumerate(data['service']):
        x,y,z=q['min'];dx,dy,dz=q['size']
        for j,(sx,sy,wx,wy) in enumerate([(x,y,dx,.06),(x,y+dy,dx,.06),(x,y,.06,dy),(x+dx,y,.06,dy)]):
            b.box(f'service{i}_{j}',assembly,(wx,wy,.015),(sx+wx/2,sy+wy/2,.015),'crane')
