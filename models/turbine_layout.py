"""Dimensional reservations for a revised motor-BFP plant arrangement, metres.
Boxes are analyst allowances, not vendor outlines. Machinery fit is not piping,
structural, crane reach, transport or personnel/egress qualification.
"""
from pathlib import Path
import json,sys,math
L,W,H=60.,40.,28.
ITEMS=[];SERVICE=[]
def item(name,kind,x,y,z,dx,dy,dz):ITEMS.append(dict(name=name,kind=kind,min=[x,y,z],size=[dx,dy,dz]))
def service(name,x,y,z,dx,dy,dz):SERVICE.append(dict(name=name,kind='service',min=[x,y,z],size=[dx,dy,dz]))
for i,x in enumerate([2,11,20],1):
 item(f'C{i}','condenser',x,17,.5,7,16,9);service(f'C{i} pull',x,33,.5,7,13,9)
for i,x in enumerate([37,42.25,47.5,52.75],1):
 item(f'RH{i}','reheater',x,17,.5,3.25,16,3.25);service(f'RH{i} pull',x,33,.5,3.25,13,3.25)
for name,x,y,dx,dy in [('LP1',4.25,7,3.25,7),('LP2',8.75,7,3.25,7),('LP3',13.25,7,2.25,7),('HP1',41,6,3.25,8),('HP2',45.5,6,3.5,8),('HP3',50,4,3.25,10),('HP4',54.5,2,3.5,12)]:
 item(name,'heater',x,y,.5,dx,dy,dx);service(name+' pull',x,y-(dy-1),.5,dx,dy-1,dx)
# Quarter-turn the existing 10 x 4 m BFP trains; retain their equipment sizes.
for i,x in enumerate([18,24,30],1):
 item(f'BFP{i}','pump',x,2,.5,4,10,4)
service('Pump laydown',35.5,2,.5,4,10,4)
service('BFP front access',18,12,0,21.5,2,5)
service('Cross aisle',.5,14,.0,L-1,3,5)
# West-wall pump bank, preceding the LP heaters; north end meets cross aisle.
for i,y in enumerate([10,5.25,.5],1):item(f'CEP{i}','pump',.85,y,.5,1.8,4,3)
service('CEP access',2.65,.5,0,1.2,13.5,5)
# Conceptual stage split within the original 14 m train reservation.
item('IP turbine','turbine',44,18,12,6.5,6,6)
item('HP turbine','turbine',51.5,18,12,6.5,6,6)
item('550 MVA','generator',30,18,12,12,6,6)
for i,x in enumerate([2,11,20],1):item(f'LP casing {i}','turbine',x,26,12,8,8,7)
item('350 MVA','generator',30,27,12,12,6,6)
for i,y in enumerate([4.5,10.5],1):
 item(f'DA{i}','storage',18,y,13.5,25,4.5,4.5) # 22 m straight shell + 3 m heads allowance
