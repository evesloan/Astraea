"""Pure owned-package planning; no shared mutations or engine execution."""
from pathlib import Path
import json,hashlib,math
from shapely.geometry import Polygon,box,LineString,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[3];O=R/'data/architecture/packages/crew_living'
layout=json.load(open(R/'data/spatial_layout.json'));plan=json.load(open(O/'SECTION_DISTRIBUTION_PROPOSAL.json'))
records=json.load(open(R/'data/reference/D03_crew_envelopes.json'))['records']
programmes=[p for p in json.load(open(R/'data/programme_ledger.json'))['destinations']if p['historical_deck']=='D03']
def geom(r):return Polygon(r['boundary'],r.get('holes',[]))
regions={r['id']:geom(r)for r in layout['regions']if r.get('deck')=='D03'}
voids={r['id']:geom(r)for r in layout['voids']if 'D03' in r.get('decks',[])}
hull=Polygon(next(r['inner']for r in json.load(open(R/'data/architecture/LOWER_HULL_BODY.json'))['rings']if r['y']==12))
# A west-side dogleg is deliberately kept out of the sleep-room rectangle.
# Shift quiet lobby north, preserving original8x10 sleep box,then connect to its north wall.
for a in plan['subspaces']:
 if a['package_local_key']=='home_quiet_lobby':a['x']=[-47,-39];a['z']=[-428,-423]
connect=unary_union([box(-48,-433.8,-47,-430.2),box(-48,-433.8,-44.4,-427),box(-47,-430.2,-43.4,-426.6)])
# Existing proposal would place a foyer through the southwest sleep corner;
# avoid it by moving the sleep box east4m along with its annexes.
for a in plan['subspaces']:
 if a['package_local_key'] in ['shared_home','home_hygiene','home_clean_linen']:
  a['x']=[v+4 for v in a['x']]
# Dogleg clear approach x[-48,-43.4], alongside shifted sleep boundaryX-43.
# quiet lobby endsX-39, enters home north edge atZ-428 after a turn.
connect=unary_union([box(-48,-433.8,-43.4,-430.2),box(-47.0,-433.8,-43.4,-423.0),box(-47,-426.6,-39,-423)])
route_parts=[];squares=[];centrelines=[]
for side in [-1,1]:
 points=[(side*57,-216),(side*57,-40),(side*103,-40),(side*103,40),(side*57,40),(side*57,432)]
 line=LineString(points);centrelines.append(list(line.coords));route_parts.append(line.buffer(1.8,cap_style=2,join_style=2))
 for x,z in points[1:-1]:squares.append(box(x-2.5,z-2.5,x+2.5,z+2.5))
 for z0,z1 in [(-344,-40),(40,344)]:route_parts.append(box(side*86-1.8,z0,side*86+1.8,z1))
route=unary_union(route_parts+squares)
prot=unary_union([box(a['x'][0],a['z'][0],a['x'][1],a['z'][1])for a in records]+[box(a['historical_envelope']['x'][0],a['historical_envelope']['z'][0],a['historical_envelope']['x'][1],a['historical_envelope']['z'][1])for a in programmes])
existing=unary_union(list(regions.values()));newroute=route.difference(existing);newhome=connect.difference(existing)
# Protected housing/cells and actual atrium/public/lift void polygons remain intact.
check={'route_programme_or_bank_overlap_m2':route.intersection(prot).area,'route_void_overlaps_m2':{k:route.intersection(v).area for k,v in voids.items()if route.intersection(v).area>1e-8},'route_existing_public_floor_overlap_m2':{k:route.intersection(v).area for k,v in regions.items()if 'public_core' in k and route.intersection(v).area>1e-8},'route_inside_actual_y12_inner_hull':hull.covers(route),'route_inner_hull_boundary_separation_m':route.distance(hull.boundary),'home_connector_inside_protected_cover':regions['D03_protected_crew_cover'].covers(connect),'home_connector_sleep_overlap_m2':connect.intersection(box(-43,-438,-35,-428)).area,'connector_additional_compiler_floor_area_m2':newhome.area,'route_additional_compiler_floor_area_m2':newroute.area,'no_duplicate_slabs_by_boolean_difference':True,'square_cart_operator_rotation_radius_m':2.2,'turn_square_side_m':5,'turn_square_contains_rotation_disk':all(s.covers(s.centroid.buffer(2.2))for s in squares),'scope':'pure polygon planning; wall/door/body/cart runtime untested'}
# serialize every exact proposed floor island to support parent compiler review.
def polygons(g):
 return [dict(boundary=list(p.exterior.coords)[:-1],holes=[list(h.coords)[:-1]for h in p.interiors])for p in ([g]if g.geom_type=='Polygon'else list(g.geoms))]
out={'schema':'crew_service_connector_review_v2','home_connector_union_polygons':polygons(connect),'home_new_compiler_floor_polygons':polygons(newhome),'home_floor_policy':'all connector area is already supported by protected crew cover; compiler adds zero duplicate floor','staff_route_centrelines':centrelines,'staff_route_union_polygons':polygons(route),'staff_new_compiler_floor_polygons':polygons(newroute),'floor_y':12,'slab_thickness':.24,'ceiling_underside_y':15.2,'checks':check,'cross_ship_link':'Not added: longitudinal guest spine separates sides. First build connects port network; starboard requires separate staff arrival or reviewed controlled crossover. No guest floor/void is appropriated.'}
(O/'CONNECTOR_AND_DETOUR_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');(O/'SECTION_DISTRIBUTION_PROPOSAL.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(check,indent=2))
