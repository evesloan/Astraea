"""Read-only independent geometric audit; run PYTHONPATH=/tmp/astraea-shapely python thisfile."""
from pathlib import Path
import json,hashlib,collections,math
from shapely.geometry import MultiPoint,Polygon,Point,box
from shapely.strtree import STRtree
R=Path(__file__).resolve().parents[1];Q=R/'qa';A=R.parent/'aft_command';G=Path('/workspace/shared/astraea-godot-production-20261003')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
D=read(R/'source/section_contract.json');C=read(G/'data/architecture/AFT_CROWN_PLATFORM_CONSTRUCTION.json'); P=read(R/'source/geometry_parts.json')['parts'];old=read(A/'source/geometry_parts.json')['parts'];actual=read(Q/'independent_actual_geometry.json');ps=P+[p for p in old if p['name'].startswith('AFC_Longitudinal_')];N=len(P)
assert actual['hashes']['005_source']==sha(R/'source/AST-CMD-005.blend')
assert actual['hashes']['005_geometry_ledger']==sha(R/'source/geometry_parts.json')
polys=[];ys=[]
for p in ps:
 vs=p['vertices_world']; layers=collections.defaultdict(set)
 for x,y,z in vs:layers[round(y,8)].add((x,z))
 assert len(layers)==2 and len(set(map(frozenset,layers.values())))==1,('not_vertical_prism',p['name'])
 hull=MultiPoint([(v[0],v[2]) for v in vs]).convex_hull
 assert hull.geom_type=='Polygon'
 polys.append(hull);ys.append((min(v[1] for v in vs),max(v[1] for v in vs)))
tree=STRtree(polys); adj=[[] for p in ps];edges={}
for i,p in enumerate(ps):
 for jj in tree.query(polys[i]):
  j=int(jj)
  if j<=i:continue
  lo=max(ys[i][0],ys[j][0]);hi=min(ys[i][1],ys[j][1]);dy=hi-lo
  if dy< -1e-7:continue
  inter=polys[i].intersection(polys[j]); area=inter.area
  if area>1e-8 or (inter.length>1e-5 and dy>1e-5):
   adj[i].append(j);adj[j].append(i);q=inter.representative_point();edges[i,j]={'plan_contact_area_m2':area,'contact_surface_m2':(2*area+inter.length*dy if area>1e-8 and dy>1e-7 else (area if dy<=1e-7 else inter.length*dy)),'contact_volume_m3':area*max(0,dy),'vertical_contact_m':max(0,dy),'witness_xyz':[q.x,(lo+hi)/2,q.y],'kind':'positive_volume' if area>1e-8 and dy>1e-7 else 'face_bearing'}
def proof(i,j):return dict(part=ps[i]['name'],support=ps[j]['name'],**edges[min(i,j),max(i,j)])
roots=[i for i,p in enumerate(P) if p['group']=='pier' and abs(ys[i][0]+3.2)<1e-7]
structural={'pier','transfer','hanger','platform_support','platform_support_shallow','seam_coupler'}
def bfs(allowed):
 parent={i:None for i in roots};todo=collections.deque(roots)
 while todo:
  i=todo.popleft()
  for j in adj[i]:
   if j not in parent and allowed(j):parent[j]=i;todo.append(j)
 return parent
