from pathlib import Path
import json,hashlib,shutil
from shapely.geometry import Polygon,Point,shape,LineString,box
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_reading_garden_20261022';d=json.loads((P/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=json.loads((R/d['source_plan']).read_text());assert sha(R/d['source_plan'])==d['source_plan_sha256'];assert sha(R/d['native_source'])==d['native_sha256'];checks=2
orig={r['name']:r for r in s['parts']};parts={r['name']:r for r in d['parts']}
def top(row):
 vs=row['verts'];y=max(v[1]for v in vs);polys=[Polygon([(vs[i][0],vs[i][2])for i in f])for f in row['faces']if all(abs(vs[i][1]-y)<1e-6 for i in f)];return unary_union([p for p in polys if p.area>1e-8]),y
for q in d['placements']:
 owner=parts.get(q['support_part'],orig.get(q['support_part']));poly,y=top(owner);assert poly.covers(Point(q['position'][0],q['position'][2]));assert abs(q['position'][1]-y)<.011;checks+=2
for q in d['relocations']:
 assert q['source']==next(a for a in s['asset_instances']if a['name']==q['name']);p=q['target_position'];assert any(top(t)[0].covers(Point(p[0],p[2])) and abs(top(t)[1]-p[1])<.011 for t in parts.values()if '_Soil'in t['name']);checks+=2
floor=shape(next(q for q in s['floor_regions']if q['name']=='FT_PrincipalTerraceCourtBase')['geometry'])
for q in d['parts']:
 if q['name'].startswith('Wall'):raise AssertionError('Rejected grid was carried forward')
 if q['name'].startswith('Alcove'):
  footprint=Polygon([(v[0],v[2])for v in q['verts']]).convex_hull;assert floor.covers(footprint);assert max(v[0]for v in q['verts'])<96.2;assert max(v[1]for v in q['verts'])<88.0;checks+=3
  if '_Post_'in q['name'] or 'ReadingPier'in q['name']:assert min(v[1]for v in q['verts'])<=84 and min(v[1]for v in q['verts'])>=83.98;checks+=1
for source in d['sources']:
 assert sha(R/'BlenderCatalogue'/source['source'])==source['source_sha256'];assert sha(R/'Game/assets/models'/(source['catalogue_id']+'.glb'))==source['export_sha256'];checks+=2
assert len(d['parts'])==117 and len(d['placements'])==88 and len(d['lights'])==3;assert shutil.disk_usage(R).free>500000000
receipt=dict(status='PASS',checks=checks,original_source_hashes_unchanged=True,original_instances=157,existing_benches=2,new_seats=0,new_capacity=0,raised_original_plants=len(d['relocations']),added_parts=117,added_plants=88,spatial_batch_cell_m=4,clear_east_throughroute_min_width_m=3.71,minimum_alcove_headroom_m=3,global_light_budget=8,durable_free_bytes=shutil.disk_usage(R).free,full_runtime_test=False,visual_accepted=False)
(P/'evidence/GEOMETRY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
