from pathlib import Path
import json,subprocess,hashlib,datetime
R=Path('/workspace/Astraea');git=lambda *a:subprocess.check_output(['git',*a],cwd=R,text=True).strip();base='94e29885dca264b8dd5b23c134ab38ec7b278ec9';assert git('rev-parse','HEAD')==base;assert not git('diff','--name-only')
changed=set(git('diff','--cached','--name-only').splitlines());tree=git('write-tree');now=datetime.datetime.now(datetime.timezone.utc).isoformat();p=R/'CHECKPOINT.json';old_manifest=hashlib.sha256(subprocess.check_output(['git','show',base+':CHECKPOINT.json'],cwd=R)).hexdigest();j=json.loads(p.read_text());summary=json.load(open(R/'Game/docs/validation/d17_starboard_standard_20261019/SUMMARY.json'));scope='Approved D17 nine-standard starboard physical guest receiving r002; nine source identities/18 reservations and premium808 preserved. Editable frame, exact source kits/fixtures, bounded guard successors, original-controller routes and installed import integrity checked. Broader service, primary engineering and final art remain open; existing delivery ZIP unchanged.'
for name,v in j['projects'].items():
 prefix=v['prefix'];files={}
 for f in git('ls-files',prefix).splitlines():
  rel=f[len(prefix)+1:];files[rel]=hashlib.sha256((R/f).read_bytes()).hexdigest() if f in changed or rel not in v['files'] else v['files'][rel]
 v.update(files=files,git_tree=git('rev-parse',tree+':'+prefix),signature=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest(),work_in_progress=True)
j.update(created_utc=now,scope=scope,base_checkpoint_commit=base,base_root_tree=git('rev-parse',base+'^{tree}'),snapshot_status='D17_STARBOARD_PHYSICAL_RECEIVING_VERIFIED');j['checks']['d17_starboard_standard_20261019']=summary;p.write_text(json.dumps(j,indent=2)+'\n');manifest=hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'BACKUP_STATUS.json';b=json.load(open(p));b.update(checkpoint_created_utc=now,manifest_sha256=manifest,checkpoint_status='D17_STARBOARD_REMOTE_PENDING',scope=scope,base_checkpoint_commit=base,base_root_tree=git('rev-parse',base+'^{tree}'))
for name,v in j['projects'].items():b['projects'][name].update(files=len(v['files']),signature=v['signature'],git_tree=v['git_tree'])
b['last_verified_source_checkpoint']={'commit':base,'manifest_sha256':old_manifest,'remote_readback_verified':True,'receipt':'Game/docs/validation/d17_starboard_standard_20261019/PREDECESSOR_REMOTE_VERIFICATION.json'};p.write_text(json.dumps(b,indent=2)+'\n');print('manifest',manifest)
