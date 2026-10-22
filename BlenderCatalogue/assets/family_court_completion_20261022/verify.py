from pathlib import Path
import json,hashlib,shutil
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_court_completion_20261022';d=json.loads((P/'PLAN_R004.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=json.loads((R/d['source_plan']).read_text());assert sha(R/d['source_plan'])==d['source_plan_sha256'];assert sha(R/d['native_source'])==d['native_sha256']
def top(row):
 vs=row['verts'];y=max(v[1]for v in vs);return unary_union([Polygon([(vs[i][0],vs[i][2])for i in f])for f in row['faces']if all(abs(vs[i][1]-y)<1e-6 for i in f)]),y
orig={r['name']:r for r in s['parts']};parts={r['name']:r for r in d['parts']};checks=0
for c in d['bed_contacts']:
 src,y=top(orig[c['owner']]);cap,cy=top(parts['Coping_'+c['owner']]);assert src.buffer(1e-8).covers(cap);assert abs(cy-y-.06)<1e-6;assert abs(min(v[1]for v in parts['Coping_'+c['owner']]['verts'])-y+.01)<1e-6;checks+=3
for row in d['placements']:
 soil,sy=top(orig[row['receiving_bed']]);finish,fy=top(parts['SoilFinish_'+row['receiving_bed']]);assert soil.symmetric_difference(finish).area<1e-6;assert abs(row['position'][1]-fy+.005)<1e-6;assert soil.covers(Point(row['position'][0],row['position'][2]).buffer(.55*row['scale']));checks+=3
for source in d['sources']:
 assert sha(R/'BlenderCatalogue'/source['source'])==source['source_sha256'];assert sha(R/'Game/assets/models'/(source['catalogue_id']+'.glb'))==source['export_sha256'];checks+=2
assert len(d['parts'])==93 and len(d['placements'])==36 and len(d['lights'])==3;assert shutil.disk_usage(R).free>500_000_000
receipt=dict(status='PASS',checks=checks,bed_footprints_and_positive_contacts=True,plants_on_inset_soil=True,original_source_hashes_unchanged=True,original_instances=157,added_parts=93,added_plants=36,durable_free_bytes=shutil.disk_usage(R).free,full_runtime_test=False)
(P/'evidence/GEOMETRY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
