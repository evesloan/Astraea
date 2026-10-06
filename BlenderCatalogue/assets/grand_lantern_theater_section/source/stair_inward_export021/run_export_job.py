"""Read-only preflight by default. The explicit run requires parent review and a free source slot.
Later: --run --source-slot-released --manifest-sha256 <reviewed digest>
Two serial Blender processes, two threads each; then pure binary QA. No render/Game/Catalogue write.
"""
from pathlib import Path
import sys,os,json,hashlib,argparse,subprocess,time,datetime
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from job_common import *
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true');parser.add_argument('--source-slot-released',action='store_true');parser.add_argument('--manifest-sha256');args=parser.parse_args()
 manifest=verify_pins();assert not OUT.exists()and not OUT.is_symlink(),'Preserve any existing output/partial attempt; do not overwrite or repeat'
 assert OUT.parent.resolve()==R and SOURCE.resolve()!=GLB.resolve()
 if not args.run:print('PASS_READ_ONLY_EXPORT_PREFLIGHT; no engine or export started');return
 assert args.source_slot_released and args.manifest_sha256==sha(R/'EXECUTION_MANIFEST.json'),'Explicit reviewed manifest and parent source-slot release required'
 OUT.mkdir(exist_ok=False);env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',BLIS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
 receipt={'started_utc':now(),'status':'RUNNING_SOURCE_ONLY_EXPORT_JOB','manifest_sha256':args.manifest_sha256,'wrapper_sha256':sha(__file__),'source_sha256':SOURCE_SHA,'blender_threads':2,'serial_blender_processes':2,'rendering':False,'runtime_writes':False,'catalogue_writes':False,'source_save':False,'phases':[]}
 failure=None
 try:
  for phase,script,engine,limit in [('snapshot','snapshot_channels.py',True,120),('export','export_channels.py',True,120),('binary_qa','check_binary.py',False,90)]:
   verify_pins();command=['/usr/bin/blender','-b','--factory-startup','-t','2','--python-exit-code','9','--python',str(R/script)]if engine else[sys.executable,str(R/script)]
   start=time.monotonic();log=OUT/(phase+'.log')
   with log.open('x')as output:process=subprocess.run(command,stdout=output,stderr=subprocess.STDOUT,env=env,timeout=limit)
   result={'phase':phase,'returncode':process.returncode,'seconds':round(time.monotonic()-start,3),'limit_seconds':limit,'log_sha256':sha(log)};receipt['phases'].append(result);print(result,flush=True)
   assert process.returncode==0,('Phase failed',phase,process.returncode)
  qa=read(QA);assert qa['status']=='PASS_INDEPENDENT_BINARY_EQUIVALENCE_WITH_RETAINED_CORNER_LIMIT'
  verify_pins();receipt['status']='PASS_SCRATCH_SOURCE_ONLY_EXPORT_AND_BINARY_QA';receipt['source_unchanged']=True;receipt['outputs_sha256']={p.name:sha(p)for p in [SNAPSHOT,GLB,EXPORT_RECEIPT,QA]}
 except BaseException as error:
  failure=error;receipt['status']='FAILED_PRESERVE_ALL_OUTPUTS';receipt['error_type']=type(error).__name__;receipt['error']=str(error)
  try:verify_pins();receipt['source_unchanged']=True
  except BaseException as pin_error:receipt['input_pin_error']=str(pin_error)
 finally:
  receipt['finished_utc']=now();write_new(OUT/'EXPORT_JOB_RECEIPT.json',receipt)
 print(receipt['status'],flush=True)
 if failure:raise failure
if __name__=='__main__':main()
