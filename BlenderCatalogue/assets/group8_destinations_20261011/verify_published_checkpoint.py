"""Hash independently downloaded Git blobs; never consult worktree payloads."""
from pathlib import Path
import subprocess,json,hashlib,sys,datetime
repository_argument,commit,expected_tree,expected_manifest_sha,output=sys.argv[1:]
repository=Path(repository_argument)
manifest_path='BlenderCatalogue/assets/group8_destinations_20261011/GROUP8_MANIFEST.json'
def git(*args):
    return subprocess.check_output(['git','-C',str(repository),*args])
actual_commit=git('rev-parse','HEAD').decode().strip()
actual_tree=git('rev-parse','HEAD^{tree}').decode().strip()
assert actual_commit==commit and actual_tree==expected_tree,(actual_commit,actual_tree)
manifest_bytes=git('show','HEAD:'+manifest_path)
manifest_sha=hashlib.sha256(manifest_bytes).hexdigest()
assert manifest_sha==expected_manifest_sha,manifest_sha
manifest=json.loads(manifest_bytes)
tree={}
for row in git('ls-tree','-r','-z','HEAD').split(b'\0'):
    if not row:continue
    header,path=row.split(b'\t',1)
    mode,kind,oid=header.decode().split()
    tree[path.decode()]=oid
paths=sorted([*manifest['files'],manifest_path])
with open(output+'.sparse.log','wb') as log:
    subprocess.run(['git','-C',str(repository),'sparse-checkout','init','--no-cone'],stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['git','-C',str(repository),'sparse-checkout','set','--no-cone','--stdin'],input=''.join('/'+p+'\n'for p in paths).encode(),stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['git','-C',str(repository),'checkout','HEAD'],stdout=log,stderr=subprocess.STDOUT,check=True)
checks={}
for path,expected in manifest['files'].items():
    data=git('cat-file','blob',tree[path])
    sha=hashlib.sha256(data).hexdigest()
    assert len(data)==expected['bytes'] and sha==expected['sha256'],path
    checks[path]={'bytes':len(data),'sha256':sha,'remote_git_blob':tree[path]}
assert len(checks)==manifest['total_files']
assert sum(row['bytes']for row in checks.values())==manifest['total_bytes']
receipt={'status':'PASS','independent_method':'New remote partial clone; manifest/tree and payloads read from GitHub-derived Git objects, no local worktree payload used','repository':'https://github.com/evesloan/Astraea.git','branch':manifest['owned_branch'],'commit':actual_commit,'tree':actual_tree,'manifest_sha256':manifest_sha,'payload_files_verified':len(checks),'payload_bytes_verified':manifest['total_bytes'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':checks}
Path(output).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='files'}))
