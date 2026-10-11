from pathlib import Path
import json,hashlib,subprocess,sys
W=Path(__file__).resolve().parent;R=W.parents[2];phase=sys.argv[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
G=lambda *a:subprocess.check_output(['git',*a],cwd=R,text=True).strip()
head=G('rev-parse','HEAD');base=G('rev-parse','HEAD^');c=json.load(open(R/'CHECKPOINT.json'));b=json.load(open(R/'BACKUP_STATUS.json'));p=json.load(open(W/'PLAN.json'))
stem=str(R)+'-AFT-CROWN-SITTING-BAYS-'+phase.upper()+'-';rr=json.load(open(stem+'REMOTE_VERIFICATION.json'))
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
assert refs['refs/heads/main']==refs['refs/heads/checkpoint/direct-integration-20261009']=='8c7a827351038ba40e2f29e6d3c0451d31ea1350'
assert refs['refs/heads/source/godot']=='12080c25971fa38d37766b52c0835035ce5366ca'and refs['refs/heads/source/blender']=='6a7a4cfd44e8b174ddf4d3a9987cc0c29741ffbc'
protected=json.load(open(W/'PROTECTED_NATIVE_EXPORT_PREIMAGES.json'))
for f,h in protected.items():assert sha(R/f)==h,f
for f,h in p['source_pins'].items():
 if phase=='connected'and f=='Game/scripts/ship.gd':continue
 assert sha(R/f)==h,f
if phase!='survey':
 assert p==json.load(open(W/'RUNTIME_PLAN.json'))==json.load(open(R/'Game/data/architecture/AFT_CROWN_SITTING_BAYS.json'))
 assert p['active']==(phase=='connected')
 geom=json.load(open(R/'Game/artifacts/aft_crown_sitting_bays_geometry.json'));assert geom['status']=='PASS'and geom['model_pins']==p['model_pins']and p['sealed_receipt_sha256']==sha(R/'Game/artifacts/aft_crown_sitting_bays_geometry.json')
 assert all(json.load(open(W/f))['status']=='PASS'for f in ['EXACT_NATIVE_SOURCE_AUDIT.json','BAY_SOURCE_FIT.json'])
 for q in p['native_export_records']:assert sha(W/q['native'])==q['native_sha256']and sha(W/q['export'])==sha(R/'Game/assets/models'/q['export'])==q['export_sha256']and q['fresh_native_repeat_identical']
if phase=='connected':
 conn=json.load(open(R/'Game/artifacts/aft_crown_sitting_bays_connection.json'));assert conn['status']=='PASS'and conn['model_pins']==p['model_pins']and conn['geometry_seal_sha256']==p['sealed_receipt_sha256']
 original=(W/'INTEGRATION_PREIMAGE_ship.gd').read_text();current=(R/'Game/scripts/ship.gd').read_text();line='\tload("res://scripts/aft_crown_sitting_bays.gd").build(self)\n';assert current.count(line)==1 and current.replace(line,'')==original and sha(W/'INTEGRATION_PREIMAGE_ship.gd')==p['source_pins']['Game/scripts/ship.gd']
 assert p['independently_retained_inactive_geometry_commit']==base
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
