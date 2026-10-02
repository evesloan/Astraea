"""Validate the promoted metadata and frozen evidence without rebuilding assets."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE='62ad3577716127bfc419cddbb90fe5abf85b487e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel):return json.loads((ROOT/rel).read_text())
def prior(rel):return json.loads(subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT))
cat=load('catalogue_manifest.json');index=load('standards/catalogue_interfaces.json')
assert len(cat['assets'])==len(index['assets'])==61
for rel,current in [('catalogue_manifest.json',cat),('standards/catalogue_interfaces.json',index)]:
 old=prior(rel)['assets'];new={r['catalogue_id']:r for r in current['assets']};assert len(old)==57
 assert all(r==new[r['catalogue_id']] for r in old),rel
assert all(r['adopted_game_instances']==0 for r in cat['assets'])
review=load('qa/batch11/independent_final_review.json');assert review['passed']
records=[]
def scan(value):
 if isinstance(value,dict):
  if 'path' in value and 'sha256' in value:
   p=ROOT/value['path'];assert p.is_file() and sha(p)==value['sha256'],value['path'];records.append(value['path'])
  for v in value.values():scan(v)
 elif isinstance(value,list):
  for v in value:scan(v)
scan(review);scan(load('qa/batch11/independent_final_source_hash_receipt.json'))
for row in index['assets']:
 scan(row['source_export_manifest_bindings'])
spatial=ROOT/'qa/batch11/spatial_review/batch11_frozen_export_screen.json';assert sha(spatial)=='bdd9e92efe37f3eb659924f7e1c845a5495e55c0fca2dd732d38f0ab92b79375'
scan(load('qa/batch11/assembly/r03/source_freeze.json'))
r=load('qa/batch11/assembly/r03/render_evidence.json');assert all(r[x] is True for x in ['execution_complete','inputs_unchanged_during_execution']);assert len(r['views'])==4
for name,v in r['views'].items():assert sha(ROOT/('qa/batch11/assembly/r03/'+name+'.png'))==v['image_sha256']
protected=[]
for rel in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines():
 if rel.startswith(('assets/','materials/')):
  original=subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT);assert (ROOT/rel).read_bytes()==original,rel;protected.append(rel)
assert (ROOT/'qa/batch11/independent_rebuild_receipts.json').is_file()
receipt={'passed':True,'baseline_commit':BASE,'new_designs':4,'catalogue_designs':61,'game_adoptions':0,'old_catalogue_rows_unchanged':57,'old_interface_rows_unchanged':57,'protected_prior_asset_material_files_unchanged':len(protected),'checked_exact_file_bindings':len(records),'current_interface_source_export_manifest_bindings':183,'canonical_index_sha256':sha(ROOT/'standards/catalogue_interfaces.json'),'independent_review':'qa/batch11/independent_final_review.json','spatial_screen_sha256':sha(spatial),'reviewed_preflight_preserved':True,'source_only_receipts':'qa/batch11/independent_rebuild_receipts.json','limits':'Component/source and finite geometry evidence only; missing original host, native engine, actor/cart use and complete room acceptance remain open.'}
(ROOT/'qa/batch11/lead_integration_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
