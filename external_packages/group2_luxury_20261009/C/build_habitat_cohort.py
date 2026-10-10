"""Remaining explicit habitat source batch, all heavy stages serialized."""
import pathlib,json,sys,subprocess
R=pathlib.Path(__file__).resolve().parent;receipt=R/'HABITAT_COHORT_BUILD_STATUS.json';state=json.loads(receipt.read_text()) if receipt.exists() else {'Group2_status':'UNFINISHED','jobs':[]}
for unit,kind in json.loads((R/'HABITAT_COHORT.json').read_text())['units']:
 o=R/'sections'/f'{unit}_deluxe';sr=next(x for x in json.loads((R/'ALL_81_NEIGHBOUR_SCREEN.json').read_text())['records'] if x['source_envelope_index']==unit)
 if sr['screen_status']!='NO_AABB_INTERSECTIONS':
  pr=next(x for x in json.loads((R/'PRECISE_RETAINED_TIDAL_INTERSECTIONS.json').read_text())['records'] if x['source_envelope_index']==unit);assert pr['status']=='AABB_CANDIDATE_CLEARED_BY_ACTUAL_TRIANGLES' and not sr['structural_mesh_aabb_contacts']
 if not (o/'SECTION_CONTRACT.json').exists():
  assert not (o/f'{unit}_deluxe.blend').exists(),'Preserve partial native before recovery'
  log=R/f'habitat_{unit}_{kind}_build.log'
  print('Building exact habitat reservation',unit,kind,flush=True)
  with log.open('w',encoding='utf-8') as stream:res=subprocess.run([sys.executable,str(R/'heavy.py'),str(R/'build_deluxe_variant.py'),str(unit),kind],stdout=stream,stderr=subprocess.STDOUT)
  state['jobs'].append({'unit':unit,'kind':kind,'stage':'native_export','exit_code':res.returncode,'log':log.name});receipt.write_text(json.dumps(state,indent=2))
  if res.returncode:raise RuntimeError('Preserved habitat source failure '+str(unit))
 c=json.loads((o/'SECTION_CONTRACT.json').read_text());assert all(json.loads((o/(k+'_VERIFICATION.json')).read_text())['status']=='PASS' for k in ['NATIVE','EXPORT'])
 if not c.get('review_view_rebuild'):
  script=R/f'review_{kind}_gallery.py';log=R/f'habitat_{unit}_{kind}_gallery.log'
  with log.open('w',encoding='utf-8') as stream:res=subprocess.run([sys.executable,str(R/'heavy.py'),str(script),str(unit)],stdout=stream,stderr=subprocess.STDOUT)
  state['jobs'].append({'unit':unit,'kind':kind,'stage':'main_gallery_view','exit_code':res.returncode,'log':log.name});receipt.write_text(json.dumps(state,indent=2))
  if res.returncode:raise RuntimeError('Preserved habitat view failure '+str(unit))
 print('Habitat native/export QA and main gallery view complete; actual pixels pending',unit,kind,flush=True)
