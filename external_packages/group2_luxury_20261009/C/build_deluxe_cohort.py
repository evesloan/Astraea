"""Build the explicit assigned cohort sequentially; all pixel reviews remain pending."""
import pathlib,json,subprocess,sys,time
R=pathlib.Path(__file__).resolve().parent;cohort=json.loads((R/'GENERIC_DELUXE_COHORT.json').read_text());receipt=R/'GENERIC_COHORT_BUILD_STATUS.json';done=[]
for unit in cohort['units']:
 O=R/'sections'/f'{unit}_deluxe'
 if (O/'SECTION_CONTRACT.json').exists():
  c=json.loads((O/'SECTION_CONTRACT.json').read_text());print('Existing source output preserved; no silent overwrite',unit,flush=True);continue
 logfile=R/f'deluxe_{unit}_build.log';print('Sequential source unit',unit,flush=True)
 with logfile.open('w',encoding='utf-8') as stream:result=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/'place_deluxe_family.py'),str(unit)],stdout=stream,stderr=subprocess.STDOUT)
 done.append({'unit_source_index':unit,'exit_code':result.returncode,'log':logfile.name,'pixel_review':'PENDING_ACTUAL_INSPECTION'});receipt.write_text(json.dumps({'overall_group2_status':'UNFINISHED','source_jobs':done,'source_units_in_cohort':cohort['units']},indent=2));print('Source job finished',unit,result.returncode,flush=True)
 if result.returncode:raise RuntimeError('Source failure preserved; repair before resuming '+str(unit))
print('Explicit cohort native/export construction finished; actual visual review and packaging still pending.',flush=True)
