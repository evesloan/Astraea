"""Read-only source screening. Writes only this tram package's evidence."""
from pathlib import Path
import json, math, struct, hashlib
def point_segment_distance(p,a,b):
 vx,vz=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vz)/(vx*vx+vz*vz)))
 return math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vz)
def box(x0,z0,x1,z1):return (x0,z0,x1,z1)
def intersects_box(a,b,r):
 # Segment versus expanded rectangle is conservative around rounded corners.
 x0,z0,x1,z1=r;t0,t1=0.,1.
 for origin,delta,lo,hi in [(a[0],b[0]-a[0],x0-2.002,x1+2.002),(a[1],b[1]-a[1],z0-2.002,z1+2.002)]:
  if abs(delta)<1e-12:
   if origin<lo or origin>hi:return False
  else:
   u,v=(lo-origin)/delta,(hi-origin)/delta;t0=max(t0,min(u,v));t1=min(t1,max(u,v))
   if t0>t1:return False
 return True
class Sweep:
 def intersects(self,r):return any(intersects_box(a,b,r)for a,b in zip(p,p[1:]))
sweep=Sweep()
R=Path(__file__).resolve().parents[3]
# Rounded polyline: four exact radius-12 tangent quarter-circles, no sharp vertices.
p=[]
def line(a,b):
 if not p:p.append(a)
 p.append(b)
def arc(cx,cz,a,b):
 for i in range(1,49):
  t=a+(b-a)*i/48;p.append((cx+12*math.cos(t),cz+12*math.sin(t)))
line((-5.7,-466),(-5.7,-84));arc(6.3,-84,math.pi,math.pi/2)
line((6.3,-72),(28,-72));arc(28,-60,-math.pi/2,0)
line((40,-60),(40,60));arc(28,60,0,math.pi/2)
line((28,72),(6.3,72));arc(6.3,84,-math.pi/2,-math.pi)
line((-5.7,84),(-5.7,466))

sources=['data/spatial_layout.json','data/hull_envelope.json','data/programme_ledger.json','data/reference/historical_guest_census.json','data/reference/directory_allocations.json','data/reference/D03_crew_envelopes.json','scripts/primary_atrium_core.gd','scripts/atrium_lighting.gd','scripts/grand_pool_section.gd']
conflicts=[]
for f,k in [('data/reference/directory_allocations.json','records'),('data/reference/historical_guest_census.json','guest_envelopes'),('data/reference/D03_crew_envelopes.json','records')]:
 for i,r in enumerate(json.loads((R/f).read_text())[k]):
  if r['deck'] not in [9,10]:continue
  a=sweep.intersects(box(r['x'][0],r['z'][0],r['x'][1],r['z'][1]))
  if a:conflicts.append({'source':f,'row':i,'id':r.get('programme_key',r.get('stable_id')),'deck':r['deck'],'conservative_plan_contact':a})
# Accessor/node bounds are NOT used as proof of empty space. Decode source vertices.
import numpy as np
def mesh_bounds(file,offset=(0,0,0),yaw=0):
 sources.append('assets/models/'+file)
 b=(R/'assets/models'/file).read_bytes();ln=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+ln]);binary=b[28+ln:];out=[]
 # These selected exports bake positions; record unsupported transforms rather than guessing.
 for node in d['nodes']:
  if 'mesh' not in node:continue
  if any(k in node for k in ['matrix','translation','rotation','scale']):
   out.append({'name':node.get('name'),'unsupported_node_transform':True});continue
  for prim in d['meshes'][node['mesh']]['primitives']:
   a=d['accessors'][prim['attributes']['POSITION']];v=d['bufferViews'][a['bufferView']];assert a['componentType']==5126
   start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
   pts=np.ndarray((a['count'],3),dtype='<f4',buffer=binary,offset=start,strides=(stride,4)).astype(float)
   x=pts[:,0].copy();z=pts[:,2].copy();pts[:,0]=x*math.cos(yaw)+z*math.sin(yaw);pts[:,2]=-x*math.sin(yaw)+z*math.cos(yaw);pts+=np.array(offset)
   tri_contacts=0
   if 'indices' in prim:
    ia=d['accessors'][prim['indices']];iv=d['bufferViews'][ia['bufferView']];dt={5121:'u1',5123:'<u2',5125:'<u4'}[ia['componentType']]
    ids=np.frombuffer(binary,dtype=dt,count=ia['count'],offset=iv.get('byteOffset',0)+ia.get('byteOffset',0));tris=pts[ids.reshape(-1,3)]
   else:tris=pts.reshape(-1,3,3)
   los=tris.min(axis=1);his=tris.max(axis=1);mask=(los[:,1]<60.1)&(his[:,1]>55.55)
   for lo,hi in zip(los[mask],his[mask]):
    if sweep.intersects(box(lo[0],lo[2],hi[0],hi[2])):tri_contacts+=1
   out.append({'name':node.get('name'),'min':pts.min(axis=0).tolist(),'max':pts.max(axis=0).tolist(),'conservative_triangle_aabb_contacts':tri_contacts})
 return out
