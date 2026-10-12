"""Illustrative machinery exteriors inside the checked layout reservations.

Shapes are presentation geometry, not supplier outlines or pressure-part designs.
The layout JSON and all external pipe terminals remain the governing envelopes.
"""
import hashlib
import json
import math
import bpy
from mathutils import Vector

COLORS = {'condenser':'#90BCCD', 'reheater':'#DB9661', 'heater':'#DCC778',
          'pump':'#579F87', 'turbine':'#8EA6C0', 'generator':'#9D87B1',
          'storage':'#A4CBBB', 'electrical':'#DBBC9C'}

class Detail:
    def __init__(self, b, parent, q):
        self.b, self.parent, self.q = b, parent, q
        self.size = q['size']; self.objects = []
        self.mat = 'turbine_' + q['kind']
        self.shell = None

    def point(self, xyz):
        return tuple(a+b for a,b in zip(self.q['min'], xyz))

    def tag(self, ob):
        ob['service'] = self.q['name']; ob['turbine_upper'] = self.q['min'][2] >= 12
        ob['turbine_detail'] = True; ob['geometry_status'] = 'Illustrative exterior within reserved envelope'
        self.objects.append(ob)
        return ob

    def box(self, name, size, pos, mat=None, bevel=.035):
        return self.tag(self.b.box(self.q['name']+'.'+name, self.parent, size,
                                  self.point(pos), mat or self.mat, bevel))

    def axial(self, name, axis, centre, profile, mat=None, sides=48):
        """Closed surface of revolution; profile is (axial position, radius)."""
        other=[i for i in range(3) if i != axis]; verts=[]; faces=[]
        for t,r in profile:
            for j in range(sides):
                a=2*math.pi*j/sides; p=list(centre); p[axis]=t
                p[other[0]]+=r*math.cos(a); p[other[1]]+=r*math.sin(a)
                verts.append(p)
        for k in range(len(profile)-1):
            for j in range(sides):
                a=k*sides+j; c=k*sides+(j+1)%sides
                faces.append((a,c,c+sides,a+sides))
        faces.extend([tuple(range(sides-1,-1,-1)),tuple(range((len(profile)-1)*sides,len(profile)*sides))])
        ob=self.tag(self.b.mesh(self.q['name']+'.'+name,self.parent,verts,faces,
                               mat or self.mat,self.point((0,0,0))))
        for p in ob.data.polygons[:-2]:p.use_smooth=True
        return ob

    def cylinder(self,name,axis,centre,start,end,r,mat=None,sides=48):
        return self.axial(name,axis,centre,[(start,r),(end,r)],mat,sides)

    def shell_body(self,axis,centre,start,end,r):
        d=min(r*.35,(end-start)*.12)
        self.axial('casing',axis,centre,[(start,.45*r),(start+d*.4,.83*r),(start+d,r),
                    (end-d,r),(end-d*.4,.83*r),(end,.45*r)])
        self.shell=(axis,centre,r)

    def bolts(self,name,axis,centre,t,r,bolt=.045,count=16):
        # Merge a ring of hexagonal bolt heads into one mesh.
        axes=[i for i in range(3) if i!=axis];verts=[];faces=[]
        for j in range(count):
            a=2*math.pi*j/count; c=list(centre)
            c[axes[0]]+=r*math.cos(a);c[axes[1]]+=r*math.sin(a)
            base=len(verts)
            for z in (t,t+.06):
                for k in range(6):
                    p=c.copy();p[axis]=z;theta=2*math.pi*k/6
                    p[axes[0]]+=bolt*math.cos(theta);p[axes[1]]+=bolt*math.sin(theta);verts.append(p)
            faces.extend([tuple(base+k for k in range(5,-1,-1)),tuple(base+6+k for k in range(6))])
            faces.extend((base+k,base+(k+1)%6,base+6+(k+1)%6,base+6+k) for k in range(6))
        self.tag(self.b.mesh(self.q['name']+'.'+name,self.parent,verts,faces,'machinery_bolts',self.point((0,0,0))))

    def vessel(self):
        dx,dy,dz=self.size;axis=0 if self.q['kind']=='storage' else 1
        length=self.size[axis];width=self.size[1-axis];r=min(width*.41,dz*.40)
        c=[dx/2,dy/2,dz*.55];self.shell_body(axis,c,length*.035,length*.965,r)
        for j,f in enumerate((.18,.82)):
            pos=[dx/2,dy/2,dz*.18];pos[axis]=length*f
            size=[width*.86,length*.05,dz*.27] if axis==1 else [length*.035,width*.86,dz*.27]
            self.box('saddle'+str(j),size,pos,'machinery_base')
        for j,t in enumerate((length*.085,length*.915)):
            self.cylinder('end flange'+str(j),axis,c,t-.04,t+.04,r*1.055,'machinery_flange')
            self.bolts('cover bolts'+str(j),axis,c,t+.04,r*.94,bolt=.038,count=20)
        # Insulation jacket seams, not fabricated internal partitions.
        for j in range(1,6):
            t=length*(.13+.12*j)
            self.cylinder('jacket band'+str(j),axis,c,t-.018,t+.018,r*1.008,'machinery_flange')

    def turbine(self):
        dx,dy,dz=self.size;c=[dx/2,dy/2,15.2-self.q['min'][2]];r=min(dy*.36,dz*.35)
        self.box('bedplate',(dx*.97,dy*.84,dz*.07),(dx/2,dy/2,dz*.065),'machinery_base')
        for j,t in enumerate((dx*.09,dx*.91)):
            self.box('bearing pedestal'+str(j),(dx*.13,dy*.32,dz*.43),(t,dy/2,dz*.28),'machinery_base')
            self.cylinder('bearing'+str(j),0,c,t-dx*.06,t+dx*.06,r*.42,'machinery_flange')
        self.cylinder('shaft',0,c,.025,dx-.025,r*.13,'machinery_bolts')
        self.shell_body(0,c,dx*.16,dx*.84,r)
        self.box('horizontal split flange',(dx*.72,2*r*1.10,.14),(dx/2,dy/2,c[2]),'machinery_flange')
        for j,f in enumerate((.22,.34,.50,.66,.78)):
            self.cylinder('casing rib'+str(j),0,c,dx*f-.035,dx*f+.035,r*1.025)
        for side in (-1,1):
            for j in range(10):
                self.cylinder(f'split bolt{side}_{j}',2,(dx*(.18+.07*j),dy/2+side*r*1.055,0),c[2]+.07,c[2]+.15,.05,'machinery_bolts',6)
        if self.q['name'].startswith('LP casing'):
            self.box('exhaust skirt',(dx*.63,dy*.69,dz*.32),(dx/2,dy/2,dz*.265))

    def generator(self):
        dx,dy,dz=self.size;c=[dx/2,dy/2,15.2-self.q['min'][2]];r=min(dy*.33,dz*.32)
        self.box('base',(dx*.96,dy*.88,.35),(dx/2,dy/2,.28),'machinery_base')
        self.shell_body(0,c,dx*.12,dx*.88,r)
        self.cylinder('shaft',0,c,.03,dx-.03,.25,'machinery_bolts')
        for j,t in enumerate((dx*.08,dx*.92)):
            self.box('end bearing support'+str(j),(dx*.12,dy*.30,dz*.43),(t,dy/2,dz*.26),'machinery_base')
            self.cylinder('end shield'+str(j),0,c,t,t+.10,r*.60,'machinery_flange')
        for j,t in enumerate((dx*.24,dx*.50,dx*.76)):
            self.box('cooler enclosure'+str(j),(dx*.21,dy*.59,dz*.15),(t,dy/2,dz*.87))
            for k in range(6):
                self.box(f'cooler grille{j}_{k}',(dx*.17,.025,.08),(t,dy*(.26+.09*k),dz*.955),'machinery_dark',0)
        self.box('terminal housing',(dx*.23,dy*.16,dz*.27),(dx*.65,dy*.86,dz*.36),'machinery_flange')

    def pump(self):
        dx,dy,dz=self.size;self.box('skid',(dx*.95,dy*.97,.20),(dx/2,dy/2,.16),'machinery_base')
        if self.q['name'].startswith('CEP'):
            c=[dx/2,dy/2,dz/2];r=dx*.37
            self.cylinder('pump bowl',2,c,.23,dz*.40,r)
            self.cylinder('motor',2,c,dz*.48,dz*.89,r*.95,'machinery_dark')
            self.cylinder('coupling guard',2,c,dz*.40,dz*.48,r*.70,'machinery_guard')
            self.cylinder('motor fan cover',2,c,dz*.89,dz*.94,r,'machinery_flange')
            self.shell=(2,c,r)
            for j in range(12):
                a=j*2*math.pi/12
                self.box('motor cooling fin'+str(j),(.045,.045,dz*.34),(c[0]+r*math.cos(a),c[1]+r*math.sin(a),dz*.69),'machinery_flange',0)
        else:
            c=[dx/2,dy/2,dz*.48];r=dx*.30
            self.shell_body(1,c,dy*.16,dy*.65,r)
            self.cylinder('coupling guard',1,c,dy*.66,dy*.73,r*.55,'machinery_guard')
            self.cylinder('motor',1,c,dy*.74,dy*.94,r*1.04,'machinery_dark')
            for j in range(8):
                t=dy*(.19+j*.06)
                self.cylinder('barrel band'+str(j),1,c,t,t+.045,r*1.025,'machinery_flange')
            for j,t in enumerate((dy*.22,dy*.56,dy*.80,dy*.90)):
                self.box('foot'+str(j),(dx*.70,.40,dz*.24),(dx/2,t,dz*.24),'machinery_base')
            self.bolts('barrel cover bolts',1,c,dy*.64,r*.87,count=12)

    def condenser(self):
        dx,dy,dz=self.size
        self.box('shell',(dx*.85,dy*.77,dz*.62),(dx/2,dy/2,dz*.55))
        self.box('hotwell',(dx*.62,dy*.60,dz*.20),(dx/2,dy/2,dz*.14))
        for j,y in enumerate((dy*.08,dy*.92)):
            self.box('water box'+str(j),(dx*.91,dy*.14,dz*.67),(dx/2,y,dz*.54))
            self.box('water box flange'+str(j),(dx*.94,.09,dz*.70),(dx/2,dy*(.145 if j==0 else .855),dz*.54),'machinery_flange')
            for k in range(2):
                c=[dx*(.28+.44*k),0,dz*.50]
                t=dy*.003 if j==0 else dy*.995-.07
                self.cylinder(f'access cover{j}_{k}',1,c,t,t+.07,dx*.14,'machinery_flange')
                self.bolts(f'access bolts{j}_{k}',1,c,t+.005,dx*.12,bolt=.045,count=12)
        for j in range(6):
            y=dy*(.20+j*.12)
            for side in (-1,1):
                self.box(f'shell stiffener{j}_{side}',(.075,.10,dz*.65),(dx/2+side*dx*.43,y,dz*.55),'machinery_flange')
        for x in (dx*.15,dx*.85):
            for y in (dy*.20,dy*.80):
                self.box(f'foot{x}_{y}',(dx*.20,dy*.09,dz*.19),(x,y,dz*.105),'machinery_base')

    def port(self,route,p):
        """Join an unchanged external terminal to the illustrative casing."""
        rel=[p[i]-self.q['min'][i] for i in range(3)]
        face=min(((abs(rel[i]-v),i,v) for i in range(3) for v in (0,self.size[i])))
        assert face[0]<1e-5,(self.q['name'],p)
        _,axis,v=face;r=route['spec']['jacket_od']/2
        c=[s/2 for s in self.size]
        if self.shell:c=list(self.shell[1])
        # A straight local connector reaches the shell axis / interior box.
        end=c[axis];start=rel[axis];a,z=sorted((start,end))
        self.cylinder('nozzle '+route['name'],axis,rel,a,z,r,self.mat)
        # Collar lies inside the original reservation, clear of its terminal.
        t=start+(.12 if v==0 else -.22)
        clearance=min(min(rel[i],self.size[i]-rel[i]) for i in range(3) if i!=axis)
        collar=min(r*1.07,clearance-.005)
        if collar>r:self.cylinder('nozzle collar '+route['name'],axis,rel,t,t+.08,collar,'machinery_flange')
        return dict(route=route['name'],terminal=p,body_connection=self.point([end if i==axis else rel[i] for i in range(3)]),jacket_od_m=2*r)

    def verify(self):
        bad=[];lo=self.q['min'];hi=[a+b for a,b in zip(lo,self.size)]
        for ob in self.objects:
            for v in ob.data.vertices:
                p=ob.matrix_basis@v.co
                if any(p[i]<lo[i]-.001 or p[i]>hi[i]+.001 for i in range(3)):
                    bad.append(ob.name);break
        assert not bad, 'Detail outside reserved envelope: '+str(bad)
        return len(self.objects)


