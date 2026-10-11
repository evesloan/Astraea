from pathlib import Path
import json,hashlib,subprocess
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
P=json.load(open(W/'PLAN.json'));C=json.load(open(R/'CHECKPOINT.json'));assert not P['active'];assert P==json.load(open(R/'Game/data/architecture/STAR_ATLAS_D17_STANDARD_BATCH.json'))
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();assert head==P['base_commit']=='bc731d6d6d54bb2595331ee2f4368558d4d24fda'
checked=0
for name,p in C['projects'].items():
 for f,h in p['files'].items():assert sha(R/p['prefix']/f)==h,f;checked+=1
for f,h in P['protected_native_exports'].items():assert sha(R/f)==h,f
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f,h in P['model_pins'].items():assert sha(R/'Game/assets/models'/f)==h,f
q=P['structure'];assert sha(W/q['native'])==q['native_sha256'];assert sha(W/q['export'])==q['export_sha256'];assert q['fresh_native_repeat_identical']
a=json.load(open(W/'EXACT_NATIVE_AUDIT.json'));c=json.load(open(R/'Game/artifacts/star_atlas_d17_standard_batch_sealed.json'));assert a['status']==c['status']=='PASS';assert a['checks']==1617 and c['checks']==5391;assert len(c['walks'])==153 and c['moving_leaf_samples']==135;assert len(c['bearings'])==135 and all(v['pass']for v in c['bearings']);assert c['model_pins']==P['model_pins'];assert len(P['rooms'])==9;assert sum(len(r['allocation']['proposed_rest_slot_ids'])for r in P['rooms'])==18
assert sha(R/'Game/artifacts/star_atlas_d17_standard_batch_native.json')==P['native_audit_sha256']
for f in ['NATIVE_AUDIT002.log','IMPORT002.log','SEALED002.log','SOURCE_VIEW001.log']:assert 'SCRIPT ERROR:'not in(W/f).read_text()and'ERROR:'not in(W/f).read_text(),f
assert json.load(open(W/'SOURCE_PHOTO_RECEIPT.json'))['status']=='PASS'
assert not [q for q in subprocess.check_output(['ps','-eo','comm'],text=True).splitlines()if q in ['godot','blender']]
report={'status':'PASS_SEALED_SOURCE_BASELINE_INTEGRITY_NOT_GIT_PUBLICATION_OR_PRODUCTION','base_commit':head,'baseline_files_byte_identical':checked,'native_export_original_and_retained_revision_files_byte_identical':len(P['protected_native_exports']),'native_checks':a['checks'],'actual_main_checks':c['checks'],'route_legs':153,'moving_leaf_samples':135,'bearing_witnesses':135,'new_source_street_m2':P['new_floor_m2'],'new_unit_or_rest_allocation':False,'production_active':False,'original_ship_or_shared_floor_files_modified':False,'Git_transport_hold':True,'no_engine_running':True}
(W/'SOURCE_STAGE_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
