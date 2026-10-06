from pathlib import Path
import sys,json,hashlib,struct
import numpy as np
R=Path(__file__).resolve().parent;E=R/'export001';sys.path.insert(0,str(R));from source_common import *
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from geometry_review import glb
s=read(E/'EXPORT_RECEIPT.json');assert sha(s['path'])==s['glb_sha256']and sha(OUT)==s['source_sha256'];assert sha(E/'source_triangle_attributes.npz')==s['witness_sha256'];expected=np.load(E/'source_triangle_attributes.npz');g=glb(s['path']);nodes={x['name']:x for x in g['nodes']};parts={x['node']:x for x in s['parts']};assert len(g['meshes'])==7 and len(parts)==7;rows=[]
def canonical(x,u,n):
 choose=np.array([min(range(3),key=lambda i:tuple(np.round(row[i],6)))for row in x]);order=(choose[:,None]+np.arange(3))%3;ix=np.arange(len(x))[:,None];x=x[ix,order];u=u[ix,order];n=n[ix,order];key=np.round(x,6).reshape(-1,9);ix=np.lexsort(tuple(key[:,i]for i in range(8,-1,-1)));return x[ix],u[ix],n[ix]
for m in g['meshes']:
 name=m['node'];assert name in parts and m['material']==parts[name]['material'];x=m['triangles'];u=m['uv'][m['indices']];n=(m['normals']@np.linalg.inv(nodes[name]['world_matrix'][:3,:3]))[m['indices']];n/=np.linalg.norm(n,axis=2)[:,:,None];ex=expected[name+'_xyz'];eu=expected[name+'_uv'];en=expected[name+'_normal'];assert len(x)==len(ex)==parts[name]['triangles']
 if np.max(abs(x-ex))>1e-6:x,u,n=canonical(x,u,n);ex,eu,en=canonical(ex,eu,en)
 pe=float(abs(x-ex).max());ue=float(abs(u-eu).max());ne=float(abs(n-en).max());c=np.cross(x[:,1]-x[:,0],x[:,2]-x[:,0]);assert pe<1e-6 and ue<1e-6 and ne<2e-4 and np.all(np.linalg.norm(c,axis=1)>1e-12)and np.all((c*n.mean(1)).sum(1)>0),(name,pe,ue,ne)
 rows.append({'node':name,'position_error_m':pe,'uv_error':ue,'normal_error':ne,'triangles':len(x)})
blob=Path(s['path']).read_bytes();chunks={};o=12
while o<len(blob):size,kind=struct.unpack_from('<II',blob,o);chunks[kind]=blob[o+8:o+8+size];o+=8+size
image_hashes=[]
for im in g['doc'].get('images',[]):
 v=g['doc']['bufferViews'][im['bufferView']];data=chunks[0x004e4942][v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];image_hashes.append(hashlib.sha256(data).hexdigest())
assert len(g['doc']['materials'])==len(s['material_expectations'])==2
for mat in g['doc']['materials']:
 src=s['material_expectations'][mat['name']];pbr=mat.get('pbrMetallicRoughness',{});assert abs(pbr.get('roughnessFactor',1)-src['roughness'])<1e-6 and abs(pbr.get('metallicFactor',1)-src['metallic'])<1e-6;assert np.max(abs(np.array(pbr.get('baseColorFactor',[1,1,1,1]))-src['base_color']))<1e-6
 emission=np.array(mat.get('emissiveFactor',[0,0,0]))*mat.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1);assert np.max(abs(emission-np.array(src['emission_color'])*src['emission_strength']))<1e-6
 if src['image_sha256']:assert image_hashes[g['doc']['textures'][pbr['baseColorTexture']['index']]['source']]==src['image_sha256']
 else:assert'baseColorTexture'not in pbr
assert len(image_hashes)==1 and len(g['nodes'])==8 and not g['doc'].get('animations')and not g['doc'].get('cameras')and'KHR_lights_punctual'not in g['doc'].get('extensions',{})
marker=nodes['CA8_BANK0_source_attachment_export'];assert np.max(abs(marker['world_matrix']-np.eye(4)))<1e-7;assert marker['extras']['source_id']=='FP2_D11_BANK_0'
report={'status':'PASS_SOURCE_BINARY_EQUIVALENCE','source_sha256':s['source_sha256'],'glb_sha256':s['glb_sha256'],'meshes':7,'triangles':sum(x['triangles']for x in rows),'materials':2,'embedded_images':image_hashes,'source_axis_metadata':marker['extras']['optical_axis_native'],'root_native_translation':s['root_native_translation'],'rows':rows,'old_batch_replacement_not_yet_tested':True,'Game_import_or_native_picture':False};write_new(E/'INDEPENDENT_EXPORT_QA.json',report);print(json.dumps(report))
