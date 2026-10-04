"""Clean source-only reproduction; QA validation is introduced only after the authoring process exits."""
from pathlib import Path
import json,hashlib,subprocess,shutil,sys,datetime
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=['assets/clinical_support/source/build_clinical_support.py','standards/materials.py','standards/care_materials.py','materials/material_manifest.json','materials/care/manifest.json']
m=json.loads((CAT/'materials/material_manifest.json').read_text())
paths +=['materials/'+v['base_color_file']for v in m['materials'].values()]
c=json.loads((CAT/'materials/care/manifest.json').read_text())
paths +=['materials/care/'+v['file']for v in c['materials'].values()]
paths=sorted(set(paths));deps=[{'path_from_catalogue_root':x,'sha256':sha(CAT/x),'bytes':(CAT/x).stat().st_size,'purpose':'Builder input; includes every material role loaded by shared helpers, even when not used in these meshes'}for x in paths]
(BASE/'dependency_manifest.json').write_text(json.dumps({'scope':'Exact external file closure for clean authoring; Python/Blender standard modules and Blender 4.3.2 are execution dependencies','source_only_inputs':deps,'generated_not_input':['source/AST-MED-003.blend','source/AST-MED-004.blend','exports/AST-MED-003.glb','exports/AST-MED-004.glb','manifest.json','marker_api.json','collision_proposals.json'],'provenance_auxiliary':['materials/care/source/generate_care_materials.py'],'qa_only_dependencies':['standards/qa_frame.py'],'source_only_does_not_read':'Existing new outputs, blend sources, QA files, renders, original game or host scenes'},indent=2)+'\n')
stage=BASE/'qa/source_only_stage/catalogue'
if stage.exists():raise RuntimeError('Stage already exists; preserve it and choose a fresh stage path before rerunning')
for x in paths:
 d=stage/x;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(CAT/x,d)
staged=stage/'assets/clinical_support';before=sorted(str(p.relative_to(stage))for p in stage.rglob('*')if p.is_file())
assert before==paths
command=['blender','--background','--threads','2','--python-exit-code','1','--python',str(staged/'source/build_clinical_support.py')]
run=subprocess.run(command,capture_output=True,text=True);log=BASE/'qa/source_only_build.log';log.write_text(run.stdout+'\n'+run.stderr)
comparisons=[]
if run.returncode==0:
 for ident in('AST-MED-003','AST-MED-004'):
  a=json.loads((BASE/(ident+'.manifest.json')).read_text());b=json.loads((staged/(ident+'.manifest.json')).read_text());keys=['bounds_blender_z_up','evaluated_triangles','semantic_parts','material_roles','physical_and_proposal_markers','joins','receiver_voids','details']
  comparisons.append({'id':ident,'glb_byte_equal':sha(BASE/a['export'])==sha(staged/b['export']),'geometry_interface_record_equal':all(a[k]==b[k]for k in keys),'staged_glb_sha256':sha(staged/b['export']),'staged_source_sha256':sha(staged/b['source']),'packed_source_hash_note':'Editable blend bytes may differ due to saved staging pathname; compared via staged reload and semantic/export signatures'})
 # Checkers are copied only after building, preserving the input-isolation proof above.
 checks=[]
 for script in('check_sources.py','validate_glb.py'):
  d=staged/'qa'/script;shutil.copy2(BASE/'qa'/script,d)
  cmd=['blender','--background','--threads','1','--python-exit-code','1','--python',str(d)]if script=='check_sources.py'else[sys.executable,str(d)]
  q=subprocess.run(cmd,capture_output=True,text=True);(BASE/'qa'/('source_only_'+script+'.log')).write_text(q.stdout+'\n'+q.stderr);checks.append({'script':script,'sha256':sha(d),'returncode':q.returncode})
 validation=json.loads((staged/'qa/glb_validation.json').read_text())['all_passed']and json.loads((staged/'qa/source_reload_checks.json').read_text())['all_passed']
else:checks=[];validation=False
receipt={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runner_sha256':sha(Path(__file__)),'dependency_manifest_sha256':sha(BASE/'dependency_manifest.json'),'stage_relative':str(stage.relative_to(BASE)),'initial_input_paths':before,'no_prior_outputs_or_qa_inputs':before==paths,'command':command,'build_returncode':run.returncode,'build_log_sha256':sha(log),'comparisons':comparisons,'post_build_checkers':checks,'post_build_validation':validation,'passes':run.returncode==0 and validation and all(q['glb_byte_equal']and q['geometry_interface_record_equal']for q in comparisons)}
(BASE/'qa/source_only_rebuild_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if not receipt['passes']:sys.exit(1)
