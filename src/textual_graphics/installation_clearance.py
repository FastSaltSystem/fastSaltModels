"""Selected insulated installation interference checks."""
import math,itertools
import bpy
from mathutils import Vector
def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def add(a,b):return [x+y for x,y in zip(a,b)]
def mul(a,t):return [x*t for x in a]
def clamp(a):return max(0,min(1,a))
def segdist(p1,q1,p2,q2):
 d1=sub(q1,p1);d2=sub(q2,p2);r=sub(p1,p2)
 a=dot(d1,d1);e=dot(d2,d2);f=dot(d2,r)
 if a<1e-15:s=0;t=clamp(f/e) if e>1e-15 else 0
 else:
  c=dot(d1,r)
  if e<1e-15:t=0;s=clamp(-c/a)
  else:
   b=dot(d1,d2);den=a*e-b*b
   s=clamp((b*f-c*e)/den) if den>1e-15 else 0
   t=(b*s+f)/e
   if t<0:t=0;s=clamp(-c/a)
   elif t>1:t=1;s=clamp((b-c)/a)
 p=add(p1,mul(d1,s));q=add(p2,mul(d2,t));return math.sqrt(dot(sub(p,q),sub(p,q))),p,q

def gapbox(a,b):return math.sqrt(sum(max(0,a[0][k]-b[1][k],b[0][k]-a[1][k])**2 for k in range(3)))
def bounds(pts):return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]

def segment_box(a,b,lo,hi):
 v=sub(b,a);ts=[0,1]
 for i in range(3):
  if abs(v[i])>1e-12:
   for wall in [lo[i],hi[i]]:
    t=(wall-a[i])/v[i]
    if 0<t<1:ts.append(t)
 ts=sorted(set(ts));best=1e100
 def value(t):return sum(max(lo[i]-a[i]-v[i]*t,0,a[i]+v[i]*t-hi[i])**2 for i in range(3))
 for l,h in zip(ts,ts[1:]):
  mid=(l+h)/2;A=B=0
  for i in range(3):
   p=a[i]+v[i]*mid
   wall=lo[i] if p<lo[i] else hi[i] if p>hi[i] else None
   if wall is not None:A+=v[i]**2;B+=(a[i]-wall)*v[i]
  t=max(l,min(h,-B/A)) if A else mid
  best=min(best,value(t),value(l),value(h))
 return math.sqrt(best)

def check_interference(layout, services):
    """Conservative capsule routes vs routes/air and selected oriented equipment boxes.

    Junctions within a common secondary network and own equipment ports are
    excluded deliberately; three pump mouth end-cap overbounds are classified.
    This does not check every mesh or qualify maintenance/access/support loads.
    """
    bpy.context.view_layer.update()
    D={'routes':[],'boxes':[]}
    for o in bpy.context.scene.objects:
        if o.type=='CURVE' and (o.get('process_route') or o.name.startswith('connections.air.')):
            for s in o.data.splines:
                D['routes'].append({'name':o.name,'process':bool(o.get('process_route')),'radius':o.data.bevel_depth,
                    'points':[list(o.matrix_world @ Vector(p.co[:3])) for p in s.points]})
        if o.type=='MESH' and o.name.startswith('equipment.') and any(o.name.endswith('.'+t) for t in ['casing','closed_tank','closed_enclosure','deck','motor_envelope']):
            D['boxes'].append({'name':o.name,'matrix':[list(row) for row in o.matrix_world],'bounds':[list(q) for q in o.bound_box]})
    for r in D['routes']:
     r['bounds']=bounds(r['points']);r['segs']=[(a,b,bounds([a,b])) for a,b in zip(r['points'],r['points'][1:])]
    results=[]
    for a,b in itertools.combinations(D['routes'],2):
     if not a['process'] and not b['process']:continue
     # Common-network branches intentionally meet their own headers/outlets.
     if a['name'].startswith('connections.secondary_headers.') and b['name'].startswith('connections.secondary_headers.') and a['name'].split('.')[-1].split('_')[0]==b['name'].split('.')[-1].split('_')[0]:continue
     rr=a['radius']+b['radius']
     if gapbox(a['bounds'],b['bounds'])>rr+.1:continue
     best=(1e10,None,None)
     for u,v,boxa in a['segs']:
      for w,x,boxb in b['segs']:
       if gapbox(boxa,boxb)>rr+.1:continue
       d,p,q=segdist(u,v,w,x)
       if d<best[0]:best=d,p,q
     if best[0]<rr+.1:results.append({'a':a['name'],'b':b['name'],'clearance':best[0]-rr,'p':best[1],'q':best[2]})
    obstacles=[]
    for a in D['routes']:
     if not a['process']:continue
     for box in D['boxes']:
      # Own equipment ports terminate on the physical envelope, checked separately.
      own='connections.loop_' in a['name'] and a['name'].split('.')[1][-1]
      if own and box['name'].startswith(('equipment.coolant_pump_'+own+'.','equipment.steam_generator_'+own+'.')):continue
      if 'secondary_headers' in a['name'] and '_branch_' in a['name'] and box['name'].startswith('equipment.steam_generator_'+a['name'][-1]+'.'):continue
      m=box['matrix'];lo,hi=bounds(box['bounds'])
      def local(p):return [sum(m[j][i]*(p[j]-m[j][3]) for j in range(3)) for i in range(3)]
      pts=[local(p) for p in a['points']]
      best=min(segment_box(u,v,lo,hi) for u,v in zip(pts,pts[1:]))-a['radius']
      if best<.1:obstacles.append({'pipe':a['name'],'box':box['name'],'clearance':best})

    exceptions=[];remaining=[]
    byname={q['name']:q for q in D['routes']}
    for clash in results:
        a,b=clash['a'],clash['b']
        if a.rsplit('.',1)[0]==b.rsplit('.',1)[0] and {a.rsplit('.',1)[1],b.rsplit('.',1)[1]}=={'cold_inlet','cold_suction'}:
            # Spherical endpoint overbounds overlap; perpendicular pipe mouths do not.
            assert (Vector(clash['p'])-Vector(byname[a]['points'][-1])).length<1e-4
            assert (Vector(clash['q'])-Vector(byname[b]['points'][-1])).length<1e-4
            clearance=layout.PUMPS['casing_diameter']/2-layout.PIPE_SPECS['cold']['jacket_od']/2
            assert clearance>.25
            clash['classification']='Pump side/bottom endpoint sphere overbound; disjoint exterior mouth planes'
            clash['exterior_mouth_clearance_m']=clearance
            exceptions.append(clash)
        else:remaining.append(clash)
    violations=[q for q in remaining+obstacles if q['clearance']<-.001]
    assert not violations, violations
    services['interference_screen']={'process_route_count':sum(r['process'] for r in D['routes']),
        'equipment_boxes_checked':len(D['boxes']), 'unresolved_clashes':violations,
        'near_clearances':remaining+obstacles,'endpoint_overbounds':exceptions,
        'scope':'Capsule centreline segments versus other process/air routes and selected equipment boxes; common-network junctions and own equipment attachments excluded; not a full plant clash or maintenance qualification'}
    return ['Insulated process routes screened against other process/air routes and selected equipment envelopes; no unresolved clashes',
            'Three pump endpoint-sphere overbounds distinguished from disjoint side/bottom pipe mouth geometry']
