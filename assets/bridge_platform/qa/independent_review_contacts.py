import json,math,itertools,collections,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];SRC=R/'source';QA=R/'qa'
J=json.loads((QA/'independent_review_geometry.json').read_text());P=J['parts'];EPS=2e-5

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(points):
 points=sorted(set((round(p[0],5),round(p[2],5)) for p in points));lo=[];hi=[]
 for p in points:
  while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=1e-9:lo.pop()
  lo.append(p)
 for p in reversed(points):
  while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=1e-9:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def clip(poly,b):
 for c,d in zip(b,b[1:]+b[:1]):
  out=[]
  if not poly:return []
  a=poly[-1];va=cross(c,d,a);ia=va>=-1e-8
  for z in poly:
   vz=cross(c,d,z);iz=vz>=-1e-8
   if ia != iz:
    den=va-vz
    if abs(den)>1e-20:
     t=va/den;out.append((a[0]+t*(z[0]-a[0]),a[1]+t*(z[1]-a[1])))
   if iz:out.append(z)
   a,va,ia=z,vz,iz
  poly=out
 return poly
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>2 else 0

def contact(a,b):
 aa=a['aabb'];bb=b['aabb'];dy=min(aa[3],bb[3])-max(aa[2],bb[2])
 if dy<-EPS:return None
 for k in (0,4):
  if min(aa[k+1],bb[k+1])-max(aa[k],bb[k])<-EPS:return None
 q=clip(a['poly'],b['poly']);ar=area(q)
 if ar>1e-8:
  return {'kind':'volume'if dy>EPS else'bearing_face','plan_area':ar,'vertical_overlap':max(0,dy),'volume':ar*max(0,dy)}
 if dy>EPS and len(q)>1:
  dist=max(math.dist(v,w)for v in q for w in q)
  if dist>EPS:return {'kind':'side_face','face_area':dist*dy,'vertical_overlap':dy,'volume':0}
 return None
for i,p in enumerate(P):p['poly']=hull(p['vertices']);p['index']=i
spatial=collections.defaultdict(list)
for i,p in enumerate(P):
 b=p['aabb']
 for x in range(math.floor((b[0]-EPS)/4),math.floor((b[1]+EPS)/4)+1):
  for y in range(math.floor((b[2]-EPS)/4),math.floor((b[3]+EPS)/4)+1):
   for z in range(math.floor((b[4]-EPS)/4),math.floor((b[5]+EPS)/4)+1):spatial[x,y,z].append(i)
pairs=set()
for ls in spatial.values():pairs.update(itertools.combinations(ls,2))
adj=[{}for p in P];edges=[]
for i,j in sorted(pairs):
 c=contact(P[i],P[j])
 if c:adj[i][j]=c;adj[j][i]=c;edges.append((i,j,c))
struct={'pier','transfer','bypass_transfer','roof_support','hanger','platform_support','platform_support_shallow'}
roots=[i for i,p in enumerate(P)if p['group']=='pier'and abs(p['aabb'][2]+3.2)<EPS]
def bfs(allowed):
 seen=set(roots);q=collections.deque(roots);parent={i:None for i in roots}
 while q:
  i=q.popleft()
  for j in adj[i]:
   if j not in seen and P[j]['group']in allowed:seen.add(j);q.append(j);parent[j]=i
 return seen,parent
reach,parents=bfs(struct);allreach,allparents=bfs(set(p['group']for p in P))
disconnected=[p['name']for i,p in enumerate(P)if p['group']in struct and i not in reach]
def query_box(b,groups=None):
 v=[[x,y,z]for x in b[:2]for y in b[2:4]for z in b[4:6]];q={'vertices':v,'aabb':b,'poly':hull(v)}
 result=[]
 for i,p in enumerate(P):
  if groups and p['group']not in groups:continue
  c=contact(p,q)
  if c and c['kind']=='volume'and c['volume']>1e-8:result.append({'name':p['name'],'group':p['group'],'volume':c['volume']})
 return result
