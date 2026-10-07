"""One editor import, then registered pool architecture and lighting checks. No full suite."""
from pathlib import Path
import datetime,hashlib,json,os,re,subprocess,sys,threading,time
from PIL import Image
S=Path(__file__).resolve().parent;G=Path('/workspace/shared/astraea-godot-production-20261003');M=S/'FINAL_APPLY_MANIFEST.json';EXPECTED='e15ddd0611fd59ce133570b5ab0debdb799d3de42286c369366853523f844dae';ENGINE='/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64';ENGINE_SHA='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def snapshot():
 out={}
 for directory,dirs,names in os.walk(G):
  dirs[:]=sorted(d for d in dirs if d not in {'.git','.godot'})
  for n in names:
   p=Path(directory)/n;need(not p.is_symlink(),'Source symlink encountered')
   if p.is_file():out[str(p.relative_to(G))]=sha(p)
 return out
def sections(p):
 result={};section=''
 for line in Path(p).read_text().splitlines():
  s=line.strip()
  if s.startswith('[')and s.endswith(']'):section=s[1:-1];result[section]={}
  elif '='in s:
   k,v=s.split('=',1);result[section][k]=v
 return result
def uid(p):
 text=Path(p).read_text();m=re.search(r'uid://[a-z0-9]+',text);need(m is not None,'Generated UID missing: '+str(p));return m.group()
