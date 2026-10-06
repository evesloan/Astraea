"""Deferred parent-coordinated source slot only. One serial subprocess at a
 time, two CPU threads, fixed timeouts, fresh scratch only. A CLI acknowledgement
 is not independent authorization. No native engine or shared writes.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import argparse,os,subprocess,time,datetime
from gate import gate,require,run_path,sha,read,write_new

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--parent-approved-source-slot',action='store_true');args=ap.parse_args()
    require(args.parent_approved_source_slot,'Parent must coordinate and authorize the source slot before launching')
    gate();out=run_path(args.run);require(not out.exists(),'Choose a fresh run label; preserve surviving work')
    logs=run_path(args.run+'_logs');require(not logs.exists(),'Preserve previous logs');logs.parent.mkdir(exist_ok=True);logs.mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',BLIS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
    env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
    base=['/usr/bin/blender','--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','1','--python']
    stages=[('pure_tests',['/usr/bin/python3',str(HERE/'test_preparation.py')],60),
        ('read_only_snapshot',base+[str(HERE/'snapshot_east_gallery.py'),'--','--run',args.run],300),
        ('selected_glb_export',base+[str(HERE/'export_east_gallery.py'),'--','--run',args.run],300),
        ('independent_equivalence',['/usr/bin/python3',str(HERE/'verify_east_gallery.py'),'--run',args.run],300)]
    records=[]
    try:
        for label,command,timeout in stages:
            gate();log=logs/(label+'.log');started=time.monotonic()
            with log.open('x') as handle:
                process=subprocess.Popen(command,env=env,stdout=handle,stderr=subprocess.STDOUT,start_new_session=True)
                try:code=process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    import signal
                    os.killpg(process.pid,signal.SIGKILL);process.wait();raise
            row=dict(stage=label,command=command,timeout_s=timeout,elapsed_s=time.monotonic()-started,exit_code=code,log=str(log),log_sha256=sha(log));records.append(row)
            write_new(logs/(label+'_RECEIPT.json'),row);require(code==0,'Stage failed; preserve all output: '+label)
        q=out/'equivalence/GLB_EQUIVALENCE.json';require(read(q)['status']=='PASS_FOUR_ACTUAL_SOURCE_GLB_EQUIVALENCE','Independent check did not pass')
        gate();write_new(logs/'RUN_RECEIPT.json',dict(status='PASS_FOUR_EXPORTS_AND_INDEPENDENT_EQUIVALENCE_ONLY',stages=records,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),equivalence_sha256=sha(q),native_imported=False,shared_project_writes=False))
    except BaseException as error:
        write_new(logs/'RUN_FAILURE.json',dict(status='FAILED_PRESERVE_ALL_OUTPUTS',stages=records,error=repr(error)));raise
if __name__=='__main__':main()
