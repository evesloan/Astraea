#!/usr/bin/env python3
"""One bounded headless physics attempt. Independent memory/error/time guard."""
import hashlib,json,os,selectors,signal,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
GIB=1024**3

def memory():
 values={}
 for l in Path('/proc/meminfo').read_text().splitlines():
  k,v=l.split(':',1);values[k]=int(v.split()[0])*1024
 available=values['MemAvailable'];cg={}
 for name in ['memory.max','memory.current','memory.swap.max']:
  f=Path('/sys/fs/cgroup')/name
  if f.exists():cg[name]=f.read_text().strip()
 if cg.get('memory.max','max')!='max':available=min(available,int(cg['memory.max'])-int(cg['memory.current']))
 return {'effective_available_bytes':available,'system_available_bytes':values['MemAvailable'],'system_total_bytes':values['MemTotal'],'swap_total_bytes':values['SwapTotal'],'cgroup':cg}

def main():
 inputs=Path(os.getenv('ASTRAEA_CARRY_INPUTS',str(HERE/'prepared'))).resolve()
 status=json.loads((inputs/'closure_status.json').read_text());assert not status['unknown']
 rows=json.loads((inputs/'source_map.json').read_text())
 for row in rows:assert hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()==row['sha256']
 run_name=os.getenv('ASTRAEA_CARRY_RUN','run-001');out=HERE/'runs'/run_name;out.mkdir(parents=True,exist_ok=False)
 before=memory();receipt={'preflight':before,'min_available_bytes':3*GIB,'max_rss_bytes':2*GIB,'max_wall_seconds':300,'simulated_fixed_hz':60,'source_count':len(rows),'graphical':False}
 (out/'preflight.json').write_text(json.dumps(receipt,indent=2)+'\n')
 if before['effective_available_bytes']<5*GIB:raise SystemExit('Unsafe preflight: need 5GiB available for 2GiB bounded cap + 3GiB reserve')
 env=os.environ.copy()
 for k,dirname in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
  p=out/'xdg'/dirname;p.mkdir(parents=True);env[k]=str(p)
 env.update(ASTRAEA_CARRY_MAP=str(inputs/'source_map.json'),ASTRAEA_CARRY_BASE=status['retained_pack'],ASTRAEA_CARRY_OVERLAY=str(out/'current-inputs.pck'),ASTRAEA_CARRY_RESULT=str(out/'result.json'))
 script=HERE/os.getenv('ASTRAEA_CARRY_SCRIPT','validate_actual_player_carry.gd')
 env['ASTRAEA_CARRY_SUCCESSOR']=str(HERE/'committed_pose_motor.gd')
 receipt['motor_variant']=env.get('ASTRAEA_CARRY_MOTOR','unchanged');receipt['extended']=env.get('ASTRAEA_CARRY_EXTEND','0')
 cmd=['/usr/local/bin/godot','--headless','--audio-driver','Dummy','--fixed-fps','60','--path',str(HERE/'test-project'),'--script',str(script),'--quit-after','300000']
 receipt['command']=cmd;receipt['test_sha256']=hashlib.sha256(script.read_bytes()).hexdigest()
 receipt['successor_sha256']=hashlib.sha256((HERE/'committed_pose_motor.gd').read_bytes()).hexdigest()
 print('START',out,flush=True);started=time.monotonic();proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,start_new_session=True,bufsize=0)
 selector=selectors.DefaultSelector();selector.register(proc.stdout,selectors.EVENT_READ);pending=b'';abort=None;peak=0;minimum=before['effective_available_bytes'];last_watch=0
 with (out/'engine.log').open('wb') as log,(out/'memory.jsonl').open('w') as memlog:
  while proc.poll() is None:
   for key,_ in selector.select(.1):
    data=os.read(key.fd,65536)
    if not data:continue
    log.write(data);log.flush();pending+=data
    while b'\n' in pending:
     line,pending=pending.split(b'\n',1)
     text=line.decode('utf-8',errors='replace')
     if 'TRAM_CARRY ' in text or 'ERROR:' in text or 'SCRIPT ERROR' in text:print(text[:1800],flush=True)
     if 'SCRIPT ERROR:' in text or text.startswith('ERROR:'):abort='engine_error'
   now=time.monotonic()
   if now-last_watch>.25:
    last_watch=now;m=memory();rss=0
    try:
     for l in Path(f'/proc/{proc.pid}/status').read_text().splitlines():
      if l.startswith('VmRSS:'):rss=int(l.split()[1])*1024
    except FileNotFoundError:pass
    peak=max(peak,rss);minimum=min(minimum,m['effective_available_bytes']);memlog.write(json.dumps({'elapsed_seconds':now-started,'rss_bytes':rss,**m})+'\n');memlog.flush()
    if rss>2*GIB:abort='bounded_rss_limit'
    if m['effective_available_bytes']<3*GIB:abort='available_memory_reserve'
    if now-started>300:abort='wall_timeout'
   if abort and proc.poll() is None:
    os.killpg(proc.pid,signal.SIGTERM)
    try:proc.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL)
  rest=proc.stdout.read();log.write(rest)
  if rest:print(rest.decode(errors='replace')[-3000:],flush=True)
 receipt.update(exit_code=proc.wait(),abort_reason=abort,wall_seconds=time.monotonic()-started,peak_rss_bytes=peak,min_effective_available_bytes=minimum,result_present=(out/'result.json').exists())
 mismatches=[]
 for row in rows:
  if hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()!=row['sha256']:mismatches.append(row['path'])
 receipt['post_run_source_hash_mismatches']=mismatches
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
 raise SystemExit(1 if abort or mismatches or proc.returncode or not receipt['result_present'] else 0)
if __name__=='__main__':main()
