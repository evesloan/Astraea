"""Source-only independent Grand Pool finish checks. No source/runtime/engine writes."""
import sys, json, math, hashlib, collections
from pathlib import Path
sys.path.insert(0,'/workspace/scratch/375c2e438292/pool-market-stock')
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
from geometry import *
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, Point
from shapely import constrained_delaunay_triangles, union_all
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');GAME=Path('/workspace/shared/astraea-godot-production-20261003')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FINPATH=BASE/'pool-finish-envelope-source/source/finish_contract.json'
D=read(FINPATH);S=read(CAT/'assets/grand_pool_orchard_section/source/connected_contract.json'); F=read(GAME/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json');ST=read(BASE/'pool-market-stock/stock_placement_contract.json')
TOL=5e-5
INPUTS=[FINPATH, BASE/'pool-finish-envelope-source/source/plan_finish_envelope.py',BASE/'pool-finish-envelope-source/source/build_finish_envelope.py',CAT/'assets/grand_pool_orchard_section/source/connected_contract.json', CAT/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb', GAME/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json',BASE/'pool-market-stock/stock_placement_contract.json']
INPUTS += [CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend',GAME/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json',GAME/'data/architecture/cleaning_cart_contacts.json',GAME/'tests/grand_pool_cart_probe.gd',GAME/'tests/validate_grand_pool_service_cart.gd',BASE/'pool-market-stock/SOURCE_CHECK_REPORT.json',CAT/'assets/retail_display/qa/evaluated_source_geometry.json',BASE/'pool-market-stock/geometry.py']
PINS={str(p):sha(p)for p in INPUTS}
def record(name,v,tris,**kw):
 return {'name':name,'vertices':v,'triangles':tris,'bounds':bounds(v),**kw}
def triang_face(v,face):
 q=np.array([v[i]for i in face]); n=np.cross(q[1]-q[0],q[2]-q[0]);axis=int(np.argmax(np.abs(n)));proj=np.delete(q,axis,1);p=Polygon(proj)
 if len(face)==3:return [tuple(tuple(x)for x in q)]
 assert p.is_valid,(face,q.tolist())
 out=[]
 for t in constrained_delaunay_triangles(p).geoms:
  vv=[]
  for a in list(t.exterior.coords)[:3]:
   ix=np.argmin(np.linalg.norm(proj-a,axis=1));assert np.linalg.norm(proj[ix]-a)<1e-7;vv.append(tuple(q[ix]))
  # Preserve winding of polygon face.
  if dot(cross(sub(vv[1],vv[0]),sub(vv[2],vv[0])),n)<0:vv.reverse()
  out.append(tuple(vv))
 return out
NEW=[record(p['name'],p['world_vertices'],[t for f in p['faces']for t in triang_face(p['world_vertices'],f)],meta=p)for p in D['parts']]
NM={p['name']:p for p in NEW}
# Associate actual indexed retained triangles to exact source vertex sets.
A=read_glb(CAT/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');at=np.array(A['triangles']); unique_v=np.unique(at.reshape((-1,3)),axis=0);tree=cKDTree(unique_v)
source_members=collections.defaultdict(set); mapstats=[]
for p in S['source_parts']:
 if p.get('export_excluded'):continue
 distance,ix=tree.query(p['world_vertices']);assert max(distance)<TOL,(p['name'],max(distance))
 for i in ix:source_members[int(i)].add(p['name'])
tri_ix=tree.query(at.reshape((-1,3)))[1].reshape((-1,3));mapped=collections.defaultdict(list);ambig=[];unmapped=[]
for i,idx in enumerate(tri_ix):
 names=set.intersection(*(source_members[int(j)]for j in idx))
 if not names:unmapped.append(i)
 if len(names)>1:ambig.append([i,sorted(names)])
 for n in names:mapped[n].append(tuple(tuple(v)for v in at[i]))
OLD=[]
for p in S['source_parts']:
 if p.get('export_excluded'):continue
 assert mapped[p['name']],p['name']; OLD.append(record(p['name'],p['world_vertices'],mapped[p['name']],meta=p))
OM={p['name']:p for p in OLD}
# Retained whole-furnishing primitives keep their actual GLB indexing.
CACHE={};FURN=[]
for p in F['placements']+ST['placements']:
 path=CAT/p['retained_export']
 if path not in CACHE:CACHE[path]=read_glb(path);PINS[str(path)]=sha(path)
 a=CACHE[path];pos=p['position_xyz'];yaw=p['yaw_radians'];v=[transform(q,pos,yaw)for q in a['vertices']];tri=[tuple(transform(q,pos,yaw)for q in t)for t in a['triangles']]
 FURN.append(record(p['name'],v,tri,meta=p))
FM={p['name']:p for p in FURN}
# exact floor volumes (each compiler triangle extrusion is a convex component)
FLOORS=[]
for f in S['floor_regions']:
 tris=[];vv=[]
 for tr in f['triangles']:
  v=[(x,y,z)for y in [f['floor_y']-f['thickness'],f['floor_y']]for x,z in tr];ff=[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
  tris.extend(t for face in ff for t in triang_face(v,face));vv.extend(v)
 FLOORS.append(record('COMPILER_FLOOR_'+f['id'],vv,tris,meta=f))
FLM={p['name']:p for p in FLOORS}
ALL=OLD+FURN+NEW+FLOORS
# vectorized segment predicate retains strict interior endpoint semantics.
for p in ALL:
 p['ta']=np.array(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
def rayhits(a,b,parts,eps=1e-7):
 a=np.array(a);b=np.array(b);d=b-a;rb=bounds([a,b]);result=[]
 for p in parts:
  if not overlap(rb,p['bounds'],-TOL):continue
  tri=p['ta'];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);ok=np.abs(det)>1e-12;inv=np.divide(1,det,out=np.zeros_like(det),where=ok);s=a-tri[:,0];u=np.einsum('ij,ij->i',s,h)*inv;q=np.cross(s,e1);v=q.dot(d)*inv;t=np.einsum('ij,ij->i',e2,q)*inv;ix=np.where(ok&(u>=-eps)&(v>=-eps)&(u+v<=1+eps)&(t>eps)&(t<1-eps))[0]
  for i in ix:result.append({'part':p['name'],'triangle':int(i),'distance_m':float(t[i]*np.linalg.norm(d)),'point_xyz':(a+t[i]*d).tolist()})
 return sorted(result,key=lambda r:r['distance_m'])

def topology(p):
 key=lambda q:tuple(round(float(x),7)for x in q)
 edges=collections.Counter();direct=collections.Counter();degenerate=[];areas=[]
 for i,t in enumerate(p['triangles']):
  ar=length(cross(sub(t[1],t[0]),sub(t[2],t[0])))*.5;areas.append(ar)
  if ar<1e-10:degenerate.append(i)
  for j in range(3):
   a,b=key(t[j]),key(t[(j+1)%3]);edges[tuple(sorted((a,b)))]+=1;direct[(a,b)]+=1
 bad=[(edge,n)for edge,n in edges.items()if n!=2];winding=[edge for edge in edges if direct[edge]!=direct[tuple(reversed(edge))]]
 return dict(name=p['name'],triangles=len(p['triangles']),degenerate_triangles=degenerate,min_triangle_area_m2=min(areas),nonmanifold_edges=bad,inconsistent_winding_edges=len(winding),closed_after_coordinate_weld=not bad)
TOPO=[topology(p)for p in NEW]
# Broad overlap reports are only candidates, never proof of interference.
BROAD=[]
for a in NEW:
 for b in OLD+FURN+FLOORS:
  if overlap(a['bounds'],b['bounds'],TOL):BROAD.append([a['name'],b['name']])
LIGHTS=[]
for label,fixtures in [('old',S['fixtures']),('new',D['fixtures'])]:
 for f in fixtures:
  pos=f['position_xyz'];dire=f.get('direction_xyz',f.get('direction'));end=add(pos,mul(dire,.06));exit_hit=rayhits(pos,end,ALL)
  row={'kind':label,'name':f['name'],'exit_60mm_hits':exit_hit}
  if label=='new':
   rr=f.get('all_source_receiver_rays',[{'receiver_world_xyz':f['receiver_xyz'],'receiver':'declared_receiver'}]);row['receiver_rays']=[]
   for r in rr:
    v=sub(r['receiver_world_xyz'],pos);angle=math.degrees(math.acos(max(-1,min(1,dot(unit(v),unit(dire))))));hits=rayhits(pos,r['receiver_world_xyz'],ALL)
    row['receiver_rays'].append({'receiver':r['receiver'],'angle_from_axis_degrees':angle,'distance_m':length(v),'hits':hits})
  LIGHTS.append(row)
INITIAL={'source_only':True,'contract_sha256':PINS[str(FINPATH)],'parts':len(NEW),'indexed_old_triangle_mapping':{'triangles':len(at),'unmapped':unmapped,'ambiguous':ambig},'topology':TOPO,'broad_overlap_candidates':BROAD,'light_checks':LIGHTS}
(HERE/'INITIAL_GEOMETRY_REVIEW.json').write_text(json.dumps(INITIAL,indent=2)+'\n')
print(json.dumps({'parts':len(NEW),'topology_failures':[p for p in TOPO if p['degenerate_triangles']or p['nonmanifold_edges']],'mapping_unmapped':len(unmapped),'mapping_ambiguous':len(ambig),'broad_candidates':BROAD,'light_issues':[p for p in LIGHTS if p['exit_60mm_hits']or any(r['hits']for r in p.get('receiver_rays',[]))]},indent=2))
# Contact/interference: surface triangle SAT plus strict interior witnesses on
# vertices, triangle centroids and edge intervals split at true intersections.
def surface_points(p):
 vv=list({tuple(q):q for q in p['vertices']}.values());return vv+[tuple(np.mean(t,axis=0))for t in p['ta']]
def on_surface(q,p,tol=TOL):
 q=np.array(q);tr=p['ta'];a=tr[:,0];e=tr[:,1]-a;f=tr[:,2]-a;n=np.cross(e,f);nn=np.einsum('ij,ij->i',n,n);dist=np.einsum('ij,ij->i',q-a,n);ok=(nn>1e-18)&(np.abs(dist)<=tol*np.sqrt(nn))
 if not ok.any():return False
 a=a[ok];e=e[ok];f=f[ok];v=q-a;d00=np.einsum('ij,ij->i',e,e);d01=np.einsum('ij,ij->i',e,f);d11=np.einsum('ij,ij->i',f,f);d20=np.einsum('ij,ij->i',v,e);d21=np.einsum('ij,ij->i',v,f);den=d00*d11-d01*d01;u=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den
 return bool(((u>=-1e-6)&(w>=-1e-6)&(u+w<=1+1e-6)).any())
def strict_inside(q,p):
 if p['name'].startswith('COMPILER_FLOOR_'):
  f=p['meta'];shape=Polygon(f['boundary'],f['holes']);return f['floor_y']-f['thickness']+TOL<q[1]<f['floor_y']-TOL and shape.buffer(-TOL).contains(Point(q[0],q[2]))
 if any(q[i]<=p['bounds'][0][i]+TOL or q[i]>=p['bounds'][1][i]-TOL for i in range(3)):return False
 if on_surface(q,p):return False
 end=add(q,mul(unit((1,.371,.529)),3000));h=rayhits(q,end,[p]);d=[]
 for x in h:
  if not d or x['distance_m']-d[-1]>TOL:d.append(x['distance_m'])
 return bool(len(d)%2)
def contact_pair(a,b,interior=True):
 if not overlap(a['bounds'],b['bounds'],-TOL):return {'touch':False,'penetration':False}
 pairs=[]
 for i,t in enumerate(a['triangles']):
  lo,hi=np.array(bounds(t));ix=np.where(np.all(b['tmax']>=lo-TOL,axis=1)&np.all(b['tmin']<=hi+TOL,axis=1))[0]
  for j in ix:
   if triangle_intersects(t,b['triangles'][j]):pairs.append([i,int(j)])
 if interior and overlap(a['bounds'],b['bounds'],TOL):
  for x,y in [(a,b),(b,a)]:
   for q in surface_points(x):
    if strict_inside(q,y):return {'touch':bool(pairs),'penetration':True,'witness_part':x['name'],'inside_part':y['name'],'witness_xyz':list(q),'triangle_pairs':len(pairs)}
  for x,y in [(a,b),(b,a)]:
   c=np.mean(np.array(x['vertices']),axis=0)
   if strict_inside(c,x)and strict_inside(c,y):return {'touch':bool(pairs),'penetration':True,'witness_part':x['name'],'inside_part':y['name'],'witness_xyz':c.tolist(),'triangle_pairs':len(pairs),'method':'shared strict interior centre'}
  if pairs:
   for x,y,ids in [(a,b,sorted({i for i,j in pairs})),(b,a,sorted({j for i,j in pairs}))]:
    for i in ids:
     t=x['triangles'][i]
     for j in range(3):
      aa,bb=t[j],t[(j+1)%3];ll=length(sub(bb,aa))
      if ll<TOL:continue
      hs=[0,1]+[h['distance_m']/ll for h in rayhits(aa,bb,[y])];hs=sorted(set(hs))
      for l,r in zip(hs,hs[1:]):
       q=add(aa,mul(sub(bb,aa),(l+r)/2))
       if strict_inside(q,y):return {'touch':True,'penetration':True,'witness_part':x['name'],'inside_part':y['name'],'witness_xyz':list(q),'triangle_pairs':len(pairs)}
 near=bool(pairs)
 if not near:
  near=any(on_surface(q,b)for q in surface_points(a))or any(on_surface(q,a)for q in surface_points(b))
 return {'touch':near,'penetration':False,'triangle_pairs':len(pairs),'near_surface_tolerance_m':TOL if near and not pairs else 0}

COLL=[]
for a,b in BROAD:
 x=NM[a];y=(OM|FM|FLM)[b];result=contact_pair(x,y)
 if result['touch']or result['penetration']:COLL.append({'new':a,'existing':b,**result})
(HERE/'INTERFERENCE_REVIEW.json').write_text(json.dumps(COLL,indent=2)+'\n')
print('EXACT_COLLISIONS',json.dumps(COLL,indent=2),flush=True)
# Build only literal named/qualified targets; any prefix resolution is separately
# reported and must be made explicit in the editable source contract.
SUPPORT=[];QUAL={}
for p in NEW:
 declared=p['meta']['support'];group=False
 if declared.endswith('_underside'):
  targets=[FLM['COMPILER_FLOOR_'+declared[:-10]]]
 elif declared in NM:targets=[NM[declared]]
 elif declared in OM:targets=[OM[declared]]
 elif '::'in declared:
  host,part=declared.split('::');meta=FM[host]['meta'];cache=CACHE[CAT/meta['retained_export']]
  evaluated=read(CAT/'assets/retail_display/qa/evaluated_source_geometry.json')['AST-RTL-001']['parts']
  local=[]
  for e in evaluated:
   ev=[(x,z,-y)for x,y,z in e['vertices']];et=[tuple(ev[i]for i in t)for t in e['triangles']];local.append(record(e['name'],ev,et))
  key=lambda t:tuple(sorted(tuple(round(x,5)for x in v)for v in t))
  assert collections.Counter(key(t)for m in local for t in m['triangles'])==collections.Counter(key(t)for t in cache['triangles'])
  prims=[m for m in local if m['name']==part];assert prims
  v=[transform(q,meta['position_xyz'],meta['yaw_radians'])for m in prims for q in m['vertices']];tr=[tuple(transform(q,meta['position_xyz'],meta['yaw_radians'])for q in t)for m in prims for t in m['triangles']];z=record(declared,v,tr);z['ta']=np.array(tr);z['tmin']=z['ta'].min(axis=1);z['tmax']=z['ta'].max(axis=1);targets=[z];QUAL[declared]=z
 else:targets=[x for x in NEW if x['name'].startswith(declared+'_')];group=True
 contacts=[{'name':t['name'],**contact_pair(p,t)}for t in targets]
 row={'name':p['name'],'declared_support':declared,'resolved_prefix_requires_explicit_members':group,'resolved_members':[t['name']for t in targets],'contacts':contacts,'has_geometric_contact':any(t['touch']or t['penetration']for t in contacts)}
 row['contact_witness_checks']=[{'point_xyz':w['point_xyz'],'on_support_surface':any(on_surface(w['point_xyz'],t)for t in targets),'on_part_surface':on_surface(w['point_xyz'],p)}for w in p['meta'].get('contact_witnesses',[])]
 SUPPORT.append(row)
(HERE/'SUPPORT_REVIEW.json').write_text(json.dumps(SUPPORT,indent=2)+'\n')
print('SUPPORT_FAILURES',json.dumps([r for r in SUPPORT if not r['has_geometric_contact']or any(not w['on_support_surface']or not w['on_part_surface']for w in r['contact_witness_checks'])],indent=2),flush=True)
# Test new/new intersections instead of broad-whitelisting support families.
NN=[]
for i,a in enumerate(NEW):
 for b in NEW[i+1:]:
  if not overlap(a['bounds'],b['bounds'],TOL):continue
  z=contact_pair(a,b)
  if z['touch']or z['penetration']:NN.append({'a':a['name'],'b':b['name'],**z})
(HERE/'NEW_NEW_REVIEW.json').write_text(json.dumps(NN,indent=2)+'\n')
print('NEW_NEW',json.dumps(NN,indent=2),flush=True)
# Source-only static body/cart and retained protected envelopes. Reuse exact
# saved source routes, but independently test the new geometry, not stock.
SR=read(BASE/'pool-market-stock/SOURCE_CHECK_REPORT.json');ROUTES=[]
def envelope_hits(lo,hi):return[p['name']for p in NEW if overlap([lo,hi],p['bounds'],TOL)]
def checkroute(name,points,rad,height,step=.04):
 hits=set();count=0
 for a,b in zip(points,points[1:]):
  n=max(1,math.ceil(length(sub(b,a))/step))
  for i in range(n+1):
   q=add(a,mul(sub(b,a),i/n));hits.update(envelope_hits(add(q,(-rad,.03,-rad)),add(q,(rad,height+.03,rad))));count+=1
 return {'name':name,'samples':count,'broad_envelope_hits':sorted(hits)}
for r in SR['protected_route_envelopes']:ROUTES.append({'name':r['name'],'broad_envelope_hits':envelope_hits(*r['bounds'])})
for r in SR['preserved_original_approaches']:ROUTES.append(checkroute('original_approach:'+r['item'],r['points'],.32,1.8))
for r in SR['display_approaches']:ROUTES.append(checkroute('display:'+r['display'],r['points_xyz'],r['body_radius_m'],r['body_height_m']))
for r in SR['retained_access_routes']:ROUTES.append(checkroute(r['name'],r['points_xyz'],r['radius_m'],r['height_m']))
# Exact same expression parser for stored literal cart line/arc source (no exec).
import ast,re
def arith(s):
 n=ast.parse(s.strip(),mode='eval').body
 def go(x):
  if isinstance(x,ast.Constant)and isinstance(x.value,(int,float)):return x.value
  if isinstance(x,ast.Name)and x.id=='PI':return math.pi
  if isinstance(x,ast.UnaryOp)and isinstance(x.op,ast.USub):return-go(x.operand)
  if isinstance(x,ast.BinOp)and type(x.op)in (ast.Add,ast.Sub,ast.Mult,ast.Div):return {ast.Add:lambda a,b:a+b,ast.Sub:lambda a,b:a-b,ast.Mult:lambda a,b:a*b,ast.Div:lambda a,b:a/b}[type(x.op)](go(x.left),go(x.right))
  raise ValueError(ast.dump(x))
 return go(n)
for r in SR['retained_cart_static_paths']:
 code=r['source_code'];y=r['floor_y'];m=re.search(r'line\([^,]+,\s*Vector2\(([^,]+),([^\)]+)\),\s*Vector2\(([^,]+),([^\)]+)\)',code)
 if m:
  x,z,xx,zz=map(arith,m.groups());points=[(x,y,z),(xx,y,zz)]
 else:
  m=re.search(r'arc\([^,]+,\s*Vector2\(([^,]+),([^\)]+)\),\s*([^,]+),\s*([^,]+),\s*([^\)]+)\)',code);assert m;x,z,rad,a,b=map(arith,m.groups());n=math.ceil(abs(b-a)*rad/.04);points=[(x+rad*math.cos(a+(b-a)*i/n),y,z+rad*math.sin(a+(b-a)*i/n))for i in range(n+1)]
 ROUTES.append(checkroute('cart:'+code+':'+str(y),points,r['yaw_independent_radius_m'],1.82))
(HERE/'CIRCULATION_REVIEW.json').write_text(json.dumps(ROUTES,indent=2)+'\n');print('ROUTE_HITS',json.dumps([r for r in ROUTES if r['broad_envelope_hits']],indent=2),flush=True)
assert all(sha(Path(p))==h for p,h in PINS.items()),'Input changed during QA'
(HERE/'INPUT_HASHES.json').write_text(json.dumps(PINS,indent=2)+'\n')
# Analytic finite-cone/triangle check. Clip each triangle to the 60 mm
# forward slab, then minimize its quadratic cone inequality on vertices,
# edges and interior stationary points. No angular sampling is used.
def cone_triangle(pos,direction,half_angle,tr,L=.06):
 o=np.array(pos);d=np.array(unit(direction));k=1+math.tan(math.radians(half_angle))**2;Q=np.eye(3)-k*np.outer(d,d)
 poly=[np.array(x)-o for x in tr]
 for lo,sgn in [(1e-6,1),(L,-1)]:
  out=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   fa=sgn*(a.dot(d)-lo);fb=sgn*(b.dot(d)-lo)
   if fa>=0:out.append(a)
   if (fa>=0)!=(fb>=0):out.append(a+(b-a)*fa/(fa-fb))
  poly=out
  if not poly:return None
 candidates=[(float(q@Q@q),q)for q in poly]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  e=b-a;A=float(e@Q@e);B=float(2*a@Q@e)
  if A>1e-16:
   s=max(0,min(1,-B/(2*A)));q=a+s*e;candidates.append((float(q@Q@q),q))
 for j in range(1,len(poly)-1):
  a=poly[0];M=np.stack((poly[j]-a,poly[j+1]-a),axis=1);H=M.T@Q@M
  if min(np.linalg.eigvalsh(H))>1e-16:
   xy=-np.linalg.solve(H,M.T@Q@a)
   if min(xy)>=0 and sum(xy)<=1:
    q=a+M@xy;candidates.append((float(q@Q@q),q))
 val,q=min(candidates,key=lambda x:x[0])
 return {'cone_quadratic_m2':val,'point_xyz':(q+o).tolist(),'axial_m':float(q@d)}if val<=1e-12 else None
CONES=[]
for kind,fixtures in [('old',S['fixtures']),('new',D['fixtures'])]:
 for f in fixtures:
  pos=f['position_xyz'];dire=f.get('direction_xyz',f.get('direction'));angle=f['suggested_spot_angle_degrees'];rad=.06*math.tan(math.radians(angle));bb=[add(pos,(-rad-.06,-rad-.06,-rad-.06)),add(pos,(rad+.06,rad+.06,rad+.06))];hits=[]
  for p in ALL:
   if not overlap(bb,p['bounds'],-TOL):continue
   for i,t in enumerate(p['triangles']):
    h=cone_triangle(pos,dire,angle,t)
    if h is not None:hits.append({'part':p['name'],'triangle':i,**h})
  row={'kind':kind,'name':f['name'],'forward_length_m':.06,'half_angle_degrees':angle,'analytic_triangle_cone_hits':hits}
  if kind=='new':
   lens=NM[f['physical_lens']];rh=rayhits(pos,add(pos,mul(dire,-.10)),[lens]);row['physical_lens_behind_marker_hits']=rh;row['declared_receiver_on_geometry']=any(on_surface(f['receiver_xyz'],p)for p in ALL if overlap(bounds([f['receiver_xyz']]),p['bounds'],-TOL))
  CONES.append(row)
(HERE/'SOURCE_CONE_REVIEW.json').write_text(json.dumps(CONES,indent=2)+'\n')
print('CONE_ISSUES',json.dumps([r for r in CONES if r['analytic_triangle_cone_hits']or (r['kind']=='new'and(not r['physical_lens_behind_marker_hits']or not r['declared_receiver_on_geometry']))],indent=2),flush=True)
# Closed-form continuous clearance resolves the sole conservative square hit.
cart=read(GAME/'data/architecture/cleaning_cart_contacts.json');cart_radius=max(math.hypot(v[0],v[2])for b in cart['boxes']for v in corners([sub(b['center'],mul(b['size'],.5)),add(b['center'],mul(b['size'],.5))]));operator_min_x=-50.75-math.hypot(1.2,1.62)-.30;cart_min_x=-50.75-1.2-cart_radius
TURN={'route':'arc(path, Vector2(-50.75,-459.2), 1.2, PI, PI/2)','actor_capsule_radius_m':.30,'operator_offset_m':1.62,'operator_swept_min_x':operator_min_x,'cart_compound_radial_envelope_m':cart_radius,'cart_swept_min_x':cart_min_x,'finish_max_x':-.0+NM['Finish_WetWest_StonePlinth']['bounds'][1][0],'operator_continuous_x_clearance_m':operator_min_x-NM['Finish_WetWest_StonePlinth']['bounds'][1][0],'cart_continuous_x_clearance_m':cart_min_x-NM['Finish_WetWest_StonePlinth']['bounds'][1][0],'scope':'Continuous nominal retained route proof, not dynamics. Conservative cart/operator square candidate is cleared analytically.'}
assert min(TURN['operator_continuous_x_clearance_m'],TURN['cart_continuous_x_clearance_m'])>.04
(HERE/'CART_TURN_RESOLUTION.json').write_text(json.dumps(TURN,indent=2)+'\n')
assert all(sha(Path(p))==h for p,h in PINS.items()),'Input changed during QA'
# Every intentional new/new embed is enumerated, rather than exempting broad
# old-source/furnishing envelopes. All old-source positive overlap remains a fail.
def join_reason(a,b):
 x,y=NM[a]['meta'],NM[b]['meta']
 if x['support']==b or y['support']==a:return 'explicit direct fixture/support join'
 if a.startswith('Finish_RoofCoffer_')and b.startswith('Finish_RoofCoffer_')and a.split('_')[2]==b.split('_')[2]and ('PaleCentralField'in a+b)and('InnerJunction'in a+b):return 'metal inner-junction ledge seats 5 mm into matching central field'
 if a.startswith('Finish_Market_')and b.startswith('Finish_Market_')and a.split('_')[2]==b.split('_')[2]and('PaleStockField'in a+b)and('SplayedEnd'in a+b):return 'matching fixed wall-bay backing/return junction'
 if a=='Finish_WetWest_PaleQuietField'and b.endswith('_ProfiledCrown'):return 'profiled wall crown joins its underlying pale field'
 if a.startswith('Finish_WetWest_')and b.startswith('Finish_WetWest_')and a.split('_')[2]==b.split('_')[2]and('RecessBacking'in a+b)and('ProfiledCrown'in a+b):return 'matching recess backing/crown junction'
 if a.endswith('_ProfiledCrown')and b=='Finish_WetWest_ShelteredSoffit':return 'profiled crown reaches the supported sheltered soffit'
 if a.startswith('WetRestWash_')and b.startswith('WetRestWash_')and a.split('_')[1]==b.split('_')[1]:return 'backplate/arm/housing embed in the same supported wet-rest luminaire'
 return None
for r in NN:
 if r['penetration']:r['intentional_join_reason']=join_reason(r['a'],r['b'])
(HERE/'NEW_NEW_REVIEW.json').write_text(json.dumps(NN,indent=2)+'\n')
roots=set();names=set(NM)
while True:
 prior=len(roots)
 for r in SUPPORT:
  if any((c['touch']or c['penetration'])and(c['name']not in names or c['name']in roots)for c in r['contacts']):roots.add(r['name'])
 if len(roots)==prior:break
volumes={p['name']:sum(dot(sub(t[0],p['vertices'][0]),cross(sub(t[1],p['vertices'][0]),sub(t[2],p['vertices'][0])))/6 for t in p['triangles'])for p in NEW}
failures=[]
for r in TOPO:
 if r['degenerate_triangles']or r['nonmanifold_edges']or r['inconsistent_winding_edges']:failures.append('Topology: '+r['name'])
for n,v in volumes.items():
 if v<=1e-10:failures.append('Volume: '+n)
for r in COLL:
 if r['penetration']:failures.append('Retained interference: '+r['new']+' / '+r['existing'])
for r in NN:
 if r['penetration']and not r['intentional_join_reason']:failures.append('Unapproved new-new interference: '+r['a']+' / '+r['b'])
for r in SUPPORT:
 if not r['has_geometric_contact']or any(not w['on_support_surface']or not w['on_part_surface']for w in r['contact_witness_checks']):failures.append('Support: '+r['name'])
if roots!=names:failures.append('Unrooted: '+str(names-roots))
for r in CONES:
 if r['kind']=='new'and(r['analytic_triangle_cone_hits']or not r['physical_lens_behind_marker_hits']or not r['declared_receiver_on_geometry']):failures.append('New fixture cone/receiver: '+r['name'])
 if r['kind']=='old'and any(h['part']in NM for h in r['analytic_triangle_cone_hits']):failures.append('Newly blocked old cone: '+r['name'])
for r in LIGHTS:
 if r['exit_60mm_hits']or any(x['hits']for x in r.get('receiver_rays',[])):failures.append('Light ray: '+r['name'])
for r in ROUTES:
 if r['broad_envelope_hits']and r['name']!='cart:'+TURN['route']+':46.2':failures.append('Route: '+r['name'])
summary={'status':'SOURCE_ONLY_ADDITIVE_GEOMETRY_PASS'if not failures else'SOURCE_ONLY_FAIL','contract_sha256':sha(FINPATH),'part_count':len(NEW),'planned_triangle_count':sum(len(p['triangles'])for p in NEW),'retained_indexed_triangle_count':len(at),'retained_source_parts':len(OLD),'retained_and_planned_furnishing_instances':len(FURN),'compiler_floor_regions':len(FLOORS),'closed_nondegenerate_consistently_oriented_positive_volume_parts':sum(not r['nonmanifold_edges']and not r['degenerate_triangles']and not r['inconsistent_winding_edges']and volumes[r['name']]>1e-10 for r in TOPO),'minimum_signed_volume_m3':min(volumes.values()),'retained_positive_overlap_count':sum(r['penetration']for r in COLL),'unapproved_new_new_overlap_count':sum(r['penetration']and not r.get('intentional_join_reason')for r in NN),'enumerated_intentional_new_new_joins':sum(r['penetration']and bool(r.get('intentional_join_reason'))for r in NN),'supported_rooted_parts':len(roots),'explicitly_resolved_prefix_groups':[{'part':r['name'],'members':r['resolved_members']}for r in SUPPORT if r['resolved_prefix_requires_explicit_members']],'old_fixture_centerline_exits_clear':sum(r['kind']=='old'and not r['exit_60mm_hits']for r in LIGHTS),'old_fixture_cones_clear_of_new_geometry':sum(r['kind']=='old'and not any(h['part']in NM for h in r['analytic_triangle_cone_hits'])for r in CONES),'new_fixture_full_60mm_cones_clear':sum(r['kind']=='new'and not r['analytic_triangle_cone_hits']for r in CONES),'new_receiver_rays_clear':sum(not rr['hits']for r in LIGHTS if r['kind']=='new'for rr in r['receiver_rays']),'all_new_receivers_inside_suggested_spot_half_angle':all(rr['angle_from_axis_degrees']<=f['suggested_spot_angle_degrees']for r,f in zip([r for r in LIGHTS if r['kind']=='new'],D['fixtures'])for rr in r['receiver_rays']),'circulation_route_records':len(ROUTES),'circulation_samples':sum(r.get('samples',0)for r in ROUTES),'cart_turn_operator_margin_after_40mm_m':TURN['operator_continuous_x_clearance_m']-.04,'failures':failures,'retained_baseline_caveat':'Market fixture DATUM_light_GP_MarketBayFixture_2_-417.4 full 75-degree half-angle cone intersects existing GP_UpperPier_2 within the tested first 60 mm. It is unchanged by this additive finish; its centreline and all retained cones versus new geometry are clear.','support_caveat':'Source geometry contact verification is not civil-engineering certification.','pending_proofs':['Blender editable-source creation/reopen and material/packed-texture/UV/normal verification','Retained editable-source hash and independent backup before export','GLB source-to-export indexed-triangle roundtrip','Engine collision integration, old-fixture preservation, source selector/eight-shadow budget and photometry','In-engine walking/cart/ordinary input tests, sign legibility and visual approval','The parent-owned full111 suite is outside this read-only source review'],'input_preservation_verified':all(sha(Path(p))==h for p,h in PINS.items())}
roof_pads=[]
for p in NEW:
 if p['meta']['support']=='D10_shared_table_reserved_cap_underside':
  top=[(q[0],q[2])for q in p['vertices']if abs(q[1]-60.76)<1e-7];pad=Polygon(top).convex_hull;assert pad.area>1e-6
  roof_pads.append({'part':p['name'],'ceiling_contact_area_m2':pad.area})
summary['roof_positive_area_attachment_pads']=roof_pads
(HERE/'FINAL_SOURCE_GEOMETRY_REVIEW.json').write_text(json.dumps(summary,indent=2,default=lambda x:x.item())+'\n')
print('FINAL_SUMMARY',json.dumps(summary,indent=2,default=lambda x:x.item()),flush=True)
