from pathlib import Path
import datetime,hashlib,json,os,subprocess,time,threading
S=Path(__file__).resolve().parent
G=Path('/workspace/shared/astraea-godot-production-20261003')
ENGINE='/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(G)):sha(p)for p in G.rglob('*')if p.is_file()and not {'.git','.godot'}&set(p.relative_to(G).parts)}
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
PINS={'probe.gd': 'ff48b07519f56c1c4c0af1a72eb1f91b51eb10e4683317465222cb98ee981f25', 'SOURCE_RECEIVER_PROOF.json': '3c22da28602d18a31bf14b4b56182d010ace88854c080a2d479fb8885a0c8e55'}
for rel,digest in PINS.items():assert sha(S/rel)==digest,rel
assert sha(ENGINE)=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
assert subprocess.run(['pgrep','-x','godot'],capture_output=True).returncode==1
assert not list(Path('/workspace/shared/astraea-review-queue').glob('*.request'))
assert not (S/'RUN.log').exists()
before=snapshot();assert before==json.loads((S.parent/'focused_run001/SOURCE_FINAL.json').read_text())
write(S/'SOURCE_BEFORE.json',before);start=time.time();env=os.environ.copy()
for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:p=S/name;p.mkdir();env[key]=str(p)
receipt={'status':'RUNNING_READ_ONLY_RECEIVER_DIAGNOSIS','source_count':len(before),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write(S/'RECEIPT.json',receipt)
try:
 with (S/'RUN.log').open('x')as log:
  p=subprocess.Popen([ENGINE,'--headless','--path',str(G),'--fixed-fps','60','--script',str(S/'probe.gd')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env)
  timer=threading.Timer(90,p.kill);timer.start();errors=[]
  try:
   for line in p.stdout:
    log.write(line);log.flush();print(line,end='',flush=True)
    if any(x in line for x in ['ERROR:','Assertion failed','Parse Error']):
     errors.append(line.strip())
     if len(errors)==1:threading.Timer(1,p.terminate).start()
   p.wait()
  finally:timer.cancel()
 receipt.update(returncode=p.returncode,errors=errors,seconds=time.time()-start)
 assert p.returncode==0 and not errors and (S/'RESULT.json').is_file()
 receipt.update(status='PASS_READ_ONLY_RECEIVER_DIAGNOSIS',result_sha256=sha(S/'RESULT.json'))
finally:
 after=snapshot();receipt.update(source_unchanged=after==before,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());write(S/'RECEIPT.json',receipt);print(json.dumps(receipt));assert after==before
