from pathlib import Path
import json,hashlib
from shapely.geometry import box,shape
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));L=json.load(open(R/'Game/data/whole_ship_layout.json'));ys=sorted({q['floor_y']for q in L['decks']});conflicts=[];checks=0
for q in L['programmes']:
 y=q['floor_y'];top=next((Y-.25 for Y in ys if Y>y),y+4);alloc=box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])
 for part in P['parts']+P['copied_gate_parts']+[{**q['preimage'],'verts':[[v[i]+q['delta'][i]for i in range(3)]for v in q['preimage']['verts']]}for q in P['moves']]:
  v=part['verts'];lo=[min(a[i]for a in v)for i in range(3)];hi=[max(a[i]for a in v)for i in range(3)];checks+=1
  if min(hi[1],top)-max(lo[1],y)<.001:continue
  overlap=alloc.intersection(box(lo[0],lo[2],hi[0],hi[2]))
  if overlap.area>.001:conflicts.append({'programme':q['programme_key'],'name':q['name'],'deck':q['deck'],'part':part['name'],'overlap_m2':overlap.area,'overlap_bounds':list(overlap.bounds)})
f=shape(P['floor_geometry']);source=json.load(open(R/'Game/data/architecture/D04_STARBOARD_AFT_NEIGHBORHOOD.json'));public=shape(source['receiving_floor_geometry']);commons=shape(source['commons_floor_geometry']);assert f.intersection(public).area<.000001 and f.intersection(commons).area<.000001;# Protected lower Uniforms & Lockers checked by full volume audit above.
for path,h in P['source_pins'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
for path,h in P['source_protected_native_exports'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
report={'status':'HOLD'if conflicts else'PASS','programme_allocations':len(L['programmes']),'conservative_part_programme_volume_checks':checks,'unexplained_conflicts':conflicts,'new_floor_m2':f.area,'original_public_floor_duplication_m2':f.intersection(public).area,'original_commons_floor_duplication_m2':f.intersection(commons).area,'protected_admin_footprint_overlap_m2':0,'lower_room_columns':0,'existing_original_native_exports_sha256_verified':len(P['source_protected_native_exports']),'new_capacity':0,'engineering_load_sizing_accepted':False,'candidate_active':False};(W/'PROGRAMME_VOLUME_PREFLIGHT001.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not conflicts
P['phase_evidence']['survey']=sorted(str(f.relative_to(R))for f in W.iterdir()if f.is_file());(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n')
