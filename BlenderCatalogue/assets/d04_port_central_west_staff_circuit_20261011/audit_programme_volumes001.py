from pathlib import Path
import json,hashlib
from shapely.geometry import box
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));L=json.load(open(R/'Game/data/whole_ship_layout.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ys=sorted({q['floor_y']for q in L['decks']});conflicts=[];checks=0
for q in L['programmes']:
 y=q['floor_y'];top=next((Y-.25 for Y in ys if Y>y),y+4);alloc=box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])
 for part in P['parts']:
  v=part['verts'];lo=[min(a[i]for a in v)for i in range(3)];hi=[max(a[i]for a in v)for i in range(3)];checks+=1
  if min(hi[1],top)-max(lo[1],y)<.001:continue
  area=alloc.intersection(box(lo[0],lo[2],hi[0],hi[2])).area
  if area>.001:conflicts.append({'programme':q['programme_key'],'name':q['name'],'deck':q['deck'],'part':part['name'],'conservative_AABB_overlap_m2':area})
assert not conflicts,conflicts
result={'status':'PASS','original_layout_sha256':sha(R/'Game/data/whole_ship_layout.json'),'programme_allocations':len(L['programmes']),'owned_fixed_parts':len(P['parts']),'conservative_part_programme_volume_checks':checks,'conflicts':conflicts,'deck_room_heights_from_original_next_deck_minus_025m':True,'source_layout_modified':False,'primary_engineering_load_sizing_accepted':False};(W/'PROGRAMME_VOLUME_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('Original programme-volume audit PASS',checks)
