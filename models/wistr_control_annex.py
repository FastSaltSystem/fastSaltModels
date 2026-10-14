"""D-069 control-building spatial reservation; not a qualified building design."""
SOURCE='outputs/site-coolant-pid/fast-salt-coolant-pid.blend'
OUTPUT='outputs/site-control-annex'
ORIGIN=(-36.,-41.,-9.1)
SIZE=(20.,25.,5.5)
WALL=.4
BARRIER=.6  # Visual allowance only; no fire, shielding or missile rating.
OPERATORS=dict(origin=(.65,.65),size=(15.,12.))
VESTIBULE=dict(x=(.6,4.6),y=(21.,24.6),door_y=(22.1,23.5),inner_door_x=(1.7,3.1))
ROOMS=[dict(name='Control equipment',x=(5.,9.),y=(16.,24.6)),
       dict(name='UPS reservation',x=(9.3,13.3),y=(16.,24.6)),
       dict(name='Ventilation reservation',x=(13.6,19.6),y=(16.,24.6))]
SCOPE='Provisional 500 m2 footprint, 180 m2 operator area. Independent slab and control-side barrier reservation; structural independence, shared-wall detail, fire/seismic/missile/shielding design, HVAC, electrical separation and complete egress remain unresolved.'
