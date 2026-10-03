"""Validate reviewed/current catalogue bindings and freeze production inputs."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE='735f22d67bd31d93ec14c4eab4ff295d8cef2c4c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel):return json.loads((ROOT/rel).read_text())
def prior(rel):return json.loads(subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT))
cat=load('catalogue_manifest.json');index=load('standards/catalogue_interfaces.json');assert len(cat['assets'])==len(index['assets'])==77
for rel,current in [('catalogue_manifest.json',cat),('standards/catalogue_interfaces.json',index)]:
 old=prior(rel)['assets'];new={row['catalogue_id']:row for row in current['assets']};assert len(old)==73 and all(row==new[row['catalogue_id']] for row in old)
assert all(row['adopted_game_instances']==0 for row in cat['assets'])
review=load('qa/batch15/independent_final_review.json');assert review['passed'];records=[]
def scan(value):
 if isinstance(value,dict):
  if 'path' in value and 'sha256' in value:
   p=ROOT/value['path'];assert p.is_file() and sha(p)==value['sha256'],value['path'];records.append(value['path'])
  for v in value.values():scan(v)
 elif isinstance(value,list):
  for v in value:scan(v)
scan(review)
for row in index['assets']:scan(row['source_export_manifest_bindings'])
r=load('qa/batch15/assembly/r02/render_evidence.json');assert r['execution_complete'] and r['inputs_unchanged_during_execution'];assert len(r['views'])==4
assert sha(ROOT/'qa/batch15/assembly/build_inspection.py')==r['executed_script_sha256'];assert sha(ROOT/'qa/batch15/assembly/plan.json')==r['plan_sha256']
for row in r['items']:
 assert sha(ROOT/row['export'])==row['export_sha256']
 source_row=next(x for x in load('qa/batch15/assembly/plan.json')['items'] if x['key']==row['key'].removesuffix('_alternative'))
 for key,h in row['base_hashes'].items():assert sha(ROOT/source_row[key])==h
for name,v in r['views'].items():assert sha(ROOT/('qa/batch15/assembly/r02/'+name+'.png'))==v['image_sha256']
protected=[]
for rel in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines():
 if rel.startswith(('assets/','materials/')):
  old=subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT);assert (ROOT/rel).read_bytes()==old,rel;protected.append(rel)
inputs=[]
for folder in ['assets/crew_rest','assets/crew_personal']:
 for p in sorted((ROOT/folder).rglob('*')):
  rel=p.relative_to(ROOT)
  if p.is_file() and not any(x in ('qa','packages','__pycache__') for x in rel.parts) and p.suffix not in ('.blend1','.blend2'):
   inputs.append({'path':str(rel),'sha256':sha(p),'bytes':p.stat().st_size})
for rel in ['standards/materials.py','standards/staff_materials.py','standards/qa_frame.py','batches/batch15/CONTRACT.md','batches/batch15/reference_manifest.json','qa/batch15/assembly/plan.json','qa/batch15/assembly/build_inspection.py','qa/batch15/assembly/r02/render_evidence.json','qa/batch15/assembly/captured_geometry_metadata_bridge.json','batches/batch15/shared_interface_agreement.json']:
 p=ROOT/rel;inputs.append({'path':rel,'sha256':sha(p),'bytes':p.stat().st_size})
frozen={'scope':'Current production/input bytes at lead freeze; evidence scope remains defined by the independent review and source-only/capture receipts','files':inputs,'original_game_recovered':False,'game_adoptions':0};(ROOT/'qa/batch15/lead_frozen_input_receipt.json').write_text(json.dumps(frozen,indent=2)+'\n')
receipt={'passed':True,'baseline_commit':BASE,'new_designs':4,'catalogue_designs':77,'game_adoptions':0,'old_catalogue_rows_unchanged':73,'old_interface_rows_unchanged':73,'protected_prior_asset_material_files_unchanged':len(protected),'checked_final_review_and_index_bindings':len(records),'current_interface_source_export_manifest_bindings':231,'canonical_index_sha256':sha(ROOT/'standards/catalogue_interfaces.json'),'independent_review':'qa/batch15/independent_final_review.json','source_only_receipts':'qa/batch15/independent_rebuild_receipts.json','actual_arrangement':'qa/batch15/assembly/r02/render_evidence.json','frozen_input_receipt_sha256':sha(ROOT/'qa/batch15/lead_frozen_input_receipt.json'),'limits':'Component/source evidence only. Original crew room, berth identity, complete privacy, live curtain/drawer/light behavior, loads, body/species, engine and target-PC acceptance remain unverified.'}
(ROOT/'qa/batch15/lead_integration_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
