"""Sequential source builds for the explicit Premium cohort; actual pixel review remains separate."""
import pathlib,json,sys,subprocess
R=pathlib.Path(__file__).resolve().parent;receipt=R/'PREMIUM_COHORT_BUILD_STATUS.json'
old=json.loads(receipt.read_text()) if receipt.exists() else {'Group2_status':'UNFINISHED','jobs':[]}
for unit in json.loads((R/'PREMIUM_COHORT.json').read_text())['units']:
 o=R/'sections'/f'{unit}_premium'
 if (o/'SECTION_CONTRACT.json').exists():
  n=o/'NATIVE_VERIFICATION.json';g=o/'EXPORT_VERIFICATION.json'
  assert n.exists() and g.exists() and json.loads(n.read_text())['status']==json.loads(g.read_text())['status']=='PASS','Preserve failed source and repair before resuming'
  print('Existing Premium candidate preserved',unit,flush=True);continue
 assert not (o/f'{unit}_premium.blend').exists(),'Partial native requires explicit evidence preservation'
 log=R/f'premium_{unit}_build.log'
 print('Building exact Premium reservation',unit,flush=True)
 with log.open('w',encoding='utf-8') as stream:result=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/'build_premium.py'),str(unit)],stdout=stream,stderr=subprocess.STDOUT)
 old['jobs'].append({'unit':unit,'exit_code':result.returncode,'log':log.name,'pixel_review':'PENDING_ACTUAL_INSPECTION'});receipt.write_text(json.dumps(old,indent=2))
 if result.returncode:raise RuntimeError('Preserved source failure '+str(unit))
 print('Premium native/export QA passed, pixels pending',unit,flush=True)
