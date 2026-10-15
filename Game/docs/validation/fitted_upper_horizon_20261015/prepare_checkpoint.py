from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
V=Path(__file__).resolve().parent;C=V.parent;R=Path('/workspace/astraea-protected-integration-20261012');E=Path('/workspace/astraea-protected-integration-evidence-20261012');base='394d5795ed1107757a73bc0be4e5c67af0d03479';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
assert git('rev-parse','HEAD')==base and not git('diff','--cached','--name-only')
for n in ['horizon_default262','nested_authentication263']:assert json.loads((E/(n+'.json')).read_text())['passed']
check=json.loads((V/'INSTALLED_RUNTIME.json').read_text());assert check['status']=='PASS'and len(check['actual_controller_legs'])==27 and len(check['retained_floor_foot_pins'])==344 and check['old_contact_inventory']==[]
for row in json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text())['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
docs=R/'Game/docs/validation/fitted_upper_horizon_20261015';docs.mkdir(parents=True,exist_ok=True)
for p in V.iterdir():
 if p.is_file()and p.suffix in ['.json','.gd','.txt','.log','.py']:shutil.copyfile(p,docs/p.name)
for n in ['horizon_resources259','horizon_candidate260','horizon_candidate261','horizon_default262','nested_authentication263']:
 for ext in ['json','log']:shutil.copyfile(E/(n+'.'+ext),docs/(n+'.'+ext))
shutil.copyfile(C/'theater_backstage_receiving_20261015/BACKSTAGE_FINAL_PROTECTION.json',docs/'PREDECESSOR_BACKSTAGE_FINAL_PROTECTION.json')
visual=R/'BlenderCatalogue/assets/fitted_upper_horizon_20261015/visual_review';visual.mkdir(parents=True,exist_ok=True)
for p in (V/'visual_review').iterdir():shutil.copyfile(p,visual/p.name)
shutil.copyfile(V/'render_bounded_review.py',visual/'render_bounded_review.py')
summary={'individual_native_meshes':320,'runtime_batches':70,'source_triangles_geometry_uv_verified':17888,'original_source_image_payloads_unchanged':10,'retained_floor_contacts':344,'original_controller_legs':27,'clear_work_stances':10,'original_foyer_sitting_meshes_unchanged':860,'source_lights_registered_once':2,'unexplained_old_contacts':0,'new_floor_room_ids_or_capacity':0,'operational_species_stock_pressure_save_or_final_art_accepted':False}
p=R/'CONSOLIDATED_CONSTRUCTION_INVENTORY.json';inv=json.loads(p.read_text());inv['fitted_upper_horizon_20261015']=summary
for g in inv['groups']:
 if g['group']==8:
  g['live_installed_and_checked']+=';Upper Horizon source interiors now physically fitted between retained foyer and sitting bays:320 editable meshes/70 runtime batches,27 controller legs,344 floor contacts,10 clear work positions,two original task lights.860 retained foyer/sitting meshes unchanged;no new capacity.'
  g['not_installed_or_unaccepted']=g['not_installed_or_unaccepted'].replace('Upper Horizon held;','Upper Horizon physical fit installed;occupied use/stock/species/persistence and final visuals remain open;')
p.write_text(json.dumps(inv,indent=2)+'\n');status=R/'Game/docs/CURRENT_STATUS.md';status.write_text('## Latest physical integration: fitted Upper Horizon interiors\n\nOriginal records cabinets, study consoles, four reading chairs, two task lamps and counters now fit between the retained D18 foyer and sitting bays. The versioned native retains320 editable source meshes and70 original runtime batches.27 original-controller legs,344 retained-floor contacts and10 clear work positions pass;860 existing foyer/sitting meshes stay unchanged. Original geometry, UVs and10 image payloads are preserved. No new floor, room IDs orcapacity. Operational species/stock/save/pressure andfinal Godot/CRT visuals remain unfinished.\n\n'+status.read_text())
owned=sorted(set(git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard','--','Game','BlenderCatalogue').splitlines()));assert all(x.startswith(('Game/','BlenderCatalogue/'))or x=='CONSOLIDATED_CONSTRUCTION_INVENTORY.json'for x in owned);subprocess.run(['git','-C',str(R),'add','--sparse','-f','--',*owned],check=True)
old=(R/'CHECKPOINT.json').read_bytes();cp=json.loads(old);tree0=git('write-tree','--missing-ok')
for path in owned:
 for k,prefix in[('Godot','Game/'),('Blender','BlenderCatalogue/')]:
  if path.startswith(prefix):cp['projects'][k]['files'][path[len(prefix):]]=sha((R/path).read_bytes())
for pr in cp['projects'].values():pr['files']=dict(sorted(pr['files'].items()));pr['signature']=sha(json.dumps(pr['files'],sort_keys=True,separators=(',',':')).encode());pr['git_tree']=git('rev-parse',tree0+':'+pr['prefix'])
scope='Fit retained Upper Horizon source furniture into original D18 enclosure between foyer and sitting bays, preserving original source variants and architecture.320 editable source meshes,70 runtime batches,17888 unchanged source triangles with UV,10 image payloads;27 controller legs,344 retained-floor contacts,10 clear work positions,860 original context meshes unchanged,two registered original source lights. No new floor/room IDs/capacity. Stock/species/persistence/pressure/operation and final visuals remain open;continue all-eight construction and new preview packaging.'
cp.update(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=scope,base_checkpoint_commit=base,base_root_tree=git('rev-parse',base+'^{tree}'),snapshot_status='FITTED_UPPER_HORIZON_PHYSICAL_WIP',canonical_adoption_pending=True);cp['checks']['fitted_upper_horizon_20261015']=summary;cb=(json.dumps(cp,indent=2)+'\n').encode();(R/'CHECKPOINT.json').write_bytes(cb)
b=json.loads((R/'BACKUP_STATUS.json').read_text());b.update(manifest_sha256=sha(cb),scope=scope,checkpoint_status='HORIZON_REMOTE_PENDING',base_checkpoint_commit=base,automatic_watcher_active=False);b['last_verified_source_checkpoint']={'commit':base,'manifest_sha256':sha(old),'remote_readback_verified':True,'receipt':'Game/docs/validation/fitted_upper_horizon_20261015/PREDECESSOR_BACKSTAGE_FINAL_PROTECTION.json'}
for k,pr in cp['projects'].items():b['projects'][k]={'prefix':pr['prefix'],'files':len(pr['files']),'signature':pr['signature'],'git_tree':pr['git_tree']}
(R/'BACKUP_STATUS.json').write_text(json.dumps(b,indent=2)+'\n');subprocess.run(['git','-C',str(R),'add','CHECKPOINT.json','BACKUP_STATUS.json'],check=True);tree=git('write-tree','--missing-ok');commit=subprocess.check_output(['git','-C',str(R),'commit-tree',tree,'-p',base],input=b'Fit original Horizon interiors between retained foyer and sitting bays\n').decode().strip();subprocess.run(['git','-C',str(R),'update-ref','refs/heads/handoff/fitted-upper-horizon-20261015',commit],check=True)
files={}
for path in git('diff-tree','--no-commit-id','--name-only','-r',base,commit).splitlines():
 data=(R/path).read_bytes();files[path]={'bytes':len(data),'sha256':sha(data),'git_blob_sha':git('rev-parse',commit+':'+path),'mode':git('ls-tree',commit,'--',path).split()[0]}
delta={'commit':commit,'parent':base,'tree':tree,'checkpoint_sha256':sha(cb),'counts':{k:len(v['files'])for k,v in cp['projects'].items()},'files':files};(V/'HORIZON_CHECKPOINT_DELTA.json').write_text(json.dumps(delta,indent=2)+'\n');print(commit,len(files))
