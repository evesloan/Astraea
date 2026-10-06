"""Actual compact mesh triangle rays, source only; no Blender or engine."""
from pathlib import Path
import json,math,hashlib,collections
O=Path(__file__).resolve().parent;file=O/'mechanism_package_compact.json';p=json.loads(file.read_text());motions={m['id']:m for m in p['motion_groups']}
def inside(mid):
 while mid:
  if mid=='THEATER_LIFT_CABIN':return True
  mid=motions[mid].get('parent')
 return False
def sub(a,b):return [x-y for x,y in zip(a,b)]
def add(a,b):return[x+y for x,y in zip(a,b)]
def mul(a,k):return[x*k for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a):
 n=math.sqrt(dot(a,a));return[x/n for x in a]
triangles=[]
for o in p['objects']:
 if not inside(o['motion_group']):continue
 v=o['vertices_world']
 for fi,f in enumerate(o['faces']):
  for k in range(1,len(f)-1):
   a,b,c=[v[i]for i in[f[0],f[k],f[k+1]]];e1,e2=sub(b,a),sub(c,a);triangles.append((a,e1,e2,{'object':o['name'],'face':fi,'fan_triangle':k-1,'material_ref':o['material_ref'],'normal_world':norm(cross(e1,e2))}))
def ray(origin,direction):
 hits=[]
 for a,e1,e2,meta in triangles:
  h=cross(direction,e2);det=dot(e1,h)
  if abs(det)<1e-12:continue
  inv=1/det;s=sub(origin,a);u=dot(s,h)*inv
  if u<-1e-8 or u>1+1e-8:continue
  q=cross(s,e1);v=dot(direction,q)*inv
  if v<-1e-8 or u+v>1+1e-8:continue
  t=dot(e2,q)*inv
  if t>1e-7:hits.append({'distance_m':t,'point_world':add(origin,mul(direction,t)),**meta})
 hits.sort(key=lambda r:r['distance_m']);return hits
results=[]
for marker in p['markers']:
 if not(marker['name'].startswith('THEATER_CABIN_light_')and marker['kind']=='lens_attachment'):continue
 origin=marker['position_world'];up=ray(origin,[0,1,0]);down=ray(origin,[0,-1,0]);samples=[]
 for angle in[0,20,35,50,70]:
  for az in([0]if angle==0 else range(0,360,45)):
   a=math.radians(angle);z=math.radians(az);d=[math.sin(a)*math.cos(z),-math.cos(a),math.sin(a)*math.sin(z)];hits=ray(origin,d)
   samples.append({'angle_from_down_degrees':angle,'azimuth_degrees':az,'direction_world':d,'first_hit':hits[0]if hits else None,'first_50mm_exit_clear':not hits or hits[0]['distance_m']>.05})
 result={'marker':marker,'upward_first_hit':up[0]if up else None,'downward_first_hit':down[0]if down else None,'downward_sample_rays':samples,'receiver_counts':dict(collections.Counter(s['first_hit']['object']if s['first_hit']else'NO_HIT'for s in samples))}
 result['pass']=bool(up and down) and up[0]['object']=='THEATER_CABIN_CAB_lens_0' and abs(up[0]['distance_m']-.03)<1e-6 and up[0]['normal_world'][1]<-.99 and down[0]['object']=='THEATER_CABIN_CAB_warm_stone_0' and abs(down[0]['distance_m']-2.97)<1e-6 and all(s['first_50mm_exit_clear']and s['first_hit'] is not None for s in samples)
 results.append(result)
out={'scope':'Source actual compact cabin/gate/guide-shoe triangles at D11 rest pose, not combined AABB. Upward lens contact, downward50mm clear exit and33 receiving rays per source marker. Not illumination/photometry or engine acceptance.','package_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'triangle_count_checked':len(triangles),'lights':results,'pass':len(results)==2 and all(x['pass']for x in results),'translation_invariance':'Both markers/lenses/receivers are cabin-owned; geometry translates rigidly through all stops. Source host/other scene lighting and shadows remain parent validation.'}
(O/'mechanism_compact_cabin_light_ray_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'triangles':len(triangles),'lights':[{k:r[k]for k in['marker','upward_first_hit','downward_first_hit','receiver_counts','pass']}for r in results]},indent=2))
