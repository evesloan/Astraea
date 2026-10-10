"""Read exact pinned Git blobs into this isolated source inventory; no checkout."""
from pathlib import Path
import json,subprocess,hashlib,sys,os
R=Path(__file__).resolve().parent;repo=R/'read_repository'
tree=json.loads((R/'TREE_AT_PIN.json').read_text());rows={e['path']:e for e in tree['files']}
receipt_path=R/'INPUT_PIN_RECEIPT.json'
receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else dict(checkpoint=tree['checkpoint'],independent_retained_remote='Private evesloan/Astraea; exact fetched commit; not a local receiving-copy assumption',files=[])
def extended(p):return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p
def fetch(path):
 row=rows[path];target=extended(R/'inputs'/path)
 proc=subprocess.run(['git','cat-file','blob',row['git_blob']],cwd=repo,capture_output=True);assert proc.returncode==0,proc.stderr.decode(errors='replace');raw=proc.stdout
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==raw,'Existing isolated input differs; preserve and investigate '+path
 else:target.write_bytes(raw)
 rec=dict(path=path,git_blob=row['git_blob'],bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
 receipt['files']=[x for x in receipt['files'] if x['path']!=path]+[rec]
 return rec
if __name__=='__main__':
 paths=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
 for i,p in enumerate(paths):
  rec=fetch(p)
  if i%10==0:print('Retained',i+1,'of',len(paths),p,flush=True)
 receipt['files'].sort(key=lambda x:x['path']);receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8');print('Verified exact inputs',len(receipt['files']))
