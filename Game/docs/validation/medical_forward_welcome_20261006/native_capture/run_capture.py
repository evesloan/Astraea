#!/usr/bin/env python3
"""Root graphical-terminal only. Capture actual installed medical; no import."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,threading,time,datetime
S=Path(__file__).resolve().parent;R=S.parent;G=Path('/workspace/shared/astraea-godot-production-20261003');ENGINE=Path('/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64');ENGINE_SHA='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snap(root,excluded=set()):return {str(p.relative_to(root)):sha(p)for p in root.rglob('*')if p.is_file()and not set(p.relative_to(root).parts)&excluded}
def source():return snap(G,{'.git','.godot','artifacts','__pycache__'})
def write(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2);f.write('\n')
def diff(a,b):return [{'path':n,'before':a.get(n),'after':b.get(n)}for n in sorted(set(a)|set(b))if a.get(n)!=b.get(n)]
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--release-reference');a=p.parse_args()
if not a.run:print('PREPARED: no capture, import or source changes');raise SystemExit(0)
assert a.release_reference and (os.environ.get('DISPLAY')or os.environ.get('WAYLAND_DISPLAY')),'Use the existing root graphical terminal and confirmed serialized boundary'
assert sha(ENGINE)==ENGINE_SHA and not list(Path('/workspace/shared/astraea-review-queue').glob('*.request'))
assert not(S/'output').exists()and not(S/'run001').exists()and not(S/'FREEZE.json').exists(),'Preserve previous views'
f=R/'FOCUSED_CHECKS_FOR_VIEWS.json';focused=json.loads(f.read_text());assert focused['structure_passed']and focused['access_passed']and focused['lighting_passed'];assert focused['cart_outcome']in ['PASS','FAIL_RECORDED'];assert source()==focused['source']
before=source();cache=snap(G/'.godot');assert before==source()and cache==snap(G/'.godot')
freeze={'release_reference':a.release_reference,'game_source':before,'game_cache':cache,'prepared_sha256':{n:sha(S/n)for n in ['capture.gd','run_capture.py']},'focused_sha256':sha(f),'engine_sha256':ENGINE_SHA};write(S/'FREEZE.json',freeze)
out=S/'run001';out.mkdir();env=os.environ.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:q=out/sub;q.mkdir();env[key]=str(q)
env['ASTRAEA_MEDICAL_INSTALLED_CAPTURE']='root_approved';cmd=[str(ENGINE),'--audio-driver','Dummy','--path',str(G),'--resolution','1280x720','--script',str(S/'capture.gd')];start=time.monotonic();errors=[];lines=[];proc=None;timer=None
receipt={'status':'RUNNING_INSTALLED_MEDICAL_CAPTURE','command':cmd,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'focused_sha256':sha(f),'scope':'Actual installed visual review only; no final department acceptance'}
try:
 with (out/'engine.log').open('x')as log:
  proc=subprocess.Popen(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);timer=threading.Timer(300,proc.kill);timer.start()
  for line in proc.stdout:
   lines.append(line);log.write(line);log.flush()
   if any(x in line for x in ['ERROR:','Assertion failed','Parse Error']):
    errors.append(line.rstrip())
    if proc.poll()is None:proc.terminate()
  proc.wait();timer.cancel()
 assert proc.returncode==0 and not errors and 'INSTALLED_MEDICAL_CAPTURE_COMPLETE'in ''.join(lines)
 result=json.loads((S/'output/RESULT.json').read_text());assert result['capture_count']==8
 for c in result['captures']:assert sha(S/'output'/c['file'])==c['sha256']and c['eye_error_m']<.0001 and c['fov']==72.0
 receipt['status']='INSTALLED_MEDICAL_VIEWS_COMPLETE_PENDING_REVIEW'
finally:
 if timer:timer.cancel()
 if proc and proc.poll()is None:proc.terminate();proc.wait(timeout=10)
 after=source();after_cache=snap(G/'.godot');write(out/'SOURCE_AFTER.json',after);write(out/'CACHE_AFTER.json',after_cache);delta={'source':diff(before,after),'cache':diff(cache,after_cache)};write(out/'BYTE_DIFFS.json',delta);receipt.update(returncode=proc.returncode if proc else None,seconds=round(time.monotonic()-start,3),errors=errors,source_unchanged=not delta['source'],cache_unchanged=not delta['cache'])
 if delta['source']or delta['cache']:receipt['status']='CAPTURE_REQUIRES_MUTATION_REVIEW'
 write(out/'RECEIPT.json',receipt)
 assert not delta['source']and not delta['cache'],'Preserve and classify any engine cache/source change'
print(json.dumps(receipt))
