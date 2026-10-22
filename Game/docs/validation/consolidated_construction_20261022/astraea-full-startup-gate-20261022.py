import subprocess,time,os,signal,json
from pathlib import Path
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');E=R/'Game/docs/validation/consolidated_construction_20261022';log=E/'FULL_STARTUP_attempt001.log';assert not log.exists()
os.environ['DISPLAY']=':111';os.environ['LIBGL_ALWAYS_SOFTWARE']='1';os.environ['ASTRAEA_TRACE_STARTUP']='1'
start=time.monotonic();peak=0;stop=None
with log.open('w')as out:
 p=subprocess.Popen(['/usr/local/bin/godot','--display-driver','x11','--audio-driver','Dummy','--rendering-method','gl_compatibility','--path',str(R/'Game'),'--script','/tmp/astraea-startup-gate-20261022.gd'],stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll()is None:
  time.sleep(1)
  try:
   status=Path('/proc/'+str(p.pid)+'/status').read_text();rss=int(next(l.split()[1]for l in status.splitlines()if l.startswith('VmRSS:')))*1024;peak=max(peak,rss)
  except (FileNotFoundError,StopIteration):rss=0
  tail=log.read_text(errors='replace')[-20000:]
  mem={r.split(':')[0]:int(r.split()[1])*1024 for r in Path('/proc/meminfo').read_text().splitlines()if r.startswith('MemAvailable:')}
  if rss>6*1024**3:stop='6GiB diagnostic RSS guard'
  elif mem['MemAvailable']<1024**3:stop='1GiB available-memory guard'
  elif time.monotonic()-start>600:stop='600-second startup guard'
  elif 'ERROR:'in tail or 'SCRIPT ERROR:'in tail:stop='engine error; inspect retained log'
  if stop:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   break
 result={'command':'godot4.6.3 X11 GL Compatibility full main; Dummy audio','exit_code':p.wait(),'stop':stop,'seconds':round(time.monotonic()-start,2),'peak_rss_bytes':peak,'startup_process_passed':p.returncode==0 and stop is None,'graphical_editor_acceptance':False,'runtime_ready':(E/'FULL_STARTUP_RECEIPT.json').exists()}
(E/'FULL_STARTUP_attempt001.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
