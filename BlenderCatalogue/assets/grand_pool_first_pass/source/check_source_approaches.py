"""Conservative source-only capsule envelope and real triangle-floor checks.
No physics/gameplay claim; parent must run actual capsule and cart regressions.
"""
import json,math,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
c=json.loads((HERE/'source/placement_contract.json').read_text());sec=json.loads((ROOT/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text());qa=json.loads((HERE/'qa/editable_source_report.json').read_text());assert not qa['issues']
obstacles=[]
for p in sec['source_parts']:
 if p.get('export_excluded'):continue
 v=p['world_vertices'];obstacles.append((p['name'],([min(x[k] for x in v) for k in range(3)],[max(x[k] for x in v) for k in range(3)])))
for p in qa['records']:obstacles.append((p['item'],p['source_bounds_godot']))
def overlap(a,b):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>1e-5 for k in range(3))
def intri(p,t):
 (ax,az),(bx,bz),(cx,cz)=t;den=(bx-ax)*(cz-az)-(cx-ax)*(bz-az)
 if abs(den)<1e-10:return False
 u=((p[0]-ax)*(cz-az)-(cx-ax)*(p[1]-az))/den;v=((bx-ax)*(p[1]-az)-(p[0]-ax)*(bz-az))/den
 return min(u,v,1-u-v)>-1e-8
def native(p,it):
 x,y,z=p;a=it['yaw_radians'];xx,yy,zz=it['position_xyz'];return [xx+math.cos(a)*x-math.sin(a)*y,yy+z,zz-math.sin(a)*x-math.cos(a)*y]
paths=[]
for it in c['placements']:
 x,y,z=it['position_xyz'];a=it['asset']
 if a=='lounger':
  target=native([.9,-.12,0],it);paths.append(dict(item=it['name'],purpose='One clear side-entry and return; opposite side not claimed',floor=it['support'],points=[[-45.9,y,target[2]],target]))
 elif a=='bench':
  for i,xx in enumerate([-.548,.548]):
   target=native([xx,-.95,0],it);start=[-45.9,y,target[2]] if y==52.5 else [-43,y,target[2]];paths.append(dict(item=it['name'],seat=i,purpose='Independent approach to each candidate seat',floor=it['support'],points=[start,target]))
 elif a in ['towels','return']:
  target=native([0,-.9,0],it);paths.append(dict(item=it['name'],purpose='Guest front retrieval/return stance',floor=it['support'],points=[[-45.9,y,z],target]))
issues=[];checks=[]
for path in paths:
 floor=next(f for f in sec['floor_regions'] if f['id']==path['floor']);samples=0
 for a,b in zip(path['points'],path['points'][1:]):
  n=max(1,math.ceil(math.dist(a,b)/.05))
  for i in range(n+1):
   p=[a[k]+(b[k]-a[k])*i/n for k in range(3)];box=([p[0]-.32,p[1]+.03,p[2]-.32],[p[0]+.32,p[1]+1.83,p[2]+.32]);hits=[name for name,bounds in obstacles if overlap(box,bounds)]
   if hits:issues.append(dict(item=path['item'],at=p,blocked=hits))
   for dx,dz in itertools.product([-.32,0,.32],repeat=2):
    if not any(intri([p[0]+dx,p[2]+dz],t) for t in floor['triangles']):issues.append(dict(item=path['item'],unsupported=[p[0]+dx,p[2]+dz]))
   samples+=1
 checks.append(dict(**path,samples=samples))
# Full extracted-bin / service staging reserve must not meet fixed other assets.
it=next(i for i in c['placements'] if i['asset']=='return');m=json.loads((ROOT/'assets/aquatic_towel_use/AST-AQU-008.manifest.json').read_text())['motion'];reserves=[]
for key in ['swept_reserve','service_staging']:
 pts=[native(p,it) for p in itertools.product(*zip(m[key+'_min_m'],m[key+'_max_m']))];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)];lo[1]+=.03
 hits=[name for name,bounds in obstacles if name!=it['name'] and overlap((lo,hi),bounds)]
 if hits:issues.append(dict(item=it['name'],reserve=key,blocked=hits))
 reserves.append(dict(name=key,min_xyz=lo,max_xyz=hi,other_obstacle_hits=hits))
report=dict(status='source_approach_checks_pass' if not issues else 'failed',basis='Actual repaired evaluated-mesh AABBs, all retained architecture-part vertex envelopes and actual floor triangles',capsule_envelope=dict(radius_m=.32,height_m=1.8,floor_query_lift_m=.03),path_step_max_m=.05,paths=checks,return_reserves=reserves,issues=issues,limits=['Conservative box encloses .3m player capsule plus .02m lateral margin; no actual engine motion','Seat contact comfort/occupied animation and towel manipulation unimplemented','Run unchanged Grand Pool access/lift/loaded-cart checks after adoption'])
(HERE/'qa/source_approach_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],paths=len(checks),samples=sum(x['samples'] for x in checks),issues=issues),indent=2));assert not issues
