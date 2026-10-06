from pathlib import Path
import sys,subprocess,os,time,json,hashlib,argparse,datetime
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from common import *
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--source-slot-released',action='store_true');a=p.parse_args();pins();assert not OUT.exists()
if not a.run:print('PASS_PREPARED_TWO_MESH_SOURCE_INPUTS_NO_ENGINE');raise SystemExit
assert a.source_slot_released;OUT.mkdir(exist_ok=False);env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'1'};rows=[];r={'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'threads':2,'source_sha256':SOURCE_SHA,'steps':rows}
def save():(OUT/'JOB_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for label,script,engine in [('build','build_call_source.py',True),('reopen_export','reopen_export.py',True),('binary_qa','check_binary.py',False)]:
  cmd=['/usr/bin/blender','-b','--factory-startup','-t','2','--python-exit-code','9','--python',str(R/script)]if engine else[sys.executable,'-B',str(R/script)];start=time.monotonic()
  with(OUT/(label+'.log')).open('x')as log:process=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
  row={'label':label,'exit_code':process.returncode,'seconds':round(time.monotonic()-start,3),'log_sha256':sha(OUT/(label+'.log'))};rows.append(row);save();print(row,flush=True);assert process.returncode==0
 pins();assert read(OUT/'BINARY_QA.json')['status']=='PASS_ACTUAL_SOURCE_EXPORT_AND_CONTROL_FIT';r.update(status='PASS_SOURCE_REOPEN_EXPORT_FIT',source_blend_sha256=sha(BLEND),glb_sha256=sha(GLB),originals_unchanged=True)
except BaseException as e:r.update(status='FAILED_PRESERVED',error=str(e));raise
finally:r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print(r['status'])
