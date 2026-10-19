import pathlib,json,hashlib,numpy as np
R=pathlib.Path(__file__).resolve().parents[4];W=pathlib.Path(__file__).resolve().parent/'receiving_inputs';P=R/'BlenderCatalogue/assets/group3_remaining_receiving_20261019'
code=(pathlib.Path(__file__).parent/'screen_source_columns.py').read_text().split('candidates=json.load')[0]
a={'__file__':__file__};exec(code,a);b={'__file__':__file__};exec(code.replace('RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/remaining_crew_bank_source_batch015/exports/AST-CRW-G3-003.glb','BlenderCatalogue/assets/group3_remaining_receiving_20261019/exports/AST-CRW-G3-003_current_columns_r001.glb'),b)
report=json.load(open(P/'qa/COLUMN_SUCCESSOR.json'));edited={q['name']for q in report['edited_shell_meshes']};plans={q['allocation']:q['world_translation']for q in report['furniture_plans']};nodes={n['name']:(i,n)for i,n in enumerate(b['g']['nodes'])};assert len(nodes)==len(a['g']['nodes'])==len(b['g']['nodes'])
assert a['g']['materials']==b['g']['materials'];checked=0;moved=0;mesh_count=0
for i,n in enumerate(a['g']['nodes']):
 j,nn=nodes[n['name']];delta=np.zeros(3)
 if n.get('extras',{}).get('source_allocation_key')in plans and n['name'].split('__')[1]!='Shell':delta=np.array(plans[n['extras']['source_allocation_key']])
 ma=a['world'](i).copy();ma[:3,3]+=delta;assert np.max(np.abs(ma-b['world'](j)))<.0001,(n['name'],'matrix')
 checked+=1;moved+=int(np.linalg.norm(delta)>0)
 if 'mesh'not in n or n['name']in edited:continue
 aa=a['g']['meshes'][n['mesh']]['primitives'];bb=b['g']['meshes'][nn['mesh']]['primitives'];assert len(aa)==len(bb)
 for p,q in zip(aa,bb):
  assert p.get('material')==q.get('material');assert p['attributes'].keys()==q['attributes'].keys()
  for k in p['attributes']:assert np.array_equal(a['acc'](p['attributes'][k]),b['acc'](q['attributes'][k])),(n['name'],k)
  assert np.array_equal(a['acc'](p['indices']),b['acc'](q['indices']))
 mesh_count+=1
out={'status':'PASS_EXPORTED_SUCCESSOR_PRESERVATION','glb_sha256':hashlib.sha256(b['b']).hexdigest(),'exact_node_identity_count':checked,'mesh_nodes_with_exact_geometry_uv_normals_material_and_indices':mesh_count,'bounded_edited_shell_mesh_nodes':len(edited),'rigidly_translated_nodes':moved,'material_table_exact':True,'maximum_matrix_tolerance_m':.0001,'source_column_surface_penetrations':len(json.load(open(W/'SUCCESSOR_COLUMN_TRIANGLE_SCREEN.json'))['hits']),'runtime_and_visual_acceptance':False};assert out['source_column_surface_penetrations']==0
(P/'qa/INDEPENDENT_SUCCESSOR_EXPORT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
