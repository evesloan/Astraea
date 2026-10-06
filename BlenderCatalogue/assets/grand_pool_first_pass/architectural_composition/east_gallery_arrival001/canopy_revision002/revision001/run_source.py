from pathlib import Path
import json,hashlib,os,subprocess,datetime,time,sys
B=Path(__file__).resolve().parent;R=B/'job001';assert not R.exists();R.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
pins={str(p):sha(p)for p in [B/'CORE_PLAN.json',B/'CORE_REVIEW.json',B/'build_correction.py',B/'reopen_correction.py',B/'review_core.py']}
assert json.loads((B/'CORE_REVIEW.json').read_text())['status']=='PASS_CORE_PURE_GEOMETRY'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',BLIS_NUM_THREADS='2')
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=R/name;p.mkdir();env[key]=str(p)
out={'status':'RUNNING','started_utc':now(),'pins':pins,'steps':[],'threads':2,'Game_or_Catalogue_writes':False,'exports':[],'renders':[]}
def save():(R/'RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n')
save()
base=['/usr/bin/blender','--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','1','--python']
try:
 for label,cmd in [('build',base+[str(B/'build_correction.py')]),('reopen',base+[str(B/'reopen_correction.py')]),('evaluated_fit',[sys.executable,str(B/'review_core.py'),'--plan',str(B/'source001/qa/REOPEN_EVALUATED_CORE.json'),'--output',str(B/'ACTUAL_CORE_REVIEW.json')])]:
  print('SOURCE_START',label,now(),flush=True);start=time.monotonic()
  with (R/(label+'.log')).open('x')as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=240)
  out['steps'].append({'label':label,'returncode':p.returncode,'seconds':time.monotonic()-start,'log_sha256':sha(R/(label+'.log'))});save();print('SOURCE_END',label,p.returncode,flush=True);assert p.returncode==0
 for p,h in pins.items():assert sha(p)==h
 out.update(status='PASS_CORRECTED_SOURCE_BUILD_REOPEN_FIT',finished_utc=now(),source=json.loads((B/'source001/qa/BUILD_RECEIPT.json').read_text()))
except BaseException as e:out.update(status='FAILED_PRESERVE_EVIDENCE',finished_utc=now(),error=repr(e));raise
finally:save()
print(json.dumps(out),flush=True)
