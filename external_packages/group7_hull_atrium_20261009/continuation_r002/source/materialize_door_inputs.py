"""Exact pinned door-family inputs, writing only continuation_r002."""
from pathlib import Path
import json,hashlib,subprocess
P=Path(__file__).resolve().parents[1];OLD=P.parent;HOST=OLD.parents[1];D=P/'dependencies';D.mkdir(exist_ok=True)
tree={r['path']:r['sha1'] for r in json.loads((OLD/'qa/canonical_tree_9d6f85.json').read_text())['files']};request=['BlenderCatalogue/assets/staff_threshold/source/AST-STF-008.blend','BlenderCatalogue/assets/staff_threshold/exports/AST-STF-008.glb','BlenderCatalogue/assets/staff_threshold/AST-STF-008.manifest.json','Game/scripts/service_door.gd'];rows=[];pending=[]
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def save(path,b,method):
 assert blob(b)==tree[path],path;target=D/path;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==b
 else:target.write_bytes(b)
 rows.append({'path':path,'git_blob':tree[path],'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'method':method})
for path in request:
 found=False
 for q in [D/path,OLD/'dependencies/canonical_9d6f85'/path,HOST/path]:
  if not q.is_file():continue
  raw=q.read_bytes()
  for b in [raw,raw.replace(b'\r\n',b'\n')]:
   if blob(b)==tree[path]:save(path,b,'Exact pinned existing bytes');found=True;break
  if found:break
 if not found:pending.append(path)
if pending:
 G=P/'retention/input_git';G.parent.mkdir(exist_ok=True)
 def git(*a,input=None):return subprocess.run(['git','-C',str(G),*a],input=input,capture_output=True,check=True).stdout
 if not G.exists():subprocess.run(['git','init','--bare',str(G)],capture_output=True,check=True);git('remote','add','origin','https://github.com/evesloan/Astraea.git')
 git('-c','fetch.negotiationAlgorithm=noop','fetch','origin','--no-tags','--no-write-fetch-head','--filter=blob:none','--stdin',input=('\n'.join(tree[p] for p in pending)+'\n').encode())
 for path in pending:save(path,git('cat-file','blob',tree[path]),'Bounded exact pinned blob fetch')
(P/'qa').mkdir(exist_ok=True);(P/'qa/door_input_receipt.json').write_text(json.dumps({'commit':'9d6f8518f9ddbe5892711ca4eb4849a46fbd32be','files':rows},indent=2)+'\n');print('DOOR_INPUTS',len(rows),'fetched',len(pending))
