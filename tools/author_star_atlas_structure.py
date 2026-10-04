"""Compile the authored library/commons section into existing structural ownership.
No new room registry, passenger allocation or public capacity is generated.
"""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box,LineString,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];P=R/'data/architecture/D12_D14_star_atlas.json';D=json.loads(P.read_text());owner='D12_D14_star_atlas'
def rect(v):return box(v['x'][0],v['z'][0],v['x'][1],v['z'][1])
def polygons(g):return [g]if g.geom_type=='Polygon'else [v for v in g.geoms if v.geom_type=='Polygon']
outer=Polygon(D['lower_outline_xz']);upper=rect(D['upper_envelope_xz']);lift=rect(D['lift']['floor_hole_xz']);connectors={v['deck']:rect(v)for v in D['arrival_connectors']}
cut13=unary_union([Polygon(D['D13_court_opening_xz']),rect(D['first_stair']['upper_floor_hole_xz']),lift]);cut14=unary_union([Polygon(D['D14_court_opening_xz']),rect(D['second_stair']['upper_floor_hole_xz']),lift])
full13=upper.union(connectors['D13']);full14=upper.union(connectors['D14'])
shapes={'D12':outer.union(connectors['D12']).difference(lift),'D13':full13.difference(cut13),'D14':full14.difference(cut14)}
roof13=outer.difference(full13);roof15=full14
assert all(g.is_valid for g in [*shapes.values(),roof13,roof15])
assert rect(D['lower_envelope_xz']).covers(outer)
assert shapes['D13'].intersection(roof13).area<1e-8
census=json.loads((R/'data/reference/historical_guest_census.json').read_text())['guest_envelopes']
for deck,g in shapes.items():
 for room in census:
  if room['deck']==int(deck[1:]):assert g.intersection(rect(room)).area<1e-8,room
for route in D['route_reservations']:
 path=LineString(route['centerline_xz']);corridor=path.buffer(route['half_width_m'],cap_style=2,join_style=2)
 assert shapes[route['deck']].buffer(1e-7).covers(corridor),(route['purpose'],'unsupported route strip',corridor.difference(shapes[route['deck']]).area)
 for pier in D['support_reservations']:
  assert path.distance(Point(pier['center_xz']))>route['half_width_m']+pier['maximum_radius_m'],(route['purpose'],pier['id'])
layout_path=R/'data/spatial_layout.json';layout=json.loads(layout_path.read_text());existing12=next(v for v in layout['regions']if v['id']=='D12_atrium_circulation');assert existing12['thickness']==.55
regions=[]
for stem,deck,g,public in [('ground','D12',shapes['D12'],True),('gallery','D13',shapes['D13'],True),('lower_roof','D13',roof13,False),('gallery','D14',shapes['D14'],True),('protected_cover','D15',roof15,False)]:
 for i,p in enumerate(polygons(g)):
  regions.append({'id':f'{deck}_star_atlas_{stem}_{i}','authoring_owner':owner,'deck':deck,'boundary':[list(v)for v in p.exterior.coords[:-1]],'holes':[[list(v)for v in h.coords[:-1]]for h in p.interiors],'priority':-10,'thickness':.24,'material_role':'guest_floor','walkable_public':public,'status':'Authored Star Atlas section; runtime/art acceptance pending'})
voids=[]
for deck,g in [('D12',lift),('D13',cut13),('D14',cut14)]:
 for i,p in enumerate(polygons(g)):
  assert not p.interiors
  voids.append({'id':f'star_atlas_{deck}_opening_{i}','authoring_owner':owner,'decks':[deck],'boundary':[list(v)for v in p.exterior.coords[:-1]],'source':'Reviewed production section; preserve openings in subsequent floor work'})
for v in layout['voids']:
 if v['id']=='theater_upper_volume':
  for deck,g in shapes.items():
   if deck in v['decks']:assert g.intersection(Polygon(v['boundary'])).area<1e-8
layout['regions']=[v for v in layout['regions']if v.get('authoring_owner')!=owner]+regions
layout['voids']=[v for v in layout['voids']if v.get('authoring_owner')!=owner]+voids
layout_path.write_text(json.dumps(layout,indent=2)+'\n')
D['floor_regions']=regions;D['opening_regions']=voids
D['compiled_area_accounting']={'lower_gross_envelope_m2':rect(D['lower_envelope_xz']).area,'new_region_geometric_areas_before_existing_ring_priority_m2':{k:v.area for k,v in shapes.items()},'existing_D12_ring_overlap_retained_at_0_55m_m2':shapes['D12'].intersection(Polygon(existing12['boundary'],existing12.get('holes',[]))).area,'D13_lower_roof_not_public_m2':roof13.area,'D13_D14_shared_open_vertical_area_m2':Polygon(D['D13_court_opening_xz']).intersection(Polygon(D['D14_court_opening_xz'])).area,'guest_envelope_intersections':0,'route_reservations_supported_in_plan':True,'support_reservations_clear_of_routes':True,'note':'Geometric ownership only, not seating capacity, finished rooms or runtime acceptance'}
P.write_text(json.dumps(D,indent=2)+'\n')
cat=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/star_atlas_architecture')
for sub in ['source','exports']:(cat/sub).mkdir(parents=True,exist_ok=True)
(cat/'source/section_contract.json').write_text(P.read_text())
print(json.dumps(D['compiled_area_accounting']))