need(not sys.flags.optimize and sys.argv[1:]==['--run'],'Explicit reviewed --run required')
need(sha(M)==EXPECTED and sha(ENGINE)==ENGINE_SHA,'Reviewed manifest/engine changed')
need(sha(S/'check_compatibility.gd')=='710fb8de17f2401bf97d4a226046a4ce32f19c50ee774ea280ccf7f37b7e0a17','Compatibility check changed')
m=json.loads(M.read_text());need(subprocess.run(['pgrep','-x','godot'],capture_output=True).returncode==1,'Another Godot active')
need(not list(Path('/workspace/shared/astraea-review-queue').glob('*.request')),'Queued graphical review has priority')
need(sha(S/'EXPECTED_GENERATED_IMPORT_FILES.json')==m['expected_import_outputs_sha256'],'Expected import output classification changed')
receipts=list((S/'apply_receipts').glob('*/RECEIPT.json'));need(len(receipts)==1,'Expected one terminal apply receipt');apply=json.loads(receipts[0].read_text());need(apply['status']=='INSTALLED_CONNECTED_CURVED_POOL_GALLERY_CANDIDATE_IMPORT_AND_FOCUSED_CHECK_PENDING'and apply['written_count']==13 and not apply['unexpected_changes'],'Apply not terminal/verified')
before=dict(m['source_before']);before.update({r['target']:r['sha256']for r in m['files']});need(snapshot()==before,'Installed candidate differs before import')
need(subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip()==m['game_head']and sha(G/'.git/index')==m['index_sha256'],'Git state changed')
R=S/'focused_run001';R.mkdir();write(R/'SOURCE_BEFORE.json',before)
env=os.environ.copy()
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=R/name;p.mkdir();env[key]=str(p)
env['ASTRAEA_EAST_GALLERY_RECEIPT']=str(R/'GALLERY_PHYSICAL_RESULT.json')
receipt={'status':'RUNNING_BOUNDED_IMPORT_AND_FOCUSED_CHECKS','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':EXPECTED,'scope':'One import; exact medical/pool file-chain compatibility; registered pool architecture, lighting smoke and retained pool access. No full suite or visual acceptance.','checks':[],'full_suite':False,'visual_acceptance':False}
def save():write(R/'RECEIPT.json',receipt)
save();post_import=None
try:
 for label,args,timeout in [('import',['--editor','--quit'],180),('canopy_compatibility',['--script',str(S/'check_compatibility.gd')],30),('grand_pool_architecture',['--quit-after','12000','--fixed-fps','60','--script','res://tests/validate_grand_pool_architecture.gd'],240),('lighting_budget',['--quit-after','2400','--fixed-fps','60','--script','res://tests/validate_lighting_budget.gd'],90),('grand_pool_access',['--quit-after','12000','--fixed-fps','60','--script','res://tests/validate_grand_pool_access.gd'],240)]:
  if post_import is not None:need(snapshot()==post_import,'Frozen source changed before '+label)
  command=[ENGINE,'--headless','--path',str(G),*args];start=time.monotonic();errors=[];lines=[]
  with (R/(label+'.log')).open('x')as log:
   process=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);timer=threading.Timer(timeout,process.kill);timer.start()
   try:
    for line in process.stdout:
     log.write(line);log.flush();lines.append(line);print(line,end='',flush=True)
     if any(x in line for x in ['ERROR:','Assertion failed','Parse Error']):
      errors.append(line.strip())
      if process.poll()is None and len(errors)==1:
       context_timer=threading.Timer(1.0,process.terminate);context_timer.start()
    process.wait()
   finally:
    timer.cancel()
    if process.poll()is None:process.terminate();process.wait(timeout=10)
  passed=process.returncode==0 and not errors and (label=='import'or'PASS:'in''.join(lines))
  receipt['checks'].append({'check':label,'passed':passed,'returncode':process.returncode,'errors':errors,'seconds':round(time.monotonic()-start,4),'command':command});save()
  need(passed,'Stopped at first failed check: '+label)
  if label=='import':
   after=snapshot();policy=json.loads((S/'EXPECTED_GENERATED_IMPORT_FILES.json').read_text());allowed_added=set();classified=[]
   old_uids={uid(G/p)for p in before if p.endswith('.uid')or p.endswith('.import')and p not in {r['target']for r in m['files']if r['target'].endswith('.glb.import')}}
   new_uids=set()
   for image in policy['images']:
    rel=image['destination'];sc=image['import_sidecar_destination'];allowed_added.update([rel,sc]);need(rel in after and sc in after and rel not in before and sc not in before,'Expected new extracted image absent/already existed')
    need(sha(G/rel)==image['expected_encoded_png_sha256'],'Extracted PNG encoded bytes differ')
    im=Image.open(G/rel);need(list(im.size)==[image['width'],image['height']]and hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()==image['expected_rgba8_sha256'],'Extracted RGBA pixels differ')
    cfg=sections(G/sc);need(cfg['remap']['importer']=='"texture"'and cfg['deps']['source_file']=='"res://'+rel+'"'and cfg['params']['compress/mode']=='0','Unexpected new texture importer policy')
    u=uid(G/sc);need(u not in old_uids and u not in new_uids,'New texture UID collides');new_uids.add(u);classified.append({'path':rel,'sha256':after[rel],'sidecar':sc,'sidecar_sha256':after[sc],'rgba8_exact':True})
   for rel in policy['new_script_uids']:
    allowed_added.add(rel);need(rel in after and rel not in before,'New script UID missing');u=uid(G/rel);need(u not in old_uids and u not in new_uids,'New script UID collides');new_uids.add(u)
   allowed_changed={r['target']for r in m['files']if r['target'].endswith('.glb.import')}
   for rel in allowed_changed:
    expected=sections(S/'staged/Game'/rel);actual=sections(G/rel);need(actual['params']==expected['params']and actual['deps']==expected['deps'],'New model importer changed reviewed parameters/dependencies')
    for k,v in expected['remap'].items():need(actual['remap'].get(k)==v,'New model remap changed beyond UID')
    need(set(actual['remap'])==set(expected['remap'])|{'uid'},'Unclassified model remap metadata');u=uid(G/rel);need(u not in old_uids and u not in new_uids,'New model UID collides');new_uids.add(u)
   actual_added=set(after)-set(before);actual_removed=set(before)-set(after);actual_changed={p for p in before if p in after and before[p]!=after[p]}
   need(actual_added==allowed_added and not actual_removed and actual_changed<=allowed_changed,'Unclassified source mutation during import')
   post_import=after;write(R/'SOURCE_AFTER_IMPORT.json',after);write(R/'IMPORT_CLASSIFICATION.json',{'status':'PASS_ONLY_EXPECTED_NEW_ASSET_GENERATION','new_paths':sorted(actual_added),'new_uid_count':len(new_uids),'new_scene_sidecars_updated':sorted(actual_changed),'images':classified,'all_prior_source_bytes_unchanged':True})
  else:need(snapshot()==post_import,'Portable source changed during focused check')
 receipt.update(status='PASS_CONNECTED_CURVED_POOL_GALLERY_IMPORT_AND_FOCUSED_CHECKS',installed_canopy_physical_check=True,lighting_budget_smoke=True,aggregate_full_suite=False)
except BaseException as e:
 receipt.update(status='STOPPED_PRESERVE_FIRST_FAILURE',error=repr(e));raise
finally:
 after=snapshot();write(R/'SOURCE_FINAL.json',after);receipt.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_final_sha256=sha(R/'SOURCE_FINAL.json'),source_after_import_unchanged=after==post_import if post_import is not None else None,head_and_index_unchanged=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip()==m['game_head']and sha(G/'.git/index')==m['index_sha256']);save();print(json.dumps(receipt),flush=True)
