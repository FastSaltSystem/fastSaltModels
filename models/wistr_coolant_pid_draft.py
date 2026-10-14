"""Spatial reservations only; P&ID identities/topology come from the hub TOML."""
SOURCE='outputs/site-compact-services/fast-salt-compact-services.blend'
OUTPUT='outputs/site-coolant-pid'
PID='design/pids/coolant-system/coolant-system.toml'
FRESH_HEADER_END_ANGLE=76.
TEE_HEIGHT=.20
GAS=dict(header_radius=16.8,header_z=12.,header_od=.050,branch_od=.025,
         insulation=.025,accumulator_diameter=.60,accumulator_height=1.,
         accumulator_bottom_local=17.7,gas_takeoff_local=(.8,-2.1,16.545),
         accumulator_xy_local=(.8,-2.6),panel=(14.4,26.,-7.7),common_tee=(13.7,21.5,-7.7))
RELIEF=dict(display_od=.15,scope='Unsized interface stub only; does not select flow area, capacity or destination')
SCOPE='P&ID-to-3D coverage and spatial draft. Unsized components are labeled reservations; proposed instruments/valves retain their source status. No hydraulic, protection or equipment qualification.'

# D-068 clean utility layout; diameters are visual reservations, not sizing.
NITROGEN=dict(header_height=4.65,header_od=.050,branch_od=.025,
    header=[(-7.4,31.65),(12.35,31.65),(12.35,37.15),(22.,37.15)],
    branches=[(-5.5,31.65),(5.,31.65),(14.4,37.15)],
    station_height=1.6,valve_height=2.7)
