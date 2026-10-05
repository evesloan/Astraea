"""Per-part physical contact graph and protected-volume proof; no neighbour exemptions."""
from pathlib import Path
from collections import deque
import json,hashlib,math
from shapely.geometry import MultiPoint,Polygon,box,Point
from shapely.strtree import STRtree
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());new=json.loads((R/'source/geometry_parts.json').read_text())['parts'];old=json.loads((C/'assets/aft_crown_platform/source/geometry_parts.json').read_text())['parts'];older=json.loads((C/'assets/aft_command/source/geometry_parts.json').read_text())['parts'];parts=new+old+older
polys=[Polygon(p['footprint_xz'])if 'footprint_xz'in p else MultiPoint([(v[0],v[2])for v in p['vertices_world']]).convex_hull for p in parts];assert all(p.is_valid and p.area>1e-10 for p in polys)
tree=STRtree(polys);adj=[[]for p in parts]
def contact(i,j):
 a,b=parts[i],parts[j];lo=max(a['world_aabb'][2],b['world_aabb'][2]);hi=min(a['world_aabb'][3],b['world_aabb'][3]);inter=polys[i].intersection(polys[j]);return{'part':a['name'],'support':b['name'],'part_family':'006'if i<len(new)else'005'if i<len(new)+len(old)else'002','support_family':'006'if j<len(new)else'005'if j<len(new)+len(old)else'002','plan_contact_wkt':inter.wkt,'plan_contact_area_m2':inter.area,'y_overlap':[lo,hi],'volume_overlap_m3':inter.area*max(0,hi-lo),'contact_area_if_seam_m2':inter.length*max(0,hi-lo)if inter.area<1e-8 else inter.area,'rationale':'Measured actual solid footprint and vertical overlap; explicit parent edge in the six-root physical contact network'}
for i,p in enumerate(parts):
 for jj in tree.query(polys[i]):
  j=int(jj)
  if j<=i:continue
  dy=min(p['world_aabb'][3],parts[j]['world_aabb'][3])-max(p['world_aabb'][2],parts[j]['world_aabb'][2])
  if dy< -1e-7:continue
  q=polys[i].intersection(polys[j])
  if q.area>1e-8 or(q.length>1e-5 and dy>1e-5):adj[i].append(j);adj[j].append(i)
roots=[i for i,p in enumerate(parts)if p['group']=='pier'and abs(p['world_aabb'][2]+3.2)<1e-7 and i>=len(new)and i<len(new)+len(old)];parent={i:None for i in roots};Q=deque(roots)
while Q:
 i=Q.popleft()
 for j in adj[i]:
  if j not in parent:parent[j]=i;Q.append(j)
missing=[p['name']for i,p in enumerate(new+old)if i not in parent];assert not missing,missing
ledger=[contact(i,parent[i])for i in range(len(new))];assert len(ledger)==len(new)
# Full old/new network retained so every chosen parent link is traceable to one of six piers.
network=[contact(i,j)for i,j in parent.items()if j is not None]
def hits(bounds):
 q=box(bounds[0],bounds[4],bounds[1],bounds[5]);return[p['name']for i,p in enumerate(new)if min(p['world_aabb'][3],bounds[3])-max(p['world_aabb'][2],bounds[2])>1e-7 and polys[i].intersection(q).area>1e-8]
queries={k:{'bounds':b,'hits':hits(b)}for k,b in D['protected_new_volumes'].items()};assert not any(q['hits']for q in queries.values()),queries
# Shared doors remain unchanged, and all four fixed/moving approaches have no new material.
for sign in[-1,1]:
 for x,z in[(sign*7.5,101.92),(sign*32,141.92)]:
  b=[x-1.9,x+1.9,106.5,109.4,z-2,z+2];hh=hits(b);assert not hh,(x,z,hh);queries[f'door_{x}_{z}']={'bounds':b,'hits':hh}
