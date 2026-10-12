"""Main-circuit routing reservations. SI; no pressure design or hydraulic closure."""
from pathlib import Path
import json, math, csv, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'fastSalt/calculations/power-cycle/motor-equipment-sizing.json'
LAYOUT=ROOT/'models/turbine-layout.json'
COLORS={'steam':'#ad6098','cold_reheat':'#d79b45','hot_reheat':'#d45142','crossover':'#886ac0','condensate':'#3baca7','feedwater':'#447dc1','suction':'#248a65','condensate_suction':'#248a9e','heating_return':'#a97e49'}

def make():
 data=json.loads(LAYOUT.read_text());equipment={q['name']:q for q in data['items']}
 basis=json.loads(SOURCE.read_text());sizes={p['service']:p for p in basis['pipes']};routes=[]
 def spec(service,wall,insulation,bore=None):
  p=sizes[service];d=p['bore_m'] if bore is None else bore
  return dict(bore=d,wall_allowance=wall,insulation_allowance=insulation,jacket_od=d+2*(wall+insulation),source_service=service,dimension_status='Geometric wall/insulation allowances; not a pressure or thermal design')
 main=spec('Main steam header (existing bore)',.195,.35)
 main['dimension_status']='Retained conditional main-header wall and insulation from existing installation'
 fw=spec('Feedwater header (existing bore)',.120,.175);fw['dimension_status']=main['dimension_status']
 hp=spec('HP admission after reheat split',.15,.35)
 hs=spec('Reheater heating supply',.10,.35)
 cr=spec('Cold reheat',.025,.20);hr=spec('Hot reheat',.035,.35)
 cross=spec('IP-to-LP crossover',.025,.20)
 ret=spec('Reheater heating return',.14,.25)
 lp=spec('Condensate through LP heater bank',.015,.10)
 su=spec('Deaerator to feed pumps',.015,.10)
 suhead=spec('Deaerator to feed pumps',.015,.10,.725)
 cs=spec('Condensate through LP heater bank',.015,0,.65)
 def add(name,net,s,pts,contacts=()):
  routes.append(dict(name=name,network=net,spec=s,points=[list(p) for p in pts],contacts=list(contacts)))
 # Local hall coordinates. Existing external steam/feedwater terminal datum.
 end=(57,15.805160522460938);zmain=15.500000095367432;zfw=5.3200000286102295
 tee=(55,end[1],zmain)
 add('Main steam to HP','steam',main,[(end[0],end[1],zmain),tee,(53,end[1],zmain),(53,18,zmain)],['HP turbine'])
 add('Reheater heating header','steam',hs,[tee,(55,tee[1],8.6),(56,18.8,8.6),(56,18.8,5.8),(38.625,18.8,5.8)])
 for i,x in enumerate([38.625,43.875,49.125,54.375],1):
  add(f'RH{i} heating supply','steam',hs,[(x,18.8,5.8),(x,18.8,3.75)],[f'RH{i}'])
 # Two parallel process reheat trains; each serves two modules.
 for group,(xs,port) in enumerate([([38.625,43.875],45),([49.125,54.375],56)],1):
  cold_path=[(53,24,15),(53,26,15),(53,26,7.2),(46.5,26,7.2),(46.5,23,7.2),(xs[0],23,7.2)] if group==1 else [(port,24,15),(port,25.8,15),(port,25.8,7.2),(port,23,7.2),(xs[0],23,7.2)]
  add(f'Cold reheat train {group}','cold_reheat',cr,cold_path,['HP turbine'])
  for x in xs:
   i=[38.625,43.875,49.125,54.375].index(x)+1
   add(f'RH{i} cold inlet','cold_reheat',cr,[(x,23,7.2),(x,23,3.75)],[f'RH{i}'])
  add(f'Hot reheat train {group} header','hot_reheat',hr,[(xs[0],28,9.4),(xs[1],28,9.4)])
  middle=sum(xs)/2;ip_port=45.25 if group==1 else 48.75
  add(f'Hot reheat train {group} return','hot_reheat',hr,[(middle,28,9.4),(middle,31,9.4),(ip_port,31,9.4),(ip_port,31,15),(ip_port,24,15)],['IP turbine'])
  for x in xs:
   i=[38.625,43.875,49.125,54.375].index(x)+1
   add(f'RH{i} hot outlet','hot_reheat',hr,[(x,28,3.75),(x,28,9.4)],[f'RH{i}'])
 add('Heating condensate header to HP4','heating_return',ret,[(38.625,31,6.7),(57.8,31,6.7),(57.8,5,6.7),(55.75,5,6.7),(55.75,5,4)],['HP4'])
 for i,x in enumerate([38.625,43.875,49.125,54.375],1):
  add(f'RH{i} heating return','heating_return',ret,[(x,31,3.75),(x,31,6.7)],[f'RH{i}'])
 # Nested lanes avoid crossing the three large parallel crossover pipes.
 for i,(x,port,lane) in enumerate([(6,49.2,38.7),(15,47.1,36.6),(24,45,34.5)],1):
  add(f'IP to LP casing {i}','crossover',cross,[(port,21,18),(port,21,21.2),(port,lane,21.2),(x,lane,21.2),(x,30,21.2),(x,30,19)],['IP turbine',f'LP casing {i}'])
 # Condenser suction channels below floor, not an overhead lift of hotwell water.
 add('Condensate suction collector','condensate_suction',cs,[(23.5,15.5,-1.3),(1.75,15.5,-1.3),(1.75,2.5,-1.3)])
 for i,x in enumerate([5.5,14.5,23.5],1):
  add(f'C{i} hotwell outlet','condensate_suction',cs,[(x,20,.5),(x,20,-1.3),(x,15.5,-1.3)],[f'C{i}'])
 for i,y in enumerate([12,7.25,2.5],1):
  add(f'CEP{i} suction','condensate_suction',lp,[(1.75,y,-1.3),(1.75,y,.5)],[f'CEP{i}'])
  add(f'CEP{i} discharge','condensate',lp,[(1.75,y,3.5),(1.75,y,6)],[f'CEP{i}'])
 add('CEP discharge collector','condensate',lp,[(1.75,2.5,6),(1.75,12,6),(3,12,6),(3,9,6),(5.875,9,6),(5.875,9,3.75)],['LP1'])
 for i,(x,xn,z,zn) in enumerate([(5.875,10.375,3.75,3.75),(10.375,14.375,3.75,2.75)],1):
  add(f'LP{i} to LP{i+1}','condensate',lp,[(x,12,z),(x,12,5.8),((x+xn)/2,12,5.8),((x+xn)/2,9,5.8),(xn,9,5.8),(xn,9,zn)],[f'LP{i}',f'LP{i+1}'])
 add('LP3 to deaerator feed header','condensate',lp,[(14.375,12,2.75),(14.375,12,6.8),(16.5,12,6.8),(16.5,9.5,6.8),(16.5,9.5,15.8)],['LP3'])
 add('Deaerator feed header','condensate',lp,[(16.5,6.75,15.8),(16.5,12.75,15.8)])
 for i,y in enumerate([6.75,12.75],1):
  add(f'DA{i} condensate inlet','condensate',lp,[(16.5,y,15.8),(18,y,15.8)],[f'DA{i}'])
 # Two DA downcomers feed a common larger collector; three 50% pumps.
 for i,(x,y) in enumerate([(23,6.75),(29,12.75)],1):
  add(f'DA{i} downcomer','suction',su,[(x,y,13.5),(x,y,7.6),(x,8,7.6)],[f'DA{i}'])
 add('BFP suction collector','suction',suhead,[(20,8,7.6),(32,8,7.6)])
 for i,x in enumerate([20,26,32],1):
  add(f'BFP{i} suction','suction',su,[(x,8,7.6),(x,8,4.5)],[f'BFP{i}'])
  add(f'BFP{i} discharge','feedwater',fw,[(x,5,4.5),(x,5,6),(x,5,6)],[f'BFP{i}'])
 add('BFP discharge collector to HP1','feedwater',fw,[(20,5,6),(42.625,5,6),(42.625,9,6),(42.625,9,3.75)],['HP1'])
 for i,(x,xn,z,zn) in enumerate([(42.625,47.25,3.75,4),(47.25,51.625,4,3.75),(51.625,56.25,3.75,4)],1):
  add(f'HP{i} to HP{i+1}','feedwater',fw,[(x,12,z),(x,12,6.5),((x+xn)/2,12,6.5),((x+xn)/2,9,6.5),(xn,9,6.5),(xn,9,zn)],[f'HP{i}',f'HP{i+1}'])
 add('HP4 feedwater to SG interface','feedwater',fw,[(56.25,12,4),(56.25,12,8.5),(54,12,8.5),(54,end[1],8.5),(54,end[1],zfw),(end[0],end[1],zfw)],['HP4'])
 # Clean duplicate nodes; network junctions are validated geometrically below.
 for q in routes:
  pts=[p for i,p in enumerate(q['points']) if i==0 or math.dist(p,q['points'][i-1])>1e-6]
  q['points']=[p for i,p in enumerate(pts) if i==0 or i==len(pts)-1 or abs(math.dist(pts[i-1],p)+math.dist(p,pts[i+1])-math.dist(pts[i-1],pts[i+1]))>1e-7]
 return dict(title='Main turbine-hall pipe routing draft',layout=data,routes=routes,colors=COLORS,source_hashes={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,LAYOUT)},scope='Main-circuit pipe outer envelopes; provisional equipment ports',omissions=['Heater extraction steam and cascading drains (except reheat heating return to HP4)','Deaerator heating steam','Cooling-water circuits, vents, drains, minimum-flow recirculation, bypasses and valves','Pipe supports, thermal-expansion flexibility, seismic/stress qualification and installation sequence','LP exhaust transitions (not modeled)'],assumptions=['Internal wall/insulation dimensions are geometric allowances except retained steam/feedwater headers','Module branches conservatively retain their upstream header bore; no new branch sizing asserted','Below-floor condensate suction channel requires civil design, hotwell/nozzle elevations and NPSH verification','Equipment endpoint contacts are allowed only in a local nozzle region','Geometry does not revise the closed-cycle pressure budget or prove hydraulic performance'])

