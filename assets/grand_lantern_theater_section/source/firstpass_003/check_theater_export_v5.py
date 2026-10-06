"""Independent source-to-binary GLB equality. No Blender or Game writes."""
from pathlib import Path
import sys,json,hashlib,struct
import numpy as np
R=Path(__file__).resolve().parent;E=R/'exports_run005';sys.path.insert(0,'/workspace/scratch/375c2e438292/engineering-dense-bays/qa');from geometry_review import glb
S=json.loads((E/'EXPORT_RECEIPT.json').read_text());expected=np.load(E/'source_triangle_attributes.npz');batches={b['name']:b for b in S['batches']};errors=[];records=[];seen=set();image_hashes=set();material_names=set();all_nodes={}
def canonical(x,u,n):
 # Keep cyclic winding. Sort with a coarse key only to match triangles; the
 # final direct position/UV/normal tolerances remain strict for every corner.
 key=np.round(x,3)
 choose=np.array([min(range(3),key=lambda i:tuple(row[i]))for row in key]);order=(choose[:,None]+np.arange(3))%3;idx=np.arange(len(x))[:,None]
 x=x[idx,order];u=u[idx,order];n=n[idx,order]
 keys=np.round(x,3).reshape(-1,9);sort=np.lexsort(tuple(keys[:,i]for i in range(8,-1,-1)))
 return x[sort],u[sort],n[sort]
for row in S['export_records']:
 p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];g=glb(p);nodes={n['name']:n for n in g['nodes']};all_nodes.update(nodes)
 blob=p.read_bytes();off=12;binary=None
 while off<len(blob):
  length,kind=struct.unpack_from('<II',blob,off)
  if kind==0x004e4942:binary=blob[off+8:off+8+length]
  off+=8+length
 for im in g['doc'].get('images',[]):
  assert 'bufferView'in im
  v=g['doc']['bufferViews'][im['bufferView']];b=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];image_hashes.add(hashlib.sha256(b).hexdigest())
 for mesh in g['meshes']:
  name=mesh['node'];assert name in batches and name not in seen,(name,'duplicate/missing');seen.add(name);spec=batches[name];material_names.add(mesh['material']);assert mesh['material']==spec['material'],name
  x=mesh['triangles'];u=mesh['uv'][mesh['indices']];matrix=nodes[name]['world_matrix'];n=(mesh['normals']@np.linalg.inv(matrix[:3,:3]))[mesh['indices']];n/=np.linalg.norm(n,axis=2)[:,:,None]
  ex=expected[name+'_xyz'];eu=expected[name+'_uv'];en=expected[name+'_normal'];assert len(x)==len(ex)==spec['triangles']
  # glTF texture origin conversion is rounded once to float32 on export.
  eu_storage=eu.astype(np.float32).astype(float)
  if np.max(abs(x-ex))>1e-4:x,u,n=canonical(x,u,n);ex,eu_storage,en=canonical(ex,eu_storage,en)
  pe=float(np.max(abs(x-ex)));ue=float(np.max(abs(u-eu_storage)));ne=float(np.max(abs(n-en)));cr=np.cross(x[:,1]-x[:,0],x[:,2]-x[:,0]);zero=int((np.linalg.norm(cr,axis=1)<1e-12).sum());opposed=int((np.einsum('ij,ij->i',cr,n.mean(1))< -1e-10).sum())
  ok=pe<=1e-4 and ue<=1e-6 and ne<=2e-4 and zero==0 and opposed==0
  if not ok:errors.append({'batch':name,'position_error_m':pe,'uv_error':ue,'normal_error':ne,'degenerate':zero,'opposed_normals':opposed})
  records.append({'batch':name,'kind':row['kind'],'triangles':len(x),'position_error_m':pe,'uv_error':ue,'normal_error':ne})
assert seen==set(batches),(len(seen),len(batches))
source_images={r['packed_sha256']for r in S['used_material_images']};missing_images=source_images-image_hashes
if missing_images:errors.append({'source_images_not_identical_in_export':sorted(missing_images)})
motion_nodes=[n for n in all_nodes.values()if 'motion_contract'in n['extras']];assert len(motion_nodes)==39
motion=[]
for n in motion_nodes:
 spec=json.loads(n['extras']['motion_contract']);expected_pos=np.array(spec['closed_root_world']);actual=n['world_matrix'][:3,3];err=float(abs(actual-expected_pos).max());motion.append({'id':spec['id'],'pivot_error_m':err});
 if err>1e-4:errors.append({'motion_pivot':spec['id'],'error_m':err})
assert len(set(m['id']for m in motion))==39
assert len([i for i in S['instances']if i['audience_chair']])==2200
assert len({i['id']for i in S['instances']})==len(S['instances'])
report={'passed':not errors,'source_sha256':S['source_sha256'],'source_unchanged':hashlib.sha256(Path(S['source']).read_bytes()).hexdigest()==S['source_sha256'],'export_count':len(S['export_records']),'batch_count':len(batches),'triangles':sum(r['triangles']for r in records),'triangles_by_kind':{k:sum(r['triangles']for r in records if r['kind']==k)for k in ['static','moving','prototype']},'maximum_position_error_m':max(r['position_error_m']for r in records),'maximum_uv_storage_error':max(r['uv_error']for r in records),'maximum_normal_error':max(r['normal_error']for r in records),'embedded_image_unique_hashes':len(image_hashes),'source_image_unique_hashes':len(source_images),'source_packed_image_bytes_preserved':not missing_images,'source_chair_instances':2200,'unique_instance_ids':len(S['instances']),'motion_groups':motion,'batch_records':records,'errors':errors,'scope':'Strict binary source/export attribute/material-image equality, not imported collision, runtime traversal, light selection or final art acceptance'}
out=E/'INDEPENDENT_EXPORT_QA.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['batch_records','motion_groups']},indent=2));assert report['passed']and report['source_unchanged']