queries={
 'old_spine_fore':[-3.99998,3.99998,106.50,110.45,-181.05,-180.95],
 'old_spine_aft':[-3.99998,3.99998,106.50,110.45,-173.05,-172.95],
 'fore_apron':[-55,55,106.50,110.45,-79.99998,-74],
 'd17_spine_belowfloor':[-4.09998,4.09998,102.1,106.25998,-181,-80],
 'six_metre_turn':[-47,-41,106.50,110.40,-180,-174],
 'longitudinal_seven_metre_path':[-47.5,-40.5,106.50,110.40,-174,-80],
 'transverse_seven_metre_path':[-44,3.99998,106.50,110.40,-180.5,-173.5],
 'core_cover_volume':[-2,2,106.50,109.85,-108.2,-103.8],
 'core_public_body_clearance':[-7.8,7.8,106.5,109.85,-113,-80],
 'core_roof_clearance':[-7.8,7.8,109.85,111.0,-113,-80],
}
query_results={k:query_box(v)for k,v in queries.items()}
# Individual actual prism to vertex ledger comparison, useful only to detect mismatch.
L=json.loads((SRC/'geometry_parts.json').read_text())['parts'];lm={p['name']:p for p in L}
ledger_mismatch=[]
for p in P:
 lp=lm.get(p['name'])
 if not lp or max(abs(a-b)for a,b in zip(p['aabb'],lp['world_aabb']))>EPS:ledger_mismatch.append(p['name'])
# Pier envelopes and roots tied to independently stored parent-runtime audited positions.
Parent=Path('/workspace/shared/astraea-godot-production-20261003');audit=[]
for f in ['BRIDGE_PIER_RUNTIME_AUDIT.json','BRIDGE_AFT_PIER_RUNTIME_AUDIT.json']:audit+=json.loads((Parent/'docs'/f).read_text())['records']
pier_results=[]
for n,a in enumerate(audit,1):
 ps=[p for p in P if p['group']=='pier'and p['assembly'].startswith(f'BRP_Pier_{n:02d}_')]
 bounds=[min(p['aabb'][k]for p in ps)if k%2==0 else max(p['aabb'][k]for p in ps)for k in range(6)]
 ex=[a['x']-.4,a['x']+.4,-3.2,114,a['z']-.6,a['z']+.6]
 pier_results.append({'pier':n,'bounds':bounds,'matches_audited_envelope':max(abs(x-y)for x,y in zip(bounds,ex))<EPS,'previous_actual_keel_support_ray_count':len(a['supports']),'all_actual_parts_connected_to_base':all(p['index']in reach for p in ps)})
# Examples of explicit all-structural base-to-top-to-hanger chains.
assemblies={}
for i,p in enumerate(P):assemblies.setdefault(p['assembly'],[]).append(i)
path_examples={}
for an,ids in assemblies.items():
 if not any(P[i]['group']in {'hanger','platform_support_shallow'}for i in ids):continue
 dest=next((i for i in ids if i in parents),None)
 if dest is None:continue
 path=[]
 while dest is not None:
  an2=P[dest]['assembly']
  if not path or path[-1]!=an2:path.append(an2)
  dest=parents[dest]
 path_examples[an]=list(reversed(path))
# Every hanger independently needs actual top contact with the new roof frame and a bottom support contact.
hanger_seats=[]
for an,ids in assemblies.items():
 if not any(P[i]['group']=='hanger'for i in ids):continue
 top=[];bottom=[]
 for i in ids:
  for j,c in adj[i].items():
   g=P[j]['group']
   if c['kind']!='volume':continue
   if g in {'transfer','bypass_transfer'} and P[j]['aabb'][3]>111:top.append(P[j]['assembly'])
   if g in {'platform_support','platform_support_shallow'} and P[j]['aabb'][2]<106.5:bottom.append(P[j]['assembly'])
 hanger_seats.append({'hanger':an,'positive_roof_seats':sorted(set(top)),'positive_floor_support_seats':sorted(set(bottom)),'pass':bool(top and bottom)})
