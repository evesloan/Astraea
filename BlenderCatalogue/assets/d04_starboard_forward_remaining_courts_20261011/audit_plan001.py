from pathlib import Path
import json,hashlib
from shapely.geometry import box,shape
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_starboard_forward_remaining_courts_20261011';P=json.load(open(W/'PLAN.json'));L=json.load(open(R/'Game/data/whole_ship_layout.json'));ys=sorted({q['floor_y']for q in L['decks']});conflicts=[];interfaces=[];checks=0
for q in L['programmes']:
 y=q['floor_y'];top=next((Y-.25 for Y in ys if Y>y),y+4);alloc=box(q['allocation_x'][0],q['allocation_z'][0],q['allocation_x'][1],q['allocation_z'][1])
 for part in P['parts']+P['copied_gate_parts']+P['closed_staging_parts']:
  v=part['verts'];lo=[min(a[i]for a in v)for i in range(3)];hi=[max(a[i]for a in v)for i in range(3)];checks+=1
  if min(hi[1],top)-max(lo[1],y)<.001:continue
  overlap=alloc.intersection(box(lo[0],lo[2],hi[0],hi[2]));area=overlap.area
  if area>.001:
   row={'programme':q['programme_key'],'name':q['name'],'deck':q['deck'],'part':part['name'],'conservative_AABB_overlap_m2':area,'overlap_bounds':list(overlap.bounds)}
   allowed=box(63,-356.4,66,-356).union(box(63,-384,74,-383.3))
   if part['name']=='SFW_StaffHeader5':allowed=allowed.union(box(63.826,-356.41,65.327,-356.17))
   if part['name']=='SFW_G5_D04PC_CourtSouth_Control':allowed=allowed.union(box(65.106,-356.631,65.227,-356.565))
   if q['deck']=='D04' and q['allocation_x']==[63.0,97.0] and q['allocation_z']==[-384.0,-356.0] and allowed.covers(overlap):interfaces.append(row)
   else:conflicts.append(row)
assert not conflicts,conflicts
f=shape(P['floor_geometry']);assert f.intersection(box(85,-384,97,-356)).area==0 and f.intersection(box(63,-383,69.3,-372.2)).area==0
for path,h in P['source_pins'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
for path,h in P['source_protected_native_exports'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
report={'status':'PASS','programme_allocations':len(L['programmes']),'conservative_part_programme_volume_checks':checks,'unexplained_conflicts':conflicts,'owned_bounded_commons_threshold_interfaces':interfaces,'north_end_condition_new_floor_m2':0,'outer_perimeter_floor_overlap_m2':0,'stair_void_floor_overlap_m2':0,'existing_original_native_exports_sha256_verified':len(P['source_protected_native_exports']),'retained_layout_sha256':hashlib.sha256((R/'Game/data/whole_ship_layout.json').read_bytes()).hexdigest(),'new_capacity':0,'engineering_load_sizing_accepted':False,'candidate_active':False}
(W/'PROGRAMME_VOLUME_PREFLIGHT001.json').write_text(json.dumps(report,indent=2)+'\n');(W/'audit_plan001.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in report.items()if k not in ['owned_bounded_commons_threshold_interfaces']}));print('bounded_interface_rows',len(interfaces))
P['phase_evidence']['survey']=[str(x.relative_to(R))for x in sorted(W.iterdir())if x.is_file()];(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n')
