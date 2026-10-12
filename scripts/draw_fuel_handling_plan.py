"""Generate the D-044 SVG floor plan, site option and selected geometry checks.
Standard-library only. Run: python3 scripts/draw_fuel_handling_plan.py
This study does not modify the current Blender scene.
"""
from pathlib import Path
import sys, math, json, html
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'models'))
import fuel_handling_layout as p
OUT=ROOT/'outputs/fuel-handling-study'
OUT.mkdir(parents=True,exist_ok=True)
BG='#f8fafb'; INK='#203443'; SHIELD='#94a0aa'; HOT='#efd5a4'; ROOM='#dbeef5'; GALLERY='#e6edef'
class Drawing:
 def __init__(self,w,h):
  self.w=w; self.h=h; self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="{BG}"/><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="M0,0 L7,3.5 L0,7" fill="#526776"/></marker></defs>']
 def text(self,x,y,t,size=17,anchor='start',fill=INK,weight='normal'):
  self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{html.escape(t)}</text>')
 def rect(self,x,y,w,h,fill,stroke=INK,dash=None):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" '+(f'stroke-dasharray="{dash}"' if dash else '')+'/>')
 def line(self,pts,color=INK,width=1.5,arrow=False,dash=None):
  self.parts.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' marker-end="url(#arrow)"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def poly(self,pts,fill,stroke=INK):
  self.parts.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
 def save(self,name): (OUT/name).write_text(''.join(self.parts)+'</svg>')
def polar(r,a):
 a=math.radians(a);return r*math.cos(a),r*math.sin(a)
def arc(d,T,rin,rout,a,b,fill):
 if abs(b-a)==360 and rin==0:
  cx,cy=T(0,0);ex,ey=T(rout,0);radius=math.hypot(ex-cx,ey-cy)
  d.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}" stroke="{INK}"/>')
  return
 n=max(2,int(abs(b-a)*2)); angles=[a+(b-a)*i/n for i in range(n+1)]
 d.poly([T(*polar(rout,t)) for t in angles]+[T(*polar(rin,t)) for t in reversed(angles)],fill)
def floor(d,T,detail=True):
 arc(d,T,0,p.CENTRAL_CLEAR_RADIUS,0,360,ROOM)
 arc(d,T,p.CENTRAL_CLEAR_RADIUS,p.CELL_INNER_RADIUS,-72,252,SHIELD)
 for ri,ro,c in [(5,9.5,HOT),(9.5,11,SHIELD),(11,13.5,GALLERY),(13.5,14,SHIELD)]:arc(d,T,ri,ro,-45,225,c)
 # End shielding occupies the ends of the equipment ring, normal to its radial boundaries.
 for a,sign in [(-45,1),(225,-1)]:
  u=polar(1,a);v=(-u[1]*sign,u[0]*sign)
  d.poly([T(r*u[0]+t*v[0],r*u[1]+t*v[1]) for r,t in [(5,0),(11,0),(11,1.5),(5,1.5)]],SHIELD)
 # Entry connects the central occupied room through the open end.
 d.poly([T(x,y) for x,y in [(-1.5,-2.9),(1.5,-2.9),(1.5,-14),(-1.5,-14)]],ROOM)
 for i,a in enumerate(p.STATION_ANGLES,1):
  u=polar(1,a);v=(-u[1],u[0]);r=7.25
  pts=[T((r+dr)*u[0]+dt*v[0],(r+dr)*u[1]+dt*v[1]) for dr,dt in [(-.7,-1),(-.7,1),(.7,1),(.7,-1)]]
  d.poly(pts,'#c89c5a')
  if detail:
   x,y=T(*polar(r,a));d.text(x,y+5,f'E{i}',14,'middle')
 for a in [0,45,90,135,180]:
  for ri,ro in [(3.5,5),(9.5,11)]:arc(d,T,ri,ro,a-3,a+3,'#67b9ce')
 if detail:
  d.text(*T(0,.6),'CENTRAL',17,'middle',weight='bold');d.text(*T(0,-.5),'OBSERVATION',15,'middle');d.text(*T(0,-1.6),'7.0 m clear',15,'middle')
  d.text(*T(0,-8.5),'ACCESS',14,'middle');d.text(*T(0,-10),'3.0 m',14,'middle')
  d.text(*T(0,-15),'Open end / personnel approach',16,'middle')