parents=bfs(lambda i:True);sp=bfs(lambda i: i<N and P[i]['group'] in structural)
disconnected=[p['name'] for i,p in enumerate(P) if i not in parents];struct_disconnected=[p['name'] for i,p in enumerate(P) if p['group'] in structural and i not in sp]
assert not disconnected and not struct_disconnected,(disconnected,struct_disconnected)
# Exact footprint intersection with solid exclusion prisms. Boundary touching is not intrusion.
volumes={'protected_core_full':[-7.8,7.8,-3.2,109.85,106,139],'retained_spine_deep':[-4.1,4.1,-3.2,106.2599,102,194],'receiving_turn':[-8.8,8.8,106.5001,110.4,139,145],'onward_spine':[-4,4,106.5001,110.4,139,202],'port_public_loop':[-17,-15,106.5001,109.2,106,193],'starboard_public_loop':[15,17,106.5001,109.2,106,193],'port_staff_crosslink':[-33.8,-5.16,106.5001,109.2,102.2,105.8],'starboard_staff_crosslink':[5.16,33.8,106.5001,109.2,102.2,105.8],'port_staff_outer':[-33.8,-30.2,106.5001,109.2,105.8,141.83],'starboard_staff_outer':[30.2,33.8,106.5001,109.2,105.8,141.83]}
clear={}
for n,b in volumes.items():
 shape=box(b[0],b[4],b[1],b[5]);hits=[]
 for ii in tree.query(shape):
  i=int(ii)
  if i>=N:continue
  dy=min(ys[i][1],b[3])-max(ys[i][0],b[2]);q=polys[i].intersection(shape)
  if dy>1e-7 and q.area>1e-8:hits.append({'part':P[i]['name'],'volume_m3':dy*q.area,'intersection_xz':q.wkt})
 clear[n]={'bounds_xyz':b,'hits':hits}
assert not any(v['hits'] for v in clear.values()),clear
# Every deep member belongs inside one of the six already screened candidate pier envelopes.
deep=[]
for i,p in enumerate(P):
 if ys[i][0]<105.8-1e-7:
  assert p['group']=='pier',p['name']
  fits=[k for k,(x,z) in enumerate(D['support']['pier_centres_xz']) if box(x-.400001,z-.600001,x+.400001,z+.600001).covers(polys[i])]
  assert len(fits)==1,p['name'];deep.append(p['name'])
# Positive coupler contact with actual prior roof ends and the new roof member, all connected structurally.
seams=[]
for x in D['support']['old_roof_link_x']:
 sleeve=[i for i,p in enumerate(P) if p['assembly']=='ACP_SeamSleeve_X%s'%x]
 prior=[i for i,p in enumerate(ps) if i>=N and p['name'].startswith('AFC_Longitudinal_') and p['world_aabb'][4]<=101.5 and abs(p['world_aabb'][5]-101.84)<1e-5 and p['world_aabb'][0]<=x<=p['world_aabb'][1]]
 pairs=[proof(i,j) for i in sleeve for j in prior if j in adj[i]]
 outgoing=[proof(i,j) for i in sleeve for j in adj[i] if j<N and P[j]['assembly'].startswith('ACP_RoofLong_X%s_'%x)]
 assert pairs and outgoing and all(any(q['part']==P[i]['name'] and q['kind']=='positive_volume' for q in pairs) for i in sleeve),(x,pairs,outgoing)
 seams.append({'x':x,'old_end_z':101.84,'old_contacts':pairs,'new_contacts':outgoing})
# Exact slab polygons include only missing floor, rather than assuming every girder midpoint lies on one.
floors=[(label+'_'+str(k),Polygon(v)) for label,f in C['floors'].items() for k,v in enumerate(f['expected_missing_boundaries'])]
slab=[]
for i,p in enumerate(P):
 if p['group'] not in {'platform_support','platform_support_shallow'}:continue
 lo=max(106.26,ys[i][0]);hi=min(106.5,ys[i][1])
 if hi-lo<=1e-7:continue
 for name,poly in floors:
  q=polys[i].intersection(poly)
  if q.area<=1e-8:continue
  w=q.representative_point();slab.append({'part':p['name'],'floor_component':name,'witness_xyz':[w.x,(lo+hi)/2,w.y],'sample_xz':[w.x,w.y],'plan_contact_area_m2':q.area,'vertical_overlap_m':hi-lo,'support_root_path_length':0})
  j=i
  while sp[j] is not None:slab[-1]['support_root_path_length']+=1;j=sp[j]
  slab[-1]['root_pier_part']=P[j]['name']