meshes={};hits=[]
for f in ['PRIMARY_ATRIUM_CORE','FORWARD_PUBLIC_CORE','FORE_MIDSHIP_PUBLIC_CORE','AFT_MIDSHIP_PUBLIC_CORE','AFT_PUBLIC_CORE']:
 fn='data/architecture/'+f+'.json';sources.append(fn);d=json.loads((R/fn).read_text());bounds=mesh_bounds(d.get('enclosure_file','AST-CIR-005.glb'),d['origin']);meshes[f]=bounds
 # AABB overlap is conservative, not an exact triangle collision.
 for q in bounds:
  if 'min' not in q:continue
  lo,hi=q['min'],q['max']
  if q['conservative_triangle_aabb_contacts']>0:hits.append({'instance':f,**q})
for f in ['AST-AQU-016.glb','AST-ATR-001.glb']:
 bounds=mesh_bounds(f);meshes[f]=bounds
 for q in bounds:
  if 'min' not in q:continue
  lo,hi=q['min'],q['max']
  if q['conservative_triangle_aabb_contacts']>0:hits.append({'instance':f,**q})
# Installed nearby ceilings, shop shells and lift enclosure.
for f,at,yaw in [('AST-AQU-012.glb',(8,61,182),0),('AST-CIR-004.glb',(12,44,235),0),('AST-RTL-009.glb',(4,52.5,-250),0),('AST-RTL-007.glb',(8,52.5,-216),0),('AST-SAL-007.glb',(64,52.5,-15),0)]:
 bounds=mesh_bounds(f,at,yaw);meshes[f]=bounds
 for q in bounds:
  if 'min' not in q:continue
  if q['conservative_triangle_aabb_contacts']>0:hits.append({'instance':f,**q})
# D09 source bearing fans/columns, runtime origins and yaw read from atrium_lighting.gd.
for x,z in [(-31,-18),(-31,18),(31,-18),(31,18),(-18,-46),(18,-46),(-18,46),(18,46)]:
 yaw=(0 if x>0 else math.pi) if abs(x)>abs(z) else (math.pi/2 if z<0 else -math.pi/2)
 for f in ['AST-STR-001-H826.glb','AST-STR-002-H826.glb']:
  bounds=mesh_bounds(f,(x,52.5,z),yaw)
  for q in bounds:
   if 'min' not in q:continue
   lo,hi=q['min'],q['max']
   if q['conservative_triangle_aabb_contacts']>0:hits.append({'instance':f+'@'+str((x,z)),**q})
hull=json.loads((R/'data/hull_envelope.json').read_text())['plan_xz_m']
def inside(q):
 odd=False
 for a,b in zip(hull,hull[1:]+hull[:1]):
  if (a[1]>q[1])!=(b[1]>q[1]) and q[0]<(b[0]-a[0])*(q[1]-a[1])/(b[1]-a[1])+a[0]:odd=not odd
 return odd
hull_ok=all(inside(q) and min(point_segment_distance(q,a,b)for a,b in zip(hull,hull[1:]+hull[:1]))>4.002 for q in p)
report={'status':'Proposal screening only; no adopted guideway, complete collision certification, structural or boarding acceptance','route_centerline_xyz':[[x,56.1,z]for x,z in p],'radius_m':12,'guideway_width_m':4.0,'structure_underside_y':55.55,'running_y':56.1,'vehicle_clearance_top_y':60.1,'d10_nominal_slab_underside_y':60.76,'swept_plan_within_historical_hull_2m_inset':hull_ok,'d09_d10_programme_and_home_plan_conflicts':conflicts,'conservative_source_aabb_contacts':hits,'source_bounds':meshes,'source_sha256':{f:hashlib.sha256((R/f).read_bytes()).hexdigest()for f in sorted(set(sources))},'limitations':['Source vertices and index triangles decoded; triangle AABB screening is conservative broadphase only, not exact capsule collision','No complete scene graph, live collision, support/load, vibration/noise or accessible boarding validation','Historical hull is a plan guide, not accepted 3D shell','No guideway support exists or is created by this study','Full-size original architectural imagery remains a pre-authoring gate']}
(R/'data/architecture/packages/tram/D09_SCREEN_20261006.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:report[k]for k in ['swept_plan_within_historical_hull_2m_inset','d09_d10_programme_and_home_plan_conflicts']});print('Conservative mesh contacts',[(q['instance'],q['name'])for q in hits])
