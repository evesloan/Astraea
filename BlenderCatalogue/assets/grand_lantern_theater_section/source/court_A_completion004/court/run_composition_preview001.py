from pathlib import Path
import os,sys,json,hashlib,subprocess,time,resource,datetime
R=Path(__file__).resolve().parent;W=R/'reopen_qa001/winding_repair001/authored_source001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();report=json.loads((W/'REOPEN_REPORT.json').read_text());assert report['status']=='PASS_SOURCE_ONLY'and report['sha256']=='7456c069315f3ed1f74c327ba0af53a90942cd1549b6905d3abe58ba76633c49'
jobs=[('compose',R/'compose_court_A_review002.py','60409262a61a9324d7eb0c8040401a1a1a002d0aa65638f15ceb1551c5422e48'),('render',R/'render_court_A_composition001.py','1d20e5c1ad9b8fb4341f3db78e0e564fd33c6af2b105c2d54ecc129b14480f53')]
for _,p,h in jobs:assert sha(p)==h
run=R/'composition_job001';run.mkdir(exist_ok=False);env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',MALLOC_ARENA_MAX='2')
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:p=run/sub;p.mkdir();env[key]=str(p)
receipt={'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'threads':2,'standalone_source_sha256':report['sha256'],'jobs':[]};(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');okay=True
for label,script,h in jobs:
 start=time.monotonic();expr='import sys,runpy;sys.dont_write_bytecode=True;sys.argv='+repr([str(script)])+';runpy.run_path('+repr(str(script))+',run_name="__main__")'
 with(run/(label+'.log')).open('x')as log:r=subprocess.run(['blender','-b','-t','2','--factory-startup','--python-expr',expr],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=420)
 text=(run/(label+'.log')).read_text(errors='replace');errors=[line for line in text.splitlines()if'Traceback'in line or'Error:'in line or'AssertionError'in line];passed=r.returncode==0 and not errors;receipt['jobs'].append({'job':label,'script_sha256':h,'seconds':round(time.monotonic()-start,3),'returncode':r.returncode,'errors':errors,'passed':passed});(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 if not passed:okay=False;break
final=R/'composition_view001/RECEIPT.json';okay=okay and final.exists();receipt.update(status='CAPTURED_SOURCE_COMPOSITION_REVIEW_PENDING'if okay else'FAILED_PRESERVED',peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,render_receipt_sha256=sha(final)if final.exists()else None,standalone_source_unchanged=sha(Path(report['source']))==report['sha256']);(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));sys.exit(0 if okay else 1)
