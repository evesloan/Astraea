"""Apply only the four hash-verified delivery-fix files; never launch Godot."""
import argparse,hashlib,json,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path);p.add_argument('--apply',action='store_true');a=p.parse_args();S=Path(__file__).resolve().parent;R=a.repo.resolve();d=json.loads((S/'PATCH.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();pending=[]
for row in d['files']:
 rel=Path(row['path']);assert not rel.is_absolute()and '..'not in rel.parts
 target=R/rel;assert R in target.resolve().parents
 blob=(S/'payload'/rel).read_bytes();assert sha(blob)==row['after_sha256']
 if target.exists():
  current=target.read_bytes();h=sha(current)
  if h==row['after_sha256']:continue
  assert row['before_sha256']is not None and h==row['before_sha256'],'Refuse mismatch: '+str(rel)
 else:
  assert row['before_sha256']is None,'Missing required baseline: '+str(rel);current=None
 backup=R/'.astraea-delivery-backups/quiet-d14-composed'/rel
 if backup.exists():assert current is not None and backup.read_bytes()==current,'Backup mismatch'
 pending.append((target,backup,current,blob))
if a.apply:
 for target,backup,current,blob in pending:
  target.parent.mkdir(parents=True,exist_ok=True)
  if current is not None:
   backup.parent.mkdir(parents=True,exist_ok=True)
   if not backup.exists():
    with backup.open('xb')as f:f.write(current)
   assert target.read_bytes()==current,'Concurrent target edit'
   tmp=target.with_name(target.name+'.quiet-d14-fix.tmp')
   with tmp.open('xb')as f:f.write(blob)
   os.replace(tmp,target)
  else:
   with target.open('xb')as f:f.write(blob)
 for row in d['files']:assert sha((R/row['path']).read_bytes())==row['after_sha256']
print(json.dumps({'status':'APPLIED'if a.apply else 'READY','changed_files':len(pending)if a.apply else 0,'pending_files':len(pending),'launch_started':False}))
