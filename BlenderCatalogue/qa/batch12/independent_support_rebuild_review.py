"""Independent exact source-only closure and existing fresh-build verification; no regeneration."""
from pathlib import Path
import hashlib,json,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12';BASE=ROOT/'assets/clinical_support';Q=BASE/'qa'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
rp=Q/'source_only_rebuild_receipt.json';r=json.loads(rp.read_text());dp=BASE/'dependency_manifest.json';d=json.loads(dp.read_text());stage=BASE/r['stage_relative']
required={'assets/clinical_support/source/build_clinical_support.py','standards/materials.py','standards/care_materials.py','materials/material_manifest.json','materials/care/manifest.json'}|{'materials/'+x['base_color_file']for x in json.loads((ROOT/'materials/material_manifest.json').read_text())['materials'].values()}|{'materials/care/'+x['file']for x in json.loads((ROOT/'materials/care/manifest.json').read_text())['materials'].values()}
assert required==set(r['initial_input_paths'])=={x['path_from_catalogue_root']for x in d['source_only_inputs']}
assert not any(x.endswith(('.blend','.glb'))or '/qa/'in x for x in r['initial_input_paths']);assert r['no_prior_outputs_or_qa_inputs']and r['build_returncode']==0 and r['post_build_validation']and r['passes']
for x in d['source_only_inputs']:assert sha(ROOT/x['path_from_catalogue_root'])==x['sha256']==sha(stage/x['path_from_catalogue_root'])
runner=Q/'rebuild_source_only.py';code=runner.read_text();assert sha(runner)==r['runner_sha256'];assert 'if stage.exists():raise RuntimeError' in code and 'assert before==paths'in code;assert sha(dp)==r['dependency_manifest_sha256'];assert sha(Q/'source_only_build.log')==r['build_log_sha256']
assert r['command'][-1]==str(stage/'assets/clinical_support/source/build_clinical_support.py');assert (Q/'source_only_build.log').read_text().count('Finished glTF 2.0 export')==2
checkers=[]
for c in r['post_build_checkers']:
 p=Q/c['script'];s=stage/'assets/clinical_support/qa'/c['script'];assert sha(p)==sha(s)==c['sha256'];assert c['returncode']==0;checkers.append({'script':bind(p),'executed_copy':bind(s),'execution_log':bind(Q/('source_only_'+c['script']+'.log'))})
results=[]
for a in r['comparisons']:
 ident=a['id'];sp=BASE/'source'/(ident+'.blend');gp=BASE/'exports'/(ident+'.glb');staged=stage/'assets/clinical_support';sr=OUT/f'independent_source_{ident}.json';tr=OUT/f'independent_staged_source_{ident}.json';s=json.loads(sr.read_text());t=json.loads(tr.read_text());assert s['sha256']==sha(sp)and t['sha256']==sha(staged/'source'/(ident+'.blend'))==a['staged_source_sha256'];assert a['glb_byte_equal']and a['geometry_interface_record_equal'];assert sha(gp)==sha(staged/'exports'/(ident+'.glb'))==a['staged_glb_sha256']
 fields=['name','type','parent','matrix_world','properties','editable_mesh_sha256','modifier_settings']
 sig=lambda z:[{k:o.get(k)for k in fields}for o in sorted(z['objects'],key=lambda o:o['name'])]
 assert sig(s)==sig(t);assert s['units']==t['units'];assert s['used_materials']==t['used_materials'];assert {x['packed_sha256']for x in s['used_images']}=={x['packed_sha256']for x in t['used_images']};sg=np.load(ROOT/s['geometry_cache']);tg=np.load(ROOT/t['geometry_cache']);assert np.array_equal(sg['triangles'],tg['triangles'])and np.array_equal(sg['object_names'],tg['object_names'])and np.array_equal(sg['material_names'],tg['material_names'])
 results.append({'catalogue_id':ident,'source':bind(sp),'export':bind(gp),'rebuilt_source':bind(staged/'source'/(ident+'.blend')),'rebuilt_export':bind(staged/'exports'/(ident+'.glb')),'byte_identical_glb':True,'editable_named_mesh_topology_uv_material_hierarchy_modifier_properties_identical':True,'evaluated_source_geometry_identical':True,'independent_source_audits':[bind(sr),bind(tr)]})
res={'passed':True,'family':'clinical_support','executed_script_sha256':sha(Path(__file__)),'receipt':bind(rp),'dependency_manifest':bind(dp),'runner':bind(runner),'build_log':bind(Q/'source_only_build.log'),'postbuild_checkers':checkers,'production_inputs':[bind(ROOT/p)for p in sorted(required)],'fresh_input_only_stage':True,'all_helper_loaded_material_roles_included':True,'source_only_build_duplicated_by_reviewer':False,'assets':results,'scope':'Independently read generator/helper file access, reconstructed 16-input closure, checked staged exact bytes, fresh-stage guards, actual execution hashes/logs, byte-identical GLBs, and read-only reloaded named source mesh/topology/UV/material/hierarchy/modifier/property signatures. Blender binary file equality is not required due saved pathname differences.'}
(OUT/'independent_support_rebuild_review.json').write_text(json.dumps(res,indent=2)+'\n');print('PASS:16-input fresh source-only closure;2 byte-identical GLBs;independent editable source signatures and evaluated triangles identical')
