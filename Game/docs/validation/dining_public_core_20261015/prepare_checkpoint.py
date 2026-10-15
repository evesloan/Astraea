from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
V=Path(__file__).resolve().parent;C=V.parent;R=Path('/workspace/astraea-protected-integration-20261012');E=Path('/workspace/astraea-protected-integration-evidence-20261012');base='bded1209e702ae699698606fe15e7d685fbb0d99';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
assert git('rev-parse','HEAD')==base and not git('diff','--cached','--name-only')
for n in['dining_default251','nested_authentication252']:assert json.loads((E/(n+'.json')).read_text())['passed']
check=json.loads((V/'INSTALLED_RUNTIME.json').read_text());assert check['status']=='PASS'and len(check['routes'])==3 and len(check['stances'])==30 and check['retained_source_places']==720
for row in json.loads((C/'RETAINED_UNTRACKED_52_PROTECTION_VERIFICATION.json').read_text())['verified_files']:assert sha((R/row['path']).read_bytes())==row['sha256']
docs=R/'Game/docs/validation/dining_public_core_20261015';docs.mkdir(parents=True,exist_ok=True)
for p in V.iterdir():
 if p.is_file()and p.suffix in['.json','.gd','.txt','.log','.py']:shutil.copyfile(p,docs/p.name)
for n in['dining_public_core248','dining_local249','dining_public250','dining_default251','nested_authentication252']:
 for ext in['json','log']:shutil.copyfile(E/(n+'.'+ext),docs/(n+'.'+ext))
shutil.copyfile(C/'approved_combined_receivers_20261014/wet_receiving/WET_FINAL_PROTECTION.json',docs/'PREDECESSOR_WET_FINAL_PROTECTION.json')
visual=R/'BlenderCatalogue/assets/dining_public_core_20261015/visual_review';visual.mkdir(parents=True,exist_ok=True)
for p in(V/'visual_review').iterdir():shutil.copyfile(p,visual/p.name)
shutil.copyfile(V/'render_bounded_portal.py',visual/'render_bounded_portal.py')
summary={'native_enclosure_wall_successors':4,'new_public_portals':2,'clear_width_m':4,'clear_height_m':3.2,'dining_rooms_publicly_received':3,'original_controller_legs':sum(len(r['legs'])for r in check['routes']),'floor_and_capsule_stances':len(check['stances']),'retained_source_places':720,'new_places_or_programmes':0,'outside_clipped_source_triangles_uv_exact':156,'source_embedded_image_bytes_preserved':2,'original_core_source_file_unchanged':True,'original_lift_stairs_floors_primary_supports_unchanged':True,'kitchen_clean_used_stock_hygiene_pressure_species_or_final_art_accepted':False}
p=R/'CONSOLIDATED_CONSTRUCTION_INVENTORY.json';inv=json.loads(p.read_text());inv['dining_public_core_20261015']=summary;inv['parked_fitting_candidates_20261015']['dining_runtime_adopted']=True
for g in inv['groups']:
 if g['group']==8:
  g['live_installed_and_checked']+=';Shared Table and Sunward dining now receive two fitted4x3.2m public portals through four exact forward-core wall/dado resources. Lantern retained axial connection also verified. Ten original-controller legs,30 supported clear stances and720 unchanged source places;no new capacity orprogramme.'
  g['not_installed_or_unaccepted']=g['not_installed_or_unaccepted'].replace('dining external public approaches and clean/used kitchen routes remain blocked','dining public receiving isphysically installed andchecked;externalclean/used kitchen routes remain unfinished')
  g['physical_missing_or_conditional']=[x.replace('Dining external approaches and clean/used kitchen connections remain blocked.','Dining public approaches are physically installed andchecked;external clean/used kitchen connections remain unfinished.')for x in g['physical_missing_or_conditional']]
