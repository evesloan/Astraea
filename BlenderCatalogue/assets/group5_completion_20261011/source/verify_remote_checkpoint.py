"""Read the handoff through a separate remote-only partial Git object store."""
import subprocess,json,pathlib,hashlib,datetime,sys
repo='/tmp/astraea-group5-independent-verification.git'
branch='handoff/group5-completion-20261011'
commit=sys.argv[1] if len(sys.argv)>1 else subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
def git(*args):return subprocess.check_output(['git','-C',repo,*args])
remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0]
assert remote==commit,(remote,commit)
subprocess.run(['git','-C',repo,'fetch','--depth=2','--filter=blob:none','origin','refs/heads/'+branch+':refs/heads/verified-group5'],check=True)
tree=git('rev-parse',commit+'^{tree}').decode().strip()
manifest_path='BlenderCatalogue/assets/group5_completion_20261011/MANIFEST.json'
local_manifest=subprocess.check_output(['git','show',commit+':'+manifest_path]);m=json.loads(local_manifest)
entries={}
for line in git('ls-tree','-r','-z',commit).split(b'\0'):
    if not line:continue
    head,path=line.split(b'\t',1);mode,typ,oid=head.split();entries[path.decode()]=oid.decode()
wanted=m['files']+[{'path':manifest_path,'sha256':hashlib.sha256(local_manifest).hexdigest()}]
ids=sorted({entries[x['path']] for x in wanted})
# Promisor cat-file fetches any absent reachable blob through protocol v2.
# Bulk direct blob wants are not supported by every authenticated endpoint.
proc=subprocess.Popen(['git','-C',repo,'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
errors=[]
for row in wanted:
    proc.stdin.write((entries[row['path']]+'\n').encode());proc.stdin.flush()
    h=proc.stdout.readline().split();size=int(h[2]);data=proc.stdout.read(size);assert proc.stdout.read(1)==b'\n'
    if hashlib.sha256(data).hexdigest()!=row['sha256']:errors.append(row['path'])
proc.stdin.close();assert proc.wait()==0
r={'status':'PASS' if not errors else 'HOLD','remote':'https://github.com/evesloan/Astraea.git','branch':branch,'commit':commit,'tree':tree,'manifest_sha256':hashlib.sha256(local_manifest).hexdigest(),'manifest_files_checked':len(m['files']),'manifest_itself_checked':True,'errors':errors,'independent_store':repo,'method':'independently initialized bare repository;remote commit/tree and all scoped blobs fetched from GitHub;actual blob SHA256 compared to committed manifest;no object alternates or local clone','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
p=pathlib.Path('/workspace/group5-checkpoints')/('VERIFIED_'+commit[:8]+'.json');p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
assert not errors
