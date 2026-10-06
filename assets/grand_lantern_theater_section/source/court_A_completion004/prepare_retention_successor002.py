"""Narrow historical-context successor; never reads changed live optical JSONs."""
from pathlib import Path
import copy,hashlib,importlib.util,json,tempfile
P=Path(__file__).resolve().parent;G='/workspace/shared/astraea-godot-production-20261003/'
OLD_HASH='ed65e5d9491332dbcdc58896287b2822dd3129ac36976afad0f2426073dca3ad'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,data):
 with (P/name).open('x')as f:
  if isinstance(data,str):f.write(data)
  else:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
assert sha(P/'RETENTION_MANIFEST.json')==OLD_HASH
old=json.loads((P/'RETENTION_MANIFEST.json').read_text());T=Path(old['target']);assert not T.exists()
archive=json.loads((P/'historical_game_context002/ARCHIVE_RECEIPT.json').read_text())['files']
for r in archive:assert sha(r['archived_source'])==r['sha256']
runtime=G+'data/architecture/THEATER_RUNTIME_STAGE001.json';fixtures=G+'tests/fixtures/THEATER_TEST_FIXTURES.json'
assert {r['original_source']for r in archive}=={runtime,fixtures}
assert next(r['sha256']for r in archive if r['original_source']==runtime)=='a056941635b65c03fbcbb2f5075936eae0082fa8bfb0256a2914414d58fa7994'
assert next(r['sha256']for r in archive if r['original_source']==fixtures)=='cad1feb227176f4e24febace8aeb2ff5473f950a95bfe882eebe01a0fd5de0ce'
context={'status':'HISTORICAL_RENDER_QA_CONTEXT_ARCHIVED_EXACTLY','supersedes_packaging_manifest_sha256':OLD_HASH,'retention_only':True,'classification_scope':'The two exact old Game lighting/fixture JSONs are preserved historical render/QA context. Neither proves accepted Court lighting. Existing source/render recipes retain their old paths and hashes; a future rebuild must deliberately select this archived context or a newly reviewed successor.','archived_files':archive,'live_guard_removed':[runtime],'live_guard_never_present':[fixtures],'all_other_original_protected_inputs_retained':True,'native_proof_docs_and_helper':'No native-proof helper or native-proof report is a live protected input in manifest001. Any hashes for them in court/source_build_run001/INPUT_PINS.json belong to its unchanged historical observational Game inventory. That inventory is explicitly not a live current-state guard or a current-proof claim. No proof-specific guard was bypassed.','priority_game_correction':'The parent authorized current Game optical correction and later real-capture proof successors separately. This package does not patch, validate, accept, or restore those live successors, and does not pin future live optical hashes.','unchanged_source_candidate_sha256':'7456c069315f3ed1f74c327ba0af53a90942cd1549b6905d3abe58ba76633c49','unchanged_preview_sha256':'00f84dd3900ae5ab08503395edf5ec5212718bf8530ec7fb04aa586464784e1f','guard_policy':'The successor wrapper enforces the exact manifest001 pin, preservation of every other original protection, exactly one removed live guard, and guarded payload copies of both precise old JSONs. This is not a general exemption for Game files.'}
write('HISTORICAL_CONTEXT_SUCCESSOR002.json',context)
deps=json.loads((P/'DEPENDENCY_INDEX.json').read_text())
refs=deps['existing_retained_references'];old_runtime=[r for r in refs if r['source']==runtime];assert len(old_runtime)==1
deps['existing_retained_references']=[r for r in refs if r['source']!=runtime]
deps['historical_render_qa_context']=archive
deps['supersedes_original_index']='history/packaging001/DEPENDENCY_INDEX.json'
deps['runtime_context_resolution']='When following the historical render or pure QA recipe, map the old runtime path to historical_game_context002/data/architecture/THEATER_RUNTIME_STAGE001.json; do not silently substitute a current live optical successor. The original 3920-file Game inventory remains historical evidence only.'
write('DEPENDENCY_INDEX002.json',deps)
readme=(P/'README.md').read_text()
readme=readme.replace('Game stays frozen for full117; this package is source retention only.','The original Game freeze was historical. The parent has separately authorized a current optical correction and real-capture proof updates. This package remains source retention only and never writes Game.')
readme=readme.replace('DEPENDENCY_INDEX.json pins the already-retained','The current DEPENDENCY_INDEX.json pins the already-retained')
readme=readme.replace('These are historical and are not portable/rerunnable unchanged.','These are historical and are not portable/rerunnable unchanged.')
readme+='''\n## Historical optical-context successor002\n\nThe original manifest and seven packaging artifacts are preserved under history/packaging001/. The exact old runtime contract a0569416... and fixture contract cad1feb2... are now copied under historical_game_context002/ with an archive receipt. These bytes describe the source image and historical QA, not current native lighting. Current live lighting/proof successors are separately authorized work and are neither repinned nor reverted here.\n\nOnly the runtime-contract live input guard is replaced by the exact archived-byte guard. The fixture contract was never a live guarded input of manifest001; its hash occurred in the historical Game observation inventory. Native-proof docs/helper were likewise never live guarded dependencies. Every other original immutable/source guard remains exact. The successor wrapper validates this narrow scope against the retained original manifest; it cannot remove a second original guard or change protected source hashes.\n\nHistorical source/image files and their reports remain unchanged. Do not call this render a preview of corrected native optics, use it to set native energy, or claim finished-art/native-lighting acceptance. See HISTORICAL_CONTEXT_SUCCESSOR002.json for the complete classification.\n'''
write('README002.md',readme)
accept=json.loads((P/'ACCEPTANCE_AND_LIMITS.json').read_text());accept['packaging_context_successor']='HISTORICAL_CONTEXT_SUCCESSOR002.json';accept['current_game_state_claimed']=False
write('ACCEPTANCE_AND_LIMITS002.json',accept)
rows=copy.deepcopy(old['files'])
old_meta=['README.md','ACCEPTANCE_AND_LIMITS.json','DEPENDENCY_INDEX.json','retain_new_only.py','test_retainer.py','COPIER_TEST_REPORT.json','prepare_retention_manifest.py']
for row in rows:
 if row['destination_relative']in old_meta:row['destination_relative']='history/packaging001/'+row['destination_relative'];row['destination']=str(T/row['destination_relative'])
