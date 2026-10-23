"""Verify every preimage first; apply only reviewed additive delivery repair files."""
import argparse,hashlib,json,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path);p.add_argument('--apply',action='store_true');a=p.parse_args();S=Path(__file__).resolve().parent;R=a.repo.resolve();d=json.loads((S/'PATCH.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();pending=[]
def require(ok,message):
 if not ok:raise RuntimeError(message)
for rel, expected in d.get('requires',{}).items():
 require((R/rel).is_file() and sha((R/rel).read_bytes())==expected,'Prerequisite differs: '+rel)
for row in d['files']:
 rel=Path(row['path']);require(not rel.is_absolute()and '..'not in rel.parts,'Unsafe path')
 target=R/rel;require(R in target.resolve().parents,'Path escapes target')
 blob=(S/'payload'/rel).read_bytes();require(sha(blob)==row['after_sha256'],'Damaged payload '+str(rel))
 current=target.read_bytes()if target.exists()else None;h=sha(current)if current is not None else None
 if h==row['after_sha256']:continue
 require(h in row['allowed_before_sha256'],'Refuse unexpected source '+str(rel))
 backup=R/'.astraea-delivery-backups/route-activation-20261023'/rel
 if backup.exists():require(current is not None and backup.read_bytes()==current,'Backup mismatch '+str(rel))
 pending.append((target,backup,current,blob))
if a.apply:
 for target,backup,current,blob in pending:
  target.parent.mkdir(parents=True,exist_ok=True)
  require((target.read_bytes()if target.exists()else None)==current,'Concurrent edit '+str(target))
  if current is not None:
   backup.parent.mkdir(parents=True,exist_ok=True)
   if not backup.exists():
    with backup.open('xb')as f:f.write(current)
   tmp=target.with_name(target.name+'.release-repair.tmp')
   with tmp.open('xb')as f:f.write(blob)
   os.replace(tmp,target)
  else:
   with target.open('xb')as f:f.write(blob)
 for row in d['files']:require(sha((R/row['path']).read_bytes())==row['after_sha256'],'Post-write mismatch')
print(json.dumps({'status':'APPLIED'if a.apply else 'READY','pending_files':len(pending),'launch_started':False,'walking_crash_fix_validation':'PENDING'}))
