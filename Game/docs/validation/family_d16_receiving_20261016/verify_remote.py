import subprocess,json,hashlib,pathlib,datetime
src='/workspace/Astraea'; dst='/workspace/observation-readback.git'; sha=subprocess.check_output(['git','-C',src,'rev-parse','HEAD']).decode().strip()
def git(root,*args,input=None): return subprocess.check_output(['git','-C',root,*args],input=input)
subprocess.run(['git','-C',dst,'fetch','--depth=1','--filter=blob:none','https://github.com/evesloan/Astraea.git',sha],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
paths=git(src,'diff-tree','--no-commit-id','--name-only','-r',sha).decode().splitlines()
entries=[(p,git(src,'rev-parse',sha+':'+p).decode().strip()) for p in paths]
subprocess.run(['git','-C',dst,'fetch','--no-tags','--no-write-fetch-head','--filter=blob:none','--stdin','https://github.com/evesloan/Astraea.git'],input=('\n'.join(sorted(set(b for p,b in entries)))+'\n').encode(),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
rows=[]
for p,b in entries:
 remote=git(dst,'cat-file','blob',b); local=(pathlib.Path(src)/p).read_bytes()
 rows.append(dict(path=p,blob=b,bytes=len(remote),sha256=hashlib.sha256(remote).hexdigest(),match=remote==local,git_blob_valid=hashlib.sha1(b'blob '+str(len(remote)).encode()+b'\0'+remote).hexdigest()==b))
head=git(src,'ls-remote','origin','refs/heads/construction/group1-tidal-d15-20261010').decode().split()[0]
receipt=dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=sha,root_tree=git(dst,'rev-parse',sha+'^{tree}').decode().strip(),remote_head=head,method='Separate shallow blob-filtered GitHub object store; selective changed-blob download; byte and Git-object hash comparison',changed_files=len(rows),changed_bytes=sum(r['bytes'] for r in rows),all_match=all(r['match'] and r['git_blob_valid'] for r in rows) and head==sha,files=rows)
pathlib.Path('/workspace/family-d16-integration/REMOTE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'},indent=2))
assert receipt['all_match']