def dim(d,T,a,b,txt,offset=-10):
 A=T(*a);B=T(*b);d.line([A,B],'#526776',1)
 for x,y in [A,B]:d.line([(x-4,y-5),(x+4,y+5)],'#526776',1)
 d.text((A[0]+B[0])/2,(A[1]+B[1])/2+offset,txt,16,'middle')
d=Drawing(1260,1120)
d.text(45,45,'FAST SALT SYSTEM  /  FUEL HANDLING',28,weight='bold')
d.text(45,76,'D-044 · Preliminary floor-plan option · 12 October 2026',17)
d.text(45,103,'EBR-II-inspired arrangement; equipment, shielding and building height remain provisional.',16,fill='#596b79')
T=lambda x,y:(355+x*20,450-y*20)
floor(d,T)
dim(d,T,(-14,15.5),(14,15.5),'28.0 m overall span')
# Radius chain at the right; labels outside the drawing.
for a,b,label,yy in [(3.5,5,'1.5 m inner shielding allowance',675),(5,9.5,'4.5 m clear equipment ring',701),(9.5,11,'1.5 m outer shielding allowance',727),(11,13.5,'2.5 m outer operating gallery',753)]:
 d.rect(680,yy-13,16,16, SHIELD if 'shield' in label else HOT if 'equipment' in label else GALLERY)
 d.text(705,yy,label,17)
d.text(680,164,'ARRANGEMENT',19,weight='bold')
for i,line in enumerate(['Equipment occupies a 270° horseshoe.','The central room and outer gallery','look into the shielded working area.','','Blue slots indicate shielded viewing','windows; manipulation stations are','reserved at the outer viewing positions.','','E1–E7 are generic equipment bays,','not a selected recycling process.','','Access to the central room uses the','open end, outside the equipment cell.','End walls keep the hot-cell volume closed.']):d.text(680,195+i*26,line,18)
d.text(680,600,'SPACE ALLOWANCES',19,weight='bold')
d.text(680,630,'Central room: 7 m clear diameter',18)
d.text(680,656,'Outer building wall: 0.5 m allowance',18)
# Section, right-hand radial strip, dimensions shown explicitly.
d.text(45,805,'SCHEMATIC SECTION THROUGH ONE SIDE',19,weight='bold')
sx=65;sy=1040;sc=27
for x,w,h,c in [(0,3.5,3.2,ROOM),(3.5,1.5,6.5,SHIELD),(5,4.5,6.5,HOT),(9.5,1.5,6.5,SHIELD),(11,2.5,3.2,GALLERY),(13.5,.5,6.5,SHIELD)]:d.rect(sx+x*sc,sy-h*sc,w*sc,h*sc,c)
d.rect(sx,sy-8*sc,14*sc,1.5*sc,'#e1e5e8')
d.text(260,842,'Roof / handling services: 1.5 m allowance',14,'middle')
d.text(260,953,'6.5 m',17,'middle');d.text(260,978,'clear',16,'middle')
d.text(55,1070,'Room',15);d.text(230,1070,'Cell',15);d.text(370,1070,'Gallery',15)
d.line([(475,sy),(475,sy-8*sc)])
d.text(490,944,'8.0 m study height',17)
d.text(680,835,'INTERFACES TO RESERVE',19,weight='bold')
for i,(label,color) in enumerate([('Fuel supply → reactor','#bf7c18'),('Radioactive fuel return ← reactor','#b1495e'),('Coolant supply → reactor','#278c83'),('Reactor off-gas → treatment','#7960a1')]):
 y=870+36*i;d.line([(680,y-5),(717,y-5)],color,5);d.text(730,y,label,17)
d.text(680,1038,'Separate lines within the shared service passage.',16)
d.text(680,1062,'Routing, shielding and remote maintenance to follow.',16)
d.text(45,1100,'Reference dimensions and unresolved items: docs/fuel-handling-study.md · Geometry only; no capacity or shielding validation.',14)
d.save('fuel-handling-plan.svg')
# Site option: same world coordinates as the current installation.
s=Drawing(1260,1050);s.text(45,43,'FUEL HANDLING  /  SITE PLACEMENT OPTION',27,weight='bold')
s.text(45,74,'Same scale throughout · metres · Proposed arrangement, not yet applied to Blender',17)
S=lambda x,y:(55+(x+100)*7.3,105+(65-y)*7.3)
def box(x,y,w,h,color):
 a,b=S(x,y+h);s.rect(a,b,w*7.3,h*7.3,color)
