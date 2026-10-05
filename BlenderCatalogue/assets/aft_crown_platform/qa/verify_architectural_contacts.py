"""Convex footprint contact audit, including actual oriented fan members. Run with Shapely2."""
from pathlib import Path
from collections import deque
import json,hashlib
from shapely.geometry import MultiPoint,box,LineString
from shapely.strtree import STRtree
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/section_contract.json').read_text());P=json.loads((R/'source/geometry_parts.json').read_text())['parts'];old=json.loads((C/'assets/aft_command/source/geometry_parts.json').read_text())['parts'];ps=P+old
polys=[MultiPoint([(v[0],v[2])for v in p['vertices_world']]).convex_hull for p in ps];tree=STRtree(polys);adj=[[]for p in ps]
def contact(i,j):
 a,b=ps[i],ps[j];lo=max(a['world_aabb'][2],b['world_aabb'][2]);hi=min(a['world_aabb'][3],b['world_aabb'][3]);inter=polys[i].intersection(polys[j]);return {'part':a['name'],'support':b['name'],'plan_intersection_wkt':inter.wkt,'plan_area_m2':inter.area,'y_overlap':[lo,hi]}
for i,p in enumerate(ps):
 for jj in tree.query(polys[i]):
  j=int(jj)
  if j<=i:continue
  dy=min(p['world_aabb'][3],ps[j]['world_aabb'][3])-max(p['world_aabb'][2],ps[j]['world_aabb'][2])
  if dy< -1e-7:continue
  inter=polys[i].intersection(polys[j])
  if inter.area>1e-8 or(inter.length>1e-5 and dy>1e-5):adj[i].append(j);adj[j].append(i)
roots=[i for i,p in enumerate(P)if p['group']=='pier'and abs(p['world_aabb'][2]+3.2)<1e-7];parent={i:None for i in roots};queue=deque(roots)
while queue:
 i=queue.popleft()
 for j in adj[i]:
  if j not in parent:parent[j]=i;queue.append(j)
disconnected=[p['name']for i,p in enumerate(P)if i not in parent];assert not disconnected,disconnected
chains=[contact(i,parent[i])for i in range(len(P))if parent[i]is not None]
def volume_hits(bounds):
 shape=box(bounds[0],bounds[4],bounds[1],bounds[5]);return[p['name']for i,p in enumerate(P)if min(p['world_aabb'][3],bounds[3])-max(p['world_aabb'][2],bounds[2])>1e-7 and polys[i].intersection(shape).area>1e-8]
clearances={
 'protected_core':[-7.8,7.8,102.01,109.85,106,139],
 'receiving_turn':[-8.8,8.8,106.501,110.4,139,145],
 'onward_spine':[-4,4,106.501,110.4,139,202],
 'retained_spine_underfloor':[-4.1,4.1,102.01,106.2599,102,194],
 'port_public_wing':[-17,-15,106.501,109,106,193],
 'starboard_public_wing':[15,17,106.501,109,106,193],
 'port_staff_crosslink':[-33.799,-5.161,106.501,109.2,102.201,105.799],
 'starboard_staff_crosslink':[5.161,33.799,106.501,109.2,102.201,105.799],
 'port_staff_outer':[-33.799,-30.201,106.501,109.2,105.799,141.83],
 'starboard_staff_outer':[30.201,33.799,106.501,109.2,105.799,141.83]}
queries={n:{'volume':b,'hits':volume_hits(b)}for n,b in clearances.items()};assert not any(q['hits']for q in queries.values()),queries
for p in P:
 b=p['world_aabb'];assert b[3]<=114.5+1e-7
 if b[2]<105.7999:
  assert p['group']=='pier',p['name'];assert any(b[0]>=x-.400001 and b[1]<=x+.400001 and b[4]>=z-.600001 and b[5]<=z+.600001 for x,z in D['support']['pier_centres_xz']),p['name']
seams=[]
for x in D['support']['old_roof_link_x']:
 a=[i for i,p in enumerate(P)if p['assembly']=='ACP_SeamSleeve_X%s'%x];b=[i for i,p in enumerate(ps)if i>=len(P)and p['name'].startswith('AFC_Longitudinal_')and p['world_aabb'][4]<=101.5 and p['world_aabb'][5]>=101.84 and p['world_aabb'][0]<=x<=p['world_aabb'][1]]
 pairs=[contact(i,j)for i in a for j in b if j in adj[i]];assert pairs,x;seams.append({'x':x,'contacts':pairs})
# Slab bearing samples are geometric proposals: parent owns installed floor ray acceptance.
slab_contacts=[]
for i,p in enumerate(P):
 if p['group']in['platform_support','platform_support_shallow']and p['world_aabb'][3]>=106.26:
  q=polys[i].representative_point();slab_contacts.append({'part':p['name'],'sample_xz':[q.x,q.y],'y_overlap':[max(106.26,p['world_aabb'][2]),min(106.5,p['world_aabb'][3])]})
assert slab_contacts
report={'pass':True,'source_sha256':hashlib.sha256((R/'source/AST-CMD-005.blend').read_bytes()).hexdigest(),'part_count':len(P),'all_parts_connected_to_six_keel_bearing_piers':True,'disconnected':disconnected,'root_part_count':len(roots),'contact_network':chains,'clearance_queries':queries,'seven_old_frame_seam_couplers':seams,'slab_contact_proposals':slab_contacts,'limits':['Ledger vertices independently compared with actual Blender source in exact_roundtrip check','Geometric physical contacts, not engineering capacity or actual runtime acceptance','Parent must rerun96 pier slices,30 keel rays,doors,loaded carts,core travel and normal/effects-off views']}
(R/'qa/architectural_contacts.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTACTS_PASS',len(P),len(chains),len(seams),len(slab_contacts))
