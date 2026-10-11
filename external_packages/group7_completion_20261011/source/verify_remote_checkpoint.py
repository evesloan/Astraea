"""Verify remote checkpoint bytes in a new store with no local object alternates."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ap=argparse.ArgumentParser()
ap.add_argument('--commit',required=True);ap.add_argument('--tree',required=True)
ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--store',required=True)
ap.add_argument('--receipt',required=True);args=ap.parse_args()
repo=Path(args.store);assert not repo.exists(), 'Use a new empty independent verification store'
subprocess.run(['git','init','--bare',str(repo)],check=True,stdout=subprocess.DEVNULL)
def git(*cmd):return subprocess.check_output(['git','-C',str(repo),*cmd])
git('remote','add','origin','https://github.com/evesloan/Astraea.git')
branch='refs/heads/handoff/group7-completion-20261011'
git('fetch','--no-tags','--depth=1','--filter=blob:none','origin',branch)
head=git('rev-parse','FETCH_HEAD').decode().strip();assert head==args.commit
tree=git('rev-parse',head+'^{tree}').decode().strip();assert tree==args.tree
assert not (repo/'objects/info/alternates').exists()
paths={}
for entry in git('ls-tree','-rz',head).split(b'\0'):
    if not entry:continue
    meta,name=entry.split(b'\t',1);mode,kind,oid=meta.split();assert kind==b'blob'
    paths[name.decode()]=oid.decode()
manifest_path='external_packages/group7_completion_20261011/RESOURCE_HASHES.json'
raw=git('cat-file','blob',paths[manifest_path])
actual_manifest_hash=hashlib.sha256(raw).hexdigest();assert actual_manifest_hash==args.manifest_sha256
manifest=json.loads(raw);wanted=manifest['files']
oids=sorted({paths[name]for name in wanted})
# Fetch reachable blob objects in one request, avoiding serial lazy transfers.
# A server that restricts direct blob wants falls back to standard promisor reads.
batch=subprocess.run(['git','-C',str(repo),'fetch','--no-tags','--no-write-fetch-head','--no-auto-maintenance','origin',*oids],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
fallback=batch.returncode!=0
proc=subprocess.Popen(['git','-C',str(repo),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
verified={};total=0
for name,row in wanted.items():
    oid=paths[name];proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
    header=proc.stdout.readline().decode().strip().split()
    assert len(header)==3 and header[0]==oid and header[1]=='blob',(name,header)
    size=int(header[2]);assert size==row['bytes'],name
    data=proc.stdout.read(size);assert proc.stdout.read(1)==b'\n'
    assert len(data)==size and hashlib.sha256(data).hexdigest()==row['sha256'],name
    actual_oid=hashlib.sha1(b'blob '+str(size).encode()+b'\0'+data).hexdigest();assert actual_oid==oid
    verified[name]=row;total+=size
proc.stdin.close();assert proc.wait()==0
aggregate=hashlib.sha256(json.dumps(verified,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert aggregate==manifest['files_aggregate_sha256']
remote=git('ls-remote','origin',branch).decode().split()[0];assert remote==head
receipt={'status':'PASS','repository':'private evesloan/Astraea','branch':branch,'commit':head,'tree':tree,'manifest_sha256':actual_manifest_hash,'manifest_aggregate_sha256':aggregate,'files_sha256_verified_from_fresh_remote_blobs':len(verified),'bytes_sha256_verified':total,'unique_manifest_blob_objects':len(oids),'independent_store':str(repo),'local_alternates':False,'local_repository_objects_used':False,'direct_blob_fetch_fallback_used':fallback,'main_checkpoint_refs_written':False,'whole_group_accepted':False}
Path(args.receipt).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
