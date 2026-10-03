"""Session-scoped cloud graphical review runner. No network, OS setup or arbitrary jobs.
Launch from the cloud desktop terminal so Godot inherits its graphical display.
Only this project's fixed capture workflow is accepted. A STOP file exits the runner.
"""
from pathlib import Path
import subprocess,json,time,os
ROOT=Path(__file__).resolve().parents[1]
QUEUE=Path('/workspace/shared/astraea-review-queue');QUEUE.mkdir(exist_ok=True)
(QUEUE/'runner.json').write_text(json.dumps({'pid':os.getpid(),'project':str(ROOT),'started_unix':time.time(),'display_present':bool(os.environ.get('DISPLAY'))}))
while not (QUEUE/'STOP').exists():
 requests=sorted(QUEUE.glob('*.request'))
 if not requests:
  time.sleep(1);continue
 for request in requests:
  task=json.loads(request.read_text())
  identifier=request.stem
  if task!={'kind':'capture_current_ship'}:
   result={'status':'rejected','reason':'Only the fixed current-ship capture job is supported'}
  else:
   log=QUEUE/(identifier+'.log')
   start=time.time()
   try:
    with log.open('w') as output:
     process=subprocess.run(['godot','--path',str(ROOT),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--','--capture-validation','--capture-d06','--capture-aquatic','--capture-staff'],stdout=output,stderr=subprocess.STDOUT,timeout=180)
    errors=[line for line in log.read_text().splitlines() if 'ERROR:' in line or 'Assertion failed' in line]
    result={'status':'passed' if process.returncode==0 and not errors else 'failed','exit_code':process.returncode,'errors':errors,'seconds':round(time.time()-start,3),'scope':'Graphical capture execution only; appearance requires review, not target GPU performance'}
   except subprocess.TimeoutExpired:
    result={'status':'failed','reason':'Capture exceeded180seconds'}
  (QUEUE/(identifier+'.result.json')).write_text(json.dumps(result,indent=2)+'\n')
  request.rename(QUEUE/(identifier+'.completed-request'))
(QUEUE/'runner-stopped.json').write_text(json.dumps({'stopped_unix':time.time()}))
