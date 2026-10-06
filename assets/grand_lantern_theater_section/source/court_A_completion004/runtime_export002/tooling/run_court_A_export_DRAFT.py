"""Prepared bounded two-thread source job; requires fresh parent slot approval.
Not executed during preparation. Runs Court-only export, pure normal repack and
independent binary QA; no source save, renderer, Game import or installation.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,resource,subprocess,sys,time
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--gate',type=Path);a=p.parse_args()
 if not a.run:print('PREPARED_NOT_RUN: --run --gate NEW_REVIEWED_GATE required; no engine started');return
 assert a.gate is not None;gate=json.loads(a.gate.read_text());plan=json.loads((D/'EXPORT_PLAN.json').read_text())
 for key in ['parent_authorized_export','source_engine_slot_granted','independent_retention_verified']:assert gate.get(key)is True,key
 assert gate['production_install_authorized']is False
 artifact_pins=json.loads((D/'PREPARATION_RECEIPT.json').read_text())['artifact_sha256']
 for rel,h in artifact_pins.items():assert sha(D/rel)==h,('Prepared artifact changed',rel)
 assert gate['source_sha256']==plan['source_sha256'] and gate['export_script_sha256']==sha(D/'export_court_A_DRAFT.py')
 for path,h in plan['input_sha256'].items():assert sha(path)==h
 assert sha(gate['independent_retention_receipt'])==gate['independent_retention_receipt_sha256']
 assert not(D/'raw_export001').exists()and not(D/'packed_export001').exists()
 run=D/'source_job001';run.mkdir(exist_ok=False);env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',MALLOC_ARENA_MAX='2')
 for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:q=run/sub;q.mkdir();env[key]=str(q)
 jobs=[['blender','-b','-t','2','--factory-startup','--python',str(D/'export_court_A_DRAFT.py'),'--','--export','--gate',str(a.gate.resolve())],
       [sys.executable,'-B',str(D/'repack_court_A_normals_DRAFT.py'),'--repack'],[sys.executable,'-B',str(D/'check_court_A_export_DRAFT.py'),'--check']]
 receipts=[];start=time.monotonic()
 for label,cmd in zip(['source_export','normal_repack','independent_binary_check'],jobs):
  with(run/(label+'.log')).open('x')as log:result=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
  text=(run/(label+'.log')).read_text(errors='replace');bad=any(x in text for x in ['Traceback','AssertionError','Segmentation fault','Error:'])
  receipts.append({'phase':label,'returncode':result.returncode,'error_text':bad})
  if result.returncode or bad:break
 success=len(receipts)==3 and all(r['returncode']==0 and not r['error_text']for r in receipts)
 unchanged=all(sha(path)==h for path,h in plan['input_sha256'].items())
 qa=D/'packed_export001/INDEPENDENT_EXPORT_QA.json';success=success and unchanged and qa.exists()and json.loads(qa.read_text()).get('passed')is True
 report={'status':'PASS_SOURCE_EXPORT_BINARY_QA_ONLY'if success else'FAILED_PRESERVED_DO_NOT_ADOPT','phases':receipts,'source_inputs_unchanged':unchanged,'threads':2,'seconds':round(time.monotonic()-start,3),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gate_sha256':sha(a.gate),'qa_sha256':sha(qa)if qa.exists()else None,'peak_child_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'runtime_installed':False,'native_visual_or_collision_acceptance':False}
 with(run/'RECEIPT.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report));sys.exit(0 if success else 1)
if __name__=='__main__':main()
