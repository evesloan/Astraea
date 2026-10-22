from pathlib import Path
import json,subprocess,sys,hashlib,shutil,datetime
m=json.loads(Path(sys.argv[1]).read_text());url='https://github.com/evesloan/Astraea.git';ref='refs/heads/construction/group1-tidal-d15-20261010';base=Path('/tmp/astraea-bounded-'+m['head'][:8]);assert not base.exists();base.mkdir();meta=base/'metadata.git';blobdir=base/'blobs.git'
def git(folder,*args,input=None):return subprocess.check_output(['git','--git-dir='+str(folder),*args],input=input,stderr=subprocess.PIPE)
subprocess.run(['git','init','--bare','--quiet',str(meta)],check=True);git(meta,'fetch','--quiet','--depth=2','--filter=blob:none',url,ref);assert git(meta,'rev-parse','FETCH_HEAD').decode().strip()==m['head'];assert git(meta,'rev-parse',m['head']+'^').decode().strip()==m['parent'];assert not (meta/'objects/info/alternates').exists()
by_id={}
for r in m['files']:
 oid=git(meta,'ls-tree',m['head'],'--',r['path']).decode().split()[2];by_id.setdefault(oid,[]).append(r)
batches=[];current=[];size=0
for oid,rows in by_id.items():
 if current and size+rows[0]['bytes']>12*1024**2:batches.append(current);current=[];size=0
 current.append(oid);size+=rows[0]['bytes']
if current:batches.append(current)
verified=0;discarded=0
for i,batch in enumerate(batches):
 assert not blobdir.exists();subprocess.run(['git','init','--bare','--quiet',str(blobdir)],check=True);assert not (blobdir/'objects/info/alternates').exists();git(blobdir,'fetch','--quiet','--no-filter','--stdin',url,input=('\n'.join(batch)+'\n').encode())
 for oid in batch:
  b=git(blobdir,'cat-file','blob',oid);h=hashlib.sha256(b).hexdigest()
  for r in by_id[oid]:assert len(b)==r['bytes']and h==r['sha256'];verified+=1
 # Only this invocation's disposable blob-transfer store is removed after verification.
 before=shutil.disk_usage('/workspace').free;shutil.rmtree(blobdir);discarded+=max(0,shutil.disk_usage('/workspace').free-before)
 if (i+1)%4==0 or i+1==len(batches):print(json.dumps({'batches_verified':i+1,'of':len(batches),'files_verified':verified}),flush=True)
assert verified==len(m['files']);m.update(verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),independent_store=str(meta),alternate_objects=False,remote_ancestry_verified=True,verification_method='Independent commit/tree readback plus bounded raw-blob fetch/hash verification; each temporary blob batch removed only after verification.',temporary_blob_bytes_reclaimed=discarded)
out=Path('/workspace/astraea-'+m['head'][:8]+'-REMOTE_VERIFICATION-20261022.json');out.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'head':m['head'],'files_verified':verified,'bytes_verified':sum(x['bytes']for x in m['files']),'receipt':str(out),'scratch_bytes_reclaimed':discarded}),flush=True)
