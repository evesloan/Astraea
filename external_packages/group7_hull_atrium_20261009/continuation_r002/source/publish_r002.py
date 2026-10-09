"""Bounded continuation checkpoint on the existing Group7 branch; no host Git mutation."""
from pathlib import Path
import subprocess,shutil,json,datetime,sys,hashlib
P=Path(__file__).resolve().parents[1];OLD=P.parent;G=OLD/'retention/git';BRANCH='handoff/group7-hull-atrium-20261009-mousylaptop';URL='https://github.com/evesloan/Astraea.git';OLDPREFIX='external_packages/group7_hull_atrium_20261009';PREFIX=OLDPREFIX+'/continuation_r002';BASE='e6abd8100af7c56587dcf7dfb6eb85450dbcd1fe';OLDHASH='ef789ac9a669e337389c46c83562ca14bee6ba54ac9fda7d528d407606f785eb'
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def git(*a):
 r=subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True)
 if r.returncode:raise RuntimeError('Git '+a[0]+': '+r.stderr[:500])
 return r.stdout.strip()
assert digest(OLD/'RESOURCE_HASHES.json')==OLDHASH
original=json.loads((OLD/'RESOURCE_HASHES.json').read_text())['files']
for n,r in original.items():assert digest(OLD/n)==r['sha256'],n
assert git('branch','--show-current')==BRANCH
assert not git('status','--porcelain'),'Publisher checkout has pending changes; inspect before publishing'
parent=git('rev-parse','HEAD');remote=git('ls-remote',URL,'refs/heads/'+BRANCH).split()[0];assert parent==remote
assert git('merge-base','--is-ancestor',BASE,parent)==''
files={}
for f in sorted(P.rglob('*')):
 rel=f.relative_to(P)
 if not f.is_file() or 'retention' in rel.parts or '__pycache__' in rel.parts or f.suffix in ['.blend1','.pyc','.import'] or rel.as_posix()=='RESOURCE_HASHES.json':continue
 assert f.stat().st_size<95*1024*1024,rel
 files[rel.as_posix()]={'bytes':f.stat().st_size,'sha256':digest(f)}
manifest={'slice':'continuation_r002','baseline_first_delivery_commit':BASE,'first_delivery_manifest_sha256':OLDHASH,'files':files,'exclusions':['retention/**','__pycache__/**','*.blend1','*.pyc','*.import'],'hash':'sha256'}
(P/'RESOURCE_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n')
check=dict(files);check['RESOURCE_HASHES.json']={'sha256':digest(P/'RESOURCE_HASHES.json')}
for n,r in check.items():
 f=P/n;t=G/PREFIX/n;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,t);assert digest(f)==digest(t)==r['sha256']
git('add','--',PREFIX)
changed=git('diff','--cached','--name-only').splitlines();assert changed and all(n.startswith(PREFIX+'/') for n in changed),changed
phase=sys.argv[1] if len(sys.argv)>1 else 'terminal-source-r002'
git('-c','user.name=Codex','-c','user.email=codex@users.noreply.github.com','commit','-m','Group7 continuation r002: '+phase)
assert not git('diff',BASE,'HEAD','--name-only','--',OLDPREFIX,':(exclude)'+PREFIX),'First delivered paths changed'
allcheck={OLDPREFIX+'/'+n:r for n,r in original.items()};allcheck[OLDPREFIX+'/RESOURCE_HASHES.json']={'sha256':OLDHASH};allcheck.update({PREFIX+'/'+n:r for n,r in check.items()})
request=''.join('HEAD:'+n+'\n' for n in allcheck).encode();raw=subprocess.run(['git','-C',str(G),'cat-file','--batch'],input=request,capture_output=True,check=True).stdout;offset=0
for n,r in allcheck.items():
 end=raw.index(b'\n',offset);header=raw[offset:end].decode().split();assert header[1]=='blob',n;size=int(header[2]);data=raw[end+1:end+1+size];offset=end+1+size+1;assert hashlib.sha256(data).hexdigest()==r['sha256'],n
sha=git('rev-parse','HEAD');git('push',URL,'HEAD:refs/heads/'+BRANCH);remote=git('ls-remote',URL,'refs/heads/'+BRANCH).split()[0];assert sha==remote
r={'phase':phase,'branch':BRANCH,'commit':sha,'remote_confirmed':remote,'parent_commit':parent,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_delivery_raw_files_verified':len(original)+1,'continuation_raw_files_verified':len(check),'continuation_manifest_sha256':digest(P/'RESOURCE_HASHES.json'),'first_delivery_manifest_sha256':OLDHASH,'scope':PREFIX+' only; no main/host/source/Game/aquatic/shopping edits'}
(P/'retention').mkdir(exist_ok=True);(P/'retention'/('receipt_'+phase+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
