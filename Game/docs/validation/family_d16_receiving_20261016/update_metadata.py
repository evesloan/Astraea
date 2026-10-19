from pathlib import Path
import json,subprocess,hashlib,datetime
R=Path('/workspace/Astraea');git=lambda *a:subprocess.check_output(['git',*a],cwd=R,text=True).strip();base='e1ce100298c4c3458d0ddfe7b2203974e76f3bf0';assert git('rev-parse','HEAD')==base;assert not git('diff','--name-only')
changed=set(git('diff','--cached','--name-only').splitlines());tree=git('write-tree');now=datetime.datetime.now(datetime.timezone.utc).isoformat();p=R/'CHECKPOINT.json';old_manifest=hashlib.sha256(subprocess.check_output(['git','show',base+':CHECKPOINT.json'],cwd=R)).hexdigest();j=json.loads(p.read_text());summary=json.load(open(R/'Game/docs/validation/family_d16_receiving_20261016/SUMMARY.json'));scope='Family Terrace D16 physical staff receiving atY97.5:83.548888m2 missing-only floor,74 components,two bounded guard successors andfour retained source light bindings. Existing staff opening reused.18 original-controller route legs plus14 protected prior thresholds; all76 imported meshes exact. Approved D17 and all immutable sources preserved. Operations,primary engineering andfinal art remain open.'
for name,v in j['projects'].items():
 prefix=v['prefix'];files={}
 for f in git('ls-files',prefix).splitlines():
  rel=f[len(prefix)+1:];files[rel]=hashlib.sha256((R/f).read_bytes()).hexdigest() if f in changed or rel not in v['files'] else v['files'][rel]
 v.update(files=files,git_tree=git('rev-parse',tree+':'+prefix),signature=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest(),work_in_progress=True)
j.update(created_utc=now,scope=scope,base_checkpoint_commit=base,base_root_tree=git('rev-parse',base+'^{tree}'),snapshot_status='FAMILY_D16_PHYSICAL_RECEIVING_VERIFIED');j['checks']['family_d16_receiving_20261016']=summary;p.write_text(json.dumps(j,indent=2)+'\n');manifest=hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'BACKUP_STATUS.json';b=json.load(open(p));b.update(checkpoint_created_utc=now,manifest_sha256=manifest,checkpoint_status='FAMILY_D16_REMOTE_PENDING',scope=scope,base_checkpoint_commit=base,base_root_tree=git('rev-parse',base+'^{tree}'))
for name,v in j['projects'].items():b['projects'][name].update(files=len(v['files']),signature=v['signature'],git_tree=v['git_tree'])
b['last_verified_source_checkpoint']={'commit':base,'manifest_sha256':old_manifest,'remote_readback_verified':True,'receipt':'Game/docs/validation/family_d16_receiving_20261016/PREDECESSOR_REMOTE_VERIFICATION.json'};p.write_text(json.dumps(b,indent=2)+'\n');print('manifest',manifest)
