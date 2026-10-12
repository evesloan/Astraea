from pathlib import Path
import subprocess,json,time,sys
W=Path(__file__).resolve().parent;number=sys.argv[1];script=sys.argv[2]if len(sys.argv)>2 else'res://tests/group8/validate_medical_privacy.gd';log=W/('MOTION_RUNTIME'+number+'.log');assert not log.exists();start=time.time()
with log.open('w')as out:
 p=subprocess.Popen(['godot','--headless','--path','/workspace/group8-current-main-test-001/Game','--fixed-fps','60','--quit-after','22000','--script',script],stdout=out,stderr=subprocess.STDOUT)
 while p.poll()is None:
  time.sleep(2);s=log.read_text(errors='replace')
  if'ERROR:'in s or'Assertion failed'in s or time.time()-start>600:p.terminate();break
 code=p.wait();s=log.read_text(errors='replace');ok=code==0 and'GROUP8 MEDICAL PRIVACY PASS:'in s
 (W/('MOTION_RUNTIME'+number+'_PROCESS.json')).write_text(json.dumps({'status':'PASS'if ok else'HOLD','exit_code':code,'wall_seconds':round(time.time()-start,3),'script':script},indent=2)+'\n');print(s[-7000:]);print('status',ok,'exit',code)
