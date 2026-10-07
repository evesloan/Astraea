"""Pure data preparation. No Blender/Godot invocation; writes only beside this script."""
import json,hashlib,math,struct,pathlib,collections
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
D=pathlib.Path(__file__).resolve().parent
B=pathlib.Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x'); S=D.parent
H=json.load(open(S/'residential_whole_neighborhood_handoff_20261007/EXACT_BOUNDARY_AND_PINS.json')); P=pathlib.Path(H['current_package_root'])
R=json.load(open(S/'library_cinema_support_20261007/SELECTED_RECEIVING_SECTION_R1.json')); A=json.load(open(P/'SF_FULL_HOUSE_PLAN.json'))
def save(n,x): (D/n).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pins=[{'path':p,'retained_sha256':v,'current_sha256':sha(p),'unchanged':v==sha(p)} for p,v in H['pins'].items()]
for f in ['docs/LAYOUT_COMPILE_CHECKS.json','docs/master_source/MASTER_CURRENT_APPLICATION.json','data/reference/historical_atlas.pdf','data/reference/historical_atlas_allocations.json']:
 pins.append({'path':str(B/'Game'/f),'current_sha256':sha(B/'Game'/f)})
save('SOURCE_PINS.json',pins)
def bb(part):
 if part['kind']=='mesh':return [min(v[i] for v in part['verts']) for i in range(3)]+[max(v[i] for v in part['verts']) for i in range(3)]
 if part['kind']=='beam':
  a,b=part['a'],part['b'];w=part['width']/2;h=part['depth']/2
  return [min(a[0],b[0])-w,min(a[1],b[1])-h,min(a[2],b[2])-w,max(a[0],b[0])+w,max(a[1],b[1])+h,max(a[2],b[2])+w]
 return None
# Disjoint cuboidal partition: earlier nodes own all intersections; rails butt into their faces.
def cut(a,b):
 lo=[max(a[i],b[i]) for i in range(3)]; hi=[min(a[i+3],b[i+3]) for i in range(3)]
 if any(hi[i]-lo[i]<1e-8 for i in range(3)):return [a]
 out=[];c=a[:]
 for i in range(3):
  if c[i]<lo[i]-1e-8:q=c[:];q[i+3]=lo[i];out.append(q);c[i]=lo[i]
  if c[i+3]>hi[i]+1e-8:q=c[:];q[i]=hi[i];out.append(q);c[i+3]=hi[i]
 return out
caps=[v for v in R['volumes'] if v['id'].startswith('WP06') and '_CAP_' in v['id']]
rails=[v for v in R['volumes'] if v['id'].startswith(('ROOT_UPPER_LONG_','ROOT_UPPER_CROSS_'))]
parts=[]
def add(name,b,kind):
 pieces=[b]
 for o in parts:
  pieces=[q for a in pieces for q in cut(a,o['bounds'])]
 for k,p in enumerate(pieces):parts.append({'id':name+'__'+str(k),'bounds':[round(v,8) for v in p],'kind':kind})
for c in caps:
 b=c['min_xyz']+c['max_xyz'];b[1]=83.08;b[4]=83.20
 add('Bearing_'+c['id'],b,'bearing_node')
for r in rails:
 pieces=[r['min_xyz']+r['max_xyz']]
 for c in caps:pieces=[q for a in pieces for q in cut(a,c['min_xyz']+c['max_xyz'])]
 for k,b in enumerate(pieces):add(r['id']+'_'+str(k),b,'girder')
# Read actual retained GLB underside triangles, not allocation rectangles.
def floorpoly(u):
 path=P/'quiet_grove_interiors'/u['source_shell']; assert sha(path)==u['source_shell_sha256'],str(path); b=path.read_bytes(); n=struct.unpack_from('<I',b,12)[0]; j=json.loads(b[20:20+n]); off=20+n; ln,typ=struct.unpack_from('<II',b,off); buf=b[off+8:off+8+ln]
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];ct={'VEC3':3,'SCALAR':1}[a['type']];sz=struct.calcsize(fmt)*ct;start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',sz)
  return [struct.unpack_from('<'+fmt*ct,buf,start+k*stride) for k in range(a['count'])]
 out=[];theta=u['source_yaw_godot'];cs,sn=math.cos(theta),math.sin(theta);o=u['source_origin_world_xyz']
 for node in j['nodes']:
  if 'mesh' not in node:continue
  assert not any(k in node for k in ['matrix','rotation','scale','translation']),node
  for prim in j['meshes'][node['mesh']]['primitives']:
   v=acc(prim['attributes']['POSITION']);ix=[x[0] for x in acc(prim['indices'])]
   for k in range(0,len(ix),3):
    t=[v[i] for i in ix[k:k+3]]
    if all(abs(q[1]+o[1]-83.78)<1e-4 for q in t):
     poly=Polygon([(o[0]+cs*q[0]+sn*q[2],o[2]-sn*q[0]+cs*q[2]) for q in t])
     if poly.area>1e-8:out.append(poly)
 assert out,u['address']
 return unary_union(out)
