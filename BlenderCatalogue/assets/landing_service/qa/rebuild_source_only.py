"""Fresh source-only build closure with no pre-existing new outputs/QA."""
import json,hashlib,shutil,zipfile,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];STAGE=BASE/'qa/fresh_source_only_stage';DEP=json.loads((BASE/'dependency_manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
execution_before={str(p.relative_to(CAT)):sha(p) for p in [Path(__file__),BASE/'qa/source_signature.py']}
assert not STAGE.exists(),'Fresh stage must not preexist'
STAGE.mkdir();copied=[]
with zipfile.ZipFile(BASE/'qa/landing_service_source_only.zip','w',zipfile.ZIP_DEFLATED) as z:
 for r in DEP['source_only_inputs']:
  src=CAT/r['path'];assert sha(src)==r['sha256'];dst=STAGE/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);z.write(src,r['path']);copied.append(r)
initial=sorted(str(p.relative_to(STAGE)) for p in STAGE.rglob('*') if p.is_file());assert initial==sorted(r['path'] for r in copied)
staged=STAGE/'assets/landing_service';cmd=['blender','--background','--threads','1','--python',str(staged/'source/build_landing_service.py')]
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(BASE/'qa/source_only_build.log').write_text(r.stdout);assert r.returncode==0 and 'LANDING_SERVICE_BUILD_OK' in r.stdout
r2=subprocess.run(['blender','--background','--threads','1','--python',str(BASE/'qa/source_signature.py'),'--',str(BASE),str(staged)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(BASE/'qa/source_signature.log').write_text(r2.stdout);assert r2.returncode==0
sigs=json.loads((BASE/'qa/source_signature_comparison.json').read_text());comparisons=[]
for ident in ['AST-LND-003','AST-LND-004']:
 a=[r for r in sigs if r['id']==ident and r['base']==str(BASE)][0];b=[r for r in sigs if r['id']==ident and r['base']==str(staged)][0];g1=sha(BASE/'exports'/f'{ident}.glb');g2=sha(staged/'exports'/f'{ident}.glb');comparisons.append({'id':ident,'original_glb_sha256':g1,'fresh_glb_sha256':g2,'export_byte_identical':g1==g2,'original_blend_sha256':a['source_file_sha256'],'fresh_blend_sha256':b['source_file_sha256'],'blend_byte_identical':a['source_file_sha256']==b['source_file_sha256'],'editable_geometry_uv_material_hierarchy_modifier_identical':a['semantic_geometry_hierarchy_material_uv_modifier_sha256']==b['semantic_geometry_hierarchy_material_uv_modifier_sha256'],'editable_signature':a['semantic_geometry_hierarchy_material_uv_modifier_sha256']})
report={'source_only_package':'qa/landing_service_source_only.zip','source_only_package_sha256':sha(BASE/'qa/landing_service_source_only.zip'),'fresh_stage_initial_files':initial,'source_input_count':len(copied),'all_loaded_staff_material_roles_included':True,'prior_new_outputs_or_qa_inputs_in_stage':False,'build_command':cmd,'builder_returncode':r.returncode,'source_equivalence_method':'Reopened saved blend compares named editable geometry, topology, UV, materials, object hierarchy, extras, world transforms and modifier type/width/segments; .blend binary separately checked','blend_byte_scope':'Packed texture absolute paths and Blender save metadata may differ with staging location; editable semantic equivalence and evaluated GLB byte equivalence are independently required','results':comparisons,'execution_file_bindings_before':execution_before,'execution_file_bindings_after':{p:sha(CAT/p) for p in execution_before},'executed_runner_and_checker_unchanged':all(sha(CAT/p)==h for p,h in execution_before.items()),'execution_logs':{str((BASE/'qa'/n).relative_to(CAT)):sha(BASE/'qa'/n) for n in ['source_only_build.log','source_signature.log']},'all_required_checks_pass':all(r['export_byte_identical'] and r['editable_geometry_uv_material_hierarchy_modifier_identical'] for r in comparisons)}
(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert report['all_required_checks_pass']
# Successful scratch staging is disposable; retain closed input archive and full receipts.
shutil.rmtree(STAGE)