# Pure-Python polyline and distance routines keep the checks independent of Blender.
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def addv(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,k):return tuple(x*k for x in a)
def rounded(points,radius,junctions=()):
 result=[points[0]];radii=[]
 for a,p,c in zip(points,points[1:],points[2:]):
  if any(math.dist(p,j)<1e-6 for j in junctions):result.append(p);continue
  u=sub(a,p);v=sub(c,p);lu=math.sqrt(dot(u,u));lv=math.sqrt(dot(v,v));u=mul(u,1/lu);v=mul(v,1/lv)
  theta=math.acos(max(-1,min(1,dot(u,v))))
  if abs(theta-math.pi)<1e-5:result.append(p);continue
  if theta<1e-5:raise ValueError('Reversing route '+str(p))
  trim=min(radius/math.tan(theta/2),lu*.45,lv*.45);r=trim*math.tan(theta/2)
  centre=addv(p,mul(addv(u,v),r/math.sin(theta/2)/math.sqrt(dot(addv(u,v),addv(u,v)))))
  aa=sub(addv(p,mul(u,trim)),centre);bb=sub(addv(p,mul(v,trim)),centre);angle=math.acos(max(-1,min(1,dot(aa,bb)/r**2)))
  for j in range(17):
   t=j/16
   q=addv(mul(aa,math.sin((1-t)*angle)/math.sin(angle)),mul(bb,math.sin(t*angle)/math.sin(angle)))
   result.append(addv(centre,q))
  radii.append(r)
 result.append(points[-1]);return result,radii

