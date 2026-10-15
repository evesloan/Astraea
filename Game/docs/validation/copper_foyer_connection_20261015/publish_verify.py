from pathlib import Path
import json,subprocess,hashlib,datetime,os
V=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');m=json.loads((V/'COPPER_FOYER_CHECKPOINT_DELTA.json').read_text());target='refs/heads/construction/group1-tidal-d15-20261010';S=V/('independent_remote_'+m['commit'][:8]+'.git')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
refs=dict(line.split()[::-1]for line in git(R,'ls-remote','origin',target,'refs/heads/main','refs/heads/checkpoint/direct-integration-20261009').decode().splitlines());assert refs['refs/heads/main']=='8664ac150a1d5fc5034d1fdecd04dd241e1f3ce4';assert refs['refs/heads/checkpoint/direct-integration-20261009']=='1f68f1e1a44e4492d7b5a81ed553f0f601a89681'
observed=refs[target]
if observed==m['parent']:
 p=subprocess.run(['git','-C',str(R),'push','--porcelain','origin',m['commit']+':'+target],capture_output=True,text=True);(V/'COPPER_FOYER_PUSH_RESULT.json').write_text(json.dumps({'expected_head':m['parent'],'force_used':False,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n');assert p.returncode==0,'inspect remote before retry'
else:assert observed==m['commit'],'unexpected remote head'
if not S.exists():subprocess.run(['git','clone','--bare','--depth=1','--filter=blob:none','--single-branch','--branch',target.removeprefix('refs/heads/'),'https://github.com/evesloan/Astraea.git',str(S)],check=True)
assert not(S/'objects/info/alternates').exists();assert git(S,'rev-parse','HEAD').decode().strip()==m['commit'];header=git(S,'cat-file','commit','HEAD').decode().split('\n\n',1)[0].splitlines();assert 'tree '+m['tree'] in header and 'parent '+m['parent'] in header
# Prior checkpoint independently protects unchanged files; fetch only the changed required blob hashes below.
blobs={r['git_blob_sha']for r in m['files'].values()};present=set(git(S,'cat-file','--batch-all-objects','--batch-check=%(objectname)').decode().splitlines());missing=blobs-present
if missing:subprocess.run(['git','-C',str(S),'fetch','--refetch','--filter=blob:none','--no-tags','--no-write-fetch-head','--recurse-submodules=no','--stdin','origin'],input=('\n'.join(sorted(missing))+'\n').encode(),check=True)
tree={}
for line in git(S,'ls-tree','-r','HEAD').decode().splitlines():
 desc,path=line.split('\t',1);mode,kind,blob=desc.split();tree[path]=(mode,blob)
env=os.environ.copy();env['GIT_NO_LAZY_FETCH']='1';proc=subprocess.Popen(['git','-C',str(S),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,env=env);verified={}
for blob in sorted(blobs):
 proc.stdin.write((blob+'\n').encode());proc.stdin.flush();head=proc.stdout.readline().decode().split();assert head[:2]==[blob,'blob'];n=int(head[2]);b=proc.stdout.read(n);assert proc.stdout.read(1)==b'\n';assert hashlib.sha1(b'blob '+str(n).encode()+b'\0'+b).hexdigest()==blob;verified[blob]=(n,hashlib.sha256(b).hexdigest())
proc.stdin.close();assert proc.wait()==0
for path,row in m['files'].items():assert tree[path]==(row['mode'],row['git_blob_sha'])and verified[row['git_blob_sha']]==(row['bytes'],row['sha256']),path
cp=git(S,'show','HEAD:CHECKPOINT.json');assert hashlib.sha256(cp).hexdigest()==m['checkpoint_sha256'];assert{k:len(v['files'])for k,v in json.loads(cp)['projects'].items()}==m['counts']
assert git(R,'write-tree','--missing-ok').decode().strip()==m['tree'];subprocess.run(['git','-C',str(R),'reset','--soft',m['commit']],check=True)
report={**m,'status':'PASS_COPPER_FOYER_INDEPENDENT_REMOTE_BYTES','changed_file_readbacks':len(m['files']),'unique_blobs':len(blobs),'local_alternates_used':False,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'whole_build_complete':False};(V/'COPPER_FOYER_CHECKPOINT_REMOTE_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',m['commit'],len(m['files']),len(blobs),flush=True)
