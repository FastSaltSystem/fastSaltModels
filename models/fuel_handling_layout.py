"""D-044 floor-plan study; dimensions are provisional space allowances, metres."""
CENTRE = (18.0, 43.0)  # installation XY; floor datum follows the site
CENTRAL_CLEAR_RADIUS = 3.5
SHIELD_ALLOWANCE = 1.5  # reference-inspired placeholder, NOT shielding sizing
CELL_INNER_RADIUS = CENTRAL_CLEAR_RADIUS + SHIELD_ALLOWANCE
CELL_WIDTH = 4.5
CELL_OUTER_RADIUS = CELL_INNER_RADIUS + CELL_WIDTH
GALLERY_INNER_RADIUS = CELL_OUTER_RADIUS + SHIELD_ALLOWANCE
GALLERY_WIDTH = 2.5
OUTER_WALL = .5
OUTER_RADIUS = GALLERY_INNER_RADIUS + GALLERY_WIDTH + OUTER_WALL
START_DEG, END_DEG = -45., 225.
ENTRY_WIDTH = 3.0
STATION_ANGLES = [-20, 15, 50, 85, 120, 155, 190]
STATION_TANGENTIAL, STATION_RADIAL = 2., 1.4
CELL_CLEAR_HEIGHT = 6.5
ROOF_SERVICE_ALLOWANCE = 1.5
STUDY_HEIGHT = CELL_CLEAR_HEIGHT + ROOF_SERVICE_ALLOWANCE
COOLANT_ANNEX = (32., 36., 12., 12., 5.)  # x, y, length, width, height
REFERENCES = [
 ('Historical facility geometry', 'https://www.osti.gov/servlets/purl/4616012'),
 ('Historical plan, ANL-6853 Fig. 1', 'https://inldigitallibrary.inl.gov/Reports/ANL-6853.pdf'),
 ('INL cell height / wall inventory', 'https://nsuf.inl.gov/Home/FacilityLayer/412'),
]