# Broad, slab-height floor panels cannot hide under a different semantic group.
broad_floor_panels=[]
for p in P:
 b=p['aabb']
 if b[2]>=106.25998 and b[3]<=106.50002 and (b[1]-b[0])>3 and (b[5]-b[4])>3:broad_floor_panels.append(p['name'])
# Entire load-bearing members below the suspended floor have no extra low piers.
additional_low_structures=[p['name']for p in P if p['group']!='pier'and p['aabb'][2]<105.79]
# Source coverage of open wing ends at the exact old-spine edge.
guard_endpoints=[]
for side,sgn in [('Port',-1),('Starboard',1)]:
 for idx,z in [(0,-171.7),(3,-118.3)]:
  end={}
  for typ in ['GuardBack','GuardCap','GuardToe']:
   ps=[p for p in P if p['assembly']==f'BRP_{side}_{typ}_{idx:02d}']
   value=(max(p['aabb'][1]for p in ps)if sgn<0 else min(p['aabb'][0]for p in ps))
   end[typ]=value
  guard_endpoints.append({'side':side,'z':z,'actual_x_ends':end,'fully_closed_to_spine':all(abs(v-sgn*4)<EPS for v in end.values())})
# count assembly contacts and find members with no contact outside own assembly.
aedges={}
for i,j,c in edges:
 a,b=P[i]['assembly'],P[j]['assembly']
 if a==b:continue
 k=' | '.join(sorted([a,b]));r=aedges.setdefault(k,{'pieces':0,'max_volume':0,'contact_kinds':set()});r['pieces']+=1;r['max_volume']=max(r['max_volume'],c['volume']);r['contact_kinds'].add(c['kind'])
for r in aedges.values():r['contact_kinds']=sorted(r['contact_kinds'])
# Supported, backed guard chains and volumetric corner closures.
guard_checks=[]
for side in ['Port','Starboard']:
 for n in range(4):
  prefix=f'BRP_{side}_';back=prefix+f'GuardBack_{n:02d}';toe=prefix+f'GuardToe_{n:02d}';cap=prefix+f'GuardCap_{n:02d}';perim=prefix+f'Perimeter_{n:02d}'
  def ac(a,b):return aedges.get(' | '.join(sorted([a,b])))
  br=ac(back,toe);cr=ac(cap,back);pr=ac(toe,perim)
  guard_checks.append({'side':side,'segment':n,'back_to_toe':br,'cap_to_back':cr,'toe_to_perimeter':pr,'pass':bool(br and cr and pr)})
 for n in range(3):
  for typ in ['GuardBack','GuardCap','GuardToe']:
   r=ac(f'BRP_{side}_{typ}_{n:02d}',f'BRP_{side}_{typ}_{n+1:02d}')
   guard_checks.append({'side':side,'corner':n,'type':typ,'contact':r,'pass':bool(r and r['max_volume']>1e-8)})
# A backed inboard guard must close the otherwise reachable strip behind its endpoint.
guard_junction_returns=[]
for side,sgn in [('Port',-1),('Starboard',1)]:
 for edge,z in [('fore',-171.90),('aft',-118.10)]:
  xx=sorted([sgn*4.001,sgn*4.199]);hits=query_box([*xx,107.10,107.30,z-.01,z+.01],{'guard'})
  guard_junction_returns.append({'side':side,'edge':edge,'sample_z':z,'actual_backed_guard_hits':hits,'pass':bool(hits)})