def add(source,rel,classification):
 source=Path(source);row={'source':str(source),'sha256':sha(source),'bytes':source.stat().st_size,'destination_relative':rel,'destination':str(T/rel),'classification':classification};rows.append(row);return row
add(P/'RETENTION_MANIFEST.json','history/packaging001/RETENTION_MANIFEST.json','Exact preserved original manifest; superseded, not executable current context')
add(P/'PREPARATION_SUMMARY.json','history/packaging001/PREPARATION_SUMMARY.json','Original preparation summary')
for path in sorted((P/'historical_game_context002').rglob('*')):
 if path.is_file():add(path,'historical_game_context002/'+str(path.relative_to(P/'historical_game_context002')),'Exact archived historical render/QA lighting context; never installed')
for name,rel in [('README002.md','README.md'),('DEPENDENCY_INDEX002.json','DEPENDENCY_INDEX.json'),('ACCEPTANCE_AND_LIMITS002.json','ACCEPTANCE_AND_LIMITS.json'),('HISTORICAL_CONTEXT_SUCCESSOR002.json','HISTORICAL_CONTEXT_SUCCESSOR002.json'),('retain_new_only002.py','retain_new_only002.py'),('prepare_retention_successor002.py','prepare_retention_successor002.py')]:add(P/name,rel,'New narrow context-classification successor metadata/tooling')
protected=[r.copy()for r in old['protected_inputs']if r['source']!=runtime]
def finish():
 for row in rows:
  if not any(p['source']==row['source']for p in protected):protected.append({k:row[k]for k in ['source','bytes','sha256']})
 return {**old,'schema':'astraea.court_a.source_retention.v2','status':'PREPARED_HISTORICAL_CONTEXT_SUCCESSOR_NOT_COPIED','files':sorted(rows,key=lambda r:r['destination_relative']),'protected_inputs':sorted(protected,key=lambda r:r['source']),'historical_context':archive,'original_manifest_sha256':OLD_HASH,'payload_file_count':len(rows),'payload_bytes':sum(r['bytes']for r in rows),'expected_final_file_count_including_manifest_and_receipt':len(rows)+2}
trial=finish()
spec=importlib.util.spec_from_file_location('retainer002',P/'retain_new_only002.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
# The old copy mechanics have nine passing tests. Exercise the new narrow policy
# against actual manifest data; these are read-only checks in disposable scratch.
results=[]
for case in ['valid_context','extra_removed_guard','changed_source_pin','missing_archived_payload','wrong_historical_hash','live_fixture_guard_added']:
 d=copy.deepcopy(trial)
 if case=='extra_removed_guard':d['protected_inputs'].pop(0)
 if case=='changed_source_pin':d['protected_inputs'][0]['sha256']='0'*64
 if case=='missing_archived_payload':d['files']=[r for r in d['files']if r['source']!=archive[0]['archived_source']]
 if case=='wrong_historical_hash':d['historical_context'][0]['sha256']='0'*64
 if case=='live_fixture_guard_added':d['protected_inputs'].append({'source':fixtures,'bytes':2066031,'sha256':'cad1feb227176f4e24febace8aeb2ff5473f950a95bfe882eebe01a0fd5de0ce'})
 try:module.validate_context_successor(d)
 except RuntimeError as e:
  assert case!='valid_context',(case,e)
  results.append({'case':case,'passed':True,'rejected_reason':str(e)})
 else:
  assert case=='valid_context',case
  results.append({'case':case,'passed':True})
write('CONTEXT_POLICY_TEST_REPORT002.json',{'status':'PASS_NARROW_CONTEXT_POLICY_TESTS','wrapper_sha256':sha(P/'retain_new_only002.py'),'cases':results,'production_writes':False,'engines_or_git_started':False,'prior_copy_mechanics_report':'history/packaging001/COPIER_TEST_REPORT.json'})
add(P/'CONTEXT_POLICY_TEST_REPORT002.json','CONTEXT_POLICY_TEST_REPORT002.json','Six read-only narrow guard-policy tests; nine original copier tests retained')
manifest=finish();write('RETENTION_MANIFEST002.json',manifest)
h=sha(P/'RETENTION_MANIFEST002.json');result=module.retain(P/'RETENTION_MANIFEST002.json',h,False)
summary={**result,'wrapper_sha256':sha(P/'retain_new_only002.py'),'manifest_bytes':(P/'RETENTION_MANIFEST002.json').stat().st_size,'wrapper_bytes':(P/'retain_new_only002.py').stat().st_size,'expected_final_file_count':len(rows)+2,'bytes_before_generated_receipt':manifest['payload_bytes']+(P/'RETENTION_MANIFEST002.json').stat().st_size,'preserved_original_manifest_sha256':OLD_HASH,'historical_payload_json_bytes':sum(r['bytes']for r in archive),'scope_delta':'One removed live runtime guard, replaced by archived a0569416 bytes. Fixture cad1feb2 bytes additionally preserved as historical QA context. No other original guard changed. Original metadata moved under history/packaging001 with unchanged bytes; new current metadata and narrow policy added.','omissions_requiring_parent_decision':[]}
write('PREPARATION_SUMMARY002.json',summary)
print(json.dumps(summary,indent=2))
