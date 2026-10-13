from pathlib import Path
import subprocess,json,hashlib
C=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';P=C/'g3_full_clinical_receiving';S='/workspace/astraea-readonly-interface-review-20261012/remote_only_20261012T000749Z.git';rev='6f2d0da67429ea940edf7011348ec08a346f37db';sha=lambda b:hashlib.sha256(b).hexdigest();d=json.loads((P/'CLINICAL_SOURCE.json').read_text());T=P/'import/Game';T.mkdir(parents=True,exist_ok=True);rows=[]
def fetch(path,dest,expected=None):
 b=subprocess.check_output(['git','-C',S,'show',rev+':'+path]);h=sha(b)
 if expected is not None:assert h==expected,path
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);rows.append({'path':path,'bytes':len(b),'sha256':h,'independent_commit':rev});return b
for name,h in d['model_pins'].items():fetch('Game/assets/models/group3_clinical_full_20261011/'+name,T/'assets/models/group3_clinical_full_20261011'/name,h)
for rel in ['data/architecture/group3_clinical_full_20261011/CLINICAL.json','scripts/group3_clinical_full_20261011/physical_package.gd']:
 fetch('Game/'+rel,T/rel)
base='BlenderCatalogue/assets/group3_crew_service_20261009/extensions/clinical_full_transfer_batch020/'
for name in ['AST-MED-G3-007.blend','AST-MED-G3-008.blend','AST-MED-G3-009.blend','AST-MED-G3-010.blend','CLINICAL_COMPLETE_ARCHITECTURE.json','CLINICAL_COMPLETE_MISSING_FLOOR.json','COMPLETE_CLINICAL_CONTRACT.json']:fetch(base+'source/'+name,P/'native'/name)
fetch('Game/docs/GROUP3_CLINICAL_NETWORK_20261011.md',P/'native/GROUP3_CLINICAL_NETWORK_20261011.md')
sourcepins=[];changes=[]
for path,h in d['source_pins'].items():
 b=fetch(path,P/'pinned_inputs'/path,h);current=R/path
 if path.startswith('Game/')and current.exists():
  now=sha(current.read_bytes());sourcepins.append({'path':path,'original_sha256':h,'current_sha256':now,'current_equal':now==h})
  if now!=h:changes.append(path)
(T/'project.godot').write_text('[application]\nconfig/name="Full clinical exact source import"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\nrenderer/rendering_method.mobile="gl_compatibility"\n')
p=json.loads((G/'data/architecture/group3_port2_clinical_20261011/PHYSICAL.json').read_text());old='assets/models/group3_port2_clinical_20261011/AST-MED-G3-006.glb';assert sha((G/old).read_bytes())==p['model_pins']['AST-MED-G3-006.glb']
(P/'INPUT_VERIFICATION.json').write_text(json.dumps({'status':'PASS_EXACT_FROZEN_SOURCE_INPUTS_CURRENT_PREIMAGE_REVIEW_PENDING','source_revision':rev,'files':rows,'current_source_pins':sourcepins,'declared_current_source_successor_paths_to_review':changes,'old_bounded_visual':'ShipSpace/Group3Port2ClinicalPhysical/AST-MED-G3-006','old_bounded_glb_sha256':p['model_pins']['AST-MED-G3-006.glb'],'new_model_files':4,'instantiated_physical_models':3,'new_declared_floor_m2':d['new_floor_m2'],'fixture_sources':193,'gate_or_clinical_protocol_operation':False},indent=2)+'\n');print('PASS frozen exact input files',len(rows),'current successor pins requiring review',changes)
