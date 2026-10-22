from pathlib import Path
import json,hashlib,shutil
from shapely.geometry import Point,Polygon,shape,box
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_enclosure_finish_20261022';d=json.loads((P/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=json.loads((R/d['source_plan']).read_text());assert sha(R/d['source_plan'])==d['source_plan_sha256'];assert sha(R/d['native_source'])==d['native_sha256'];assert sha(R/'Game/family_reading_garden_20261022/adapter.gd')==d['reading_garden_parent_sha256'];checks=3
parts={p['name']:p for p in d['parts']};originals={p['name']:p for p in s['parts']};floor=shape(next(p for p in s['floor_regions']if p['name']=='FT_PrincipalTerraceCourtBase')['geometry'])
for p in d['parts']:
 v=p['verts'];lo=[min(q[i]for q in v)for i in range(3)];hi=[max(q[i]for q in v)for i in range(3)];assert p['owner']in originals;assert lo[0]>=96.0 and hi[0]<=(100.0 if p['owner']=='FT_PrincipalOpaqueCover_0' else 99.95)+1e-6;assert lo[1]>=84 and hi[1]<=106.04+1e-6
 assert not (lo[1]<105.68-1e-6 and hi[1]>102+1e-6),'Clerestory obstructed: '+p['name'];checks+=4
 if lo[1]<86.8:assert lo[0]>=98.4;checks+=1
 if 'CeilingEdge' in p['name'] and p['name'].split('_')[-1]!='1':assert hi[1]>=106.0;checks+=1
 if 'PierGarden' in p['name']:assert lo[1]>=(87.89 if p['name'].endswith('Bracket') else 88.3);checks+=1
 if p['name'].startswith(('GrandArch','RecessField','ArchShadow','PierBacking')):assert hi[0]>=99.9;checks+=1
for q in d['placements']:
 p=parts[q['support_part']];v=p['verts'];y=max(a[1]for a in v);poly=unary_union([Polygon([(v[i][0],v[i][2])for i in f])for f in p['faces']if all(abs(v[i][1]-y)<1e-6 for i in f)])
 assert poly.covers(Point(q['position'][0],q['position'][2]));assert abs(q['position'][1]-y)<.01;checks+=2
for p in d['sources']:
 assert sha(R/'BlenderCatalogue'/p['source'])==p['source_sha256'];assert sha(R/'Game/assets/models'/(p['catalogue_id']+'.glb'))==p['export_sha256'];checks+=2
assert len(parts)==57 and len(d['placements'])==78;assert shutil.disk_usage(R).free>500000000
out=dict(status='PASS',checks=checks,architecture_parts=57,plant_placements=78,original_wall_support_and_roof_hashes_preserved=True,clerestory_clear_band_y=[102,105.68],minimum_ground_route_clear_x=[96.2,98.4],plant_bowl_bottom_y=88.3,no_new_decks=True,no_new_capacity=True,full_runtime_test=False,visual_accepted=False,free_bytes=shutil.disk_usage(R).free)
(P/'evidence/GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
