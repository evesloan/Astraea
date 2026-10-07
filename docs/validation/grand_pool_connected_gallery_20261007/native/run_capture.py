"""Parent-only frozen current-Game installed capture; no import or candidate work."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys,threading,time
S=Path(__file__).resolve().parent;G=Path('/workspace/shared/astraea-godot-production-20261003');F=S/'FINAL_CURRENT_FREEZE.json';A=S.parent/'runtime_draft001';FOCUSED=A/'focused_run004/RECEIPT.json';FINAL=A/'focused_run004/SOURCE_FINAL.json';ENGINE=Path('/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64');ENGINE_SHA='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3';FILES=['capture.gd','run_capture.py','HANDOFF.md']
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_new(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def snap(root,exclude=()):
 need(root.is_dir(),'Missing root '+str(root));out={}
 for directory,dirs,names in os.walk(root):
  dirs[:]=sorted(d for d in dirs if d not in exclude)
  for n in dirs:need(not(Path(directory)/n).is_symlink(),'Symlink directory')
  for n in sorted(names):
   p=Path(directory)/n;need(not p.is_symlink(),'Symlink file')
   if p.is_file():out[str(p.relative_to(root))]=sha(p)
 return out
def source():return snap(G,{'.git','.godot'})
def diffs(a,b):return [{'path':p,'before':a.get(p),'after':b.get(p),'kind':'added' if p not in a else 'removed' if p not in b else 'changed'} for p in sorted(set(a)|set(b)) if a.get(p)!=b.get(p)]
def focused():
 need(FOCUSED.is_file() and FINAL.is_file(),'Focused gallery terminal evidence missing')
 r=read(FOCUSED);need(r['status']=='PASS_CONNECTED_CURVED_POOL_GALLERY_FOCUSED_RESUME','Focused gallery is not successful/terminal')
 need(r.get('installed_gallery_physical_check') is True and r.get('lighting_budget_smoke') is True and r.get('source_unchanged') is True and r.get('head_and_index_unchanged') is True,'Focused gallery pass/source preservation incomplete')
 need([x['check'] for x in r['checks']]==['canopy_compatibility','grand_pool_architecture','lighting_budget','grand_pool_access'] and all(x['passed'] is True and x['returncode']==0 and not x['errors'] for x in r['checks']),'Focused gallery required checks missing')
 need(sha(FINAL)==r['source_final_sha256'],'Focused gallery source snapshot changed');return r

def idle():
 need(subprocess.run(['pgrep','-x','godot'],capture_output=True).returncode==1,'Another Godot process exists or status is uncertain')
 need(not list(Path('/workspace/shared/astraea-review-queue').glob('*.request')),'Queued review work has priority')
def verify():
 focused();d=read(F);need(sha(FOCUSED)==d['focused_receipt_sha256'] and sha(FINAL)==d['focused_source_final_sha256'],'Focused evidence changed')
 for name,h in d['prepared_files'].items():need(sha(S/name)==h,'Capture preparation changed: '+name)
 need(source()==d['game_source'] and snap(G/'.godot')==d['game_cache'],'Frozen Game/cache inputs changed')
 need(sha(ENGINE)==ENGINE_SHA==d['engine_sha256'],'Existing approved engine changed');return d

def main():
 need(not sys.flags.optimize,'Optimization forbidden')
 ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');ap.add_argument('--release-reference');args=ap.parse_args()
 if not args.run:
  print(json.dumps({'status':'PREPARED_NO_CAPTURE_OR_FREEZE','focused_gallery_status':read(FOCUSED).get('status') if FOCUSED.exists() else 'NOT_AVAILABLE','engine_launched':False,'installed':True,'visual_first_pass_complete':False}));return
 need(args.release_reference,'Actual parent Game-slot release reference required')
 need(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'),'Existing approved parent graphical terminal required; no alternate display')
 need(not F.exists() and not(S/'launcher_run001').exists() and not(S/'output').exists(),'Preserve prior capture/freeze')
 receipt=focused();idle();need(sha(ENGINE)==ENGINE_SHA,'No engine switch permitted')
 before=source();need(before==read(FINAL),'Current Game differs from successful focused_gallery; obtain a current focused receipt')
 cache=snap(G/'.godot');idle();need(source()==before and snap(G/'.godot')==cache,'Inputs changed while freezing')
 d={'status':'FINAL_CURRENT_AFTER_CONNECTED_GALLERY_FOCUSED004_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release_reference':args.release_reference,'installed':True,'production_changes':False,'visual_first_pass_complete':False,'visual_acceptance':False,'focused_receipt_sha256':sha(FOCUSED),'focused_source_final_sha256':sha(FINAL),'focused_status':receipt['status'],'prepared_files':{p:sha(S/p) for p in FILES},'game_source':before,'game_cache':cache,'engine_path':str(ENGINE),'engine_sha256':ENGINE_SHA};write_new(F,d)
 R=S/'launcher_run001';R.mkdir();env=os.environ.copy()
 for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=R/name;p.mkdir();env[key]=str(p)
 env['ASTRAEA_INSTALLED_EAST_GALLERY_CAPTURE']='parent_approved';verify();idle()
 run={'status':'RUNNING_ACTUAL_INSTALLED_CAPTURE','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'installed':True,'production_changes':False,'visual_first_pass_complete':False,'visual_acceptance':False,'final_acceptance':False,'full_suite':False,'focus_receipt_sha256':sha(FOCUSED),'freeze_sha256':sha(F),'source_files':len(before),'cache_files':len(cache),'command':[str(ENGINE),'--audio-driver','Dummy','--path',str(G),'--resolution','1280x720','--script',str(S/'capture.gd')]};rp=R/'RECEIPT.json';write_new(rp,run);proc=None;timer=None;errors=[];lines=[];start=time.monotonic()
 try:
  with (R/'engine.log').open('x') as log:
   proc=subprocess.Popen(run['command'],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);timer=threading.Timer(300,proc.kill);timer.start()
   for line in proc.stdout:
    log.write(line);log.flush();lines.append(line)
    if any(x in line for x in ['ERROR:','Assertion failed','Parse Error']):
     errors.append(line.rstrip())
     if proc.poll() is None:proc.terminate()
   proc.wait();timer.cancel()
  need(proc.returncode==0 and not errors and 'INSTALLED_POOL_CONNECTED_GALLERY_CAPTURE_COMPLETE' in ''.join(lines),'Capture stopped; preserve engine log')
  result=read(S/'output/RESULT.json');need(result['installed'] is True and result['capture_count']==6 and len(result['captures'])==6 and result['visual_first_pass_complete'] is False,'Incomplete installed captures')
  need(result['budget']==8 and result['candidate_limit']==32,'Observed selector limits differ from approved limits')
  for c in result['captures']:
   need(sha(S/'output'/c['file'])==c['sha256'] and c['fov']==72.0 and c['eye_delta_m']<0.0001,'Capture file or exact camera mismatch')
  verify();run.update(status='INSTALLED_NATIVE_CAPTURE_COMPLETE_PENDING_VISUAL_REVIEW',capture_count=6,result_sha256=sha(S/'output/RESULT.json'))
 except BaseException as e:run.update(status='STOPPED_PRESERVE_CAPTURE_EVIDENCE',error=repr(e));raise
 finally:
  if timer:timer.cancel()
  if proc and proc.poll() is None:proc.terminate();proc.wait(timeout=10)
  after=source();after_cache=snap(G/'.godot');write_new(R/'GAME_SOURCE_AFTER.json',after);write_new(R/'GAME_CACHE_AFTER.json',after_cache)
  delta={'installed':True,'source':diffs(before,after),'cache':diffs(cache,after_cache),'policy':'Exact complete project source/import/UID/cache protection; command-local XDG/TMP outputs separate'};write_new(R/'EXPLICIT_BYTE_DIFFS.json',delta);same=not delta['source'] and not delta['cache']
  run.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seconds=round(time.monotonic()-start,3),returncode=proc.returncode if proc else None,errors=errors,all_game_source_and_cache_bytes_unchanged=same,source_diff_count=len(delta['source']),cache_diff_count=len(delta['cache']),diff_sha256=sha(R/'EXPLICIT_BYTE_DIFFS.json'))
  if not same:run.update(status='STOPPED_UNEXPECTED_GAME_OR_CACHE_MUTATION',production_changes='UNEXPECTED_REVIEW_REQUIRED')
  rp.write_text(json.dumps(run,indent=2)+'\n');need(same,'Unexpected Game/cache difference; no clean capture claim')
 print(json.dumps(run))
if __name__=='__main__':main()
