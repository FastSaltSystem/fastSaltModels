"""Reviewable layout variant; overlay on the current composed site, in metres."""
SOURCE = 'outputs/site-45-bends/fast-salt-site.blend'
OUTPUT = 'outputs/site-tank-bay-draft'
BAY = dict(centre=(20.5,20.5), size=(11.,11.,19.5), wall=.35,
           door_y=(18.,21.), door_height=3.)
TANK = dict(position=(20.5,20.5,-8.2), radius=4.1, height=16.,
            support_height=.9, insulation=.350, cladding=.001)
PUMP_XY = (16.75,16.75)
TRANSFER = dict(crossing_angle=45., rise_radius=16.4, drop_radius=22.6,
                crossing_height=4.9, low_height=.4)
LAYDOWN = dict(platform_bounds=(8.3,17.4,-3.7,2.4),
               cover_bay=(8.65,13.,-3.45,.85), cap_bay=(13.4,17.,-2.65,.55))
# Local footprint minima relative to the shared tray. Both items remain upright.
PLACEMENT = dict(cap=dict(angle=0., offset=(.45,.10)),
                 reflector=dict(angle=180., offset=(.10,1.50)))
SCOPE = ('Spatial draft only: tank/bay construction, supports, ventilation, pressure protection, '
         'pipe stress/drainability and loaded crane access are not qualified.')
