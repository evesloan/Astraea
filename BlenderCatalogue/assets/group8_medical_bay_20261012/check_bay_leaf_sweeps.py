from pathlib import Path
import json,math,numpy as np
W=Path(__file__).resolve().parent;bay=json.load(open(W/'ACTUAL_MEDICAL_BAY_NATIVE_BOUNDS.json'));old=np.array([q['world_aabb']for q in bay]);triage=json.load(open(W.parent/'group8_medical_privacy_20261012/ACTUAL_MEDICAL_NATIVE_BOUNDS.json'));leaves=[q for q in triage if q['name']in['TRIAGE_01_privacy_leaf_left','TRIAGE_01_privacy_leaf_right']or q['name'].startswith(('TRIAGE_01_leaf_left_','TRIAGE_01_leaf_right_'))];assert len(leaves)==10
origin=np.array([-16.5,21,-460]);checks=0;results=[]
def ry(a):
 c=math.cos(a);s=math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
for number,x,z,yaw in[(1,25.5,-418,math.pi/2),(2,30.5,-418,-math.pi/2),(3,25.5,-410,math.pi/2),(4,30.5,-410,-math.pi/2)]:
 dest=np.array([x,21,z]);rotation=ry(yaw);holds=[]
 for leaf in leaves:
  side='left'if'left'in leaf['name']else'right';sign=1 if side=='left'else-1;pivot=dest+rotation@np.array([-1.87 if side=='left'else 1.87,0,-.261]);a=leaf['world_aabb'];v=np.array([[xx,yy,zz]for xx in a[:2]for yy in a[2:4]for zz in a[4:6]]);v=(rotation@(v-origin).T).T+dest
  for step in range(91):
   vv=(ry(sign*(math.radians(step)-math.pi/2))@(v-pivot).T).T+pivot;lo=vv.min(0);hi=vv.max(0);aa=np.array([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]]);overlap=np.minimum(aa[[1,3,5]],old[:,[1,3,5]])-np.maximum(aa[[0,2,4]],old[:,[0,2,4]]);checks+=len(bay)
   for index in np.where(np.min(overlap,axis=1)>.0005)[0]:holds.append({'new_copy':leaf['name'],'original_obstacle':bay[index]['name'],'angle_deg':step,'positive_aabb_overlap_m':overlap[index].tolist()})
 results.append({'surgery':number,'source_copy_meshes':10,'angles_per_leaf':91,'original_geometry_overlap_holds':holds})
report={'status':'PASS_CONSERVATIVE_EXISTING_GEOMETRY_SCREEN'if all(not r['original_geometry_overlap_holds']for r in results)else'HOLD','source_pair_checks':checks,'exact_original_leaf_copy_geometry':'Retained TRIAGE01 ten evaluated source parts;rigid transform only;native/UV original unmodified','results':results,'limits':'Rotated AABB source screen only;new receiver/bearing/controls and actual runtime clearance/input still require verification.'};(W/'LEAF_COPY_MOTION_FEASIBILITY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'source_pair_checks':checks,'holds_per_suite':[len(r['original_geometry_overlap_holds'])for r in results]}))
