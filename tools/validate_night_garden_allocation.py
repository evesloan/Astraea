"""Validate the fitted Night garden against its existing programme and census."""
from pathlib import Path
import json
from shapely.geometry import Polygon,box
r=Path(__file__).resolve().parents[1]
programmes=json.loads((r/'data/reference/directory_allocations.json').read_text())['records']
a=next(x for x in programmes if x['programme_key']=='D12_directory_06')
layout=json.loads((r/'data/spatial_layout.json').read_text());region=next(x for x in layout['regions']if x['id']=='D12_night_garden');footprint=Polygon(region['boundary'])
assert footprint.is_valid and footprint.difference(box(a['x'][0],a['z'][0],a['x'][1],a['z'][1])).area<.001
census=json.loads((r/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
for room in census:
 if room['deck']==12:assert footprint.intersection(box(room['x'][0],room['z'][0],room['x'][1],room['z'][1])).area<.001,room
assert len(census)==1000
print('NIGHT GARDEN ALLOCATION PASS: existing D12_directory_06 envelope, no guest-unit displacement; unchanged1000-envelope census. Final capacity/service acceptance remains open.')
