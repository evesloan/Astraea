import argparse,hashlib,json,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path);p.add_argument('--apply',action='store_true');p.add_argument('--restore',action='store_true');a=p.parse_args();assert not(a.apply and a.restore)
S=Path(__file__).resolve().parent;d=json.loads((S/'PATCH.json').read_text());target=a.repo/d['target'];sha=lambda b:hashlib.sha256(b).hexdigest();old=(S/'package.gd.before').read_bytes();new=(S/'package.gd').read_bytes();assert sha(old)==d['before_sha256']and sha(new)==d['after_sha256'];current=target.read_bytes();h=sha(current);assert h in [d['before_sha256'],d['after_sha256']], 'Refuse unknown target bytes'
backup=target.with_name(target.name+'.before-quiet-d14-trace')
if a.apply or a.restore:
 if backup.exists():assert backup.read_bytes()==old,'Refuse different backup'
 else:
  with backup.open('xb')as f:f.write(old)
 desired=old if a.restore else new
 if current!=desired:
  temp=target.with_name(target.name+'.quiet-d14-trace.tmp')
  with temp.open('xb')as f:f.write(desired)
  assert target.read_bytes()==current,'Target changed concurrently; no replacement made'
  os.replace(temp,target)
 assert target.read_bytes()==desired
print(json.dumps({'target':d['target'],'sha256':sha(target.read_bytes()),'mode':'restore'if a.restore else 'apply'if a.apply else 'check','launch_started':False}))
