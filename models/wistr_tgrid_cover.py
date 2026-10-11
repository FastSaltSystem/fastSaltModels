"""Recessed T-grid cassette; adhesion is an owner-authorized design assumption."""
import math
import wistr_rigid_cover as previous
reactor=previous.reactor
COVER=dict(previous.COVER, frame_bottom=.503,guide_bottom=.713,guide_top=.728,hook_foot=.788)
RHS=dict(previous.RHS)
E=previous.E
NU=previous.NU
HANGER_DIAMETER=.006
LAYERS=5
LAYER_PITCH=.100
LAYER_CLEARANCE=0.0
COLLAR={'outer':.012,'inner':.006,'height':.010,'saddle_bore':.008,'web_clearance':.014,'block_clearance':.036}
GRID={'flange_width':.050,'flange_thickness':.003,'web_height':.045,'web_thickness':.002,
      'flange_bottom':.040,'slot_bottom':.038,'slot_top':.043,'groove_depth':.027,
      'joint_width':.004,'max_hanger_pitch':.600,'cross_pitch':.300}
STACK_RISE=(LAYERS-1)*GRID['flange_thickness']
for key in ('frame_bottom','guide_bottom','guide_top','hook_foot'):COVER[key]+=STACK_RISE

def block_bottom(layer):
    return layer*(LAYER_PITCH+GRID['flange_thickness'])

def grid_offset(layer):
    # Bottom flange is recessed. Every higher flange sits below its full block.
    return 0.0 if layer==0 else block_bottom(layer)-GRID['slot_top']

CERAMIC={'washer_outer':.040,'washer_inner':.014,'washer_height':.010,
         'sleeve_outer':.014,'sleeve_inner':.008,'frame_hole':.016,'density':6000.}
COATING={'thickness':.002,'density':1500.,'status':'Assumed adherent refractory facing; no structural credit.'}
points=previous.points
outline=previous.outline
halfwidth=previous.halfwidth
supports=previous.supports

def hanger_rows():return [.3,.6,1.2,1.8,2.4,3.0,3.6,4.02]
def cross_rows():return hanger_rows()
def stations():
    hooks=sorted(set(p[0] for p in points()))
    xs=[.15]+[round(.3*i,6) for i in range(1,14)]+[4.02,COVER['radius']-.060]
    return sorted(set([x for x in xs if all(abs(x-h)>.01 for h in hooks)]+hooks))
def hangers():
    result=[]
    for x in hanger_rows():
        half=max(.025,halfwidth(x)-.020);n=max(1,math.ceil(2*half/GRID['max_hanger_pitch']))
        result.extend((x,-half+2*half*j/n) for j in range(n+1))
    return result
SCOPE='Five suspended T-grids: bottom grooved layer and four plain blocks bearing on flanges, provisional crimp stops on shared rods, direct cap seating, ceramic-isolated ties, assumed bonded facing. Screening only; no composite block/coating strength credited.'