# Fixture markers sit just below the real lens; every actual downward path reaches the parent floor unobstructed.
D=json.loads((SRC/'section_contract.json').read_text());fixture_checks=[]
def inside(poly,x,z):return all(cross(a,b,(x,z))>=-1e-7 for a,b in zip(poly,poly[1:]+poly[:1]))
for m in D['light_markers']:
 x,y,z=m['position'];obstructions=[]
 for p in P:
  b=p['aabb']
  if b[3]<=106.50002 or b[2]>=y-1e-5 or not(b[0]-EPS<=x<=b[1]+EPS and b[4]-EPS<=z<=b[5]+EPS):continue
  if inside(p['poly'],x,z):obstructions.append(p['name'])
 housing=m['fixture_assembly']+'_Housing';lens=m['fixture_assembly']+'_Lens';support=[]
 for i in assemblies[housing]:
  for j,c in adj[i].items():
   if P[j]['group']in {'transfer','bypass_transfer','ceiling'}and c['kind']=='volume':support.append(P[j]['assembly'])
 lenscontact=aedges.get(' | '.join(sorted([housing,lens])))
 fixture_checks.append({'marker':m['name'],'downward_source_obstructions':obstructions,'housing_positive_seats':sorted(set(support)),'lens_contact':lenscontact,'pass':not obstructions and bool(support and lenscontact)})
# Real world positions prove the roof-hung east return closure, independent of the authored ledger.
east_parts=[p for p in P if p['assembly']=='BRP_EastReturnSlabHeightClosure']
east_bounds=[min(p['aabb'][k]for p in east_parts)if k%2==0 else max(p['aabb'][k]for p in east_parts)for k in range(6)]
# Intersect with the retained original centreline slab envelope, not with an invented Blender floor.
slab={'aabb':[-4,4,106.26,106.5,-181,-173],'poly':[(-4,-181),(4,-181),(4,-173),(-4,-173)]}
east_slab_overlap=sum(contact(p,slab)['volume']for p in east_parts if contact(p,slab))
east_detail={'actual_shallow_bounds':east_bounds,'retained_spine_slab_overlap_m3':east_slab_overlap,'wall_to_closure':aedges.get(' | '.join(sorted(['BRP_EastJunctionReturn','BRP_EastReturnSlabHeightClosure']))),'fore_roof_hanger':next(h for h in hanger_seats if h['hanger']=='BRP_ForeGallery_Fore_Hanger_X4p08'),'aft_roof_hanger':next(h for h in hanger_seats if h['hanger']=='BRP_ForeGallery_Aft_Hanger_X4p08')}
result={'source_sha256':J['source_sha256'],'actual_mesh_count':len(P),'method':'Reopened Blender, actual world mesh vertices. Convex XZ hulls clipped pairwise; real Y intersections. Positive volume or finite bearing/side face area. 0.00002m float tolerance. No ledger coordinates used for contacts. Structural reachability excludes ceilings, cladding, old spine and parent slab.','structural_mesh_count':sum(p['group']in struct for p in P),'actual_contact_edges':len(edges),'structural_disconnected':disconnected,'all_mesh_disconnected':[P[i]['name']for i in range(len(P))if i not in allreach],'pier_verification':pier_results,'clearance_queries':query_results,'ledger_mismatch':ledger_mismatch,'hanger_seats':hanger_seats,'guard_chain_checks':guard_checks,'guard_junction_returns':guard_junction_returns,'fixture_checks':fixture_checks,'east_return':east_detail,'broad_floor_panels':broad_floor_panels,'additional_low_structures':additional_low_structures,'guard_endpoints':guard_endpoints,'support_path_examples':path_examples,'assembly_contacts':aedges,'new_floor_slab_meshes':[p['name']for p in P if p['group']in {'floor','floor_slab','slab'}],'door_meshes':[p['name']for p in P if 'door'in p['name'].lower()]}
(QA/'independent_review_contacts.json').write_text(json.dumps(result,indent=2)+'\n')
summary={k:result[k]for k in ['source_sha256','actual_mesh_count','structural_mesh_count','actual_contact_edges','structural_disconnected','all_mesh_disconnected','pier_verification','clearance_queries','ledger_mismatch','hanger_seats','broad_floor_panels','additional_low_structures','guard_endpoints','new_floor_slab_meshes','door_meshes']};print(json.dumps(summary,indent=2))
