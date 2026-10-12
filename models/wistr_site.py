"""Provisional site envelopes, not equipment sizing or civil design."""
SOURCE = 'outputs/installation-under-cover-bundles/wistr-installation.blend'
SOURCE_REPORT = 'outputs/installation-under-cover-bundles/wistr-model-report.json'
PAD_Z = -9.1  # Illustrative common access datum; actual site grade remains open.
TURBINE = dict(name='Turbine building', centre=(-66.0, 0.0), size=(60.0, 40.0, 28.0))
FUEL_PREPARATION = dict(name='Fuel preparation', centre=(51.0, 12.0), size=(30.0, 24.0, 14.0))
WALL = .35
ROOF = .25
SERVICE_YARD = dict(centre=(30.0, 6.0), size=(12.0, 26.0))

# Aligned building centres; turn external pipes near reactor onto wall-normal approach.
TURBINE_PIPE_BAY = (-6.2, -2.2, 0, 18.0)
SECONDARY_APPROACH = dict(outlet_x=-26.0,turn_x=-27.2,terminal_x=-39.0,local_terminal_y=15.805160522460938,rack_x=(-33.5,-35.0))