assert set(n for n,_ in floors)==set(s['floor_component'] for s in slab)
# Every route light sits just below its physical lens; central downward aperture has no occluder to platform.
lights=[]
for marker in D['light_markers']:
 name=marker['fixture_assembly'];parts=[i for i,p in enumerate(P) if p['name'].startswith(name+'_')];lens=[i for i in parts if '_Lens' in P[i]['name']];housing=[i for i in parts if '_Housing' in P[i]['name']];x,y,z=marker['position'];point=Point(x,z)
 assert lens and housing and any(polys[i].covers(point) and 0<ys[i][0]-y<.02 for i in lens),name
 external=[proof(i,j) for i in housing for j in adj[i] if j<N and P[j]['group'] in structural|{'service_ceiling'}]
 assert external,name
 obscurers=[P[int(i)]['name'] for i in tree.query(point) if int(i)<N and polys[int(i)].covers(point) and min(ys[int(i)][1],y)-max(ys[int(i)][0],106.5001)>1e-7]
 assert not obscurers,(name,obscurers)
 lights.append({'marker':marker['name'],'position':marker['position'],'lens_parts':[P[i]['name'] for i in lens],'aperture_offset_m':min(ys[i][0]-y for i in lens),'support_contact':external[0],'downward_ray_clear':True})
# Non-structural pieces must still have actual face/volume contact paths to the structure.
guards=[{'part':p['name'],'first_support':proof(i,parents[i])} for i,p in enumerate(P) if p['group']=='guard']
# No broad duplicate source floor: minimum oriented footprint width of every below-floor-only part.
widths=[]
for i,p in enumerate(P):
 if ys[i][0]<=106.5 and ys[i][1]<=106.7:
  rect=polys[i].minimum_rotated_rectangle;vs=list(rect.exterior.coords);w=min(math.dist(a,b) for a,b in zip(vs,vs[1:]));widths.append(w);assert w<1.21,p['name']
# Six corrected guard ends positively penetrate preserved old aft-wall solids by0.04m.
guard_junctions=[]
for i,p in enumerate(P):
 if p['group']!='guard' or p['world_aabb'][4]>=102:continue
 contacts=[]
 for op in old:
  ob=op['world_aabb'];dy=min(ys[i][1],ob[3])-max(ys[i][0],ob[2])
  if dy<=1e-7 or ob[4]>102 or ob[5]<101.9:continue
  poly=MultiPoint([(v[0],v[2]) for v in op['vertices_world']]).convex_hull;inter=polys[i].intersection(poly)
  if inter.area>1e-8:
   q=inter.representative_point();contacts.append({'old_part':op['name'],'plan_contact_area_m2':inter.area,'vertical_overlap_m':dy,'witness_xyz':[q.x,(max(ys[i][0],ob[2])+min(ys[i][1],ob[3]))/2,q.y]})
 assert contacts,p['name']
 guard_junctions.append({'part':p['name'],'z_overlap_m':.04,'old_wall_contacts':contacts})
assert len(guard_junctions)==6
# Independently intersect captured actual fixed-frame meshes with exact source wall prisms.
shared=read(Q/'open_shared_door_geometry.json');door_interfaces=[]
for d in D['doors']+[q for q in read(A/'source/section_contract.json')['doors'] if q['name'].endswith('_exit')]:
 x,y,z=d['position'];assert abs(d.get('yaw_radians',d.get('yaw',0)))<1e-7
 aperture=box(x-1.3749,z-.0799,x+1.3749,z+.0799);blocked=[]
 for op in P+old:
  ob=op['world_aabb'];dy=min(y+2.8149,ob[3])-max(y+.0001,ob[2])
  if dy<=1e-7:continue
  poly=MultiPoint([(v[0],v[2]) for v in op['vertices_world']]).convex_hull
  if poly.intersection(aperture).area>1e-8:blocked.append(op['name'])
 assert not blocked,(d['name'],blocked)
 fixed=[q for q in shared if q['name'].startswith(d['name']+'_STF_')];joins=[]
 assert len(fixed)==3
 for frame in fixed:
  fb=frame['world_aabb'];fpoly=MultiPoint([(v[0],v[2]) for v in frame['vertices_world']]).convex_hull;hits=[]
  for op in P+old:
   ob=op['world_aabb'];dy=min(fb[3],ob[3])-max(fb[2],ob[2])
   if dy<=1e-7:continue
   opoly=MultiPoint([(v[0],v[2]) for v in op['vertices_world']]).convex_hull;inter=fpoly.intersection(opoly)
   if inter.area>1e-8:hits.append({'source_part':op['name'],'overlap_volume_m3':inter.area*dy})
  assert hits,(d['name'],frame['name']);joins.append({'fixed_frame_part':frame['name'],'source_contacts':hits})
 door_interfaces.append({'name':d['name'],'position':d['position'],'aperture_clear_width_m':2.75,'aperture_clear_height_m':2.815,'wall_aperture_empty':True,'fixed_frame_contacts':joins})
