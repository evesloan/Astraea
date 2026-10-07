from pathlib import Path
import datetime,hashlib,json,os,subprocess,threading,time
S=Path(__file__).resolve().parent;P=S/'receiver_repair002';G=Path('/workspace/shared/astraea-godot-production-20261003');ENGINE='/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def snap():return {str(p.relative_to(G)):sha(p)for p in G.rglob('*')if p.is_file()and not{'.git','.godot'}&set(p.relative_to(G).parts)}
need(sha(P/'MANIFEST.json')=='474efd21ba3a8898f41ce59cafbbc26aee3ae7e021d194b27577b060513c3885','Manifest changed');m=json.loads((P/'MANIFEST.json').read_text());need(json.loads((P/'APPLY_RECEIPT.json').read_text())['status']=='PASS_EXACT_COUNTER_RECEIVER_REPAIR_INSTALLED','Apply not complete')
need(sha(ENGINE)=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','Engine changed')
need(sha(S/'check_compatibility.gd')=='710fb8de17f2401bf97d4a226046a4ce32f19c50ee774ea280ccf7f37b7e0a17','Compatibility script changed')
need(subprocess.run(['pgrep','-x','godot'],capture_output=True).returncode==1,'Another Godot active');need(not list(Path('/workspace/shared/astraea-review-queue').glob('*.request')),'Graphical review queued')
before=dict(m['source_before']);before.update({r['path']:r['sha256']for r in m['files']});need(snap()==before,'Current repaired source differs');R=S/'focused_run002';R.mkdir();write(R/'SOURCE_BEFORE.json',before)
env=os.environ.copy()
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=R/name;p.mkdir();env[key]=str(p)
env['ASTRAEA_EAST_GALLERY_RECEIPT']=str(R/'GALLERY_PHYSICAL_RESULT.json')
receipt={'status':'RUNNING_NO_IMPORT_FOCUSED_RESUME','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],'no_import':True,'prior_import_receipt_sha256':sha(S/'focused_run001/RECEIPT.json'),'receiver_repair_manifest_sha256':sha(P/'MANIFEST.json'),'full_suite':False,'visual_acceptance':False}
def save():write(R/'RECEIPT.json',receipt)
save()
try:
 for label,args,timeout in [('canopy_compatibility',['--script',str(S/'check_compatibility.gd')],30),('grand_pool_architecture',['--quit-after','12000','--fixed-fps','60','--script','res://tests/validate_grand_pool_architecture.gd'],240),('lighting_budget',['--quit-after','2400','--fixed-fps','60','--script','res://tests/validate_lighting_budget.gd'],90),('grand_pool_access',['--quit-after','12000','--fixed-fps','60','--script','res://tests/validate_grand_pool_access.gd'],240)]:
  need(snap()==before,'Source changed before '+label);command=[ENGINE,'--headless','--path',str(G),*args];start=time.monotonic();errors=[];lines=[]
  with(R/(label+'.log')).open('x')as log:
   process=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);timer=threading.Timer(timeout,process.kill);timer.start()
   try:
    for line in process.stdout:
     log.write(line);log.flush();lines.append(line);print(line,end='',flush=True)
     if any(x in line for x in ['ERROR:','Assertion failed','Parse Error']):
      errors.append(line.strip())
      if len(errors)==1 and process.poll()is None:threading.Timer(1,process.terminate).start()
    process.wait()
   finally:
    timer.cancel()
    if process.poll()is None:process.terminate();process.wait(timeout=10)
  passed=process.returncode==0 and not errors and 'PASS:'in''.join(lines)
  receipt['checks'].append({'check':label,'passed':passed,'returncode':process.returncode,'errors':errors,'seconds':round(time.monotonic()-start,4),'command':command});save();need(passed,'Stopped at first failed check: '+label);need(snap()==before,'Source changed during '+label)
 receipt.update(status='PASS_CONNECTED_CURVED_POOL_GALLERY_FOCUSED_RESUME',installed_gallery_physical_check=True,lighting_budget_smoke=True,retained_pool_access=True)
except BaseException as e:receipt.update(status='STOPPED_PRESERVE_FIRST_FAILURE',error=repr(e));raise
finally:
 after=snap();write(R/'SOURCE_FINAL.json',after);receipt.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_final_sha256=sha(R/'SOURCE_FINAL.json'),source_unchanged=after==before,head_and_index_unchanged=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip()==m['game_head']and sha(G/'.git/index')==m['index_sha256']);save();print(json.dumps(receipt),flush=True)
