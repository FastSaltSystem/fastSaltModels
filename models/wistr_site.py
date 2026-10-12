"""Provisional site envelopes, not equipment sizing or civil design."""
SOURCE = 'outputs/installation-under-cover-bundles/wistr-installation.blend'
SOURCE_REPORT = 'outputs/installation-under-cover-bundles/wistr-model-report.json'
PAD_Z = -9.1  # Illustrative common access datum; actual site grade remains open.
TURBINE = dict(name='Turbine building', centre=(-66.0, 0.0), size=(60.0, 40.0, 28.0))
OFF_GAS = dict(name='Off-gas treatment', centre=(-1.0, 31.5), size=(10.0, 11.0, 5.0))
FUEL_PREPARATION = dict(name='Fuel refining and recycling', centre=(11.5, 32.0), size=(15.0, 12.0, 5.0))
CONVERTER = dict(name='Spent-fuel converter', centre=(11.5, 55.0), size=(20.0, 15.0, 8.0))
PROCESS_ANNEX = dict(link_floor_z=PAD_Z+3.5, link_height=1.0, link_width=4.0,
    shared_link_x=4.0, release_stack_xy=(-7.5,35.5),
    release_stack_height=22.0, release_stack_diameter=.8,
    gas_pipe_od=.15, liquid_pipe_od=.05, liquid_insulation=.05,
    scope='Provisional building/equipment/interface envelopes; no process, throughput, emissions, shielding or thermal sizing')
WALL = .35
ROOF = .25
SERVICE_YARD = dict(centre=(30.0, 6.0), size=(12.0, 26.0))

# Aligned building centres; turn external pipes near reactor onto wall-normal approach.
TURBINE_PIPE_BAY = (-6.2, -2.2, 0, 18.0)
SECONDARY_APPROACH = dict(outlet_x=-26.0,turn_x=-27.2,terminal_x=-39.0,local_terminal_y=15.805160522460938,rack_x=(-33.5,-35.0))

# D-046: provisional insulated storage connections, all dimensions metres.
SALT_DISTRIBUTION = dict(
    fuel_centre_height=.18, coolant_centre_height=.40, fuel_pair_spacing=.08,
    valve_box_centre=(0.,9.1,PAD_Z+.65), valve_box_size=(1.6,3.0,1.14),
    scope='Layout allowance only; valve internals, process duty and pressure design unspecified')

# D-047: fuel gas-service visual allowances; 25 mm is bare tube OD.
FUEL_PRESSURE = dict(tube_od=.025, insulation=.025, nitrogen_xy=(-10.,30.),
    scope='Three pressure-server envelopes and gas interfaces; no duty, pressure or operating logic specified')

# D-049: internal fresh-air duct; nominal clear area retained from exterior ring.
FRESH_AIR = dict(outer_radius=20.30, clear_width=2.45, clear_height=6.25/2.45,
    wall=.006, base_height=.06, branch_wall=.003, generator_area_ratio=.75,
    generator_inlet_height=1.35, generator_lead_offsets=(3.5,5.4,4.5), intake_angles=(190.,70.,310.), intake_radius=23.5, scope='Provisional steel duct, nominal 6.25 m2 passage; local flow and structure not sized')
