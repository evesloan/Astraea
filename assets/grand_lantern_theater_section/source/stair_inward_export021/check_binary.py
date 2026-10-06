"""Independent pure binary/source array, hierarchy, shader, image and ray checks. No engine."""
import sys,json,collections,math
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from job_common import *
import numpy as np
sys.path.insert(0,str(R/'dependencies'))
import proven_glb_checks as proven
from geometry_review import Query,glb

def arrays(row):return {k:np.asarray(row[k],dtype=float)for k in ['positions','local_positions','normals','uvs']}
def storage_signature(row,source=False):
 p=np.asarray(row['local_positions'],dtype=float);uv=np.asarray(row['uvs'],dtype=float)
 if source:uv=uv.astype(np.float32).astype(float)
 out=[]
 for xyz,uvs in zip(p,uv):
  corners=[tuple(x)+tuple(u)for x,u in zip(xyz,uvs)]
  out.append(min(tuple(v for point in corners[i:]+corners[:i]for v in point)for i in range(3)))
 return collections.Counter(out)
def check_storage(expected,actual):
 assert storage_signature(expected,True)==storage_signature(actual), 'Local position/UV storage or cyclic winding changed'
 return proven.match_triangles(arrays(expected),arrays(actual),check_local=True)
def main():
 verify_pins();assert not QA.exists();snapshot=read(SNAPSHOT);receipt=read(EXPORT_RECEIPT)
 assert snapshot['source_sha256']==receipt['source_sha256']==SOURCE_SHA and sha(SNAPSHOT)==receipt['snapshot_sha256']and sha(GLB)==receipt['glb_sha256']
 decoded=proven.decode(GLB);doc=decoded['doc'];nodes=decoded['nodes'];sources={o['name']:o for o in snapshot['objects']};roots={r['name']:r for r in snapshot['export_roots']}
 assert len(nodes)==40 and set(nodes)==set(sources)|set(roots);assert len(decoded['primitives'])==24 and len(doc['meshes'])==24
 assert not any(k in doc.get('extensionsUsed',[])for k in ['KHR_lights_punctual','EXT_mesh_gpu_instancing'])and 'KHR_lights_punctual'not in doc.get('extensions',{})
 assert not any(n.get('camera')is not None or 'KHR_lights_punctual'in n.get('extensions',{})for n in doc['nodes'])
 assert {n['name']for n in nodes.values()if n['parent']is None}==set(roots)
 root_by_mesh={m:r['name']for r in roots.values()for m in r['mesh_children']};mesh_reports=[];material_reports={};markers=[]
 for name,root in roots.items():
  node=nodes[name];assert node['mesh']is None and node['parent']is None and np.array_equal(node['matrix'],np.asarray(root['world_matrix_godot']))
  proven.compare_properties(root['extras'],node['extras'],name)
  assert {n['name']for n in nodes.values()if n['parent']==name}==set(root['mesh_children'])
 for name,source in sources.items():
  node=nodes[name];proven.compare_properties(source['extras'],node['extras'],name);origin_error=proven.compare_matrix(source,node)
  if source['type']=='MESH':
   assert node['parent']==root_by_mesh[name]and len(node['primitives'])==1
   assert np.array_equal(node['matrix'],np.asarray(source['world_matrix_godot'])),'Mesh origin altered'
   primitive=node['primitives'][0];assert primitive['triangles']==source['triangles'];result=check_storage(source,primitive)
   positions=np.asarray(primitive['positions']);normal=np.asarray(primitive['normals']);cr=np.cross(positions[:,1]-positions[:,0],positions[:,2]-positions[:,0]);assert np.linalg.norm(cr,axis=1).min()>1e-10 and np.all(np.einsum('ij,ij->i',cr,normal.mean(1))>0)
   base=positions[0,0];volume=float(np.einsum('ij,ij->i',positions[:,0]-base,np.cross(positions[:,1]-base,positions[:,2]-base)).sum()/6);assert volume>0
   assert max(abs(float(x))for t in primitive['local_positions']for point in t for x in point)<3
   key=(source['material'],primitive['material'])
   if key not in material_reports:material_reports[key]=proven.material_check(snapshot['materials'][source['material']],primitive['material'],decoded)
   mesh_reports.append({'name':name,**result,'positive_volume_m3':volume,'world_origin_error_m':origin_error,'exact_cyclic_local_position_and_uv_storage':True})
  else:
   assert node['mesh']is None and node['parent']==source['parent']and node['parent'].endswith('_LENS')
   local=np.linalg.inv(nodes[node['parent']]['matrix'])@node['matrix'];expected=np.asarray(source['local_matrix_godot']);assert np.max(abs(local-expected))<1e-10
   assert source['extras']['energy_unset_until_native_trial']and not source['extras']['runtime_light_installed']
   markers.append({'name':name,'parent_lens':node['parent'],'world_origin_error_m':origin_error,'local_transform_error':float(np.max(abs(local-expected))),'world_position':node['matrix'][:3,3].tolist()})
 assert len(mesh_reports)==24 and len(markers)==8 and sum(r['triangles']for r in mesh_reports)==416
 assert len(material_reports)==len(doc['materials'])==2 and len(decoded['images'])==2
 expected_images={node['image']['packed_sha256']for m in snapshot['materials'].values()for node in m['nodes']if 'image'in node}
 assert {i['sha256']for i in decoded['images']}==expected_images
 # Recheck the exported geometry and attachment coordinates against the retained
 # static triangles. Preserve the known corner occlusions instead of hiding them.
 actual=read(S/'REOPENED_GEOMETRY.json');static=glb(P/'source/firstpass_003/exports_run005/AST-CUL-005_static_003.glb');retainedq=Query(static['meshes'])
 newq=Query([{'node':p['node'],'primitive':p['primitive'],'triangles':p['positions']}for p in decoded['primitives']]);ray_rows=[];corner_counts=collections.Counter();optical=[]
 for fixture in actual['fixtures']:
  source=nodes[fixture['attachment_empty']]['matrix'][:3,3];lens=next(n for n in fixture['mesh_names']if n.endswith('_LENS'));lensq=Query([{'node':p['node'],'primitive':p['primitive'],'triangles':p['positions']}for p in nodes[lens]['primitives']]);exit_hits=lensq.rays(source,source+[.03,0,0]);assert exit_hits and abs(exit_hits[0]['distance_m']-.004)<1e-5
  optical.append({'flight':fixture['flight'],'lens_to_source_m':exit_hits[0]['distance_m']})
  for sample in fixture['samples']:
   v=np.asarray(actual['actual_source_references'][sample['tread']]['vertices_world'][:4]);targets=[v.mean(0)]+list(v)
   for index,target in enumerate(targets):
    target=target+[0,.05,0];hits=retainedq.rays(source,target);newhits=newq.rays(source,target);assert not newhits,('Exported channel occludes tread receiver',fixture['flight'],sample['tread'],index)
    if index==0:assert not hits,('Exported source center ray blocked',fixture['flight'],sample['tread']);kind='clear_center'
    elif not hits:kind='clear_corner'
    elif hits[0]['distance_m']<float(np.linalg.norm(target-source))-.0001:kind='existing_geometry_before_receiver'
    else:kind='existing_shared_edge_endpoint_only'
    corner_counts[kind]+=1;ray_rows.append({'fixture':fixture['flight'],'tread':sample['tread'],'sample':'center'if index==0 else'corner_'+str(index),'result':kind,'new_fixture_hits':0})
 assert corner_counts=={'clear_center':90,'clear_corner':180,'existing_geometry_before_receiver':62,'existing_shared_edge_endpoint_only':118},dict(corner_counts)
 verify_pins();report={'status':'PASS_INDEPENDENT_BINARY_EQUIVALENCE_WITH_RETAINED_CORNER_LIMIT','source_sha256':SOURCE_SHA,'snapshot_sha256':sha(SNAPSHOT),'glb_sha256':sha(GLB),'source_unchanged':True,'mesh_count':24,'attachment_count':8,'grouping_roots':8,'node_count':40,'triangles':416,'new_light_count':0,'mesh_checks':mesh_reports,'source_attachment_checks':markers,'material_checks':list(material_reports.values()),'embedded_images':decoded['images'],'binary_lens_exits':optical,'ray_result_counts':dict(corner_counts),'ray_checks':ray_rows,'maximum_position_error_m':max(r['max_position_deviation_m']for r in mesh_reports),'maximum_normal_error':max(r['max_normal_deviation']for r in mesh_reports),'position_limit_m':proven.POSITION_LIMIT,'normal_limit':proven.NORMAL_LIMIT,'exact_local_positions_and_representable_UVs_required':True,'native_import_or_illumination_proven':False,'runtime_installed':False,'retained_source_geometry_qa_sha256':sha(S/'SOURCE_GEOMETRY_QA.json'),'retained_negative_corner_qa_sha256':sha(S/'TREAD_CORNERS_QA.json')};write_new(QA,report);print(report['status'],sha(QA))
if __name__=='__main__':main()
