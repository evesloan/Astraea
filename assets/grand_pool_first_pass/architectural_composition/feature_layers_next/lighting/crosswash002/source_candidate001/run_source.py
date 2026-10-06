"""One serial2-thread source build/reopen/host QA; new scratch outputs only."""
from pathlib import Path
import hashlib,json,sys,subprocess,os,time,datetime
S=Path(__file__).resolve().parent;h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pins=json.loads((S/'RUN_PINS.json').read_text());builder=S/'build_feature_lighting.py';verifier=S/'reopen_feature_lighting002.py';source=S/'source/AST-AQU-016_pool_feature_lighting.blend';qa=S/'qa';receipt=qa/'SOURCE_JOB001.json'
assert not source.exists()and not receipt.exists();assert h(builder)==pins['builder_sha256']and h(verifier)==pins['verifier_sha256']and h(S/'PREPARED_SCOPE.json')==pins['scope_sha256'];qa.mkdir(exist_ok=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',BLIS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2');now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();result={'status':'RUNNING','started_utc':now(),'scope':'Source build, independent Blender snapshot, host exact geometry QA; no export/render/Game changes.','processes':[],'script_sha256':pins}
def save():receipt.write_text(json.dumps(result,indent=2)+'\n')
def run(label,command):
 assert h(builder)==pins['builder_sha256']and h(verifier)==pins['verifier_sha256'];log=qa/(label+'.log');rec={'label':label,'command':command,'started_utc':now(),'timeout_s':300};result['processes'].append(rec);save();print('SOURCE START',label,rec['started_utc'],flush=True);t=time.monotonic()
 with log.open('x')as f:r=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
 rec.update(exit_code=r.returncode,elapsed_s=time.monotonic()-t,finished_utc=now(),log_sha256=h(log));save();print('SOURCE END',label,r.returncode,flush=True);assert r.returncode==0,(label,str(log))
try:
 base=['/usr/bin/blender','--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','1','--python']
 run('build',base+[str(builder)]);build=json.loads((qa/'BUILD_RECEIPT.json').read_text());source_sha=h(source);assert build['source_sha256']==source_sha
 run('reopen_snapshot',base+[str(verifier),'--','--stage','snapshot','--run-id','reopen001_snapshot','--expected-source-sha256',source_sha])
 snap=json.loads((qa/'reopen001_snapshot/REOPEN_RECEIPT.json').read_text());assert snap['status']=='PASS_SNAPSHOT_ONLY'and not snap['issues']and h(source)==source_sha
 run('reopen_geometry',['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12',str(verifier),'--stage','geometry','--run-id','reopen001_geometry','--snapshot-run-id','reopen001_snapshot','--expected-source-sha256',source_sha])
 final=json.loads((qa/'reopen001_geometry/REOPEN_RECEIPT.json').read_text());assert final['status']=='PASS_SOURCE_ONLY'and not final['issues']and h(source)==source_sha and final['inputs_unchanged_at_finish']
 result.update(status='PASS_SOURCE_BUILD_AND_INDEPENDENT_REOPEN',finished_utc=now(),source_sha256=source_sha,reopen_receipt_sha256=h(qa/'reopen001_geometry/REOPEN_RECEIPT.json'),compound_leaf_shadow='Separate retained record:29clear,1actual leaf interception; native visual coverage pending.',exports=[],renders=[],installed=False);save();print(json.dumps(result),flush=True)
except BaseException as exc:
 result.update(status='FAILED_PRESERVE_OUTPUTS',finished_utc=now(),error=repr(exc));save();raise
