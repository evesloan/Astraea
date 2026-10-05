"""Independent read-only geometry checks; writes only its own QA report.
Run with Shapely available. All contacts use actual convex prism footprints,
not overlapping AABBs. Does not claim load capacity or runtime collision proof.
"""
from pathlib import Path
import collections, hashlib, json, math, struct, subprocess
from shapely.geometry import MultiPoint, box, LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree
C=Path(__file__).resolve().parents[3]; R=C/'assets'; G=C.parent/'astraea-godot-production-20261003'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=R/'bridge_enclosure'; B=R/'bridge_platform'
a=json.loads((A/'source/geometry_parts.json').read_text())['parts']; b=json.loads((B/'source/geometry_parts.json').read_text())['parts']; ps=a+b
polys=[]
for p in ps:
 v=p['vertices_world']; ys=sorted(set(q[1]for q in v)); assert len(ys)==2,p['name']
 lower=MultiPoint([(q[0],q[2])for q in v if q[1]==ys[0]]).convex_hull
 upper=MultiPoint([(q[0],q[2])for q in v if q[1]==ys[1]]).convex_hull
 assert lower.equals(upper)and lower.area>0,p['name'];polys.append(lower)
tree=STRtree(polys);adj=[[]for p in ps]
def witness(i,j):
 p,q=ps[i],ps[j];lo=max(p['world_aabb'][2],q['world_aabb'][2]);hi=min(p['world_aabb'][3],q['world_aabb'][3]); inter=polys[i].intersection(polys[j]);dy=max(0,hi-lo)
 return {'part':p['name'],'part_asset':'AST-CMD-004'if i<len(a)else'AST-CMD-003','support_part':q['name'],'support_asset':'AST-CMD-004'if j<len(a)else'AST-CMD-003','footprint_intersection_wkt':inter.wkt,'overlap_y':[lo,hi],'plan_area_m2':inter.area,'contact_volume_m3':inter.area*dy,'contact_surface_m2':inter.area if dy<1e-8 else inter.length*dy}
for i,p in enumerate(ps):
 for jj in tree.query(polys[i]):
  j=int(jj)
  if j<=i:continue
  q=ps[j];dy=min(p['world_aabb'][3],q['world_aabb'][3])-max(p['world_aabb'][2],q['world_aabb'][2])
  if dy< -1e-8:continue
  inter=polys[i].intersection(polys[j])
  if inter.area>1e-8 or (inter.length>1e-5 and dy>1e-5):adj[i].append(j);adj[j].append(i)
# Multi-source BFS: one explicit shortest contact chain for every004 part to003.
parent={i:None for i in range(len(a),len(ps))};queue=collections.deque(parent)
while queue:
 i=queue.popleft()
 for j in adj[i]:
  if j not in parent:parent[j]=i;queue.append(j)
assert all(i in parent for i in range(len(a)))
network=[witness(i,parent[i])for i in range(len(a))]
D=json.loads((A/'source/section_contract.json').read_text());outline=D['boundary_xz'];boundary=LineString(outline+[outline[0]])
levels=sorted(set([106.5,114.32]+[p['world_aabb'][k]for p in ps for k in[2,3]if 106.5<=p['world_aabb'][k]<=114.32]));levels=sorted(levels+[sum(v)/2 for v in zip(levels,levels[1:])]);gaps=[]
for y in levels:
 shape=unary_union([polys[i]for i,p in enumerate(ps)if p['world_aabb'][2]-1e-7<=y<=p['world_aabb'][3]+1e-7]);test=boundary
 if y<109.315:
  for z in[-171.7,-118.3]:test=test.difference(box(-1.375,z-.5,1.375,z+.5))
 gap=test.difference(shape.buffer(1e-5))
 if gap.length>1e-5:gaps.append({'y':y,'gap':gap.wkt})
assert not gaps
apertures=[]
for z in[-171.7,-118.3]:
 poly=box(-1.375,z-.33,1.375,z+.33);hits=[]
 for i,p in enumerate(ps):
  dy=min(p['world_aabb'][3],109.315)-max(p['world_aabb'][2],106.5)
  if dy>1e-8 and polys[i].intersection(poly).area>1e-8:hits.append(p['name'])
 assert not hits,hits;apertures.append({'center':[0,106.5,z],'clear_volume':[-1.375,1.375,106.5,109.315,z-.33,z+.33],'intersecting_parts':hits})
fixture_hits=[];lens_parts=0
for p in b:
 if p['group']!='fixture'or'Lens'not in p['assembly']:continue
 lens_parts+=1;poly=MultiPoint([(v[0],v[2])for v in p['vertices_world']]).convex_hull
 for i,q in enumerate(a):
  if min(q['world_aabb'][3],p['world_aabb'][3])-max(q['world_aabb'][2],106.5)>1e-8 and polys[i].intersection(poly).area>1e-8:fixture_hits.append([p['name'],q['name']])
