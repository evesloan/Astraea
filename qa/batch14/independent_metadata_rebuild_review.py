"""Independent generated JSON equivalence and hand-authored dependency/material inventory checks."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
def norm(x):
 if isinstance(x,dict):return{k:norm(v)for k,v in x.items()if k not in ['source_sha256','blend_sha256']}
 if isinstance(x,list):return[norm(v)for v in x]
 return x
for family,revision in [('aquatic_wet_use','r02'),('aquatic_towel_use','r01')]:
 rp=OUT/f'independent_rebuild_{family}_{revision}.json';r=json.loads(rp.read_text());assert r['passed'];base=ROOT/'assets'/family;stage=ROOT/r['stage']/'assets'/family;generated=[];ancillary=[]
 for p in sorted(base.glob('*.json')):
  q=stage/p.name
  if q.exists():
   a,b=norm(json.loads(p.read_text())),norm(json.loads(q.read_text()));generated.append({'path':str(p.relative_to(ROOT)),'current_sha256':sha(p),'rebuilt_path':str(q.relative_to(ROOT)),'rebuilt_sha256':sha(q),'bytes_identical':sha(p)==sha(q),'semantic_records_equal_except_source_blend_binary_hash':a==b,'differing_top_level_fields':[k for k in set(a)|set(b)if a.get(k)!=b.get(k)]if isinstance(a,dict)and isinstance(b,dict)else[]})
  else:ancillary.append(str(p.relative_to(ROOT)))
 dp=base/'dependency_manifest.json';d=json.loads(dp.read_text());inputs=d.get('inputs',d.get('source_only_inputs'));actual={x['path']:x['sha256']for x in r['production_inputs']};declared={x['path_from_catalogue_root']:x['sha256']for x in inputs};dependency_pass=actual==declared
 mats=[];matp=base/'material_role_manifest.json'
 if matp.exists():
  mm=json.loads(matp.read_text());expected=set()
  for mp in base.glob('AST-*.manifest.json'):expected.update(json.loads(mp.read_text())['material_roles'])
  for v in mm['used_roles']:
   p=ROOT/v['path_from_catalogue_root'];mats.append({'role':v['role'],'image_path':str(p.relative_to(ROOT)),'declared_hash_matches_current':sha(p)==v['sha256']})
  material_pass={x['role']for x in mats}==expected and all(x['declared_hash_matches_current']for x in mats)
 else:material_pass=True
 row={'family':family,'rebuild_receipt_sha256':sha(rp),'generated_json_comparisons':generated,'ancillary_not_written_by_builder':ancillary,'dependency_manifest_sha256':sha(dp),'declared_source_only_closure_exactly_matches_independent_seeds':dependency_pass,'used_material_inventory_checks':mats,'used_material_inventory_passed':material_pass,'pass':all(x['semantic_records_equal_except_source_blend_binary_hash']for x in generated)and dependency_pass and material_pass};rows.append(row);print(family,row['pass'],'differences',[(x['path'],x['differing_top_level_fields'])for x in generated if not x['semantic_records_equal_except_source_blend_binary_hash']],flush=True)
(OUT/'independent_metadata_rebuild_review.json').write_text(json.dumps({'passed':all(x['pass']for x in rows),'families':rows,'scope':'Every builder-produced top-level JSON is compared against current production metadata. Only source .blend binary hashes are normalized because rebuild path/storage serialization changes those bytes; editable/evaluated source equivalence and actual current source hashes are independently verified. Ancillary inventories not emitted by the builder are explicitly classified and checked against actual inputs and material assets.','executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
