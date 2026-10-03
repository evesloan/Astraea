"""Check authored first residence/circulation against historical protected envelopes."""
from pathlib import Path
import json
from shapely.geometry import Polygon,box
root=Path(__file__).resolve().parents[1];layout=json.loads((root/'data/spatial_layout.json').read_text());census=json.loads((root/'data/reference/historical_guest_census.json').read_text())['guest_envelopes'];profile=json.loads((root/'data/architecture/D13_13017_profile.json').read_text());target=profile['historical_evidence'];checks=[]
for region in layout['regions']:
 if region['id'] not in ['D13_address13017','D13_residential_street_connection','D13_residential_street_pilot','D13_window_terrace']:continue
 shape=Polygon(region['boundary']);assert shape.is_valid
 for room in census:
  if room['deck']!=13:continue
  footprint=box(room['x'][0],room['z'][0],room['x'][1],room['z'][1]);overlap=shape.intersection(footprint).area
  if region['id']=='D13_address13017' and max(abs(a-b)for key in ['x','z']for a,b in zip(room[key],target['allocation_'+key]))<.005:
   assert abs(overlap-footprint.area)<.001
  else:assert overlap<.001,(region['id'],room,overlap)
 checks.append(region['id'])
assert len(checks)==4 and len(census)==1000
print('RESIDENTIAL ALLOCATION PASS: four authored regions do not consume another guest envelope; original1000-envelope census untouched. Not final residence or luxury reconciliation.')
