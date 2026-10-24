import subprocess,time,json,os,signal
from pathlib import Path
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');E=Path('/tmp/astraea-tram-r003')
command=json.loads((E/'command.json').read_text())
started=time.monotonic();peak=0;stop=None;maximum=420
with (E/'installed-world.log').open('wb')as output:
 p=subprocess.Popen(command,cwd=R,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll()is None:
  try:
   rows=Path('/proc/'+str(p.pid)+'/status').read_text().splitlines();rss=int(next(s.split()[1]for s in rows if s.startswith('VmRSS:')))*1024;peak=max(peak,rss)
  except (FileNotFoundError,StopIteration):rss=0
  if rss>13*1024**3:stop='13GiB owned-process RSS safety boundary'
  elif time.monotonic()-started>maximum:stop='420s bounded installed-world check deadline'
  if stop:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   break
  time.sleep(.5)
 result={'exit_code':p.wait(),'stop':stop,'seconds':round(time.monotonic()-started,3),'peak_rss_bytes':peak,'scope':'One source-only headless installed-world tram gate; no export, graphics FPS or passenger motion acceptance','command':command}
 (E/'MONITOR.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
