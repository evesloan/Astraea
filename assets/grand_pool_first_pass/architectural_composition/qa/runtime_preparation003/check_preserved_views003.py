"""Additional explicit old sign/media/lounge-view protection with actual new triangles."""
from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent
code=(S/'check_new_seat_approaches003b.py').read_text().split('results=[];issues=[]')[0]
exec(compile(code,str(S/'check_new_seat_approaches003b.py'),'exec'),globals())
checks=[];issues=[]
for sign in runtime['signs']:
 target=add(sign['origin_xyz'],mul(sign['normal_xyz'],.124));start=sign['viewpoint_xyz'];hits=rayhits(start,target,NEW+bot);row=dict(kind='retained_sign',name=sign['id'],eye_xyz=start,target_xyz=list(target),new_occlusions=hits);checks.append(row)
 if hits:issues.append(row)
for candidate in runtime['media_candidates']:
 for probe in candidate['sampled_current_triangle_sightlines']:
  hits=rayhits(probe['eye_xyz'],probe['target_xyz'],NEW+bot);row=dict(kind='retained_screen',name=candidate['name'],eye_xyz=probe['eye_xyz'],target_xyz=probe['target_xyz'],new_occlusions=hits);checks.append(row)
  if hits:issues.append(row)
for entry in first['placements']:
 if entry.get('asset')!='lounger':continue
 probes=[p for p in first['seat_contact_probes']if p['item']==entry['name']];assert probes
 for probe in probes:
  eye=list(probe['position_xyz']);eye[1]+=.52;target=[-36,46.25,eye[2]];hits=rayhits(eye,target,NEW+bot);row=dict(kind='retained_lounger_water_view',name=entry['name']+'_'+probe['role'],eye_xyz=eye,target_xyz=target,new_occlusions=hits);checks.append(row)
  if hits:issues.append(row)
r=dict(status='PASS_RETAINED_SIGNS_MEDIA_AND_LOUNGER_WATER_VIEWS'if not issues else'FAIL_NEW_OCCLUSION',source_plan_sha256=hashlib.sha256((P/'architectural_composition/source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json').read_bytes()).hexdigest(),count=len(checks),checks=checks,issues=issues,scope='New architecture and12new botanical instances checked against old actual sign/media/seat probes. Native physical and visual gates remain separate.');(S/'PRESERVED_VIEWS_003.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(checks),'rays;',len(issues),'issues');assert not issues
