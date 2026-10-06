"""Independent pure binary Court-only check. New report only; no engines.
The court-local static GLB is compared after its explicit native root translation.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct,sys
import numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check():
 E=D/'packed_export001';S=json.loads((E/'EXPORT_RECEIPT.json').read_text());plan=json.loads((D/'EXPORT_PLAN.json').read_text())
 assert S['source_sha256']==plan['source_sha256']==sha(S['source']);assert len(S['instances'])==24
 assert sha(E/'source_triangle_attributes.npz')==S['source_attribute_archive_sha256']
 expected=np.load(E/'source_triangle_attributes.npz',allow_pickle=False);batches={b['name']:b for b in S['batches']};seen=set();records=[];errors=[];images_seen=set();defs=set();materials_seen=set()
 helper=Path(plan['retained_package']).parent/'firstpass_003/dependencies/geometry_review.py'
 assert sha(helper)==plan['input_sha256'][str(helper)]
 spec=importlib.util.spec_from_file_location('court_binary_glb',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 def close(a,b,tol=1e-6):return np.max(abs(np.array(a)-np.array(b)))<=tol
 def canonical(x,u,n):
  key=np.round(x,3);choose=np.array([min(range(3),key=lambda i:tuple(row[i]))for row in key]);order=(choose[:,None]+np.arange(3))%3;ix=np.arange(len(x))[:,None]
  x=x[ix,order];u=u[ix,order];n=n[ix,order];k=np.round(x,3).reshape(-1,9);order=np.lexsort(tuple(k[:,i]for i in range(8,-1,-1)))
  return x[order],u[order],n[order]
 for row in S['export_records']:
  path=Path(row['path']);assert path.parent==E and sha(path)==row['sha256'];g=module.glb(path);nodes={n['name']:n for n in g['nodes']}
  assert not g['doc'].get('animations')and not g['doc'].get('cameras') and 'KHR_lights_punctual'not in g['doc'].get('extensions',{})
  for node in g['nodes']:
   if 'definition_id'in node['extras']:assert row['kind']=='prototype';defs.add(node['extras']['definition_id'])
  assert not set(i['id']for i in S['instances']).intersection(nodes), 'Placement duplicates in GLB'
  blob=path.read_bytes();offset=12;binary=None
  while offset<len(blob):
   length,kind=struct.unpack_from('<II',blob,offset)
   if kind==0x004e4942:binary=blob[offset+8:offset+8+length]
   offset+=8+length
  image_hashes=[]
  for im in g['doc'].get('images',[]):
   assert 'bufferView'in im;view=g['doc']['bufferViews'][im['bufferView']];data=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
   h=hashlib.sha256(data).hexdigest();image_hashes.append(h);images_seen.add(h)
  for mat in g['doc'].get('materials',[]):
   name=mat['name'];assert name in S['material_expectations'];src=S['material_expectations'][name];materials_seen.add(name);pbr=mat.get('pbrMetallicRoughness',{});ext=mat.get('extensions',{})
   assert close(pbr.get('roughnessFactor',1),src['roughness'])and close(pbr.get('metallicFactor',1),src['metallic']),('PBR factors',name)
   assert close(pbr.get('baseColorFactor',[1,1,1,1]),src['base_color']),('Base colour',name)
   sp=ext.get('KHR_materials_specular',{});assert close(sp.get('specularFactor',1),src['specular_factor'])and close(sp.get('specularColorFactor',[1,1,1]),src['specular_color']),('Specular translation',name)
   assert close(ext.get('KHR_materials_ior',{}).get('ior',1.5),src['ior']),('IOR',name)
   assert mat.get('doubleSided',False)==src['double_sided'] and mat.get('alphaMode','OPAQUE')=='OPAQUE'
   assert close(mat.get('emissiveFactor',[0,0,0]),[0,0,0])
   assert not any(k in mat for k in ['normalTexture','occlusionTexture','emissiveTexture'])
   assert not set(ext)-{'KHR_materials_specular','KHR_materials_ior'},('Unexpected shader extension',name,ext.keys())
   if src['image']:
    t=pbr['baseColorTexture'];assert t.get('texCoord',0)==0 and not t.get('extensions')
    texture=g['doc']['textures'][t['index']];assert image_hashes[texture['source']]==src['image']['sha256']
    sampler=g['doc'].get('samplers',[])[texture['sampler']]if'sampler'in texture else{}
    wrap=33071 if src['image']['extension']=='EXTEND' else 10497
    assert sampler.get('wrapS',10497)==wrap and sampler.get('wrapT',10497)==wrap
    assert sampler.get('magFilter',9729)==9729 and sampler.get('minFilter',9987)in {9729,9987}
   else:assert'baseColorTexture'not in pbr
  for mesh in g['meshes']:
   name=mesh['node'];assert name in batches and name not in seen;seen.add(name);b=batches[name]
   assert mesh['material']==b['material'];assert bool(nodes[name]['extras']['collides'])==b['collides'];assert nodes[name]['extras']['source_role']==b['role']
   x=mesh['triangles'];x=x+np.array(S['court_origin_native'])if row['kind']=='authored'else x
   u=mesh['uv'][mesh['indices']];matrix=nodes[name]['world_matrix'];n=(mesh['normals']@np.linalg.inv(matrix[:3,:3]))[mesh['indices']];n/=np.linalg.norm(n,axis=2)[:,:,None]
   ex=expected[name+'_xyz'];eu=expected[name+'_uv'].astype(np.float32).astype(float);en=expected[name+'_normal'];assert len(x)==len(ex)==b['triangles']
   if np.max(abs(x-ex))>1e-4:x,u,n=canonical(x,u,n);ex,eu,en=canonical(ex,eu,en)
   pe=float(np.max(abs(x-ex)));ue=float(np.max(abs(u-eu)));ne=float(np.max(abs(n-en)));cross=np.cross(x[:,1]-x[:,0],x[:,2]-x[:,0]);zero=int((np.linalg.norm(cross,axis=1)<1e-12).sum());opposed=int((np.einsum('ij,ij->i',cross,n.mean(1))< -1e-10).sum())
   rec={'batch':name,'kind':row['kind'],'triangles':len(x),'position_error_m':pe,'uv_error':ue,'normal_error':ne,'degenerate':zero,'opposed':opposed};records.append(rec)
   if pe>1e-4 or ue>1e-6 or ne>2e-4 or zero or opposed:errors.append(rec)
 assert seen==set(batches)and defs==set(plan['expected_definitions'])
 assert materials_seen==set(S['material_expectations'])
 assert {r['packed_sha256']for r in S['used_material_images']}<=images_seen
 assert len({r['id']for r in S['instances']})==24 and {r['id']for r in S['instances']}=={r['id']for r in plan['placements']}
 assert sum(r['collides']for r in S['instances'])==3
 assert len({r['semantic_id']for r in S['source_semantic_triangle_counts']if r['kind']=='authored'})==157
 assert len({(r['definition'],r['semantic_id'])for r in S['source_semantic_triangle_counts']if r['kind']=='prototype'})==120
 for instance in S['instances']:
  restored=np.array(instance['court_local_matrix']);restored[:3,3]+=np.array(S['court_origin_native']);assert close(restored,instance['native_matrix'],1e-7)
 for p,h in S['protected_input_sha256'].items():assert sha(p)==h
 report={'status':'PASS_SOURCE_BINARY_EQUIVALENCE_ONLY'if not errors else'FAIL_SOURCE_BINARY_EQUIVALENCE','passed':not errors,'source_sha256':S['source_sha256'],'source_unchanged':True,'batches':records,'errors':errors,'authored_meshes':157,'retained_definition_meshes':120,'placements':24,'definitions':4,'root_translation_accounted':S['court_origin_native'],'materials':len(materials_seen),'embedded_images':len(images_seen),'pending':['Actual Godot LOD0 and material interpretation','Independent physics face/ray/stance/cart tests','Sibling increment preservation','Native visual acceptance and six-species reach'],'engine_run':False}
 out=E/'INDEPENDENT_EXPORT_QA.json'
 with out.open('x')as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in report.items()if k!='batches'}));assert not errors
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.check:check()
 else:print('PREPARED_NOT_RUN: --check verifies packed_export001 independently; no engines')
