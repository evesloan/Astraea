from pathlib import Path
import os,sys,json,hashlib,subprocess,time,resource,datetime
R=Path(__file__).resolve().parent;W=R/'reopen_qa001/winding_repair001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
jobs=[('repair',W/'repair_saved_source.py','439ceda9ae088f6028f55c71be4b9a9cccda26c80299fccada89cf5919b75937',[]),('reopen',R/'reopen_qa001/reopen_court_A_winding_readonly.py','6df0377418129d03c52eabd4ccf3d7d7988aeb5670994eb100e95f01fe3b1863',['--','--check'])]
for _,s,h,_ in jobs:assert sha(s)==h
run=R/'source_winding_run001';run.mkdir(exist_ok=False);env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',MALLOC_ARENA_MAX='2')
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:p=run/sub;p.mkdir();env[key]=str(p)
old=R/'printed_materials001/authored_preview001/AST-CUL-005_arrival_court_A_004.blend';original=sha(old);assert original=='54433eb9a9efba6509e79e783deaf9a5fe27c43d449ee63ad1e1bad257c2be72'
receipt={'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'threads':2,'original_source_sha256':original,'jobs':[]};(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');okay=True
for label,script,h,args in jobs:
 start=time.monotonic();expr='import sys,runpy;sys.dont_write_bytecode=True;sys.argv='+repr([str(script)]+args)+';runpy.run_path('+repr(str(script))+',run_name="__main__")'
 with(run/(label+'.log')).open('x')as log:r=subprocess.run(['blender','-b','-t','2','--factory-startup','--python-expr',expr],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
 text=(run/(label+'.log')).read_text(errors='replace');errors=[line for line in text.splitlines()if'Traceback'in line or'Error:'in line or'AssertionError'in line];passed=r.returncode==0 and not errors
 receipt['jobs'].append({'job':label,'script_sha256':h,'seconds':round(time.monotonic()-start,3),'returncode':r.returncode,'errors':errors,'passed':passed});(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 if not passed:okay=False;break
assert sha(old)==original
report=W/'authored_source001/REOPEN_REPORT.json';okay=okay and report.exists()and json.loads(report.read_text())['status']=='PASS_SOURCE_ONLY';receipt.update(status='PASS_CORRECTED_SOURCE_REOPEN'if okay else'FAILED_PRESERVED',original_source_unchanged=True,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,report_sha256=sha(report)if report.exists()else None);(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));sys.exit(0 if okay else 1)
