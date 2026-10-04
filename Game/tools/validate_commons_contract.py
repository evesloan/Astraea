"""Read-only preconstruction checks for the existing D13/D14 commons contract.
Does not claim in-engine circulation, structural load or visual acceptance.
"""
from pathlib import Path
import json
from shapely.geometry import Polygon,LineString,box,Point
from shapely.ops import unary_union
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'data/architecture/D13_D14_starboard_commons.json').read_text())
outer=Polygon(d['envelope_xz_m'])
void=unary_union([Polygon(d['upper_main_void_xz_m']),Polygon(d['upper_stair_void_xz_m'])])
assert void.geom_type=='Polygon','Stair and central opening must join without a narrow intervening ribbon'
upper=outer.difference(void)
assert upper.is_valid and upper.geom_type=='Polygon'
for key in ['lower_arrival_centerline_xz_m','upper_arrival_centerline_xz_m']:
 points=d[key];assert points[0]==[50,0] and points[1]==[54,0]
 route=LineString(points).buffer(d['arrival_authored_floor_width_m']/2,cap_style='flat',join_style='mitre')
 assert route.intersection(box(50,-2,51,2)).area>3.99,'Must join compiled atrium floor with full throat'
 if key.startswith('upper'):
  assert route.intersection(void).area<1e-8,'Arrival must not run into stair void'
landing=d['stair']['upper_landing'];land=box(landing['x'][0],landing['z'][0],landing['x'][1],landing['z'][1])
assert land.intersection(void).area<1e-8
assert landing['z'][1]-landing['z'][0]>=4.4-1e-8
for x,z in d['support_intent']['commons_piers_xz_m']:
 assert outer.covers(box(x-.36,z-.36,x+.36,z+.36)),'Pier/collar must fit authored envelope'
l=d['lift'];hole=Polygon(l['floor_hole_xz_m']);platform=box(92.2,-2,95.8,2)
assert hole.covers(platform.buffer(.019,join_style='mitre'))
assert abs(l['moving_platform_front_x_m']-l['fixed_sill_front_extent_x_m'][1]-.01)<1e-7
assert d['floors_y_m']==[84,88.5] and d['roof_top_y_m']<93
assert d['floors_y_m'][0]-.24>83.38
assert d['section']['roof_underside_y_m']-88.5>=3.6
assert d['programme_keys']==['D13_directory_05','D14_directory_04']
print('PASS: revised commons arrivals overlap atrium, stair/main voids join, upper landing clears opening, pier collars fit, positive lift gaps, protected deck datums. Geometry contract only; actual integration pending.')
layout=json.loads((root/'data/spatial_layout.json').read_text())
census=json.loads((root/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
for deck in [13,14]:
 region=next(x for x in layout['regions']if x['id']==f'D{deck}_starboard_commons_authored')
 footprint=Polygon(region['boundary'],region.get('holes',[]))
 for room in census:
  if room['deck']==deck:assert footprint.intersection(box(room['x'][0],room['z'][0],room['x'][1],room['z'][1])).area<.001,room
assert len(census)==1000
print('PASS: integrated commons floor regions preserve all1000 guest envelopes')

clear_arrival=LineString(d['upper_arrival_centerline_xz_m']).buffer(2.0,cap_style='flat',join_style='mitre').union(land)
for x,z in d['support_intent']['commons_piers_xz_m']+[d['support_intent']['offset_arrival_pier_xz_m']]:
 pier=box(x-.336,z-.336,x+.336,z+.336)
 assert pier.intersection(clear_arrival).area<1e-8,'Support intrudes into four-metre arrival/landing'
 for room in census:
  if room['deck']in[12,13,14]:assert pier.intersection(box(room['x'][0],room['z'][0],room['x'][1],room['z'][1])).area<.001
print('PASS: pier bands exclude the full arrival/landing clearway and protected guest envelopes')

garden_approach=LineString([(54.5,-15),(75,-15)]).buffer(.65,cap_style='square')
for x,z in d['support_intent']['commons_piers_xz_m']+[d['support_intent']['offset_arrival_pier_xz_m']]:assert box(x-.336,z-.336,x+.336,z+.336).intersection(garden_approach).area<1e-8
print('PASS: support shafts clear the protected garden approach with650mm path buffer')

assert d["lift"]["moving_platform_front_x_m"]-(d["lift"]["landing_gate_x_m"]+.105)>=.01499
print("PASS: station header clears the full moving platform envelope")