def point_box(p,b):
 return math.sqrt(sum(max(b['min'][i]-p[i],0,p[i]-b['min'][i]-b['size'][i])**2 for i in range(3)))
def samples(pts,step=.15):
 for a,b in zip(pts,pts[1:]):
  n=max(1,math.ceil(math.dist(a,b)/step))
  for j in range(n):yield addv(a,mul(sub(b,a),j/n))
 yield pts[-1]
def segment_distance(p1,q1,p2,q2):
 d1=sub(q1,p1);d2=sub(q2,p2);r=sub(p1,p2);a=dot(d1,d1);e=dot(d2,d2);f=dot(d2,r)
 if a<1e-12:return math.dist(p1,addv(p2,mul(d2,max(0,min(1,f/e))))) if e else math.dist(p1,p2)
 c=dot(d1,r)
 if e<1e-12:s=max(0,min(1,-c/a));t=0
 else:
  b=dot(d1,d2);den=a*e-b*b;s=max(0,min(1,(b*f-c*e)/den)) if abs(den)>1e-12 else 0;t=(b*s+f)/e
  if t<0:t=0;s=max(0,min(1,-c/a))
  elif t>1:t=1;s=max(0,min(1,(b-c)/a))
 return math.dist(addv(p1,mul(d1,s)),addv(p2,mul(d2,t)))

