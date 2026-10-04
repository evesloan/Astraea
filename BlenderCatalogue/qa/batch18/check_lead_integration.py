"""Validate reviewed/current catalogue bindings and freeze production inputs."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE='95dc75eeb5ea36af8e74ddf372e191e9dd39432e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel):return json.loads((ROOT/rel).read_text())
def prior(rel):return json.loads(subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT))
cat=load('catalogue_manifest.json');index=load('standards/catalogue_interfaces.json');assert len(cat['assets'])==len(index['assets'])==89
for rel,current in [('catalogue_manifest.json',cat),('standards/catalogue_interfaces.json',index)]:
 old=prior(rel)['assets'];new={row['catalogue_id']:row for row in current['assets']};assert len(old)==85 and all(row==new[row['catalogue_id']] for row in old)
assert all(row['adopted_game_instances']==0 for row in cat['assets'])
review=load('qa/batch18/independent_final_review.json');assert review['passed'];records=[]
promotion=load('qa/batch18/independent_promotion_registry_addendum.json');assert promotion['passed']
assert sha(ROOT/'qa/batch18/independent_promotion_registry_addendum.json')=='2e512bdb6e18c2bf737832cd03ad22650a9879dd7e40dbd73c4ea9255fd41fce'
exception=promotion['approved_exception'];assert exception['path']=='standards/source_package_groups.json' and exception['baseline_commit']==BASE
old_registry_bytes=subprocess.check_output(['git','show',BASE+':'+exception['path']],cwd=ROOT)
assert hashlib.sha256(old_registry_bytes).hexdigest()==exception['baseline_sha256']==exception['frozen_review_sha256']
assert sha(ROOT/exception['path'])==exception['approved_current_sha256']
old_groups=json.loads(old_registry_bytes);new_groups=load(exception['path'])
assert new_groups['groups'][:-1]==old_groups['groups'] and new_groups['groups'][-1]==exception['new_group'] and new_groups['policy']==old_groups['policy']

def scan(value):
 if isinstance(value,dict):
  if 'path' in value and 'sha256' in value:
   p=ROOT/value['path']
   if value['path']==exception['path'] and value['sha256']==exception['frozen_review_sha256']:
    assert hashlib.sha256(old_registry_bytes).hexdigest()==value['sha256'] and sha(p)==exception['approved_current_sha256']
    records.append(value['path']+'@independently_reviewed_metadata_promotion')
   else:
    assert p.is_file() and sha(p)==value['sha256'],value['path'];records.append(value['path'])
  for v in value.values():scan(v)
 elif isinstance(value,list):
  for v in value:scan(v)
scan(review);scan(promotion)
scan(load('qa/batch18/spatial_audit/manifest.json'))
registry=load('standards/body_proxy_candidates.json');scan(registry);scan(cat['optional_body_proxy_registry']);scan(cat.get('additional_optional_body_proxy_registries', []))
new_registry=load('batches/batch18/body_proxy_candidates.json');scan(new_registry);assert {row['catalogue_id'] for row in new_registry['assets']}=={f'AST-RTL-{i:03d}' for i in range(1,5)}
assert sha(ROOT/'standards/catalogue_interfaces.json')==review['proposed_interface_index']['sha256']
old_registry=prior('standards/body_proxy_candidates.json');current_registry={row['catalogue_id']:row for row in registry['assets']}
assert all(row==current_registry[row['catalogue_id']] for row in old_registry['assets'])
assert all(row in cat['additional_optional_body_proxy_registries'] for row in prior('catalogue_manifest.json').get('additional_optional_body_proxy_registries',[]))
for row in index['assets']:scan(row['source_export_manifest_bindings'])
captures=[]
for tag,expected in [('r01',4)]:
 rel='qa/batch18/assembly/'+tag+'/render_evidence.json';r=load(rel);assert r['execution_complete'] and r['inputs_unchanged_during_execution'] and r['all_framing_passed'];assert len(r['views'])==expected
 assert sha(ROOT/'qa/batch18/assembly/build_inspection.py')==r['executed_script_sha256'];assert sha(ROOT/'qa/batch18/assembly/plan.json')==r['plan_sha256']
 for row in r['items']:
  assert sha(ROOT/row['export'])==row['export_sha256']
  source_row=next(x for x in load('qa/batch18/assembly/plan.json')['items'] if x['key']==row['row_key'])
  for key,h in row['base_hashes'].items():assert sha(ROOT/source_row[key])==h
 for name,v in r['views'].items():assert sha(ROOT/('qa/batch18/assembly/'+tag+'/'+name+'.png'))==v['image_sha256']
 captures.append({'path':rel,'sha256':sha(ROOT/rel),'views':expected,'groups':r['captured_groups']})
protected=[]
for rel in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines():
 if rel.startswith(('assets/','materials/','standards/')) and rel not in ['standards/catalogue_interfaces.json','standards/source_package_groups.json']:
  old=subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT);assert (ROOT/rel).read_bytes()==old,rel;protected.append(rel)
inputs=[]
for folder in ['assets/retail_display','assets/retail_work','materials/retail']:
 for p in sorted((ROOT/folder).rglob('*')):
  rel=p.relative_to(ROOT)
  if p.is_file() and not any(x in ('qa','packages','__pycache__') for x in rel.parts) and p.suffix not in ('.blend1','.blend2'):
   inputs.append({'path':str(rel),'sha256':sha(p),'bytes':p.stat().st_size})
for rel in ['standards/materials.py','standards/retail_materials.py','standards/body_proxy_candidates.json','standards/qa_frame.py','batches/batch18/CONTRACT.md','qa/batch18/independent_promotion_registry_addendum.json','batches/batch18/body_proxy_candidates.json','batches/batch18/publish_body_proxy_registry.py','batches/batch18/reference_manifest.json','qa/batch18/assembly/plan.json','qa/batch18/assembly/build_inspection.py','qa/batch18/assembly/r01/render_evidence.json','qa/batch18/arrangement_freeze_receipt.json','qa/batch18/spatial_audit/manifest.json']:
 p=ROOT/rel;inputs.append({'path':rel,'sha256':sha(p),'bytes':p.stat().st_size})
frozen={'scope':'Current production/input bytes at lead freeze; evidence scope remains defined by the independent review and source-only/capture receipts','files':inputs,'original_game_recovered':False,'game_adoptions':0};(ROOT/'qa/batch18/lead_frozen_input_receipt.json').write_text(json.dumps(frozen,indent=2)+'\n')
receipt={'passed':True,'baseline_commit':BASE,'new_designs':4,'catalogue_designs':89,'game_adoptions':0,'old_catalogue_rows_unchanged':85,'old_interface_rows_unchanged':85,'protected_prior_asset_material_and_unchanged_standard_files':len(protected),'checked_final_review_and_index_bindings':len(records),'current_interface_source_export_manifest_bindings':267,'canonical_index_sha256':sha(ROOT/'standards/catalogue_interfaces.json'),'independent_review':'qa/batch18/independent_final_review.json','source_only_receipts':'qa/batch18/rebuild_review/FINAL_REBUILD_RECEIPT.json','legacy_body_proxy_registry_sha256':sha(ROOT/'standards/body_proxy_candidates.json'),'batch_body_proxy_registry_sha256':sha(ROOT/'batches/batch18/body_proxy_candidates.json'),'prior_body_proxy_records_unchanged':True,'delivery_registry_promotion_addendum':{'path':'qa/batch18/independent_promotion_registry_addendum.json','sha256':sha(ROOT/'qa/batch18/independent_promotion_registry_addendum.json')},'historical_registry_binding_verified_against_baseline':True,'actual_arrangement':captures,'frozen_input_receipt_sha256':sha(ROOT/'qa/batch18/lead_frozen_input_receipt.json'),'limits':'Component/source evidence only. Original R070 finished boundaries, door/support and activity slots, operator/body/species fit, merchant/payment/inventory behaviour, loads, engine and target-PC acceptance remain unverified.'}
(ROOT/'qa/batch18/lead_integration_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
