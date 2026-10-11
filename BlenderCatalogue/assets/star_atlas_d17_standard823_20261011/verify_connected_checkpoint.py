from pathlib import Path
import json,hashlib,subprocess,sys
W=Path(__file__).resolve().parent;R=W.parents[2];phase=sys.argv[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
G=lambda *a:subprocess.check_output(['git',*a],cwd=R,text=True).strip()
head=G('rev-parse','HEAD');base=G('rev-parse','HEAD^');c=json.load(open(R/'CHECKPOINT.json'));b=json.load(open(R/'BACKUP_STATUS.json'));p=json.load(open(W/'PLAN.json'))
stem=str(R)+'-STAR-ATLAS-D17-STANDARD823-'+phase.upper()+'-';rr=json.load(open(stem+'REMOTE_VERIFICATION.json'))
assert rr['commit']==head and rr['root_tree']==G('rev-parse','HEAD^{tree}')and rr['manifest_sha256']==sha(R/'CHECKPOINT.json')==b['manifest_sha256']
assert c['base_checkpoint_commit']==b['base_checkpoint_commit']==rr['base']['commit']==base
assert c['base_root_tree']==b['base_root_tree']==rr['base']['root_tree']==G('rev-parse',base+'^{tree}')
assert c['protection']['last_verified_source_checkpoint']==b['last_verified_source_checkpoint']==rr['base']
previous=json.load(open(rr['base']['receipt']));assert previous['commit']==base and previous['root_tree']==rr['base']['root_tree']and previous['manifest_sha256']==rr['base']['manifest_sha256']
counts={};checked=0
for k,v in c['projects'].items():
 fs={f.removeprefix(v['prefix']+'/')for f in G('ls-files',v['prefix']).splitlines()};assert fs==set(v['files'])
 for f,h in v['files'].items():assert sha(R/v['prefix']/f)==h,f;checked+=1
 sig=hashlib.sha256(json.dumps(v['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert v['signature']==b['projects'][k]['signature']==sig and v['git_tree']==b['projects'][k]['git_tree']==G('rev-parse',head+':'+v['prefix']);counts[k]=len(fs)
refs={q.split()[1]:q.split()[0]for q in G('ls-remote','origin','construction/group1-tidal-d15-20261010','main','checkpoint/direct-integration-20261009','source/godot','source/blender').splitlines()}
assert refs['refs/heads/construction/group1-tidal-d15-20261010']==head
assert refs['refs/heads/main']==refs['refs/heads/checkpoint/direct-integration-20261009']=='9c301f656257ddb2d420e6680e8ed9c1f7af9337'
assert refs['refs/heads/source/godot']=='12080c25971fa38d37766b52c0835035ce5366ca'and refs['refs/heads/source/blender']=='6a7a4cfd44e8b174ddf4d3a9987cc0c29741ffbc'
protected=p['protected_native_exports']
for f,h in protected.items():assert sha(R/f)==h,f
for f,h in p['source_pins'].items():
 if phase=='connected'and f in ['Game/scripts/ship.gd']:continue
 assert sha(R/f)==h,f
assert p==json.load(open(R/'Game/data/architecture/STAR_ATLAS_D17_STANDARD823.json'))
assert p['active'] and phase=='connected'
assert p['sealed_independent_commit']==base
assert sha(R/'Game/artifacts/star_atlas_d17_standard823_sealed.json')==p['sealed_receipt_sha256']
assert json.load(open(R/'Game/artifacts/star_atlas_d17_standard823_sealed.json'))['status']=='PASS'
assert json.load(open(W/'SOURCE_PHOTO_RECEIPT.json'))['status']=='PASS'

audit=json.load(open(W/'EXACT_NATIVE_AUDIT.json'));check=json.load(open(R/'Game/artifacts/star_atlas_d17_standard823.json'))
assert audit['status']==check['status']=='PASS'and check['unchanged_room_meshes']==405 and check['new_fixture_meshes']==24 and len(check['walks'])==17
q=p['structure'];assert sha(W/q['native'])==q['native_sha256']and sha(W/q['export'])==sha(R/'Game/assets/models'/q['export'])==q['export_sha256']and audit['fresh_saved_native_repeat_export_identical']
original=(W/'PREIMAGE_ship.gd.txt').read_bytes();current=(R/'Game/scripts/ship.gd').read_bytes();line=b'\tload("res://scripts/star_atlas_d17_standard823.gd").build(self)\n';assert current.count(line)==1 and current.replace(line,b'')==original and sha(W/'PREIMAGE_ship.gd.txt')==p['source_pins']['Game/scripts/ship.gd']
assert sha(R/'Game/assets/models'/p['room_model'])==p['room_model_sha256']
assert json.load(open(W/'LIBRARY_PHOTO_DELIVERY.json'))['status']=='CONFIRMED_LIBRARY_CREATE_AND_LOCAL_METADATA'
assert sha(R/'Game/artifacts/star_atlas_d17_standard823_native.json')==p['native_audit_sha256']
for logfile in ['IMPORT001.log','CONNECTED002.log','NATIVE_AUDIT001.log','SOURCE_VIEW001.log']:
 assert 'SCRIPT ERROR:'not in(W/logfile).read_text()and 'ERROR:'not in(W/logfile).read_text(),logfile

inventory=json.load(open(W/(phase.upper()+'_CHANGED_FILES.json')));assert inventory['base_commit']==base
changed=G('diff','--name-only',base,head).splitlines();rel=str(W.relative_to(R))
assert set(inventory['files'])==(set(changed)|set(p['phase_evidence'][phase]))-{'CHECKPOINT.json','BACKUP_STATUS.json',rel+'/'+phase.upper()+'_CHANGED_FILES.json'}
for f,q in inventory['files'].items():assert sha(R/f)==q['sha256']and(R/f).stat().st_size==q['bytes'],f
assert not G('status','--porcelain')
assert not any('/.godot/'in f or '/__pycache__/'in f or f.endswith('.blend1')for f in G('ls-files').splitlines())
assert subprocess.run(['pgrep','-x','godot'],stdout=subprocess.DEVNULL).returncode!=0
report={'status':'PASS_ALL_MANAGED_FILES_SOURCE_INTEGRITY_AND_REMOTE_REFS','commit':head,'root_tree':rr['root_tree'],'manifest_sha256':rr['manifest_sha256'],'counts':counts,'files_verified':checked,'prior_native_export_files_byte_identical':len(protected),'remote_refs':refs,'canonical_adoption_pending':True,'base_checkpoint':rr['base'],'all_eight_groups_unfinished':True,'worktree_clean':True,'godot_process_running':False}
Path(stem+'LOCAL_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
report['status']='PASS_METADATA_CHANGED_FILE_INVENTORY_PRIOR_CHAIN';report['changed_files']=len(changed);report['changed_and_evidence_hashes_verified']=len(inventory['files'])
Path(stem+'CHAIN_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k]for k in ['status','commit','counts','files_verified']}))