# Empty standing/seated diagnostic pads have supported known floor footprint. Actual body driving remains parent's gate.
for side,station in D['standing_eye_boxes'].items():
 b=[station['x'][0]-.45,station['x'][1]+.45,106.5,109.1,station['z'][0]-.45,station['z'][1]+.45];hh=hits(b);assert not hh;assert max(abs(b[0]),abs(b[1]))<36 and 142<b[4]<b[5]<182;queries[side+'_station_body_pad']={'bounds':b,'hits':hh,'source_floor_plan_supported':True}
# Optical cone from the retained lens centre to floor: sample every ring including actual downward cone perimeter.
origin=D['onward']['fixture_marker'];cone_hits=[];samples=0
for ring in range(1,81):
 dy=(origin[1]-106.5)*ring/80;r=math.tan(math.radians(82))*dy
 for radial in[0,.5,1]:
  for k in range(64):
   theta=2*math.pi*k/64;v=[origin[0]+r*radial*math.cos(theta),origin[1]-dy,origin[2]+r*radial*math.sin(theta)];samples+=1
   for jj in tree.query(Point(v[0],v[2])):
    j=int(jj)
    if j>=len(new):continue
    b=parts[j]['world_aabb']
    if b[2]<=v[1]<=b[3]and polys[j].covers(Point(v[0],v[2])):cone_hits.append({'point':v,'part':parts[j]['name']})
header_hits=[q for q in cone_hits if 'RaisedHeader'in q['part']];assert not header_hits,header_hits[:5]
fixture_exits=[]
L=json.loads((C/'assets/aft_crown_platform/source/section_contract.json').read_text())['light_markers'];assert len(L)==25
for light in L:
 p=light['position'];bad=[]
 for depth in[.01,.04,.12]:
  radius=math.tan(math.radians(82))*depth
  for k in range(32):
   v=[p[0]+radius*math.cos(2*math.pi*k/32),p[1]-depth,p[2]+radius*math.sin(2*math.pi*k/32)]
   for jj in tree.query(Point(v[0],v[2])):
    j=int(jj)
    if j<len(new)and parts[j]['world_aabb'][2]<=v[1]<=parts[j]['world_aabb'][3]and polys[j].covers(Point(v[0],v[2])):bad.append(parts[j]['name'])
 assert not bad,(light['name'],bad);fixture_exits.append({'marker':light['name'],'new_material_exit_hits':bad,'rays':96,'max_depth_m':.12,'half_angle_degrees':82})
for p in new:
 b=p['world_aabb'];assert b[3]<=114.5+1e-7
 if p['group'].startswith('shoulder'):assert b[2]>=113.4-1e-7,p['name']
assert len([p for p in new if p['group']=='glass'and 'LowBay_Glass'in p['name']])==2
assert all(any(p['assembly']==w['glass_assembly']for p in new)for w in D['windows'])
oldjoin=[contact(i,j)for i in range(len(new))for j in adj[i]if len(new)<=j<len(new)+len(old)]
report={'pass':True,'source_sha256':hashlib.sha256((R/'source/AST-CMD-006.blend').read_bytes()).hexdigest(),'part_count':len(new),'new_parts_all_connected_to_six_old_piers':True,'new_part_join_ledger':ledger,'full_chosen_contact_network':network,'all_new_to_old_contacts':oldjoin,'old_root_part_count':len(roots),'protected_queries':queries,'onward_full_downward_optical_cone':{'samples':samples,'intended_distant_wall_receivers':sorted(set(q['part']for q in cone_hits)),'receiver_sample_count':len(cone_hits),'raised_header_hits':header_hits,'half_angle':82,'note':'Fullgeometric cone tofloorsamples; outsideactual11mrange retained conservatively. Walls are legitimate receivers, not blocked fixtureexits','from':origin,'to_floor_y':106.5},'all25fixture_near_exits':fixture_exits,'all_shoulder_new_undersides_at_least_113_4':True,'two_single_solid_protective_panes':True,'limits':['Geometric contact only; no engineering load or pressure certification','Actual compiled floor, runtime colliders, source-triangle rays and body/loaded-cart driving remain separate gates']}
(R/'qa/architectural_contacts.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTACTS_PASS',len(new),len(ledger),len(oldjoin),'old',len(old),'roots',len(roots))
