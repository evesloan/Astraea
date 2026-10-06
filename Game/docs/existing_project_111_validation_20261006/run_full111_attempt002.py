from pathlib import Path
import subprocess,json,time,datetime,hashlib,shutil,sys,os
R=Path('/workspace/scratch/375c2e438292/engineering-essentials-integration/full111_attempt002');P=Path('/workspace/shared/astraea-godot-production-20261003');start=json.loads((R/'START.json').read_text());labels=[r[0] for r in start['commands']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changed=[n for n,h in start['source_sha256'].items() if not (P/n).is_file() or sha(P/n)!=h];assert not changed,('Frozen pre-run source changed',changed)
assert not (R/'RUN.log').exists(),'Preserve previous run; refuse overwrite'
old=P/'artifacts/validation_full_fixed60.json'
if old.exists():shutil.copy2(old,R/'PREVIOUS_FULL_RECEIPT.json')
t0=time.time();progress={'state':'running','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expected_checks':111,'launched_checks':0,'current_check':None,'last_output':None,'runner_pid':None};(R/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
with (R/'RUN.log').open('w') as log:
 process=subprocess.Popen(['python3',str(P/'tools/validate.py')],cwd=P,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1);progress['runner_pid']=process.pid
 for line in process.stdout:
  log.write(line);log.flush();progress['last_output']=line.strip()[-1500:]
  if line.startswith('Godot Engine '):
   progress['launched_checks']+=1;i=progress['launched_checks']-1;progress['current_check']=labels[i] if i<len(labels) else 'unexpected_extra';print('FULL111 CHECK %s/111 START: %s'%(i+1,progress['current_check']),flush=True)
  if 'PASS:' in line or 'ERROR:' in line or 'Assertion failed' in line:print(line.rstrip(),flush=True)
  progress['elapsed_seconds']=round(time.time()-t0,3);(R/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
 code=process.wait()
receipt_path=P/'artifacts/validation_full_fixed60.json';receipt=json.loads(receipt_path.read_text());shutil.copy2(receipt_path,R/'FULL_RESULT.json');shutil.copy2(P/'artifacts/validation.json',R/'CHECK_RESULTS.json')
changes=[{'path':n,'expected':h,'actual':sha(P/n) if (P/n).is_file() else None} for n,h in start['source_sha256'].items() if not (P/n).is_file() or sha(P/n)!=h]
runtime_now={str(p.relative_to(P)) for folder in ['assets','scripts','scenes','shaders','tests','data'] for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
unexpected_added_runtime=sorted(runtime_now-set(start['source_sha256']))
output_checks={}
for name,expected in start['generated_outputs'].items():
 out=json.loads((P/name).read_text());output_checks[name]={'status':out.get('status'),'test_sha256_matches':out.get('test_sha256')==expected['writer_sha256'],'writer_unchanged':sha(P/expected['writer'])==expected['writer_sha256'],'before':expected['pre_run_output_sha256'],'after':sha(P/name)}
outputs_ok=all(x['status']=='PASS' and x['test_sha256_matches'] and x['writer_unchanged'] for x in output_checks.values())
passed=sum(c['passed'] for c in receipt['checks']);complete=code==0 and passed==111 and len(receipt['checks'])==111 and not changes and not unexpected_added_runtime and outputs_ok
result={'state':'passed' if complete else 'failed','exit_code':code,'checks_completed':len(receipt['checks']),'checks_passed':passed,'expected_checks':111,'wall_seconds':round(time.time()-t0,3),'source_files_checked':len(start['source_sha256']),'source_drift':changes,'unexpected_added_runtime':unexpected_added_runtime,'generated_output_checks':output_checks,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Existing implemented-system regression only; not first-pass visual or target-GPU acceptance'};(R/'FINAL.json').write_text(json.dumps(result,indent=2)+'\n');progress.update(result);(R/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n');print('FULL111 TERMINAL '+json.dumps(result),flush=True);raise SystemExit(0 if complete else 1)
