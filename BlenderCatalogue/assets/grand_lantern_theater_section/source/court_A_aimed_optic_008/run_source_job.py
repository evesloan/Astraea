from pathlib import Path
import sys,os,json,hashlib,subprocess,time,datetime
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();m=json.loads((R/'EXECUTION_MANIFEST.json').read_text());assert '--source-slot-released'in sys.argv
for p,h in m['pins'].items():assert sha(p)==h
assert not(R/'SOURCE_JOB_RECEIPT.json').exists();assert not(R/'AST-CUL-005_CourtA_aimed_optic_008.blend').exists()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1');record={'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':[],'Game_writes':False,'rendering':False};save=lambda:(R/'SOURCE_JOB_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n');save()
try:
 for phase in ['build','reopen']:
  script=R/(phase+'_source.py');start=time.monotonic()
  with(R/(phase+'.log')).open('x')as f:r=subprocess.run(['/usr/bin/blender','-b','--factory-startup','-t','2','--python-exit-code','9','--python',str(script)],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90)
  log=(R/(phase+'.log')).read_text();row={'phase':phase,'returncode':r.returncode,'seconds':round(time.monotonic()-start,3),'log_sha256':sha(R/(phase+'.log'))};record['phases'].append(row);save();print(row,flush=True);assert r.returncode==0 and 'Traceback'not in log
 record.update(status='PASS_SOURCE_BUILD_REOPEN_NATIVE_PENDING',source_sha256=sha(R/'AST-CUL-005_CourtA_aimed_optic_008.blend'),reopen_qa_sha256=sha(R/'REOPEN_QA.json'))
except BaseException as e:record.update(status='FAILED_PRESERVED',error=str(e));raise
finally:record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print(record['status'])