item('BFP electrical annex','electrical',20,-10,0,20,10,7)
# Separate south aprons leave the central electrical annex unobstructed.
APRONS=[dict(name='north_apron',min=[0,40],size=[L,7]),dict(name='south_west_apron',min=[0,-12],size=[18,12]),dict(name='south_east_apron',min=[40,-12],size=[L-40,12])]
BUILDING=dict(length=L,width=W,height=H,centre=[-36-L/2,0],pad_z=-9.1,upper_deck_z=12,crane_underside_z=25,minimum_DA_water_level_z=14,electrical_annex=[20,10,7],north_withdrawal_apron_m=7,south_withdrawal_apron_m=12)
def overlap(a,b):return all(min(a['min'][i]+a['size'][i],b['min'][i]+b['size'][i])-max(a['min'][i],b['min'][i])>1e-7 for i in range(3))
def check():
 clashes=[]
 for i,a in enumerate(ITEMS):
  for b in ITEMS[i+1:]:
   if overlap(a,b):clashes.append((a['name'],b['name']))
 assert not clashes,clashes
 for s in SERVICE:
  for a in ITEMS:assert not overlap(s,a),(s['name'],a['name'])
 for a in ITEMS:
  if a['kind']=='electrical':continue
  assert a['min'][0]>=.35 and a['min'][1]>=.35 and a['min'][0]+a['size'][0]<=L-.35 and a['min'][1]+a['size'][1]<=W-.35,a['name']
  assert a['min'][2]+a['size'][2]<=25-5 if a['kind'] in ['turbine','generator','storage'] else a['min'][2]+a['size'][2]<11.5
 # Head/clearance screening independent of plan arrangement.
 assert min(a['min'][2] for a in ITEMS if a['kind']=='turbine')-max(a['min'][2]+a['size'][2] for a in ITEMS if a['kind']=='condenser')>=2
 # Check the owner's arrangement intent, in addition to box clearances.
 by_name={a['name']:a for a in ITEMS}
 def right(a):return a['min'][0]+a['size'][0]
 assert all(by_name[f'CEP{i}']['min'][0]+by_name[f'CEP{i}']['size'][0]<by_name['LP1']['min'][0] for i in range(1,4))
 lp=[a for a in ITEMS if a['name'] in ['LP1','LP2','LP3']]
 hp=[a for a in ITEMS if a['name'] in ['HP1','HP2','HP3','HP4']]
 bfps=[by_name[f'BFP{i}'] for i in range(1,4)]
 assert max(map(right,lp))<min(a['min'][0] for a in bfps)
 assert max(map(right,bfps))<min(a['min'][0] for a in hp)
 assert all(a['size']==[4,10,4] for a in bfps)
 assert all(bfps[i+1]['min'][0]-right(bfps[i])>=2 for i in range(2))
 assert max(right(a) for a in ITEMS if a['kind']=='condenser')<min(a['min'][0] for a in ITEMS if a['kind']=='reheater')
 assert all(a['min'][0]>L/2 for a in ITEMS if a['kind']=='reheater')
 assert by_name['550 MVA']['min'][0]==by_name['350 MVA']['min'][0]
 assert right(by_name['550 MVA'])<by_name['IP turbine']['min'][0]
 for i in range(1,4):
  assert by_name[f'C{i}']['min'][0]==by_name[f'LP casing {i}']['min'][0]
 # External pull footprints must land on an apron, not the annex.
 for a in SERVICE:
  x,y,z=a['min'];dx,dy,dz=a['size']
  if y<0:outside=(x,y,dx,-y)
  elif y+dy>W:outside=(x,W,dx,y+dy-W)
  else:continue
  x,y,dx,dy=outside
  assert any(x>=p['min'][0] and y>=p['min'][1] and x+dx<=p['min'][0]+p['size'][0] and y+dy<=p['min'][1]+p['size'][1] for p in APRONS),a['name']
 old_outside=[a['name'] for a in ITEMS if a['kind']!='electrical' and (a['min'][0]<L-45+.35 or a['min'][0]+a['size'][0]>L-.35 or a['min'][1]<8.35 or a['min'][1]+a['size'][1]>31.65 or a['min'][2]+a['size'][2]>20)]
 return dict(equipment_boxes=len(ITEMS),reserved_service_boxes=len(SERVICE),equipment_overlaps=clashes,old_envelope_violations=old_outside,minimum_turbine_to_crane_vertical_clearance_m=6,checks=['Rotated BFP envelopes retain size; 2 m between trains and reserved front-access strip','West-wall condensate pumps precede LP heaters with a reserved 1.2 m access strip','BFPs between LP and HP heater banks; reheaters grouped east; LP/condenser train west; generators aligned side by side; HP/IP east of its generator','External tube-pull footprints contained in reserved aprons','3D equipment non-overlap','reserved ground service and extraction volumes do not overlap equipment','all main-hall equipment clears inside wall planes','condenser-to-turbine separation >=2 m','>=5 m equipment-top clearance below reserved crane underside'],limitations=['Arbitrary equipment envelopes except tube packing; not vendor certified','Wall panels removed for tube extraction; panel structure/transport paths not designed','Foundations, columns, decks, stairs and full egress not modeled','Pipes, insulation, thermal expansion, valves and supports not routed','Crane capacity/reach and rotating-equipment rotor handling not verified','Auxiliary condenser/cooling-water equipment, final heat sink and electrical one-line incomplete','Larger rectangle is a workable reservation for this arrangement, not a minimum-building optimization'])