foot=unary_union([box(q['bounds'][0],q['bounds'][2],q['bounds'][3],q['bounds'][5]) for q in parts if q['bounds'][4]==83.76])
roomcontacts=[]
for u in H['current_83_application_unit_ids']:
 if u['deck']!='D13':continue
 poly=floorpoly(u);intersection=poly.intersection(foot)
 if intersection.area>1e-6:
  roomcontacts.append({'source_index':u['census_source_index'],'id':u['address'],'floor_underside':83.78,'actual_floor_polygon':mapping(poly),'shoe_contact_polygon':mapping(intersection),'area_m2':intersection.area,'shell_path':str(P/'quiet_grove_interiors'/u['source_shell']),'shell_sha256':sha(P/'quiet_grove_interiors'/u['source_shell'])})
  # Split planar intersection by individual upper cells; each rectangle stays on actual floor.
  for k,q in enumerate(parts[:]):
   b=q['bounds']
   if b[4]!=83.76:continue
   poly2=poly.intersection(box(b[0],b[2],b[3],b[5]))
   if poly2.area<1e-8:continue
   if abs(poly2.area-box(*poly2.bounds).area)>1e-5:raise ValueError('Nonrectangular shoe requires polygon builder')
   x,z,X,Z=poly2.bounds;add('RoomShoe_'+str(u['census_source_index'])+'_'+str(k),[x,83.76,z,X,83.78,Z],'room_transition')
assert len(roomcontacts)==9,len(roomcontacts)
save('GEOMETRY_PROPOSAL.json',{'status':'Exact proposed closed cuboids; NOT BUILT or exported','units':'world metres X,Y-up,Z','identity_transform':True,'material_role':'ivory_enamel / champagne_metal joint accents, existing material system on build','parts':parts,'excluded_owner_closure':[82.85,82.9],'no_outboard_geometry':True})
save('ROOM_CONTACTS.json',roomcontacts)
# exact pairwise volume and planar contact graph
contacts=[];over=[]
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  x=a['bounds'];y=b['bounds'];ds=[min(x[k+3],y[k+3])-max(x[k],y[k]) for k in range(3)]
  if min(ds)>1e-7:over.append([a['id'],b['id']])
  if sum(abs(d)<1e-7 for d in ds)==1 and all(d>=-1e-7 for d in ds):contacts.append([a['id'],b['id'],round(math.prod(d for d in ds if d>1e-7),8)])
adj={p['id']:set() for p in parts}
for a,b,_ in contacts:adj[a].add(b);adj[b].add(a)
unseen=set(adj);components=[]
while unseen:
 stack=[unseen.pop()];c=[]
 while stack:
  a=stack.pop();c.append(a)
  for b in adj[a]&unseen:unseen.remove(b);stack.append(b)
 components.append(c)
# Current compiled owner floors screened using actual triangle polygons and vertical intervals.
gen=json.load(open(B/'Game/data/generated/structural_meshes.json'));cur=json.load(open(B/'Game/data/spatial_layout.json'));old=json.load(open(P/'inputs/spatial_layout.json'))
oldmap={r['id']:r for r in old['regions']};cm={r['id']:r for r in cur['regions']}
conflicts=[]
for r in gen['regions']:
 floor=r['floor_y'];th=r['thickness'];poly=unary_union([Polygon(t) for t in r['triangles']])
 for q in parts:
  b=q['bounds'];dy=min(b[4],floor)-max(b[1],floor-th)
  if dy>1e-6:
   ar=poly.intersection(box(b[0],b[2],b[3],b[5])).area
   if ar>1e-6:conflicts.append({'owner':r['id'],'candidate':q['id'],'volume':ar*dy})
# Preserve all members; no new completion status or rest capacity asserted.
ledger=[]
ids={u['census_source_index'] for u in H['current_83_application_unit_ids']}
for m in H['house_members']:
 i=m['source_envelope_index'];ledger.append({'source_index':i,'id':m['proposed_runtime_id'],'deck':m['deck'],'family':m['proposed_family'],'status':'retained_furnished_source_not_runtime' if i in ids else ('unfinished_VIP' if m['deck']=='D17' else 'unfinished_specialty'),'receiver_scope':'local_20mm_shoe_proposed' if i in {r['source_index'] for r in roomcontacts} else 'unchanged_existing_or_pending_receiving','completion_claim':False})
save('WHOLE_147_LEDGER.json',ledger)
pier=[]
for p in A['parts']:
 if p['name'].startswith('InnerGalleryPier'):
  b=bb(p)
  if b[2]>-447 and b[5]<-417:
   f=box(b[0],b[2],b[3],b[5]);pier.append({'id':p['name'],'bounds':b,'collector_coverage_m2':f.intersection(foot).area,'pier_footprint_m2':f.area,'path':'collector top83.76 -> retained garden slab83.76..84 -> retained pier84..106.02','counterpart_acceptance':'pending source-owner composition'})
assert len(pier)==4
save('TALL_PIER_CONTACTS.json',pier)
save('QA_DATA_SCREEN.json',{'part_count':len(parts),'positive_volume_overlap_pairs':over,'coplanar_contact_pairs':len(contacts),'connected_components':[len(c) for c in components],'actual_room_floor_contacts':len(roomcontacts),'tall_pier_contacts':pier,'current_owner_regions':len(cur['regions']),'compiled_owner_regions':len(gen['regions']),'new_owner_ids':sorted(set(cm)-set(oldmap)),'changed_retained_owner_ids':[k for k in oldmap if cm.get(k)!=oldmap[k]],'current_compiled_floor_positive_volume_conflicts':conflicts,'geometry_envelope':[8.2,82.9,-465.8,54,83.78,-398.2],'library_acoustic_closure_not_owned_or_authored':True,'capacity_unchanged':True,'runtime_tests':'NOT RUN','Blender_build':'NOT RUN'})
save('INTERNAL_CONTACT_GRAPH.json',contacts)
print(json.dumps({'parts':len(parts),'overlaps':len(over),'components':[len(c) for c in components],'rooms':len(roomcontacts),'owner_conflicts':len(conflicts),'new_owners':len(set(cm)-set(oldmap))}))