box(-96,-20,60,40,'#dae3ed');s.text(*S(-66,2),'TURBINE BUILDING',19,'middle');s.text(*S(-66,-2),'60 × 40 m',17,'middle')
arc(s,S,21,24,0,360,'#cfded5');arc(s,S,0,21,0,360,'#e4e8eb')
s.text(*S(0,2),'REACTOR',18,'middle');s.text(*S(0,-2),'42 m shell',16,'middle')
box(-6,26,10,11,'#c8dbd6');s.text(*S(-1,34),'OFF-GAS',12,'middle');s.text(*S(-1,31),'10 × 11 m',12,'middle')
arc(s,lambda x,y:S(x-7.5,y+35.5),0,.7,0,360,'#7960a1')
floor(s,lambda x,y:S(x+18,y+43),False)
s.text(*S(18,59),'FUEL HANDLING: 28 m SPAN',16,'middle',weight='bold')
s.text(*S(18,43),'OBS.',11,'middle')
box(32,36,12,12,'#c6e3de');s.text(*S(38,44),'COOLANT',13,'middle');s.text(*S(38,41),'PREPARATION',12,'middle');s.text(*S(38,38),'12 × 12 × 5 m',12,'middle')
box(31,41,1,4,'#c6e3de')
# Existing duct retained up to north-side distribution allowance.
box(2,18,4,8,'#cec8dd');box(2,26,40,2,'#cec8dd')
s.line([S(4,28),S(4,30),S(10,35)],'#b1495e',3,arrow=True,dash='6 4')
s.line([S(10.5,34.5),S(4.7,29.7),S(4.7,28)],'#bf7c18',3,arrow=True,dash='6 4')
s.line([S(38,36),S(38,28)],'#278c83',3,arrow=True,dash='6 4')
# Compare the former rectangular fuel preparation footprint.
a,b=S(4,38);s.rect(a,b,15*7.3,12*7.3,'none','#ab7c7c','5 4')
s.text(*S(27,21),'Shared service passage',14,'middle');s.text(*S(27,18),'schematic branches above grade',13,'middle')
s.text(*S(37,-9),'Equipment-door',14,'middle');s.text(*S(37,-12),'approach retained',14,'middle')
# Existing cooling stack, avoiding any implication it is the off-gas stack.
arc(s,lambda x,y:S(x-19.1,y+19.1),0,1.6,0,360,'#9faab2')
s.text(45,880,'PLACEMENT AND COMPARISON',19,weight='bold')
for i,line in enumerate(['Fuel-handling centre: (18, 43) m. Outer radius: 14 m. Roof-height study: 8 m.',
 'Dashed red rectangle: former 15 × 12 m fuel/coolant building. Coolant moves to its own adjoining room.',
 'Existing off-gas building stays 10 × 11 × 5 m with its separate release stack. Common reactor entry is retained.',
 'Purple band: shared services. Gold: fuel supply. Rose: radioactive return. Teal: coolant supply. Dashed routes are schematic.',
 'This option expands beyond the former salt-preparation footprint. Receiving/transfer areas and full access remain to place.']):s.text(45,911+i*25,line,17)
s.save('fuel-handling-site-option.svg')
# Selected geometric checks; do not imply a full site clash screen.
station_corners=[]
for a in p.STATION_ANGLES:
 for dr in (-.7,.7):
  for dt in (-1,1):
   r=math.hypot(7.25+dr,dt);assert 5<r<9.5
# Conservative full-disk distance to unchanged off-gas rectangle.
cx,cy=p.CENTRE;nx=min(max(cx,-6),4);ny=min(max(cy,26),37)
gap=math.hypot(cx-nx,cy-ny)-p.OUTER_RADIUS
assert gap>0
ring_gap=math.hypot(cx,cy)-p.OUTER_RADIUS-24
assert ring_gap>0
report={'status':'floor-plan study; not applied to Blender','overall_span_m':28,
 'central_clear_diameter_m':7,'cell_radial_width_m':4.5,'outer_gallery_width_m':2.5,
 'shielding_allowance_m':1.5,'shielding_sized':False,'cell_clear_height_m':6.5,'study_height_m':8,
 'site_centre_m':p.CENTRE,'offgas_rectangle_to_full_outer_disk_gap_m':round(gap,3),
 'reactor_fresh_ring_to_full_outer_disk_gap_m':round(ring_gap,3),
 'equipment_check':'all generic bay corners within clear radial cell bounds',
 'excluded_checks':['radiation transport','process/throughput sizing','full pipe routing','crane and maintenance envelopes','egress','structural design'],
 'sources':p.REFERENCES}
(OUT/'layout-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