assert not fixture_hits
rays=[]
for eye in[(28,107.65,-145),(28,108.1,-145)]:
 dx=80;dz=dx*math.tan(math.radians(12));dy=math.hypot(dx,dz)*math.tan(math.radians(12));line=LineString([(eye[0],eye[2]),(eye[0]+dx,eye[2]+dz)]);hits=[]
 for i,p in enumerate(ps):
  if p['group']=='glass':continue
  inter=polys[i].intersection(line)
  if inter.is_empty:continue
  coords=list(inter.coords);ys=[eye[1]+(q[0]-eye[0])/dx*dy for q in coords]
  if min(max(ys),p['world_aabb'][3])-max(min(ys),p['world_aabb'][2])>1e-7:hits.append(p['name'])
 assert not hits; t=(35.7-eye[0])/dx;rays.append({'eye':eye,'wall_intersection':[35.7,eye[1]+dy*t,eye[2]+dz*t],'opaque_hits':hits})
baseline='dc8b89d8d25bb6b973961a1fff27d27b0aa839e6';path='assets/bridge_platform/source/geometry_parts.json';old=json.loads(subprocess.check_output(['git','show',baseline+':'+path],cwd=C))['parts'];old={p['name']:p for p in old};new={p['name']:p for p in b};assert set(old)==set(new);changed=[n for n in old if old[n]!=new[n]]
allowed={'BRP_Port_GuardBack_00','BRP_Port_GuardCap_00'}|{'BRP_Starboard_Guard'+k+'_%02d'%i for k in ['Back','Cap']for i in range(3)}
assert len(changed)==32 and {new[n]['assembly']for n in changed}==allowed
for n in changed:
 assert all(v[0]==w[0]and v[2]==w[2]for v,w in zip(old[n]['vertices_world'],new[n]['vertices_world']))
 assert new[n]['world_aabb'][2:4]==([107.08,107.12]if'GuardCap'in n else[106.45,107.1])
path='assets/bridge_platform/source/section_contract.json';od=json.loads(subprocess.check_output(['git','show',baseline+':'+path],cwd=C));nd=json.loads((C/path).read_text());assert od['windows']==nd['windows']and len(nd['windows'])==24;assert od['light_markers']==nd['light_markers']and len(nd['light_markers'])==20
# Read actual installed core node positions, including world origin, without engine import.
core=G/'assets/models/AST-CIR-005.glb';raw=core.read_bytes();size=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+size]);node=next(n for n in gltf['nodes']if n.get('name')=='CORE_TopCover');assert not any(k in node for k in ['matrix','translation','rotation','scale']);acc=gltf['accessors'][gltf['meshes'][node['mesh']]['primitives'][0]['attributes']['POSITION']];lo=acc['min'];hi=acc['max'];core_bounds=[lo[0],hi[0],lo[1],hi[1],lo[2]-100,hi[2]-100];assert abs(core_bounds[4]+113)<1e-6
core_contacts=[]
for p in a:
 if p['assembly']!='BRE_AftVestibule_Roof':continue
 bb=p['world_aabb'];overlap=[max(bb[k],core_bounds[k])if k%2==0 else min(bb[k],core_bounds[k])for k in range(6)]
 if all(overlap[k+1]>overlap[k]for k in[0,2,4]):core_contacts.append({'part':p['name'],'core_part':'CORE_TopCover','overlap_aabb':overlap})
assert len(core_contacts)==2
pins={}
for family,aid in [('bridge_enclosure','AST-CMD-004'),('bridge_platform','AST-CMD-003')]:
 for rel in [f'source/{aid}.blend',f'exports/{aid}.glb','source/geometry_parts.json','source/section_contract.json']:pins[f'assets/{family}/{rel}']=sha(R/family/rel)
pins['installed:assets/models/AST-CIR-005.glb']=sha(core)
report={'schema':1,'pass':True,'scope':'Independent source geometric contact and preservation audit; no load-capacity, species-fit, optical photometry, actual runtime collision or final-art claim. Convex vertical prisms verified for all source pieces. Contact graph permits positive face contact and positive-volume overlap, never isolated point/line contact.','hashes':pins,'enclosure_part_count':len(a),'platform_part_count':len(b),'contact_network':network,'direct_003_contact_pair_count':sum(sum(j>=len(a)for j in adj[i])for i in range(len(a))),'perimeter':{'height_slices':levels,'gap_count':0,'tolerance_m':.00001},'door_apertures':apertures,'guard_preservation':{'baseline_git':baseline,'changed_part_count':len(changed),'unchanged_part_count':len(b)-len(changed),'allowlist':sorted(allowed),'changed_parts':changed,'all_other_full_records_exact':True,'panes':24,'fixtures':20,'window_and_light_contracts_exact':True},'fixtures':{'lens_piece_count':lens_parts,'new_geometry_intersecting_lens_vertical_exit_columns':fixture_hits,'receiver_cone_runtime_check_required':True},'planet_upper_limb_rays':rays,'core_cover':{'actual_installed_bounds':core_bounds,'roof_contacts':core_contacts},'bounds':{'minimum_new_y':min(p['world_aabb'][2]for p in a),'maximum_new_y':max(p['world_aabb'][3]for p in a),'new_geometry_below_D18':False},'parts':[{'name':p['name'],'assembly':p['assembly'],'group':p['group'],'role':p['role'],'vertices_world':p['vertices_world']}for p in a]}
assert report['bounds']['minimum_new_y']==106.5 and report['bounds']['maximum_new_y']==114.32
out=A/'qa/independent_contact_audit.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':True,'path':str(out),'sha256':sha(out),'parts':len(a),'contact_network_edges':len(network),'height_slices':len(levels),'guard_changes':len(changed)}))
