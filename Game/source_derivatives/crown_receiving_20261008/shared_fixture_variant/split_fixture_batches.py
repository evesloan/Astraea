from pathlib import Path
import json,struct,copy,hashlib,collections,numpy as np
B=Path(__file__).resolve().parent;A='AST-CMD-001_crown_fixture_relocation_20261008_r002';proof=json.loads((B/'BINARY_EDIT_PROOF.json').read_text());old=B/(proof['variant']+'.glb');raw=old.read_bytes();size=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+size]);off=20+size;bs,bt=struct.unpack_from('<II',raw,off);binary=bytearray(raw[off+8:off+8+bs]);oldbinary=bytes(binary);before=copy.deepcopy(j)
def acc(i):
 a=j['accessors'][i];bv=j['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],n),dt,binary,bv.get('byteOffset',0)+a.get('byteOffset',0),strides=(bv.get('byteStride',n*dt.itemsize),dt.itemsize)).copy()
def append_accessor(array,template,target):
 array=np.ascontiguousarray(array);binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);binary.extend(array.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':array.nbytes,'target':target});a=copy.deepcopy(template);a.update(bufferView=vi,byteOffset=0,count=len(array));a.pop('min',None);a.pop('max',None)
 if a['type']=='VEC3':a.update(min=array.min(0).tolist(),max=array.max(0).tolist())
 ai=len(j['accessors']);j['accessors'].append(a);return ai
def compact(primitive,triangle_indices):
 oldidx=acc(primitive['indices']).ravel().reshape(-1,3);chosen=oldidx[triangle_indices];vertices=np.unique(chosen);newidx=np.searchsorted(vertices,chosen).astype('<u4').reshape(-1,1);p=copy.deepcopy(primitive);p['attributes']={k:append_accessor(acc(ai)[vertices],j['accessors'][ai],34962)for k,ai in primitive['attributes'].items()};p['indices']=append_accessor(newidx,{'componentType':5125,'type':'SCALAR'},34963);return p
# Store exact oriented per-triangle byte signatures for all attributes and material.
def signatures(doc):
 result=collections.Counter()
 for n in doc['nodes']:
  if 'mesh' not in n:continue
  for p in doc['meshes'][n['mesh']]['primitives']:
   idx=acc(p['indices']).ravel().reshape(-1,3);attrs={k:acc(v)for k,v in p['attributes'].items()}
   for t in idx:result[(p.get('material'),tuple((k,v[t].tobytes())for k,v in sorted(attrs.items())))]+=1
 return result
before_sig=signatures(before);bybatch=collections.defaultdict(list)
for part in proof['selected_source_parts']:
 for match in part['matches']:bybatch[match['batch']].append((part,match))
provenance=[];changed=[]; original_nodes=list(j['nodes']);roots=j['scenes'][j.get('scene',0)]['nodes'];assert set(roots)==set(range(len(original_nodes)))
for ni,n in enumerate(original_nodes):
 if n['name'] not in bybatch:continue
 mi=n['mesh'];ps=j['meshes'][mi]['primitives'];assert len(ps)==1;p=copy.deepcopy(ps[0]);idx=acc(p['indices']).ravel().reshape(-1,3);remove=set()
 for part,match in bybatch[n['name']]:
  tris=match['triangles'];assert not(remove&set(tris));remove.update(tris);newp=compact(p,tris);newname='CMD_FIXTURE_RELOC_'+part['name'];newmi=len(j['meshes']);j['meshes'].append({'name':newname,'primitives':[newp]});newnode={'name':newname,'mesh':newmi,'extras':{'catalogue_id':'AST-CMD-001','collision_contract':'concave_static_surface','source_part':part['name'],'historical_batch':n['name'],'variant':'crown_fixture_relocation_20261008_r002'}};nodeid=len(j['nodes']);j['nodes'].append(newnode);roots.append(nodeid);provenance.append({'source_part':part['name'],'translation':part['translation'],'historical_batch':n['name'],'historical_triangle_indices':tris,'active_batch':newname,'active_triangle_indices':list(range(len(tris))),'active_node_index':nodeid})
 keep=[i for i in range(len(idx))if i not in remove]
 if keep:j['meshes'][mi]['primitives']=[compact(p,keep)]
 else:n.pop('mesh')
 changed.append({'retained_batch_name':n['name'],'retained_triangle_original_indices':keep,'relocated_triangle_original_indices':sorted(remove),'retained_triangles':len(keep),'identity_node_retained':True,'empty_mesh_detached':not bool(keep)})
assert signatures(j)==before_sig
assert bytes(binary[:len(oldbinary)])==oldbinary
j['buffers'][0]['byteLength']=len(binary);payload=json.dumps(j,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);binary.extend(b'\0'*((-len(binary))%4));out=B/(A+'.glb');assert not out.exists();out.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(payload)+8+len(binary))+struct.pack('<II',len(payload),0x4e4f534a)+payload+struct.pack('<II',len(binary),0x004e4942)+binary)
ns={'__file__':str(B.parent/'audit.py')};exec((B.parent/'audit.py').read_text().split('runtime=json')[0],ns);_,objects=ns['glb'](out);extent=max(float((o['hi']-o['lo']).max())for o in objects);assert extent<16.001,extent
report={'variant':A,'predecessor_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'runtime_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'unchanged_oriented_triangle_attribute_material_multiset':True,'all_predecessor_binary_bytes_retained':True,'unchanged_original_node_identity_count':len(original_nodes),'new_fixture_batches':len(provenance),'maximum_active_batch_extent_m':extent,'preserved_extent_gate_m':16.001,'triangle_count':sum(before_sig.values()),'historical_to_active_membership':provenance,'modified_original_batches':changed,'native_pending':True}
(B/'BATCH_SPLIT_PROOF.json').write_text(json.dumps(report,indent=2));patch=json.loads((B/'RUNTIME_MANIFEST_PATCH.json').read_text());patch['model_selection']['proposed']=A+'.glb';(B/'RUNTIME_MANIFEST_PATCH.json').write_text(json.dumps(patch,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ['historical_to_active_membership','modified_original_batches']}))
