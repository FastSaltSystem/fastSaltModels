"""Architectural revision of the tank-bay draft. Dimensions in metres."""
SOURCE='outputs/site-tank-bay-draft/fast-salt-tank-bay.blend'
OUTPUT='outputs/site-attached-services'
COMBINED=dict(x_bounds=(-7.,13.),north_y=31.,height=5.,wall=.35,
              divider_x=3.8,divider_thickness=.25,shared_radius=21.,equipment_shift_y=-6.)
SILO=dict(centre=(20.5,20.5),inside_radius=5.9,wall=.35,height=19.5,
          access_angle=0.,access_width=1.5,access_height=2.5)
COOLANT_PREP=dict(x_bounds=(15.5,25.5),north_y=38.,height=5.,wall=.35,
                  equipment_translation=(6.,.5,0.))
INTAKE=dict(index=2,old_angle=70.,angle=33.,radius=23.5)
NITROGEN_XY=(-12.5,25.)
RELEASE_STACK_XY=(-8.2,29.5)
SCOPE=('Architectural and routing draft only. Existing process placeholders are moved without '
       'process design; shielding, segregation, ventilation, supports, heat loss and operations remain unqualified.')