p.write_text(json.dumps(inv,indent=2)+'\n')
status=R/'Game/docs/CURRENT_STATUS.md';text=status.read_text();assert text.count('Default dining startup verification ispending;')==1;status.write_text(text.replace('Default dining startup verification ispending;','Default dining startup and authentication both pass;'))
owned=sorted(set(git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard','--','Game','BlenderCatalogue').splitlines()));assert all(x.startswith(('Game/','BlenderCatalogue/'))or x=='CONSOLIDATED_CONSTRUCTION_INVENTORY.json'for x in owned);subprocess.run(['git','-C',str(R),'add','--sparse','-f','--',*owned],check=True)
old=(R/'CHECKPOINT.json').read_bytes();cp=json.loads(old);tree0=git('write-tree','--missing-ok')
for path in owned:
 for k,prefix in[('Godot','Game/'),('Blender','BlenderCatalogue/')]:
  if path.startswith(prefix):cp['projects'][k]['files'][path[len(prefix):]]=sha((R/path).read_bytes())
for pr in cp['projects'].values():pr['files']=dict(sorted(pr['files'].items()));pr['signature']=sha(json.dumps(pr['files'],sort_keys=True,separators=(',',':')).encode());pr['git_tree']=git('rev-parse',tree0+':'+pr['prefix'])
scope='Fit two forward-core public dining portals through four exact wall/dado successors,4mwide and3.2mhigh. SharedTable,Sunward andretained Lantern axial receiving pass10 original-controller legs and30 supported clear stances;720 source places andall room identities unchanged.156 source clipped outside triangles/UVs andtwo image payloads exact;original lift,stairs,floors,primary supports andsourceGLB untouched. Native fresh reexport,default startup,authentication andsource failure evidence retained. Preserve original malformed unused QA draft as text whilecorrecting duplicate declaration for editor indexing. Continue all-eight construction;external kitchen clean/used,stock,services,persistence,engineering,final-art andwhole-build acceptance remainunfinished.'
cp.update(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=scope,base_checkpoint_commit=base,base_root_tree=git('rev-parse',base+'^{tree}'),snapshot_status='THREE_DINING_PUBLIC_RECEIVING_PHYSICAL_WIP',canonical_adoption_pending=True);cp['checks']['dining_public_core_20261015']=summary;cb=(json.dumps(cp,indent=2)+'\n').encode();(R/'CHECKPOINT.json').write_bytes(cb)
b=json.loads((R/'BACKUP_STATUS.json').read_text());b.update(manifest_sha256=sha(cb),scope=scope,checkpoint_status='DINING_PUBLIC_REMOTE_PENDING',base_checkpoint_commit=base,automatic_watcher_active=False);b['last_verified_source_checkpoint']={'commit':base,'manifest_sha256':sha(old),'remote_readback_verified':True,'receipt':'Game/docs/validation/dining_public_core_20261015/PREDECESSOR_WET_FINAL_PROTECTION.json'}
for k,pr in cp['projects'].items():b['projects'][k]={'prefix':pr['prefix'],'files':len(pr['files']),'signature':pr['signature'],'git_tree':pr['git_tree']}
(R/'BACKUP_STATUS.json').write_text(json.dumps(b,indent=2)+'\n');subprocess.run(['git','-C',str(R),'add','CHECKPOINT.json','BACKUP_STATUS.json'],check=True);tree=git('write-tree','--missing-ok');commit=subprocess.check_output(['git','-C',str(R),'commit-tree',tree,'-p',base],input=b'Connect all three dining public approaches with exact forward core wall successors\n').decode().strip();subprocess.run(['git','-C',str(R),'update-ref','refs/heads/handoff/dining-public-receiving-20261015',commit],check=True)
files={}
for path in git('diff-tree','--no-commit-id','--name-only','-r',base,commit).splitlines():
 data=(R/path).read_bytes();files[path]={'bytes':len(data),'sha256':sha(data),'git_blob_sha':git('rev-parse',commit+':'+path),'mode':git('ls-tree',commit,'--',path).split()[0]}
delta={'commit':commit,'parent':base,'tree':tree,'checkpoint_sha256':sha(cb),'counts':{k:len(v['files'])for k,v in cp['projects'].items()},'files':files};(V/'DINING_CHECKPOINT_DELTA.json').write_text(json.dumps(delta,indent=2)+'\n');print(commit,len(files))