def plot(out):
 from html import escape
 colors={'condenser':'#90bccd','reheater':'#eab284','heater':'#dcc778','pump':'#91baa4','turbine':'#bcc8db','generator':'#c4b3d1','storage':'#a4cbbb','electrical':'#dbbc9c'}
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1100" viewBox="0 0 1800 1100"><defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse"><path d="M0 7L7 0" stroke="#ccc" stroke-width="1"/></pattern></defs><rect width="1800" height="1100" fill="white"/>']
 def text(x,y,t,size=18,anchor='middle',rotate=False):
  transform=f' transform="rotate(-90 {x} {y})"' if rotate else ''
  svg.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" fill="#183044" text-anchor="{anchor}"{transform}>{escape(t)}</text>')
 text(900,55,'Fast Salt System | Motor-BFP equipment arrangement',32)
 text(900,99,f'Provisional main hall {L:g} × {W:g} × {H:g} m  •  Electrical annex 20 × 10 × 7 m',23)
 for ox,upper in [(55,False),(965,True)]:
  scale=11;oy=790
  def rect(x,y,dx,dy,fill,stroke='#526575',dash=''):
   svg.append(f'<rect x="{ox+x*scale}" y="{oy-(y+dy)*scale}" width="{dx*scale}" height="{dy*scale}" fill="{fill}" stroke="{stroke}" stroke-width="1.3" stroke-dasharray="{dash}"/>')
  text(ox+363,200,'Upper level: turbines +12 m; storage +13.5 m' if upper else 'Ground equipment and withdrawal zones',23)
  for x in range(0,int(L)+1,5):
   rect(x,-12,.001,59,'none','#eeeeee');text(ox+x*scale,950,str(x),13)
  for y in range(-10,48,5):
   rect(0,y,L,.001,'none','#eeeeee');text(ox-8,oy-y*scale+4,str(y),13,'end')
  if not upper:
   for p in APRONS:rect(*p['min'],*p['size'],'#f5f5f5','#ccc')
   for v in SERVICE:
    x,y,z=v['min'];dx,dy,dz=v['size'];rect(x,y,dx,dy,'url(#hatch)','#aaa')
  rect(0,0,L,W,'none','#183044');rect(L-45,8,45,24,'none','#bd6455','8 6')
  for v in ITEMS:
   if (v['min'][2]>=12)!=upper:continue
   x,y,z=v['min'];dx,dy,dz=v['size'];rect(x,y,dx,dy,colors[v['kind']]);text(ox+(x+dx/2)*scale,oy-(y+dy/2)*scale+5,v['name'],15 if dx<5 else 16,rotate=dy>dx*1.8)
  # Entry direction is fixed to the reactor-facing east wall.
  sy=oy-16*scale
  svg.append(f'<path d="M{ox+L*scale+74} {sy}H{ox+L*scale+4}m12 -7l-12 7 12 7" fill="none" stroke="#ae5534" stroke-width="2.5"/>')
  text(ox+L*scale+59,sy-31,'Steam',14)
  text(ox+L*scale+59,sy-12,'entry',14)
  if upper:
   for x1,x2,y in [(42,44,21),(50.5,51.5,21),(10,11,30),(19,20,30),(28,30,30)]:
    svg.append(f'<path d="M{ox+x1*scale} {oy-y*scale}H{ox+x2*scale}" stroke="#536278" stroke-width="3"/>')
  text(ox+363,979,'Dimensions in metres · right = reactor / steam-entry side',17)
 text(900,1015,'Dashed red: former 45 × 24 m reservation. Hatched: withdrawal / service zones; wall panels removed for extraction.',18)
 text(900,1048,'Equipment boxes are allowances. No complete piping, structure, crane-reach or egress verification.',18)
 text(900,1080,'BFPs rotated 90° • Hall shortened by 6 m • Main-hall floor area reduced 240 m² (9.1%).',18)
 svg.append('</svg>');(out/'turbine-equipment-plan.svg').write_text(''.join(svg))
if __name__=='__main__':
 out=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'preview';out.mkdir(parents=True,exist_ok=True)
 data=dict(building=BUILDING,items=ITEMS,service=SERVICE,aprons=APRONS,verification=check());(out/'turbine-layout.json').write_text(json.dumps(data,indent=2)+'\n');plot(out);print(json.dumps(data['verification'],indent=2))
