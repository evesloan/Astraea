"""Root-only native capture on the existing approved graphical display. No import."""
from pathlib import Path
import os,json,hashlib,subprocess,threading,time,argparse,datetime
S=Path(__file__).resolve().parent;F=S/'FINAL_CURRENT_FREEZE.json';ENGINE=Path('/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64');ENGINE_SHA='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def newjson(p,d):
 with Path(p).open('x')as f:json.dump(d,f,indent=2);f.write('\n')
def need(x,m):
 if not x:raise RuntimeError(m)
def source(G):return {str(p.relative_to(G)):sha(p)for p in sorted(G.rglob('*'))if p.is_file()and p.relative_to(G).parts[0] not in ['.git','.godot','artifacts']}
def cache(G):return {str(p.relative_to(G)):sha(p)for p in sorted((G/'.godot').rglob('*'))if p.is_file()}
def delta(a,b):return [{'path':p,'before':a.get(p),'after':b.get(p)}for p in sorted(set(a)|set(b))if a.get(p)!=b.get(p)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');ap.add_argument('--release-reference');a=ap.parse_args()
 if not a.run:print('PREPARED_ONLY; root graphical display and three final focused gates required');return
 need(a.release_reference,'Root engine-slot release reference required');need(os.environ.get('DISPLAY')or os.environ.get('WAYLAND_DISPLAY'),'Use existing approved graphical terminal; do not switch display here');need(sha(ENGINE)==ENGINE_SHA,'Existing approved engine bytes changed');d=read(F);G=Path(d['game_root']);R=S/'launcher_run001';need(not R.exists()and not(S/'output').exists(),'Preserve prior capture output')
 for rel,h in d['prepared_files'].items():need(sha(S/rel)==h,'Prepared capture changed: '+rel)
 for info in d['required_focused_receipts'].values():need(sha(info['path'])==info['sha256'],'Focused receipt changed')
 before=source(G);need(before==d['game_inputs'],'Game source changed after freeze');before_cache=cache(G)
 for rel,h in d['import_cache_inputs'].items():need(before_cache.get(rel)==h,'Imported source cache changed')
 R.mkdir();env=os.environ.copy()
 for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=R/name;p.mkdir();env[key]=str(p)
 env['ASTRAEA_POOL_CAPTURE_PREP']=str(S);env['ASTRAEA_INSTALLED_GALLERY_FINISH_CAPTURE']='parent_approved'
 command=[str(ENGINE),'--audio-driver','Dummy','--path',str(G),'--resolution','1280x720','--script',str(S/'capture.gd')]
 receipt={'status':'RUNNING_CURRENT_INSTALLED_NATIVE_CAPTURE','release_reference':a.release_reference,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'engine_sha256':ENGINE_SHA,'renderer':'Project gl_compatibility unchanged','display_environment':{k:env.get(k)for k in ['DISPLAY','WAYLAND_DISPLAY']if env.get(k)},'timeout_seconds':300,'freeze_sha256':sha(F),'visual_acceptance':False};rp=R/'RECEIPT.json';newjson(rp,receipt);proc=None;timer=None;errors=[];lines=[];start=time.monotonic()
 try:
  with(R/'engine.log').open('x')as log:
   proc=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);timer=threading.Timer(300,proc.kill);timer.start()
   for line in proc.stdout:
    log.write(line);log.flush();lines.append(line)
    if any(x in line for x in ['ERROR:','Assertion failed','Parse Error']):
     errors.append(line.rstrip())
     if proc.poll()is None:proc.terminate()
   proc.wait();timer.cancel()
  need(proc.returncode==0 and not errors and 'INSTALLED_POOL_CONNECTED_FINISH_CAPTURE_COMPLETE'in''.join(lines),'Native capture or outside-floor comparison failed; preserve images/log')
  result=read(S/'output/RESULT.json');need(result['capture_count']==6 and result['outside_floor_comparison']['passed'],'Complete six views and outside-floor parity required')
  for c in result['captures']:need(sha(S/'output'/c['file'])==c['sha256']and c['fov']==72.0 and c['eye_delta_m']<.0001,'Exact historical camera/file mismatch')
  receipt.update(status='NATIVE_CAPTURE_AND_OUTSIDE_PARITY_PASS_VISUAL_REVIEW_PENDING',result_sha256=sha(S/'output/RESULT.json'))
 except BaseException as e:receipt.update(status='STOPPED_PRESERVE_NATIVE_EVIDENCE',error=repr(e));raise
 finally:
  if timer:timer.cancel()
  if proc and proc.poll()is None:proc.terminate();proc.wait(timeout=10)
  after=source(G);after_cache=cache(G);changes={'source':delta(before,after),'cache':delta(before_cache,after_cache)};newjson(R/'EXPLICIT_BYTE_DIFFS.json',changes);newjson(R/'GAME_SOURCE_AFTER.json',after);newjson(R/'GAME_CACHE_AFTER.json',after_cache);same=not changes['source']and not changes['cache'];receipt.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seconds=round(time.monotonic()-start,3),returncode=proc.returncode if proc else None,errors=errors,all_source_cache_bytes_unchanged=same,source_diff_count=len(changes['source']),cache_diff_count=len(changes['cache']))
  if not same:receipt['status']='STOPPED_UNEXPECTED_SOURCE_OR_CACHE_MUTATION'
  rp.write_text(json.dumps(receipt,indent=2)+'\n');need(same,'Unexpected source/cache mutation; no clean-capture claim')
 print(json.dumps(receipt))
if __name__=='__main__':main()
