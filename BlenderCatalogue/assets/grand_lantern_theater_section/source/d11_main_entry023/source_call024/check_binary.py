from pathlib import Path
import sys,json,struct,numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from common import *
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from geometry_review import glb,Query
pins();s=read(OUT/'REOPEN_EXPORT_RECEIPT.json');assert sha(BLEND)==s['source_sha256']and sha(GLB)==s['glb_sha256']and sha(OUT/'source_arrays.npz')==s['arrays_sha256']
g=glb(GLB);arrays=np.load(OUT/'source_arrays.npz');nodes={n['name']:n for n in g['nodes']};assert len(g['meshes'])==2 and len(nodes)==4;parts={p['node']:p for p in s['parts']};rows=[]
root=nodes['D11_MAIN_EXTERIOR_CALL_ROOT']['world_matrix'];assert np.array_equal(root[:3,:3],np.eye(3))and np.max(abs(root[:3,3]-ANCHOR))<.00001
for mesh in g['meshes']:
 name=mesh['node'];assert name in parts and len(mesh['triangles'])==parts[name]['triangles']==12 and mesh['material']==parts[name]['material']
 local=mesh['triangles']-root[:3,3];uv=mesh['uv'][mesh['indices']];normal=mesh['normals'][mesh['indices']];xyz=arrays[name+'_xyz'];expected_uv=arrays[name+'_uv'].astype(np.float32).astype(float);expected_normal=arrays[name+'_normal']
 # Two source cubes retain their triangle order. Fail rather than invent a relaxed matcher.
 pe=float(abs(local-xyz).max());ue=float(abs(uv-expected_uv).max());ne=float(abs(normal-expected_normal).max());assert pe<1e-7 and ue<1e-7 and ne<2e-4,(name,pe,ue,ne)
 cross=np.cross(local[:,1]-local[:,0],local[:,2]-local[:,0]);assert np.all(np.linalg.norm(cross,axis=1)>1e-12)and np.all(np.einsum('ij,ij->i',cross,normal.mean(1))>0)
 rows.append({'node':name,'triangles':12,'position_error_m':pe,'uv_storage_error':ue,'normal_error':ne,'bounds_native':[mesh['triangles'].min((0,1)).tolist(),mesh['triangles'].max((0,1)).tolist()]})
raw=GLB.read_bytes();chunks={};o=12
while o<len(raw):size,kind=struct.unpack_from('<II',raw,o);chunks[kind]=raw[o+8:o+8+size];o+=8+size
images=[]
for image in g['doc'].get('images',[]):
 view=g['doc']['bufferViews'][image['bufferView']];data=chunks[0x004e4942][view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];images.append(hashlib.sha256(data).hexdigest())
assert set(images)==set(read(OUT/'SOURCE_EXPECTED.json')['snapshot']['packed_images'].values())
for material in g['doc']['materials']:
 expected=s['material_expectations'][material['name']];pbr=material.get('pbrMetallicRoughness',{});assert abs(pbr.get('roughnessFactor',1)-expected['roughness'])<1e-6 and abs(pbr.get('metallicFactor',1)-expected['metallic'])<1e-6;assert np.max(abs(np.array(pbr.get('baseColorFactor',[1,1,1,1]))-expected['base_color']))<1e-6
 emission=np.array(material.get('emissiveFactor',[0,0,0]))*material.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1);assert np.max(abs(emission-np.array(expected['emission_color'])*expected['emission_strength']))<1e-6
 if expected['image_sha256']:assert images[g['doc']['textures'][pbr['baseColorTexture']['index']]['source']]==expected['image_sha256']
 else:assert'baseColorTexture'not in pbr
assert len(g['doc']['materials'])==2 and not g['doc'].get('animations')and'KHR_lights_punctual'not in g['doc'].get('extensions',{})
static=glb(Path('/workspace/shared/astraea-godot-production-20261003/assets/models/AST-CUL-005_static_003.glb'));bridge=glb(Path('/workspace/shared/astraea-godot-production-20261003/assets/models/AST-CUL-005_bridge_002.glb'));q=Query(static['meshes']+bridge['meshes'])
for row in rows:assert not q.prism_hits([*row['bounds_native'][0],*row['bounds_native'][1]],tolerance=.00001),row['node']
marker=nodes['D11_MAIN_EXTERIOR_CALL_TARGET'];assert marker['extras']['source_id']=='THEATER_D11_MAIN_EXTERIOR_CALL';eye=np.array([-32.8,71.15,-128.05]);target=marker['world_matrix'][:3,3];assert np.linalg.norm(target-eye)<2.5 and not q.rays(eye,target)
pins();write_new(OUT/'BINARY_QA.json',{'status':'PASS_ACTUAL_SOURCE_EXPORT_AND_CONTROL_FIT','source_sha256':sha(BLEND),'retained_source_sha256':SOURCE_SHA,'glb_sha256':sha(GLB),'meshes':2,'triangles':24,'rows':rows,'packed_images':images,'actual_control_target_native':target.tolist(),'actual_source_approach_distance_m':float(np.linalg.norm(target-eye)),'material_factors_checked':True,'original_source_unchanged':True,'runtime_or_native_input_acceptance':False,'fixture_scope':'Exterior metal plate and opal lens only; original wall, door, floor and interior control remain unchanged.'});print('PASS_BINARY_CONTROL_FIT',sha(GLB))
