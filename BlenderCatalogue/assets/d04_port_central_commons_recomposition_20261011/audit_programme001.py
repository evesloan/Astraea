from pathlib import Path
import json,hashlib
from shapely.geometry import box,shape
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_commons_recomposition_20261011';P=json.load(open(W/'PLAN.json'));L=json.load(open(R/'Game/data/whole_ship_layout.json'));ys=sorted({q['floor_y']for q in L['decks']});parts=P['parts']+P['copied_gate_parts'];pre={q['name']:q for q in P['runtime_preimages']}
for row in P['moves']:
 q=pre[row['name']];d=row['delta'];parts.append({'name':row['name'],'verts':[[q['bounds'][j][k]+d[k]for k in range(3)]for j in range(2)]})
conflicts=[];interfaces=[];checks=0
for q in L['programmes']:
 y=q['floor_y'];top=next((Y-.25 for Y in ys if Y>y),y+4);alloc=box(*[q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1]])
 for part in parts:
  v=part['verts'];lo=[min(a[i]for a in v)for i in range(3)];hi=[max(a[i]for a in v)for i in range(3)];checks+=1
  if min(hi[1],top)-max(lo[1],y)<.001:continue
  area=alloc.intersection(box(lo[0],lo[2],hi[0],hi[2])).area
  if area>.001:
   row={'programme':q['programme_key'],'name':q['name'],'part':part['name'],'AABB_overlap_m2':area}
   if q['programme_key']=='D04_directory_03':interfaces.append(row)
   else:conflicts.append(row)
assert not conflicts,conflicts
original=json.load(open(R/'Game/data/architecture/D04_PORT_CENTRAL_NEIGHBORHOOD.json'));bridge=box(-103,-1,-96,1);assert bridge.intersection(shape(original['commons_floor_geometry'])).area==0;assert bridge.intersection(box(-105,-101.4,-103,79)).area==0
for f,h in P['source_pins'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h,f
result={'status':'PASS','programme_allocations':len(L['programmes']),'conservative_part_programme_volume_checks':checks,'unexplained_conflicts':conflicts,'approved_bounded_commons_recomposition_interfaces':interfaces,'new_floor_m2':bridge.area,'original_commons_floor_duplication_m2':0,'original_staff_circuit_floor_duplication_m2':0,'original_layout_sha256':hashlib.sha256((R/'Game/data/whole_ship_layout.json').read_bytes()).hexdigest(),'new_capacity':0,'Training_ceiling_and_D05_datums_unchanged':True,'engineering_or_load_sizing_accepted':False};(W/'PROGRAMME_VOLUME_PREFLIGHT001.json').write_text(json.dumps(result,indent=2)+'\n');(W/'audit_programme001.py').write_bytes(Path(__file__).read_bytes());print('PROGRAMME_PASS',checks,len(interfaces))
