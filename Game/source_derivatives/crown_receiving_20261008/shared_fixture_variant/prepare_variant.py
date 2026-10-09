from pathlib import Path
import json,struct,hashlib,copy,numpy as np
B=Path(__file__).resolve().parent; R=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x'); C=R/'BlenderCatalogue/assets/central_crown'; G=R/'Game'; A='AST-CMD-001_crown_fixture_relocation_20261008_r001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proposals=json.loads((B.parent/'fixture_fit_candidates/MOUNTED_FIXTURE_RELOCATION_PROPOSALS.json').read_text())
parts=json.loads((C/'source/geometry_parts.json').read_text()); original=G/'assets/models/AST-CMD-001.glb';raw=original.read_bytes();size,typ=struct.unpack_from('<II',raw,12);assert typ==0x4e4f534a;j=json.loads(raw[20:20+size]);js=copy.deepcopy(j);off=20+size;bs,bt=struct.unpack_from('<II',raw,off);assert bt==0x004e4942;binary=bytearray(raw[off+8:off+8+bs]);before=bytes(binary);allowed=set()
assert sha(original)==sha(C/'exports/AST-CMD-001.glb')
def acc(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];assert not a.get('sparse');dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',n*dt.itemsize);return np.ndarray((a['count'],n),dt,binary,offset,strides=(stride,dt.itemsize)),offset,stride
selected={}
for q in proposals:
 for name in q['move_together'][:2]:
  pp=[p for p in parts['parts'] if p['name']==name or p['name'].startswith(name+'.')];assert len(pp)==2
  for p in pp:selected[p['name']]={'part':p,'delta':np.array(q['translation']),'matches':[]}
changes=[]; masks={}; total=0
for ni,node in enumerate(j['nodes']):
 if 'mesh' not in node:continue
 assert not any(k in node for k in ['matrix','translation','rotation','scale','children'])
 for primitive in j['meshes'][node['mesh']]['primitives']:
  ai=primitive['attributes']['POSITION'];v,offset,stride=acc(ai);idx,_,_=acc(primitive['indices']);idx=idx.ravel().reshape(-1,3);material=j['materials'][primitive['material']]['name'];old=v.copy();vmask=np.zeros(len(v),bool);deltas=np.zeros(v.shape); selected_tri=np.zeros(len(idx),bool)
  for name,s in selected.items():
   p=s['part']
   if material!='ASTRAEA_'+p['role']:continue
   corners=np.array(p['vertices_world']);hit=(np.abs(old[:,None,:]-corners[None,:,:]).max(2)<1e-5).any(1);tri=hit[idx].all(1)
   if not tri.any():continue
   if not (np.abs(old[:,None,:]-corners[None,:,:]).max(2)<1e-5).any(0).all():continue
   # Require full closed twelve-triangle source box, uniquely belonging to this batch.
   assert tri.sum()==12,(name,node['name'],tri.sum());vi=np.unique(idx[tri]);assert not vmask[vi].any();vmask[vi]=True;deltas[vi]=s['delta'];selected_tri|=tri;s['matches'].append({'batch':node['name'],'accessor':ai,'vertices':vi.tolist(),'triangles':np.where(tri)[0].tolist()})
  if not vmask.any():continue
  assert np.array_equal(vmask[idx].any(1),selected_tri),('shared vertex with unrelated triangle',node['name'])
  assert ai not in masks; masks[ai]=vmask;v[vmask]=old[vmask]+deltas[vmask]
  assert np.array_equal(v[~vmask],old[~vmask]);assert np.array_equal(v[:,1],old[:,1]);total+=int(selected_tri.sum())
  for vi in np.where(vmask)[0]:
   for axis in range(3):
    if deltas[vi,axis]!=0:allowed.update(range(offset+int(vi)*stride+axis*4,offset+int(vi)*stride+axis*4+4))
  for k,fn in [('min',np.min),('max',np.max)]:j['accessors'][ai][k]=fn(v,axis=0).tolist()
  changes.append({'node':node['name'],'accessor':ai,'moved_vertices':int(vmask.sum()),'moved_triangles':int(selected_tri.sum())})
assert all(len(s['matches'])==1 for s in selected.values());assert total==240
for q in proposals:
 matches=[n for n in j['nodes'] if n.get('name')==q['existing_marker']];assert len(matches)==1;n=matches[0];assert np.max(np.abs(np.array(n['translation'])-q['old_marker_position']))<1e-5
 old=n['translation'].copy();n['translation']=[old[i]+q['translation'][i] for i in range(3)]
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,binary)))
# Only explicit accessor extrema and five datum translations may differ in JSON.
check=copy.deepcopy(j)
for c in changes:check['accessors'][c['accessor']]=js['accessors'][c['accessor']]
for i,n in enumerate(check['nodes']):
 if n.get('name') in {q['existing_marker'] for q in proposals}:check['nodes'][i]=js['nodes'][i]
assert check==js
payload=json.dumps(j,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);result=struct.pack('<III',0x46546c67,2,12+8+len(payload)+8+len(binary))+struct.pack('<II',len(payload),0x4e4f534a)+payload+struct.pack('<II',len(binary),0x004e4942)+binary
out=B/(A+'.glb');assert not out.exists();out.write_bytes(result)
manifest=G/'data/architecture/CENTRAL_CROWN_RUNTIME.json';rt=json.loads(manifest.read_text());rt0=copy.deepcopy(rt);patch=[]
for q in proposals:
 for i,m in enumerate(rt['light_markers']):
  if m['name']==q['existing_marker']:
   assert m['position']==q['old_marker_position'];m['position']=q['proposed_marker_position'];patch.append({'op':'test','path':f'/light_markers/{i}/position','value':q['old_marker_position']});patch.append({'op':'replace','path':f'/light_markers/{i}/position','value':q['proposed_marker_position']})
assert len(patch)==10
(B/'CENTRAL_CROWN_RUNTIME.proposed.json').write_text(json.dumps(rt,indent=2)+'\n');(B/'RUNTIME_MANIFEST_PATCH.json').write_text(json.dumps({'original_sha256':sha(manifest),'json_patch':patch,'model_selection':{'file':'scripts/central_command_crown.gd','old':'AST-CMD-001.glb','proposed':A+'.glb'},'registration':'No new catalogue ID allocated; parent must decide isolated derivative registration before adoption.'},indent=2))
records=[]
for name,s in selected.items():records.append({'name':name,'translation':s['delta'].tolist(),'matches':s['matches']})
report={'variant':A,'source_native':str(C/'source/AST-CMD-001.blend'),'source_native_sha256':sha(C/'source/AST-CMD-001.blend'),'original_runtime_sha256':sha(original),'original_catalogue_manifest_sha256':sha(C/'AST-CMD-001.manifest.json'),'variant_runtime_sha256':sha(out),'original_runtime_manifest_sha256':sha(manifest),'changed_mesh_accessors':changes,'selected_source_parts':records,'moved_triangles':total,'preservation':{'all_nonselected_binary_bytes_identical':True,'indices_normals_uv_material_buffers_identical':True,'json_only_affected_accessor_bounds_and_five_datums':True,'original_source_files_unchanged':True},'native_save_pending':True}
(B/'BINARY_EDIT_PROOF.json').write_text(json.dumps(report,indent=2));print(json.dumps({'output':str(out),'moved_triangles':total,'parts':len(records),'accessors':len(changes)}))
