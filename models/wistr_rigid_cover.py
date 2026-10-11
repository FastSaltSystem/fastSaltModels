"""Rigid calcium-silicate alternative; geometry and screening assumptions in SI."""
import math
import wistr_insulation_cover as wool
reactor=wool.reactor
COVER=dict(wool.COVER, density=240., frame_bottom=.565, frame_height=.012,
           guide_bottom=.775, guide_top=.790, hook_foot=.850, liner=.0015,
           skin=.001, zirconia_top=-.100)
RHS={'height':.160,'width':.060,'wall':.003}
E=140e9  # Provisional sensitivity input, not a selected alloy's hot allowable.
NU=.30
HANGER_DIAMETER=.006
TRAY={'pitch':.300,'width':.100,'wall':.002,'depth':.060}
points=wool.points
outline=wool.outline

def halfwidth(x):
    r=COVER['radius']-.060
    return max(0.,min(x/math.sqrt(3)-.060, math.sqrt(max(0.,r*r-x*x))))

def stations():
    hooks=sorted(set(p[0] for p in points()))
    regular=[round(.3*i,6) for i in range(1,14)]
    regular=[x for x in regular if all(abs(x-h)>.010 for h in hooks)]
    return sorted(set([.15]+regular+[4.02,COVER['radius']-.060]+hooks))

def hanger_rows():
    return [round(.3*i,6) for i in range(1,14)]+[4.02]

def supports():
    return [(x,side*halfwidth(x)) for x in sorted(set(p[0] for p in points())) for side in (-1,1)]

SCOPE='Concept comparison only; ideal bonded steel joints, provisional material properties; no structural credit for block bending/shear.'
