"""Independently scope/hash-check completed source-only executions without duplicate builds."""
from pathlib import Path
import json,hashlib,zipfile,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
common={'standards/materials.py','materials/material_manifest.json'}|{'materials/'+v['base_color_file']for v in json.loads((ROOT/'materials/material_manifest.json').read_text())['materials'].values()}
botanical={'standards/botanical_materials.py','materials/botanical/manifest.json'}|{'materials/botanical/'+v['file']for v in json.loads((ROOT/'materials/botanical/manifest.json').read_text())['materials'].values()}
rows=[]
for family in ['salon_threshold','salon_edges']:
 base=ROOT/'assets'/family;qa=base/'qa';gp=base/'source'/('build_'+family+'.py');expected=common|{str(gp.relative_to(ROOT))}|(botanical if family=='salon_edges'else set());dep=base/'dependency_manifest.json';d=json.loads(dep.read_text());rp=qa/'source_only_rebuild.json';r=json.loads(rp.read_text());log=qa/'source_only_rebuild.log';text=log.read_text()
 if family=='salon_threshold':
  inputs=d['unchanged_shared_dependencies']+d['production_generators'];actual={x['path']for x in inputs};assert actual==expected
  for x in inputs:assert sha(ROOT/x['path'])==x['sha256']
  archive=qa/'salon_threshold_source_only.zip';assert sha(archive)==r['source_package_sha256']
  with zipfile.ZipFile(archive)as z:
   assert z.testzip()is None and set(z.namelist())==expected
   for x in expected:assert hashlib.sha256(z.read(x)).hexdigest()==sha(ROOT/x)
  assert r['status']=='PASS' and r['package_contains_outputs']is False and r['package_file_count']==len(expected)
  runner=qa/'rebuild_source_only.py';code=runner.read_text();assert "assert not list(SANDBOX.rglob('*.glb'))"in code and "p.returncode==0"in code and "cwd='/tmp'"in code
  extra={'input_only_archive':bind(archive),'zip_crc_pass':True,'all_archive_members_current':True,'unrelated_cwd_exercised':'/tmp'}
 else:
  actual={x['path_from_catalogue_root']for x in r['input_files']};assert actual==expected==set(r['pre_run_files'])
  for x in r['input_files']:assert sha(ROOT/x['path_from_catalogue_root'])==x['sha256']
  dex={x['path_from_catalogue_root']for x in d['external_input_files']};assert dex==common|botanical
  for x in d['external_input_files']:assert sha(ROOT/x['path_from_catalogue_root'])==x['sha256']
  assert r['all_passed'] and r['process_exit_code']==0
  runner=qa/'source_only_rebuild.py';code=runner.read_text();assert 'TemporaryDirectory'in code and 'pre_run_files'in code
  extra={'pre_run_file_list_exactly_input_only':True,'process_exit_code':r['process_exit_code']}
 saved=re.findall(r'Saved "(AST-SAL-\d+\.blend)"',text);assert len(saved)==3
 exports=[]
 for a in r['assets']:
  current=base/'exports'/(a['catalogue_id']+'.glb');digest=sha(current);assert digest==a['original_glb_sha256']==a['rebuilt_glb_sha256'];exports.append(bind(current))
 assert len(exports)==3 and text.count('Finished glTF 2.0 export')==3
 rows.append({'family':family,'passed':True,'receipt':bind(rp),'runner':bind(runner),'log':bind(log),'dependency_manifest':bind(dep),'production_inputs':[bind(ROOT/p)for p in sorted(expected)],'input_scope_exactly_matches_actual_helper_reads':True,'unused_material_inputs_included':True,'fresh_editable_source_saves_observed':saved,'byte_identical_exports':exports,'runtime_external_asset_dependencies':[],'no_reviewer_duplicate_build':True,**extra})
res={'passed':True,'families':rows,'byte_identical_glbs':sum(len(x['byte_identical_exports'])for x in rows),'scope':'Parent coordinated author source-only executions. Reviewer read runners/logs, reconstructed complete input closure from actual material-helper loops, verified all current hashes and threshold input archive, and checked exact regenerated/current GLB hashes. No duplicate build.','limits':['Execution is evidenced by completed scripts/logs and receipts; deleted temporary output trees are not retained. All six GLB byte hashes match, not merely rounded geometry.','Editable source files are regenerated and save logs observed; byte equality of Blender save files is not claimed.','This source-only component restoration does not restore the missing game or prove runtime performance.']}
(OUT/'independent_rebuild_receipts.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'passed':True,'input_counts':[len(x['production_inputs'])for x in rows],'byte_identical_glbs':res['byte_identical_glbs']},indent=2))