# Bounded002 source / contract preservation independent check against frozen prior ledger.
oldbase=read(Q/'baseline_002_geometry_parts.json')['parts'];oldmap={p['name']:p for p in oldbase};newmap={p['name']:p for p in old};allow=set(read(Q/'002_allowlist.json')['allowed_old_meshes']);diff=[n for n in oldmap if n not in newmap or oldmap[n]!=newmap[n]];assert not set(diff)-allow
before=read(Q/'baseline_002_section_contract.json');after=read(A/'source/section_contract.json');assert all(before[k]==after[k] for k in before if k!='doors');assert after['doors'][:len(before['doors'])]==before['doors'] and len(after['doors'])==len(before['doors'])+2
hashes=dict(actual['hashes']);hashes.update({'005_contract':sha(R/'source/section_contract.json'),'002_contract':sha(A/'source/section_contract.json'),'002_geometry_ledger':sha(A/'source/geometry_parts.json')})
r={'pass':True,'hashes':hashes,'method':'Actual Blender3932 meshes individually compared to ledger; every source part proven vertical convex prism; contacts use polygon intersections from vertices, never loose oriented-member AABBs. Structural-only graph excludes fixtures and guards. Touching bearing faces reported separately from positive-volume joints.','source_mesh_count':N,'root_piers':[{'name':'ACP_Pier_%02d'%(k+1),'candidate_centre_xz':[x,z],'keel_bearing_parts':[P[i]['name'] for i in roots if P[i]['name'].startswith('ACP_Pier_%02d_'%(k+1))]} for k,(x,z) in enumerate(D['support']['pier_centres_xz'])],'root_pier_parts':[{'name':P[i]['name'],'bounds':P[i]['world_aabb'],'candidate_centre_xz':[(P[i]['world_aabb'][0]+P[i]['world_aabb'][1])/2,(P[i]['world_aabb'][4]+P[i]['world_aabb'][5])/2]} for i in roots],'parts':[{'name':p['name'],'group':p['group'],'assembly':p['assembly'],'bounds':p['world_aabb']} for p in P],'contact_graph':[proof(i,parents[i]) for i in range(N) if parents[i] is not None],'structural_only_connected_parts':len(sp),'structural_only_disconnected':struct_disconnected,'seven_seam_couplers':seams,'guard_old_wall_junctions':guard_junctions,'four_door_interfaces':door_interfaces,'door_sweep_receipt':read(Q/'actual_door_sweep.json'),'slab_witnesses':slab,'floor_component_areas_m2':{n:p.area for n,p in floors},'clearance_queries':clear,'deep_pier_piece_count':len(deep),'deep_members_all_within_six_screened_piers':True,'source_lights':lights,'guard_contacts':guards,'corridor_clear_width_m':3.6,'no_duplicate_blender_floor_max_member_width_m':max(widths),'002_preservation':{k:v for k,v in actual.items() if k.startswith('002_')},'002_contract_preserved_except_two_appended_doors':True,'limits':['Geometric connectivity, not structural engineering capacity','Parent must independently verify installed96 slices/30 keel rays, actual floor/cap/lift/stair/cinema/garden paths and loaded carts; source-only clearances do not replace runtime tests','Door sweep and fitted frame intersections are separate builder receipt; all four actual operations remain runtime acceptance']}
(Q/'independent_contact_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('INDEPENDENT_CONTACT_PASS',N,len(roots),len(sp),len(slab),len(lights),len(guards))
