"""One two-thread source-light composition view; new scratch pixels only."""
from pathlib import Path
import os,json,hashlib,subprocess,datetime,time
S=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
pins=json.loads((S/'PREVIEW_PINS.json').read_text())
for p,h in pins['sha256'].items():assert sha(p)==h,p
assert not(S/'RECEIPT.json').exists()and not(S/'output').exists()
assert json.loads((S.parent/'qa/INDEPENDENT_REOPEN.json').read_text())['status']=='PASS_EXACT_COMPOSED_SOURCE_REOPEN'
receipt={'status':'RUNNING','started_utc':now(),'scope':'One uninstalled source lighting/composition study. No saved source changes, export or Game operation.'}
save=lambda:(S/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
command=['/usr/bin/blender','--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','1','--python',str(S/'render.py')]
receipt['command']=command;save();print('POOL BAY LIGHT STUDY START',receipt['started_utc'],flush=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',BLIS_NUM_THREADS='2')
try:
 start=time.monotonic()
 with(S/'render.log').open('x')as log:done=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
 receipt.update(finished_utc=now(),elapsed_s=time.monotonic()-start,exit_code=done.returncode,log_sha256=sha(S/'render.log'));assert done.returncode==0,'Preserve failed render log'
 for p,h in pins['sha256'].items():assert sha(p)==h,p
 receipt.update(status='SOURCE_LIGHT_STUDY_READY_FOR_PIXEL_REVIEW',all_inputs_unchanged=True,image_sha256=sha(S/'output/upper_gallery_source_light_study.png'));save()
except BaseException as exc:
 receipt.update(status='FAILED_PRESERVE_OUTPUTS',finished_utc=now(),error=repr(exc));save();raise
print(receipt['status'],flush=True)
