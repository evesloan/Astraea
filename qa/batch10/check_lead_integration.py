"""Validate the promoted metadata and frozen evidence without rebuilding assets."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE='ea303a53c42de3d8b9fb3f05ae513c5d83cbab59'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel):return json.loads((ROOT/rel).read_text())
def prior(rel):return json.loads(subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT))
cat=load('catalogue_manifest.json');index=load('standards/catalogue_interfaces.json')
assert len(cat['assets'])==len(index['assets'])==57
for rel,current in [('catalogue_manifest.json',cat),('standards/catalogue_interfaces.json',index)]:
 old=prior(rel)['assets'];new={r['catalogue_id']:r for r in current['assets']};assert len(old)==51
 assert all(r==new[r['catalogue_id']] for r in old),rel
assert all(r['adopted_game_instances']==0 for r in cat['assets'])
review=load('qa/batch10/independent_final_review.json');assert review['passed']
records=[]
def scan(value):
 if isinstance(value,dict):
  if 'path' in value and 'sha256' in value:
   p=ROOT/value['path'];assert p.is_file() and sha(p)==value['sha256'],value['path'];records.append(value['path'])
  for v in value.values():scan(v)
 elif isinstance(value,list):
  for v in value:scan(v)
scan(review);scan(load('qa/batch10/independent_final_source_hash_receipt.json'))
for row in index['assets']:
 scan(row['source_export_manifest_bindings'])
spatial=ROOT/'qa/batch10/spatial_review/exported_arrangement_screen.json';assert sha(spatial)=='26b2f2c6aa14bf2ac5b4e33ceedfef03516ce2554c2f4a2add217a02f41b5fe4'
assert sha(ROOT/'qa/batch10/assembly/preflight.json')=='e8e3beec3107cc365c177051c8119e605ec65dba9d64724f14d3257dd5bd79db'
r=load('qa/batch10/assembly/render_evidence_v2.json');assert all(r[x] is True for x in ['execution_complete','inputs_unchanged_during_execution','all_final_views_present'])
protected=[]
for rel in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines():
 if rel.startswith(('assets/','materials/')):
  original=subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT);assert (ROOT/rel).read_bytes()==original,rel;protected.append(rel)
receipt={'passed':True,'baseline_commit':BASE,'new_designs':6,'catalogue_designs':57,'game_adoptions':0,'old_catalogue_rows_unchanged':51,'old_interface_rows_unchanged':51,'protected_prior_asset_material_files_unchanged':len(protected),'checked_exact_file_bindings':len(records),'current_interface_source_export_manifest_bindings':171,'canonical_index_sha256':sha(ROOT/'standards/catalogue_interfaces.json'),'independent_review':'qa/batch10/independent_final_review.json','spatial_screen_sha256':sha(spatial),'reviewed_preflight_preserved':True,'source_only_receipts':'qa/batch10/independent_rebuild_receipts.json','limits':'Component/source and finite geometry evidence only; missing original host, native engine, actor/cart use and complete room acceptance remain open.'}
(ROOT/'qa/batch10/lead_integration_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
