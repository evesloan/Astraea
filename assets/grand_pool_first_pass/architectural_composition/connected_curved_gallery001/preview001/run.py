from pathlib import Path
import subprocess,os,json,hashlib,datetime,time
B=Path(__file__).parent;assert not(B/'RECEIPT.json').exists();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1');r={'status':'RUNNING','started_utc':now(),'threads':2,'Game_or_Catalogue_writes':False,'installed':False};(B/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=B/name;p.mkdir();env[key]=str(p)
t=time.monotonic()
try:
 with(B/'render.log').open('x')as f:p=subprocess.run(['/usr/bin/blender','--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','1','--python',str(B/'render.py')],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=450)
 r.update(returncode=p.returncode,seconds=time.monotonic()-t,finished_utc=now(),log_sha256=sha(B/'render.log'));assert p.returncode==0
 r.update(status='PASS_TWO_SOURCE_COMPOSITION_VIEWS',report_sha256=sha(B/'output/REPORT.json'))
except BaseException as e:r.update(status='FAILED_PRESERVE_EVIDENCE',finished_utc=now(),seconds=time.monotonic()-t,error=repr(e));raise
finally:(B/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r),flush=True)
