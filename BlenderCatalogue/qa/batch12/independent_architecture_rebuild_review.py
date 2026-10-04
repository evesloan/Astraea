"""Read-only independent check of the completed architecture fresh source generation."""
from pathlib import Path
import hashlib,json,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12';BASE=ROOT/'assets/clinical_architecture';Q=BASE/'qa'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
rp=Q/'source_only_rebuild_receipt.json';r=json.loads(rp.read_text());stage=BASE/r['stage'];sb=stage/'assets/clinical_architecture'
shared={'materials/'+x['base_color_file']for x in json.loads((ROOT/'materials/material_manifest.json').read_text())['materials'].values()}
required=shared|{'standards/materials.py','standards/care_materials.py','materials/material_manifest.json','materials/care/source/generate_care_materials.py','assets/clinical_architecture/source/build_clinical_architecture.py','assets/clinical_architecture/source/make_clinical_textures.py'}
assert set(r['initial_files'])==required=={x['path']for x in r['inputs']};assert not any(x.endswith(('.blend','.glb'))or'/qa/'in x or'/textures/'in x for x in r['initial_files'])
for x in r['inputs']:assert sha(ROOT/x['path'])==sha(stage/x['path'])==x['sha256']
runner=Q/'source_only_rebuild.py';assert sha(runner)==r['runner_sha256'];code=runner.read_text();assert "assert not STAGE.exists()"in code and "assert not any(p.endswith(('.blend','.glb'))"in code
runs=[]
for i,c in enumerate(r['executed_commands']):
 p=Path(c['argv'][-1]);assert p.is_relative_to(stage);assert sha(p)==sha(ROOT/p.relative_to(stage));log=Q/f'source_only_step_{i}.log';assert sha(log)==c['log_sha256']and c['exit_code']==0;runs.append({'argv':c['argv'],'executed_script':bind(p),'log':bind(log),'exit_code':c['exit_code']})
assert (Q/'source_only_step_2.log').read_text().count('Finished glTF 2.0 export')==3
assert '--only'not in r['executed_commands'][2]['argv']
for x in r['glb_binary_comparisons']+r['interface_and_collision_comparisons']:assert x['byte_identical']and sha(BASE/x['file'])==sha(sb/x['file'])==x['original_sha256']==x['rebuilt_sha256']
for x in r['fresh_texture_comparisons']:assert x['byte_identical']and sha(ROOT/x['source'])==sha(stage/x['source'])==x['original_sha256']==x['rebuilt_sha256']
for name in ['materials/care/manifest.json','assets/clinical_architecture/material_manifest.json']:assert sha(ROOT/name)==sha(stage/name)
results=[]
for ident in ['AST-MED-001','AST-MED-002']:
 sp=BASE/'source'/(ident+'.blend');gp=BASE/'exports'/(ident+'.glb');sr=OUT/f'independent_source_{ident}.json';tr=OUT/f'independent_staged_source_{ident}.json';s=json.loads(sr.read_text());t=json.loads(tr.read_text());assert s['sha256']==sha(sp)and t['sha256']==sha(sb/'source'/(ident+'.blend'))
 fields=['name','type','parent','matrix_world','properties','editable_mesh_sha256','modifier_settings'];sig=lambda z:[{k:o.get(k)for k in fields}for o in sorted(z['objects'],key=lambda o:o['name'])];assert sig(s)==sig(t);assert s['units']==t['units']and s['used_materials']==t['used_materials'];assert {x['packed_sha256']for x in s['used_images']}=={x['packed_sha256']for x in t['used_images']};sg=np.load(ROOT/s['geometry_cache']);tg=np.load(ROOT/t['geometry_cache']);assert all(np.array_equal(sg[key],tg[key])for key in ['triangles','object_names','material_names'])
 results.append({'catalogue_id':ident,'source':bind(sp),'export':bind(gp),'rebuilt_source':bind(sb/'source'/(ident+'.blend')),'rebuilt_export':bind(sb/'exports'/(ident+'.glb')),'editable_named_mesh_topology_uv_material_hierarchy_modifier_properties_identical':True,'evaluated_source_geometry_identical':True,'independent_source_audits':[bind(sr),bind(tr)]})
a=json.loads((OUT/'independent_source_states_AST-MED-001.json').read_text());b=json.loads((OUT/'independent_staged_source_states_AST-MED-001.json').read_text());assert a['source_sha256']==sha(BASE/'source/AST-MED-001.blend')and b['source_sha256']==sha(sb/'source/AST-MED-001.blend');assert a['actions']==b['actions'];assert len(a['states'])==len(b['states'])
for x,y in zip(a['states'],b['states']):
 assert x['frame']==y['frame']and x['objects']==y['objects'];gx=np.load(ROOT/x['geometry_cache']);gy=np.load(ROOT/y['geometry_cache']);assert all(np.array_equal(gx[k],gy[k])for k in ['triangles','object_names','material_names'])
intermediate={'materials/care/manifest.json','assets/clinical_architecture/material_manifest.json'}|{x['source']for x in r['fresh_texture_comparisons']}
dep_path=BASE/'dependency_manifest.json';dep=json.loads(dep_path.read_text());assert {x['path_from_catalogue']for x in dep['source_inputs']}==required|intermediate
for x in dep['source_inputs']:assert sha(ROOT/x['path_from_catalogue'])==x['sha256']
execution_path=Q/'final_execution_bindings.json';execution=json.loads(execution_path.read_text())
for section in ['canonical_visual_files','executed_qa_scripts','qa_receipts']:
 for p,h in execution[section].items():assert sha(BASE/p)==h
res={'dependency_manifest':bind(dep_path),'author_final_execution_bindings':bind(execution_path),'passed':True,'family':'clinical_architecture','executed_script_sha256':sha(Path(__file__)),'receipt':bind(rp),'runner':bind(runner),'executions':runs,'source_only_seed_inputs':[bind(ROOT/p)for p in sorted(required)],'generated_material_intermediate_inputs':[bind(ROOT/p)for p in sorted(intermediate)],'production_inputs':[bind(ROOT/p)for p in sorted(required|intermediate)],'fresh_input_only_stage':True,'full_default_build_without_previous_output_reads':True,'maintenance_only_mode_limit':'The optional --only path reads current metadata to retain an unchanged sibling; this path is not used by the proven fresh default source-only build.','all_helper_loaded_material_roles_included':True,'source_only_build_duplicated_by_reviewer':False,'byte_identical_glb_count':3,'source_motion_actions_and_evaluated_states_identical':True,'assets':results,'scope':'14-input fresh stage regenerates5 maps,2 material manifests,2 editable sources and3 GLB states. Independently verified actual staged/current hashes, scripts/logs, byte-identical GLBs/interfaces/collisions and named editable mesh/topology/UV/material/hierarchy/modifier/property and motion-state signatures. Blender binary equality is not required due saved pathname differences.'}
(OUT/'independent_architecture_rebuild_review.json').write_text(json.dumps(res,indent=2)+'\n');print('PASS:14 source seeds,7 generated material intermediates,3 byte-identical GLBs;editable sources and motion states independently identical')
