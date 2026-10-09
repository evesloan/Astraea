"""Manual independent package checkpoint. Never operates host Git or changes main."""
from pathlib import Path
import subprocess,shutil,json,datetime,sys,hashlib
P=Path(__file__).resolve().parents[1];G=P/'retention/git';BRANCH='handoff/shopping-promenade-20261009';URL='https://github.com/evesloan/Astraea.git';PREFIX='external_packages/shopping_promenade_20261009'
def git(*a):
 r=subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True)
 if r.returncode:raise RuntimeError('Git '+a[0]+': '+r.stderr[:500])
 return r.stdout.strip()
G.mkdir(parents=True,exist_ok=True)
initial=not (G/'.git').exists() or subprocess.run(['git','-C',str(G),'rev-parse','--verify','HEAD'],capture_output=True).returncode!=0
if initial:
 assert not git('ls-remote',URL,'refs/heads/'+BRANCH),'Existing branch: inspect instead of overwriting'
 git('init','--initial-branch='+BRANCH)
 assert 'visibility' not in BRANCH
 git('config','core.longpaths','true')
else:
 assert git('branch','--show-current')==BRANCH
 assert all(n.startswith(PREFIX+'/') for n in git('ls-files').splitlines())
 assert git('rev-parse','HEAD')==git('ls-remote',URL,'refs/heads/'+BRANCH).split()[0]
head=None if initial else git('rev-parse','HEAD');D=G/PREFIX
for f in P.rglob('*'):
 rel=f.relative_to(P)
 if rel.parts[:2]==('preview','exports'):continue
 if not f.is_file() or any(k in rel.parts for k in ['retention','.godot','__pycache__']) or f.suffix in ['.blend1','.pyc','.import']:continue
 assert f.stat().st_size<95*1024*1024,rel
 t=D/rel;t.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256(f.read_bytes()).hexdigest();shutil.copyfile(f,t);assert h==hashlib.sha256(t.read_bytes()).hexdigest()==hashlib.sha256(f.read_bytes()).hexdigest()
if git('ls-files',PREFIX+'/preview/exports'):git('rm','-r','--cached','--',PREFIX+'/preview/exports')
git('add',PREFIX);git('add','--renormalize',PREFIX);phase=sys.argv[1] if len(sys.argv)>1 else 'construction'
git('-c','user.name=Codex','-c','user.email=codex@users.noreply.github.com','commit','-m','Bounded shopping delivery: '+phase)
manifest=json.loads((P/'RESOURCE_HASHES.json').read_text());check=dict(manifest['files']);check['RESOURCE_HASHES.json']={'sha256':hashlib.sha256((P/'RESOURCE_HASHES.json').read_bytes()).hexdigest()}
request=''.join('HEAD:'+PREFIX+'/'+n+'\n' for n in check).encode();raw=subprocess.run(['git','-C',str(G),'cat-file','--batch'],input=request,capture_output=True,check=True).stdout;offset=0
for n,h in check.items():
 end=raw.index(b'\n',offset);header=raw[offset:end].decode().split();assert header[1]=='blob',n;size=int(header[2]);data=raw[end+1:end+1+size];offset=end+1+size+1;assert hashlib.sha256(data).hexdigest()==h['sha256'],n
sha=git('rev-parse','HEAD');git('push',URL,'HEAD:refs/heads/'+BRANCH);remote=git('ls-remote',URL,'refs/heads/'+BRANCH).split()[0];assert sha==remote
r={'phase':phase,'branch':BRANCH,'commit':sha,'remote_confirmed':remote,'parent_commit':head,'committed_raw_files_verified':len(check),'resource_manifest_sha256':hashlib.sha256((P/'RESOURCE_HASHES.json').read_bytes()).hexdigest(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':PREFIX+' only; host branch/source/main/aquatic unchanged'}
(P/'retention'/('receipt_'+phase+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
