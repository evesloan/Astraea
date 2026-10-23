"""Add an isolated, default-off optimization successor; never edit baseline or launch."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();R=a.repo.resolve();S=Path(__file__).resolve().parent;d=json.loads((S/'INSTALL.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pending=[]
for rel,h in d['baseline_pins'].items():assert (R/rel).is_file()and sha(R/rel)==h,'Baseline mismatch: '+rel
for row in d['files']:
 rel=Path(row['path']);assert not rel.is_absolute() and '..'not in rel.parts
 f=S/'payload'/rel;t=R/rel;assert R in t.resolve().parents
 assert f.is_file()and f.stat().st_size==row['bytes']and sha(f)==row['sha256']
 if t.exists():assert t.is_file()and sha(t)==row['sha256'],'Refuse existing different file: '+str(rel)
 else:pending.append((f,t))
if a.apply:
 for f,t in pending:
  t.parent.mkdir(parents=True,exist_ok=True)
  with t.open('xb')as output:output.write(f.read_bytes())
 for rel,h in d['baseline_pins'].items():assert sha(R/rel)==h
print(json.dumps({'status':'APPLIED'if a.apply else 'READY','new_files':len(pending),'baseline_changed':False,'default_main_changed':False,'launch_started':False}))
