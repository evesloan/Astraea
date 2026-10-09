"""Bounded manual checkpoint publisher. No watcher; never touches host Git or shared refs."""
from pathlib import Path
import subprocess,shutil,json,datetime,sys,hashlib
P=Path(__file__).resolve().parents[1];G=P/'retention/git';BRANCH='handoff/aquatic-district-20261009';URL='https://github.com/evesloan/Astraea.git'
def git(*a):
 p=subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True)
 if p.returncode:raise RuntimeError('Git command failed: '+a[0]+'; '+p.stderr[:400])
 return p.stdout.strip()
assert git('branch','--show-current')==BRANCH
assert all(a.startswith('external_packages/aquatic_district_20261009/') for a in git('ls-files').splitlines())
phase=sys.argv[1] if len(sys.argv)>1 else 'construction';head=git('rev-parse','HEAD');remote=git('ls-remote',URL,'refs/heads/'+BRANCH).split()[0]
assert head==remote,'Handoff ref changed; no push attempted.'
D=G/'external_packages/aquatic_district_20261009'
for f in P.rglob('*'):
 rel=f.relative_to(P)
 if not f.is_file() or 'retention' in rel.parts or '.godot' in rel.parts or '__pycache__' in rel.parts or f.suffix in ['.blend1','.pyc','.import']:continue
 assert f.stat().st_size<95*1024*1024,rel
 t=D/rel;t.parent.mkdir(parents=True,exist_ok=True);before=hashlib.sha256(f.read_bytes()).hexdigest();shutil.copyfile(f,t);assert before==hashlib.sha256(f.read_bytes()).hexdigest()==hashlib.sha256(t.read_bytes()).hexdigest(),str(rel)
git('add','external_packages');git('add','--renormalize','external_packages/aquatic_district_20261009');git('-c','user.name=Codex','-c','user.email=codex@users.noreply.github.com','commit','-m','Aquatic bounded delivery checkpoint: '+phase)
sha=git('rev-parse','HEAD')
# Verify the committed raw blobs before upload, including the manifest itself.
manifest=json.loads((P/'RESOURCE_HASHES.json').read_text());check=dict(manifest['files']);check['RESOURCE_HASHES.json']={'sha256':hashlib.sha256((P/'RESOURCE_HASHES.json').read_bytes()).hexdigest()}
request=''.join('HEAD:external_packages/aquatic_district_20261009/'+n+'\n' for n in check).encode();raw=subprocess.run(['git','-C',str(G),'cat-file','--batch'],input=request,capture_output=True,check=True).stdout;offset=0
for n,h in check.items():
 end=raw.index(b'\n',offset);header=raw[offset:end].decode().split();assert header[1]=='blob',n;size=int(header[2]);data=raw[end+1:end+1+size];offset=end+1+size+1;assert hashlib.sha256(data).hexdigest()==h['sha256'],n
print('Committed raw byte hashes verified for '+str(len(check))+' files.',flush=True)
git('push' ,URL,'HEAD:refs/heads/'+BRANCH);confirmed=git('ls-remote',URL,'refs/heads/'+BRANCH).split()[0];assert confirmed==sha
r={'committed_raw_files_verified':len(check),'resource_manifest_sha256':hashlib.sha256((P/'RESOURCE_HASHES.json').read_bytes()).hexdigest() if (P/'RESOURCE_HASHES.json').exists() else None,'phase':phase,'branch':BRANCH,'commit':sha,'remote_confirmed':confirmed,'parent_commit':head,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Only isolated aquatic directory; original working tree and shared branches unchanged','private_repo_verification':'GitHub connector visibility private; same authorized URL'}
(P/'retention'/('receipt_'+phase+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r))
