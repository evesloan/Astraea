"""Exact triangle swept-box access and seated pool views for three new curved seats."""
from pathlib import Path
import json,hashlib,math
S=Path(__file__).resolve().parent
code=(S/'check_blockin003.py').read_text().split('issues=[];collisions=[];allowed=[]')[0]
code=code.replace("'BLOCKIN_PLAN_003.json'","'BLOCKIN_ACTUAL_PLAN_003.json'")
# Snapshot is already independently reopened; all other inputs remain actual retained GLBs.
code=code.replace("S/'BLOCKIN_ACTUAL_PLAN_003.json'","P/'architectural_composition/source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json'")
exec(compile(code,str(S/'check_blockin003.py'),'exec'),globals())
from shapely.geometry import LineString
floor=next(f for f in section['floor_regions']if f['id']=='D08_grand_pool_wet');shape=Polygon(floor['boundary'],floor['holes'])
def tri_box(tri,lo,hi):
 c=(np.array(lo)+hi)*.5;e=(np.array(hi)-lo)*.5;v=np.asarray(tri)-c
 edges=[v[(i+1)%3]-v[i]for i in range(3)];axes=[np.eye(3)[i]for i in range(3)]+[np.cross(edges[0],edges[1])]+[np.cross(edge,b)for edge in edges for b in np.eye(3)]
 for axis in axes:
  if np.linalg.norm(axis)<1e-12:continue
  d=v@axis;r=e@np.abs(axis)
  if d.min()>r+1e-8 or d.max()<-r-1e-8:return False
 return True
assert tri_box([[0,0,0],[1,0,0],[0,1,0]],[.1,.1,-.1],[.2,.2,.1])
assert not tri_box([[0,0,0],[1,0,0],[0,1,0]],[.8,.8,-.1],[.9,.9,.1])
# Include all twelve unscaled authored botanical derivatives in access/view tests.
bot=[];plantpins={}
for row in plan['plants']:
 path=P/'comfort_greenery/greenery/candidate_v001/exports_r002'/row['model_file'];plantpins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();d=geo.read_glb(path);bot.append(record(row['name'],[transform(v,row['position_xyz'],row['yaw_radians'])for v in d['vertices']],[[transform(v,row['position_xyz'],row['yaw_radians'])for v in t]for t in d['triangles']]))
allparts=OLD+FIN+FURN+NEW+bot
for p in bot:p['ta']=np.asarray(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
results=[];issues=[]
for label,z in [('Fore',-442.2),('Middle',-424.6),('Aft',-406.7)]:
 points=[[-45.9,46.2,z],[-50.95,46.2,z]];radius=.3;height=1.8;route=LineString([(p[0],p[2])for p in points]).buffer(radius,resolution=16);unsupported=route.difference(shape).area;hits=[]
 for a,b in zip(points,points[1:]):
  lo=[min(a[0],b[0])-radius,46.22,min(a[2],b[2])-radius];hi=[max(a[0],b[0])+radius,46.2+height,max(a[2],b[2])+radius]
  for part in allparts:
   if not overlap([lo,hi],part['bounds'],-1e-8):continue
   ix=np.where(np.all(part['tmax']>=np.array(lo)-1e-8,axis=1)&np.all(part['tmin']<=np.array(hi)+1e-8,axis=1))[0]
   if any(tri_box(part['triangles'][i],lo,hi)for i in ix):hits.append(part['name'])
 eye=[-51.65,47.44,z];target=[-36,46.25,z];view=rayhits(eye,target,allparts)
 result=dict(name=label,approach_xyz=points,swept_envelope_radius_m=radius,standing_height_m=height,unsupported_area_m2=unsupported,blocking_parts=hits,seated_eye_xyz=eye,pool_view_target_xyz=target,seated_view_hits=view);results.append(result)
 if unsupported>1e-8 or hits or view:issues.append(result)
r=dict(status='PASS_NEW_SEAT_ACCESS_AND_PURPOSEFUL_POOL_VIEWS'if not issues else'FAIL_SEAT_PROGRAMME',source_plan_sha256=hashlib.sha256((P/'architectural_composition/source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json').read_bytes()).hexdigest(),results=results,retained_botanical_pins=plantpins,issues=issues,limits=['Pure actual-triangle sweep and seated ray, not native Godot collision or final visual acceptance']);(S/'NEW_SEAT_ACCESS_003.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert not issues
