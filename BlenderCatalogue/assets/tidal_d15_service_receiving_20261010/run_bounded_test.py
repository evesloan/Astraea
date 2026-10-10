from pathlib import Path
import os,json,subprocess,time,resource,sys
W=Path(__file__).resolve().parent;R=W.parents[2]/'Game';env=os.environ.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
 p=Path('/tmp/astraea_d15_test_scratch')/sub;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
env['ASTRAEA_TRACE_STARTUP']='1';env.pop('ASTRAEA_FORCE_ALL_RECEIVED_ROOMS',None)
steps=[('import',['godot','--headless','--path',str(R),'--editor','--quit']),('actual_main_bounded',['godot','--headless','--path',str(R),'--fixed-fps','60','--quit-after','2400','--script','res://tests/validate_tidal_d15_service_receiving.gd'])]
results=[]
for label,cmd in steps:
 log=W/('ENGINE_'+label+'.log');start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
 with log.open('w')as out:
  try:p=subprocess.run(cmd,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=600);code=p.returncode;timed=False
  except subprocess.TimeoutExpired:code=None;timed=True
 s=log.read_text();errors=[x for x in s.splitlines()if 'ERROR:'in x or'Assertion failed'in x or'Parse Error'in x];passed=code==0 and not errors and(label=='import'or'PASS: bounded D15 receiving and D13/D14 preservation'in s)
 row={'step':label,'exit_code':code,'passed':passed,'timed_out':timed,'errors':errors,'wall_seconds':round(time.monotonic()-start,3),'child_peak_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'clock_mode':'editor'if label=='import'else'fixed60','log':log.name};results.append(row);print(json.dumps(row),flush=True)
 (W/'BOUNDED_ENGINE_RUN.json').write_text(json.dumps({'status':'PASS'if len(results)==2 and all(x['passed']for x in results)else'RUNNING_OR_FAILED','steps':results,'full_suite_run':False,'scope':'One import barrier and one bounded actual-main D15 receiving / D13 preservation check; not whole-ship route audit or performance acceptance.'},indent=2)+'\n')
 if not passed:sys.exit(1)
sys.exit(0)
