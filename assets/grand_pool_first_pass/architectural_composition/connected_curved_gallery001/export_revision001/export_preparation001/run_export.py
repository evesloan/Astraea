from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));from gate import gate,sha
assert sys.argv[1:]==['--run'];gate();R=B/'runs/connected001_logs';R.mkdir(parents=True);out={'status':'RUNNING','steps':[],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'threads':2,'source_saved':False,'Game_or_Catalogue_writes':False};env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1')
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=R/name;p.mkdir();env[key]=str(p)
base=['/usr/bin/blender','--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','1','--python']
def save():(R/'RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n')
save()
try:
 for label,cmd in [('snapshot',base+[str(B/'snapshot_east_gallery.py'),'--','--run','connected001']),('export',base+[str(B/'export_east_gallery.py'),'--','--run','connected001']),('equivalence',[sys.executable,str(B/'verify_east_gallery.py'),'--run','connected001'])]:
  gate();start=time.monotonic();print('CONNECTED_EXPORT_START',label,flush=True)
  with(R/(label+'.log')).open('x')as log:p=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
  out['steps'].append({'stage':label,'returncode':p.returncode,'seconds':time.monotonic()-start,'log_sha256':sha(R/(label+'.log'))});save();assert p.returncode==0
 out.update(status='PASS_THREE_CONNECTED_GALLERY_SOURCE_EQUIVALENT_DERIVATIVES',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print(json.dumps(out),flush=True)
except BaseException as e:out.update(status='FAILED_PRESERVE_ALL_EXPORT_EVIDENCE',error=repr(e));save();raise
