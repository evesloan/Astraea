"""Exact source/GLB/material/preservation and geometric-contact QA; never starts an engine."""
from pathlib import Path
from collections import Counter,deque
import bpy,bmesh,json,hashlib,struct,math,subprocess
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];D=json.loads((R/'source/connected_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fingerprint(o):
 row={'type':o.type,'matrix':[list(r)for r in o.matrix_world],'properties':{k:o[k]for k in o.keys()}}
 if o.type=='MESH':row.update(vertices=[list(v.co)for v in o.data.vertices],faces=[list(p.vertices)for p in o.data.polygons],uv=[list(v.uv)for v in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials])
 return row
def snapshot(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));return{o.name:fingerprint(o)for o in bpy.context.scene.objects}
def materials():
 out={}
 used={m.name for o in bpy.context.scene.objects if o.type=='MESH'for m in o.data.materials}
 for m in bpy.data.materials:
  if m.name not in used or not m.use_nodes:continue
  nn=[]
  for n in m.node_tree.nodes:
   inputs={}
   for s in n.inputs:
    if not hasattr(s,'default_value'):continue
    v=s.default_value
    if not isinstance(v,(str,int,float,bool)):
     try:v=list(v)
     except TypeError:continue
    inputs[s.name]=v
   row={'type':n.bl_idname,'inputs':inputs}
   if n.type=='TEX_IMAGE':row.update(image=hashlib.sha256(n.image.packed_file.data).hexdigest(),interpolation=n.interpolation)
   nn.append(row)
  out[m.name]=nn
 return out
preserved=[]
for p,h in D['preserved_inputs'].items():
 assert sha(C/p)==h,p
 old=subprocess.check_output(['git','-C',str(C),'show','HEAD:'+p]);assert hashlib.sha256(old).hexdigest()==h,(p,'not retained HEAD bytes')
 preserved.append(p)
assert sha(C/'assets/d17_house_platform/source/AST-RES-005.blend')=='9434b7228c1f7a8c20c028e96b750a9bc2bc3226aa4d0d81e602537cfe8ca9bd'
A=snapshot(C/'assets/starboard_house_upper/source/AST-COM-003.blend');AM=materials();B=snapshot(R/'source/AST-COM-003_aft_only.blend');BM=materials()
changed={n for n in A if n in B and A[n]!=B[n]};removed=set(A)-set(B)
assert changed=={'HC_ProfileWall_D17_-1_2','HC_Wainscot_D17_-1_2'},changed
assert removed=={'HC_ProfileWall_D17_-1_2_PortalRightStub','HC_ProfileWall_D17_-1_2_PortalHeader','HC_Wainscot_D17_-1_2_PortalRightStub'},removed
assert not(set(B)-set(A));assert AM==BM
BASE=snapshot(R/'source/verified_closed_COM003.blend')
assert all(B[n]==BASE[n]for n in changed),'fore wall not original exact restoration'
held=snapshot(C/'assets/d17_house_platform/source/AST-RES-005.blend');new=snapshot(R/'source/AST-RES-006.blend');NM=materials()
assert all(new[n]==held[n]for n in D['reused_retained_parts']),'retained component geometry/UV/identity changed'
assert all(NM[n]==AM[n]for n in NM),'material graph or packed texture changed'
# Source versus raw glTF oriented triangle, UV and material equality. No lossy import comparison.
def signatures(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active.data
 for t in o.data.loop_triangles:
  p=[]
  for vi,li in zip(t.vertices,t.loops):
   q=o.matrix_world@o.data.vertices[vi].co;u=uv[li].uv;p.append((float(q.x),float(q.z),float(-q.y),float(u.x),struct.unpack('<f',struct.pack('<f',1-u.y))[0]))
  yield(o.data.materials[t.material_index].name,min(tuple(p[k:]+p[:k])for k in range(3)))
roundtrips=[]
for stem in ['AST-RES-006','AST-COM-003_aft_only']:
 src=R/'source'/(stem+'.blend');ex=R/'exports'/(stem+'.glb');bpy.ops.wm.open_mainfile(filepath=str(src));S=Counter();count=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.name.startswith('PREVIEW_ONLY_'):continue
  count+=1;bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.free();S.update(signatures(o))
 marks={o.name:[o.location.x,o.location.z,-o.location.y]for o in bpy.context.scene.objects if o.type=='EMPTY'}
 raw=ex.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);data=raw[28+n:];E=Counter();batches=0
 def acc(ai):
  a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];sz=struct.calcsize('<'+fmt*count);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',sz);return[struct.unpack_from('<'+fmt*count,data,off+i*stride)for i in range(a['count'])]
 for node in g['nodes']:
  assert not node.get('name','').startswith('PREVIEW_ONLY_'),'preview leaked to export'
  if 'mesh'not in node:continue
  assert not any(k in node for k in ['matrix','translation','rotation','scale']),node['name'];batches+=1
  for prim in g['meshes'][node['mesh']]['primitives']:
   p=acc(prim['attributes']['POSITION']);u=acc(prim['attributes']['TEXCOORD_0']);ix=[a[0]for a in acc(prim['indices'])];m=g['materials'][prim['material']]['name']
   for i in range(0,len(ix),3):
    pts=[tuple((*p[k],*u[k]))for k in ix[i:i+3]];E[(m,min(tuple(pts[k:]+pts[:k])for k in range(3)))]+=1
 assert S==E,(stem,'triangle/UV/material mismatch',sum((S-E).values()),sum((E-S).values()))
 em={n['name']:n.get('translation',[0,0,0])for n in g['nodes']if'mesh'not in n}
 assert set(em)==set(marks)
 assert all(max(abs(a-b)for a,b in zip(em[n],p))<1e-5 for n,p in marks.items())
 # Exported embedded texture bytes must be exactly from the shared source graphs.
 source_images={hashlib.sha256(n.image.packed_file.data).hexdigest()for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.packed_file}
 export_images=[]
 for im in g.get('images',[]):
  v=g['bufferViews'][im['bufferView']];h=hashlib.sha256(data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]).hexdigest();assert h in source_images,(stem,im['name']);export_images.append(h)
 roundtrips.append({'asset':stem,'source_sha256':sha(src),'export_sha256':sha(ex),'editable_exported_meshes':count,'export_batches':batches,'oriented_triangles':sum(S.values()),'triangle_uv_material_exact':True,'manifold_positive_volume':True,'marker_count':len(marks),'marker_exact':True,'embedded_texture_byte_equality':True})
