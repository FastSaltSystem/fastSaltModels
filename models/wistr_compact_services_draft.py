"""Shared-wall coolant enclosure and joined preparation room, metres."""
SOURCE='outputs/site-attached-services/fast-salt-attached-services.blend'
OUTPUT='outputs/site-compact-services'
TANK_XY=(18.5,18.5)
PUMP_XY=(20.5,13.8)
ENCLOSURE=dict(inside_radius=5.9,wall=.35,height=19.5)
COOLANT_PREP=dict(north_y=36.5)
COOLANT_EQUIPMENT_SHIFT=(-2.,-1.5,0.)
INTAKE_ANGLE=125.
SCOPE='Architectural draft: shared reactor wall, radial tangent wall, curved outer enclosure, and common fuel/coolant preparation wall. No thermal, structural or process qualification.'
