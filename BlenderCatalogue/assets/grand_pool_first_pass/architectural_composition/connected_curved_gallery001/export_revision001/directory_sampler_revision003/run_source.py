from pathlib import Path
import json,hashlib,os,subprocess,datetime,time
B=Path(__file__).parent;R=B/'job001';assert not R.exists();R.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();pins=json.loads((B/'SOURCE_JOB_PINS.json').read_text())['inputs']
for p,h in pins.items():assert sha(p)==h,p
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',BLIS_NUM_THREADS='2')
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=R/name;p.mkdir();env[key]=str(p)
out={'status':'RUNNING','started_utc':now(),'threads':2,'source_only':True,'Game_or_Catalogue_writes':False,'steps':[]}
def save():(R/'RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n')
save()
try:
 for label in ['build','reopen']:
  cmd=['/usr/bin/blender','--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','1','--python',str(B/(label+'_source.py'))];t=time.monotonic();print('SOURCE_START',label,now(),flush=True)
  with (R/(label+'.log')).open('x')as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=240)
  out['steps'].append({'label':label,'returncode':p.returncode,'seconds':time.monotonic()-t,'log_sha256':sha(R/(label+'.log'))});save();assert p.returncode==0,(label,p.returncode)
 for p,h in pins.items():assert sha(p)==h,p
 out.update(status='PASS_SOURCE_SAMPLER_SUCCESSOR_BUILD_REOPEN',finished_utc=now())
except BaseException as e:out.update(status='FAILED_PRESERVE_EVIDENCE',finished_utc=now(),error=repr(e));raise
finally:save()
print(json.dumps(out),flush=True)
