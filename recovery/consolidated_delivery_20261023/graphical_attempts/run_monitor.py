import json,os,subprocess,time
from pathlib import Path
p=Path('/tmp/astraea-graphical-1091d34e')
env=dict(os.environ,DISPLAY=':97',XDG_DATA_HOME='/tmp/astraea-graphical-userdata-1091d34e',LIBGL_ALWAYS_SOFTWARE='1')
cmd=['/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64','--display-driver','x11','--rendering-method','gl_compatibility','--audio-driver','Dummy','--path','/workspace/Astraea-recovered-e6274e77-20261021/Game','--script',str(p/'check.gd')]
peak=0; reason=None; start=time.monotonic()
with (p/'RUN.log').open('w') as log:
 proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
 (p/'ACTIVE.json').write_text(json.dumps({'pid':proc.pid,'command':cmd,'audio':'Dummy'}))
 while proc.poll() is None:
  time.sleep(2)
  try:
   fields={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in Path(f'/proc/{proc.pid}/status').read_text().splitlines() if ':' in x}
   peak=max(peak,int(fields.get('VmRSS','0 kB').split()[0])*1024)
  except FileNotFoundError: pass
  mem={x.split(':',1)[0]:int(x.split(':',1)[1].split()[0])*1024 for x in Path('/proc/meminfo').read_text().splitlines()}
  out=(p/'RUN.log').read_text(errors='replace')
  if 'ERROR:' in out or 'SCRIPT ERROR:' in out: reason='runtime error guard'
  elif mem['MemAvailable']<1500000000: reason='memory reserve guard'
  elif time.monotonic()-start>300: reason='bounded graphical readiness deadline'
  if reason:
   proc.terminate()
   try: proc.wait(timeout=10)
   except subprocess.TimeoutExpired: proc.kill();proc.wait()
   break
 result={'source':'1091d34e914ad9c36f7ff487ed72e4d959a96886','exit_code':proc.wait(),'seconds':time.monotonic()-start,'peak_rss_bytes':peak,'stop_reason':reason,'audio':'explicit Dummy; cloud has no physical audio device','renderer':'existing Compatibility with Mesa software rendering; not target-device FPS'}
(p/'MONITOR.json').write_text(json.dumps(result,indent=2)+'\n')
(p/'ACTIVE.json').unlink()
print(json.dumps(result))
