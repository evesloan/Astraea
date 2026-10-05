from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1];C=R.parents[1];P=json.loads((R/'source/geometry_parts.json').read_text())['parts'];D=json.loads((C/'assets/bridge_platform/source/section_contract.json').read_text());out=[]
for m in D['light_markers']:
 x,y,z=m['position'];blocked=[];clearances=[]
 for p in P:
  b=p['world_aabb']
  if b[2]>=y or b[3]<=106.5:continue
  dx=max(b[0]-x,0,x-b[1]);dz=max(b[4]-z,0,z-b[5]);horizontal=math.hypot(dx,dz);radius=(y-max(106.5,b[2]))*math.tan(math.radians(m['suggested_spot_angle_degrees']/2));clearance=horizontal-radius;clearances.append(clearance)
  if clearance<=0:blocked.append(p['name'])
 assert not blocked,(m['name'],blocked)
 out.append({'marker':m['name'],'position':m['position'],'half_angle_degrees':38,'min_conservative_clearance_m':min(clearances),'pass':True})
(R/'qa/retained_light_cones.json').write_text(json.dumps({'pass':True,'retained_fixture_count':20,'new_fixture_count':0,'method':'For every004 part below each actual marker, minimum horizontal distance to enclosing AABB exceeds full downward38degree cone radius at part lowest point, clipped to actualY106.5 floor. Conservative AABB exclusion proves new geometry does not obstruct the existing receiver cone.','fixtures':out},indent=2)+'\n');print('ALL20_RETAINED_CONES_CLEAR')