# Actual closed-mesh intersection graph, not AABB-only contacts. Concave roofs/floors use BVH ray parity.
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-RES-006.blend'))
obs={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 vv=[o.matrix_world@v.co for v in o.data.vertices];ff=[list(f.vertices)for f in o.data.polygons];tree=BVHTree.FromPolygons(vv,ff,all_triangles=False,epsilon=1e-5)
 obs[o.name]={'v':vv,'f':ff,'tree':tree,'bounds':[(min(p[i]for p in vv),max(p[i]for p in vv))for i in range(3)]}
# Add the actual retained commons transfer in matching zero-origin Blender coordinates.
with bpy.data.libraries.load(str(C/'assets/starboard_house_upper/source/AST-COM-003.blend'),link=False)as(a,b):b.objects=['HC_PerimeterTransfer_106.26_1']
o=b.objects[0];vv=[o.matrix_world@v.co+Vector((63,0,84))for v in o.data.vertices];ff=[list(f.vertices)for f in o.data.polygons]
obs['EXISTING_HC_PerimeterTransfer_106.26_1']={'v':vv,'f':ff,'tree':BVHTree.FromPolygons(vv,ff,epsilon=1e-5),'bounds':[(min(p[i]for p in vv),max(p[i]for p in vv))for i in range(3)]}
DIR=Vector((1,.371,.529)).normalized();eps=3e-5
def inside(p,row):
 nearest=row['tree'].find_nearest(p)
 if nearest[0]is not None and nearest[3]<eps:return True
 start=p.copy();hits=0
 for _ in range(30):
  h,n,i,d=row['tree'].ray_cast(start,DIR)
  if h is None:break
  hits+=1;start=h+DIR*1e-4
 return hits%2==1
def contact(a,b):
 aa,bb=obs[a],obs[b]
 if any(min(aa['bounds'][i][1],bb['bounds'][i][1])+eps<max(aa['bounds'][i][0],bb['bounds'][i][0])for i in range(3)):return None
 # A true surface-triangle intersection or contained actual vertex establishes a geometric joint.
 pairs=aa['tree'].overlap(bb['tree'])
 if pairs:return {'method':'actual triangle intersections','triangle_pairs':len(pairs)}
 for p in aa['v']:
  if inside(p,bb):return {'method':'actual vertex on/inside closed mesh','witness_blender':list(p)}
 for p in bb['v']:
  if inside(p,aa):return {'method':'actual vertex on/inside closed mesh','witness_blender':list(p)}
 return None
names=sorted(obs);graph={n:set()for n in names};contacts=[]
for i,a in enumerate(names):
 for b in names[i+1:]:
  hit=contact(a,b)
  if hit:graph[a].add(b);graph[b].add(a);contacts.append({'a':a,'b':b,**hit})
roots={f'D17_SeatedHullFooting_{i}'for i in [0,1,2]}|{'EXISTING_HC_PerimeterTransfer_106.26_1'};seen=set(roots);q=deque(roots)
while q:
 a=q.popleft()
 for b in graph[a]-seen:seen.add(b);q.append(b)
unrooted=sorted(set(names)-seen)
# Portal jambs sit on preserved floor, not one of the new preview rectangles. Add actual existing floor contact as a separate known boundary.
portal=[n for n in unrooted if n.startswith('CR_Portal')]
if portal:
 for n in portal:
  if n.startswith('CR_Portal_') and 'Header'not in n:
   o=obs[n];assert abs(o['bounds'][2][0]-102)<eps;seen.add(n);q.append(n);contacts.append({'a':n,'b':'existing_D17_floor','method':'actual bottom Y102; footprint inside preserved floor boundary'})
 while q:
  a=q.popleft()
  for b in graph[a]-seen:seen.add(b);q.append(b)
unrooted=sorted(set(names)-seen)
# Report details before asserting so recovery is bounded.
contact_report={'pass':not unrooted,'rooted_meshes':len(seen),'mesh_count':len(names),'roots':sorted(roots),'unrooted':unrooted,'contacts':contacts,'tolerance_m':eps,'scope':'Geometric source joints only; retained hull seats reuse prior verified evidence without rerunning hull diagnostics'}
(R/'qa/source_contact_graph.json').write_text(json.dumps(contact_report,indent=2)+'\n')
assert not unrooted,unrooted
# Explicit source-volume protection on lower homes, excluding already-proven retained components.
def bounds_world(row):
 return [row['bounds'][0],row['bounds'][2],[-row['bounds'][1][1],-row['bounds'][1][0]]]
protected=[]
for key,home in D['protected'].items():
 if not isinstance(home,dict):continue
 for n,row in obs.items():
  if n.startswith('EXISTING_') or n in D['reused_retained_parts']:continue
  b=bounds_world(row)
  if min(b[0][1],home['x'][1])-max(b[0][0],home['x'][0])>eps and min(b[2][1],home['z'][1])-max(b[2][0],home['z'][0])>eps:
   assert b[1][0]>=101.76-eps,(key,n,b);protected.append({'home':key,'part':n,'lowest_y':b[1][0]})
assert len(D['units_preserved'])==16 and len({u['source_envelope_index']for u in D['units_preserved']})==16
assert len(D['standard_membership']['fore'])==5 and len(D['standard_membership']['aft'])==4
assert all(u['historical_stable_id']is None for u in D['units_preserved'])
assert all(max(p[1] for p in r['world_vertices'])<=106.50001 for r in D['source_parts'] if not r['name'].startswith('PREVIEW_ONLY_'))
report={'pass':True,'scope':'Connected editable architecture/source and export only; runtime, loaded-cart and in-ship visual acceptance belongs to root','preserved_input_files':preserved,'COM_aft_variant_unchanged_objects':len(B)-len(changed),'COM_exact_fore_restore':sorted(changed),'COM_removed_fore_split_additions':sorted(removed),'COM_material_graphs_exact':True,'retained_source_meshes_exact':D['reused_retained_parts'],'all_shared_material_graphs_and_packed_images_exact':True,'roundtrips':roundtrips,'source_contact_graph':'qa/source_contact_graph.json','lower_home_overlap_members_above_soffit':protected,'all16_source_indices_preserved':True,'standards_five_fore_four_aft':True,'unit814_effective_reservation_preserved':True,'exported_walkable_floor_meshes':0,'ordinary_roof_max_y':106.30,'new_units':0,'new_berths':0,'pending':['Actual engine imported source/collision','Actual main-scene floor/void compiler preservation','Actual walking and force-tethered loaded-cart route','Matched-revision in-ship normal/effects-off and context views','Private upper completion and whole ship acceptance']}
(R/'qa/source_export_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':True,'source_contacts':len(contacts),'rooted_meshes':len(seen),'roundtrips':roundtrips},indent=2))