def check(data):
 hits=[];tight=[];wall=[];pipes=[];junctions=[];pair_junctions={}
 for i,a in enumerate(data['routes']):
  for b in data['routes'][i+1:]:
   if a['network']!=b['network']:continue
   for endpoint in a['points'][::len(a['points'])-1]+b['points'][::len(b['points'])-1]:
    if all(any(segment_distance(endpoint,endpoint,u,v)<1e-6 for u,v in zip(q['points'],q['points'][1:])) for q in (a,b)):
     junctions.append(endpoint)
     pair_junctions.setdefault((a['name'],b['name']),[]).append(endpoint)
 data['junctions']=junctions
 for q in data['routes']:
  radius=q['spec']['jacket_od']/2
  pts,rs=rounded(q['points'],max(q['spec']['jacket_od']*1.5,.75),junctions);q['render_points']=pts
  q['length_m']=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]));q['minimum_bend_radius_m']=min(rs) if rs else None
  if rs and min(rs)<radius*1.05:tight.append(q['name'])
  # Sampling inflated by half sample spacing: conservative tube-to-box test.
  points=list(samples(pts));q['floor_min_m']=min(p[2] for p in pts)-radius
  for b in data['layout']['items']+data['layout']['service']:
   bad=[]
   for p in points:
    if point_box(p,b)<radius+.075:
     if b['name'] in q['contacts'] and min(math.dist(p,q['points'][0]),math.dist(p,q['points'][-1]))<radius+.15:continue
     bad.append(p)
   if bad:hits.append(dict(route=q['name'],object=b['name'],example=[round(v,3) for v in bad[len(bad)//2]]))
  if any(p[0]-radius<.35 or p[0]+radius>59.65 or p[1]-radius<.35 or p[1]+radius>39.65 or p[2]+radius>25 for p in pts):wall.append(q['name'])
 # Unrounded centreline capsules conservatively screen straight-run pairs. Rounded bends checked separately via render segments.
 for i,a in enumerate(data['routes']):
  for b in data['routes'][i+1:]:
   # Exempt only explicit centreline fittings belonging to this exact route pair.
   r=(a['spec']['jacket_od']+b['spec']['jacket_od'])/2
   # Broad-phase route bounds, then actual rendered polyline capsule distance.
   ap=a['render_points'];bp=b['render_points']
   if any(min(x[k] for x in ap)-max(x[k] for x in bp)>r or min(x[k] for x in bp)-max(x[k] for x in ap)>r for k in range(3)):continue
   found=False
   for x,y in zip(ap,ap[1:]):
    for u,v in zip(bp,bp[1:]):
     if any(min(x[k],y[k])-max(u[k],v[k])>r or min(u[k],v[k])-max(x[k],y[k])>r for k in range(3)):continue
     if segment_distance(x,y,u,v)<r-.001:
      # Allow local fitting envelopes at an explicit centreline junction only.
      if a['network']==b['network'] and any(segment_distance(j,j,x,y)<r*1.6 and segment_distance(j,j,u,v)<r*1.6 for j in pair_junctions.get((a['name'],b['name']),[])):continue
      found=True;break
    if found:break
   if found:pipes.append([a['name'],b['name']])
 stage_checks=[]
 for q in data['routes']:
  if q['name']=='Main steam to HP':assert q['contacts']==['HP turbine']
  if q['name'].startswith('Cold reheat train'):assert q['contacts']==['HP turbine']
  if q['name'].startswith('Hot reheat train') and q['name'].endswith('return'):assert q['contacts']==['IP turbine']
  if q['network']=='crossover':assert 'IP turbine' in q['contacts'] and 'HP turbine' not in q['contacts']
 stage_checks=['Main steam admits to HP','HP exhaust connects to reheater cold side','Reheater hot side returns to IP','All three LP crossover sources are on IP; no HP-to-LP crossover']
 disconnected=[]
 external=[(57,15.805160522460938,15.500000095367432),(57,15.805160522460938,5.3200000286102295)]
 for q in data['routes']:
  for ep in (q['render_points'][0],q['render_points'][-1]):
   port=any(point_box(ep,b)<1e-6 for b in data['layout']['items'] if b['name'] in q['contacts'])
   connected=any(other is not q and other['network']==q['network'] and any(segment_distance(ep,ep,a,b)<1e-6 for a,b in zip(other['render_points'],other['render_points'][1:])) for other in data['routes'])
   if not port and not connected and not any(math.dist(ep,t)<1e-6 for t in external):disconnected.append(dict(route=q['name'],endpoint=ep))
 total=sum(q['length_m'] for q in data['routes'])
 long_routes=[dict(route=q['name'],length_m=round(q['length_m'],2)) for q in data['routes'] if q['length_m']>40]
 return dict(stage_connection_checks=stage_checks,route_count=len(data['routes']),total_drawn_centreline_m=round(total,2),disconnected_endpoints=disconnected,routes_longer_than_original_40m_pressure_screen=long_routes,equipment_and_service_conflicts=hits,pipe_pair_conflicts=pipes,tight_bend_routes=tight,wall_or_crane_conflicts=wall,method='Rendered polyline capsules; box samples <=0.15 m inflated by 0.075 m; local equipment nozzle contacts exempt',limitations=['Explicit same-network junction neighborhoods exempt; no valve/fitting bodies modeled','No hydraulic/stress or pipe-support validation','Existing feedwater interface has 4.70 m underside clearance within provisional 5 m cross-aisle reservation','Crossover underside is 20.275 m: overhead turbine-maintenance/crane paths need separate review'])

def plot(data,out):
 from html import escape
 from turbine_layout import plot as equipment_plot
 equipment_plot(out)
 s=(out/'turbine-equipment-plan.svg').read_text()
 s=s.replace('Motor-BFP equipment arrangement','Main internal piping | First routing draft')
 s=s.replace('Ground equipment and withdrawal zones','Lower routes: solid above floor; dashed below floor')
 s=s.replace('Upper level: turbines +12 m; storage +13.5 m','Upper routes: steam admission and IP–LP crossovers')
 s=s.replace('BFPs rotated 90° • Hall shortened by 6 m • Main-hall floor area reduced 240 m² (9.1%).','59 routes • Provisional ports and jackets • East feedwater bay: 4.70 m clearance; 5 m reservation flagged.')
 s=s.replace('fill="#90bccd"','fill="#e6eff3"').replace('fill="#eab284"','fill="#f6e8dc"').replace('fill="#dcc778"','fill="#f3eedc"').replace('fill="#91baa4"','fill="#dfebe5"').replace('fill="#bcc8db"','fill="#e8edf4"').replace('fill="#c4b3d1"','fill="#e9e4f0"').replace('fill="#a4cbbb"','fill="#e1eee8"')
 s=s.replace('>HP turbine</text>','></text>').replace('>IP turbine</text>','></text>')
 extra=[];scale=11
 for ox,upper in [(55,False),(965,True)]:
  for q in data['routes']:
   pts=q['render_points'];color=COLORS[q['network']];width=q['spec']['jacket_od']*scale
   if not upper and q['network']=='condensate_suction':
    path='M'+' L'.join(f'{ox+p[0]*scale},{790-p[1]*scale}' for p in pts)
    extra.append(f'<path d="{path}" stroke="{color}" stroke-width="{width}" stroke-dasharray="9 6" fill="none"><title>{escape(q['name'])}: below-floor collector and risers</title></path>')
    continue
   for a,b in zip(pts,pts[1:]):
    # Clip segments at the display elevation; vertical risers project to points.
    if (a[2]>=12)==(b[2]>=12):
     if (a[2]>=12)!=upper:continue
    else:
     t=(12-a[2])/(b[2]-a[2]);mid=addv(a,mul(sub(b,a),t))
     if (a[2]>=12)==upper:b=mid
     else:a=mid
    dash=' stroke-dasharray="5 3"' if max(a[2],b[2])<0 else ''
    extra.append(f'<path d="M{ox+a[0]*scale},{790-a[1]*scale} L{ox+b[0]*scale},{790-b[1]*scale}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" fill="none"{dash}><title>{escape(q['name'])}</title></path>')
 # Legend occupies existing whitespace above the two plans.
 labels=[('steam','Main / heating steam'),('cold_reheat','Cold reheat'),('hot_reheat','Hot reheat'),('crossover','IP–LP crossover'),('condensate','Condensate / LP water'),('feedwater','BFP / HP feedwater'),('suction','Pump suction'),('heating_return','Heating return')]
 for i,(key,label) in enumerate(labels):
  x=70+(i%4)*440;y=137+(i//4)*28
  extra.append(f'<path d="M{x} {y}h30" stroke="{COLORS[key]}" stroke-width="7"/><text x="{x+40}" y="{y+5}" font-family="Arial" font-size="17" fill="#183044">{label}</text>')
 extra.append('<text x="900" y="237" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="#183044">Main steam → HP → reheaters → IP → LP</text>')
 extra.append('<text x="900" y="261" text-anchor="middle" font-family="Arial" font-size="16" fill="#526575">The separate main-steam heating branch also supplies the reheaters.</text>')
 for x,y,label in [(47.25,19.1,'IP'),(54.75,21,'HP')]:
  extra.append(f'<text x="{965+x*11}" y="{790-y*11}" text-anchor="middle" font-family="Arial" font-size="17" font-weight="bold" fill="#183044" stroke="white" stroke-width="3" paint-order="stroke">{label}</text>')
 # Highlight the retained east-wall feedwater height limitation.
 extra.append('<circle cx="682" cy="620" r="20" fill="none" stroke="#c34432" stroke-width="3"/>')
 (out/'turbine-piping-plan.svg').write_text(s.replace('</svg>',''.join(extra)+'</svg>'))

if __name__=='__main__':
 out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);data=make();data['verification']=check(data);plot(data,out)
 (out/'turbine-piping.json').write_text(json.dumps(data,indent=2)+'\n')
 with (out/'turbine-pipe-schedule.csv').open('w') as f:
  writer=csv.writer(f);writer.writerow(['route','network','bore_m','jacket_allowance_m','length_m','min_bend_radius_m'])
  for q in data['routes']:writer.writerow([q['name'],q['network'],q['spec']['bore'],q['spec']['jacket_od'],q['length_m'],q['minimum_bend_radius_m']])
 print(json.dumps(data['verification'],indent=2))
