from pathlib import Path
import subprocess,json,time,sys
W=Path(__file__).resolve().parent;n=sys.argv[1];script=sys.argv[2]if len(sys.argv)>2 else'res://tests/group8/validate_dining_fixture_adaptation.gd';log=W/('RUNTIME'+n+'.log');assert not log.exists();start=time.time();peak=0;reason=''
with log.open('w')as out:
 p=subprocess.Popen(['godot','--headless','--path','/workspace/group8-current-main-test-001/Game','--fixed-fps','60','--quit-after','40000','--script',script],stdout=out,stderr=subprocess.STDOUT)
 while p.poll()is None:
  time.sleep(2);s=log.read_text(errors='replace')
  try:
   status=Path('/proc/'+str(p.pid)+'/status').read_text();rss=int(next(l for l in status.splitlines()if l.startswith('VmRSS:')).split()[1]);peak=max(peak,rss)
  except(FileNotFoundError,StopIteration):pass
  if'ERROR:'in s or'Assertion failed'in s:reason='Runtime assertion/error;raw log retained';p.terminate();break
  if time.time()-start>600 or peak>14800*1024:reason='Bounded wall-time or memory hold';p.terminate();break
 code=p.wait();s=log.read_text(errors='replace');ok=code==0 and'GROUP8 DINING FIXTURE PASS:'in s and'ERROR:'not in s and'Assertion failed'not in s
 (W/('RUNTIME'+n+'_PROCESS.json')).write_text(json.dumps({'status':'PASS'if ok else'HOLD','exit_code':code,'wall_seconds':round(time.time()-start,3),'peak_rss_kib':peak,'reason':reason,'script':script},indent=2)+'\n');print(s[-6500:]);print('status',ok,'exit',code)