def add_equipment(b,root,site):
    file=root/'models/turbine-layout.json';data=json.loads(file.read_text());layout=data['building']
    assert tuple(site.TURBINE['size'])==(layout['length'],layout['width'],layout['height'])
    assert list(site.TURBINE['centre'])==layout['centre']
    origin=(site.TURBINE['centre'][0]-layout['length']/2,site.TURBINE['centre'][1]-layout['width']/2,site.PAD_Z)
    for k,c in COLORS.items():b.material('turbine_'+k,c,metallic=.18,roughness=.45)
    for k,c in {'base':'#53616D','flange':'#B9C3C7','bolts':'#525B62','dark':'#386375','guard':'#D8A34E'}.items():
        b.material('machinery_'+k,c,metallic=.4,roughness=.4)
    assembly=b.assembly('turbine.equipment','Turbine equipment',origin)
    assembly['source_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
    from turbine_piping import make,point_box
    routes=make()['routes'];report=[]
    bounds=b.collection('Turbine equipment reservations');bounds.hide_render=True;bounds.hide_viewport=True
    for q in data['items']:
        d=Detail(b,assembly,q);kind=q['kind'];dx,dy,dz=q['size']
        if kind in ('heater','reheater','storage'):d.vessel()
        elif kind=='turbine':d.turbine()
        elif kind=='generator':d.generator()
        elif kind=='pump':d.pump()
        elif kind=='condenser':d.condenser()
        else:
            d.box('annex',q['size'],(dx/2,dy/2,dz/2),bevel=0)
            # Annex remains a building reservation; no switchgear layout asserted.
        ports=[]
        for route in routes:
            if q['name'] not in route['contacts']:continue
            endpoints=[p for p in (route['points'][0],route['points'][-1]) if point_box(p,q)<1e-5]
            assert endpoints,(q['name'],route['name'])
            for p in endpoints:ports.append(d.port(route,p))
        n=d.verify()
        ob=b.box(q['name']+' reservation',assembly,q['size'],d.point((dx/2,dy/2,dz/2)),None)
        for col in list(ob.users_collection):col.objects.unlink(ob)
        bounds.objects.link(ob);ob.display_type='WIRE';ob.hide_render=True;ob['layout_allowance_only']=True
        # Surface labels inherit the upper-level visibility flag.
        if kind!='electrical':
            curve=bpy.data.curves.new(q['name']+'.label','FONT');curve.body=q['name'];curve.size=min(.65,dx*.21)
            curve.align_x='CENTER';curve.align_y='CENTER'
            label=bpy.data.objects.new(curve.name,curve);b.collection('Turbine equipment labels').objects.link(label)
            label.parent=assembly;label.location=d.point((dx/2,dy*.48,dz+.025));curve.materials.append(b.materials['dark'])
            label['turbine_upper']=q['min'][2]>=12;label['service']=q['name'];label['turbine_detail_label']=True
        report.append(dict(name=q['name'],kind=kind,parts=n,ports=ports,within_reservation=True))
    # Shared shaft elevation in both trains; guarded couplings occupy the
    # existing gaps, independently of the equipment reservation boxes.
    shaft_links=[]
    for j,(a,z,y) in enumerate([(10,11,30),(19,20,30),(28,30,30),(42,44,21),(50.5,51.5,21)]):
        q=dict(name='Shaft coupling '+str(j+1),kind='turbine',min=[a-.03,y-.45,14.75],size=[z-a+.06,.9,.9])
        d=Detail(b,assembly,q)
        d.cylinder('guard',0,(0,.45,.45),0,z-a+.06,.42,'machinery_flange')
        d.cylinder('centre band',0,(0,.45,.45),(z-a)/2-.06,(z-a)/2+.06,.44,'machinery_guard')
        d.verify()
        # Guard clearance to all other reservations, and to raw pipe route
        # segments. These gaps contain only the intended adjoining shafts.
        from turbine_piping import segment_distance
        contacts=[item['name'] for item in data['items'] if item['kind'] in ('turbine','generator') and abs(item['min'][1]+item['size'][1]/2-y)<1e-6 and (abs(item['min'][0]+item['size'][0]-a)<1e-6 or abs(item['min'][0]-z)<1e-6)]
        assert len(contacts)==2
        for item in data['items']:
            if item['name'] in contacts:continue
            for t in (a,(a+z)/2,z):assert point_box((t,y,15.2),item)>.44
        for route in routes:
            for p0,p1 in zip(route['points'],route['points'][1:]):
                assert segment_distance((a,y,15.2),(z,y,15.2),p0,p1)>.44+route['spec']['jacket_od']/2,(q['name'],route['name'])
        shaft_links.append(dict(name=q['name'],contacts=contacts,shaft_elevation_m=15.2,guard_radius_m=.44))
    for q in data['aprons']:
        x,y=q['min'];dx,dy=q['size'];b.box(q['name'],assembly,(dx,dy,.10),(x+dx/2,y+dy/2,-.05),'floor')
    for i,q in enumerate(data['service']):
        x,y,z=q['min'];dx,dy,dz=q['size']
        for j,(sx,sy,wx,wy) in enumerate([(x,y,dx,.06),(x,y+dy,dx,.06),(x,y,.06,dy),(x+dx,y,.06,dy)]):
            b.box(f'service{i}_{j}',assembly,(wx,wy,.015),(sx+wx/2,sy+wy/2,.015),'crane')
    b.turbine_equipment=dict(scope='Illustrative machinery exteriors; dimensions bounded by existing layout allowances',
        source_sha256=assembly['source_sha256'],items=report,shaft_links=shaft_links,
        checks=['All mechanical detail mesh vertices remain inside original equipment reservations',
                'Every existing equipment-contact pipe terminal has a local casing connector',
                'Upper machinery and labels carry the upper-level visibility flag',
                'Five guarded shaft links align at 15.2 m and clear other equipment reservations and pipe envelopes'],
        limitations=['Not supplier outlines, pressure design, material mass or internal blade/tube geometry',
                     'Upper deck, foundations, LP exhaust transitions and cooling-water circuits still require design',
                     'Bolt patterns, saddles, bearings and nozzle bodies are illustrative, not sized components'])
    return b.turbine_equipment
