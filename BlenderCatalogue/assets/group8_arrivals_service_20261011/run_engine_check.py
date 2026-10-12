from pathlib import Path
import subprocess,json,time,sys
W=Path(__file__).resolve().parent;R=W.parents[2]
attempt=sys.argv[1] if len(sys.argv)>1 else '001'
project=Path(sys.argv[2]) if len(sys.argv)>2 else R/'Game'
log=W/('RUNTIME'+attempt+'.log');started=time.perf_counter()
process=subprocess.Popen(['godot','--headless','--path',str(project),'--fixed-fps','60','--quit-after','60000','--script','res://tests/group8/validate_arrivals_service.gd'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
errors=[];passed=False
with log.open('w')as out:
    for line in process.stdout:
        out.write(line);out.flush()
        if 'GROUP8 ARRIVALS PASS:' in line:passed=True
        if 'ERROR:' in line or 'Assertion failed' in line or 'Parse Error' in line:
            errors.append(line.strip());process.terminate()
process.wait()
report={'status':'PASS' if process.returncode==0 and passed and not errors else 'FAIL','exit_code':process.returncode,'errors':errors,'wall_seconds':round(time.perf_counter()-started,3),'clock_mode':'fixed60; unchanged60Hz physics and time_scale1','scope':'Actual main plus one isolated group loader; full suite and hardware performance unaccepted'}
(W/('RUNTIME'+attempt+'_PROCESS.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));sys.exit(0 if report['status']=='PASS' else 1)
