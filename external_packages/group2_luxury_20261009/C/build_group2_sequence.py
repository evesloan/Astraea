"""Explicit source jobs, serialized through the shared Windows heavy mutex.
Passing geometry is never overwritten; failed outputs halt for evidence repair.
No pixel-review or installation claim is made by this runner.
"""
import pathlib,json,subprocess,sys
R=pathlib.Path(__file__).resolve().parent
generic=json.loads((R/'GENERIC_DELUXE_COHORT.json').read_text())['units']
jobs=[(834,'generic'),(864,'quiet'),(816,'aquatic')]+[(u,'generic') for u in generic if u not in [810,834]]
status_path=R/'GROUP2_NEXT_BUILD_STATUS.json'
done=[]
for unit,kind in jobs:
 O=R/'sections'/f'{unit}_deluxe'
 if (O/f'{unit}_deluxe.blend').exists():
  assert all(json.loads((O/f'{x}_VERIFICATION.json').read_text())['status']=='PASS' for x in ['NATIVE','EXPORT']),'Preserve failed candidate and repair before resuming '+str(unit)
  done.append({'unit':unit,'kind':kind,'status':'EXISTING_SOURCE_QA_PASS_PIXEL_REVIEW_SEPARATE'});continue
 script='place_deluxe_family.py' if kind=='generic' else 'build_deluxe_variant.py'
 args=[str(unit)]+([] if kind=='generic' else [kind]);log=R/f'next_{unit}_{kind}.log'
 assert not log.exists(),'Retain prior source log; use an explicit new run'
 print('Sequential source job',unit,kind,flush=True)
 with log.open('w',encoding='utf-8') as f:
  result=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/script)]+args,stdout=f,stderr=subprocess.STDOUT)
 done.append({'unit':unit,'kind':kind,'exit_code':result.returncode,'log':log.name,'pixel_review':'PENDING_ACTUAL_INSPECTION'})
 status_path.write_text(json.dumps({'Group2_status':'UNFINISHED','jobs':done,'explicit_source_sequence':jobs},indent=2))
 print('Source job finished',unit,result.returncode,flush=True)
 if result.returncode:raise RuntimeError('Failure retained; stop before another source job '+str(unit))
