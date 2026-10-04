"""Publish the six reviewed categorical additions without re-counting derivatives."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
review=ROOT/'qa/batch09/independent_final_review.json'
assert json.loads(review.read_text())['passed'] is True
ids={'AST-GST-001','AST-GST-002','AST-GST-003','AST-LIB-008','AST-LIB-009','AST-LIB-010'}
rows=[]
for family in ('guest_use','library_use'):
 base=ROOT/'assets'/family
 for path in sorted(base.glob('AST-*.manifest.json')):
  m=json.loads(path.read_text());assert m['catalogue_id'] in ids
  for key in ('catalogue_id','name','source','export','generator','dimensions_blender_xyz_m','evaluated_triangles','material_roles'):assert key in m,(path,key)
  source,export=base/m['source'],base/m['export'];assert source.is_file() and export.is_file() and (base/m['generator']).is_file()
  rows.append({'catalogue_id':m['catalogue_id'],'name':m['name'],'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(path.relative_to(ROOT)),'dimensions_blender_xyz_m':m['dimensions_blender_xyz_m'],'evaluated_triangles':m['evaluated_triangles'],'batch':'09','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export),'interface_record_id':m['catalogue_id']})
assert len(rows)==6 and {r['catalogue_id'] for r in rows}==ids
rows.sort(key=lambda r:r['catalogue_id'])
manifest={'batch':'09','kind':'existing_family_categorical_expansion','started_utc':'2026-10-02T16:38:40Z','unique_authored_asset_count':6,'assets':rows,'actual_game_adoptions':0,'scope':'Guest reading floor lamp, wall sconce and luggage/personal-use console; library study fixture, low periodical browser and catalogue terminal stand. Original script-assisted editable components.','review_completed_utc':a.review_completed_utc,'review':'qa/batch09/independent_final_review.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch09/reference_manifest.json','source_only_rebuild':'qa/batch09/source_only_rebuild/report.json','category_coverage':'CATEGORY_COVERAGE.json','quality_baseline_user_message':'Sentinel_1f1516ffa9a08191a5f37800301a001c','limitations':['Neutral imported-component views do not implement or certify room lighting','Switches, screen art and control positions are proposed interfaces, without implemented engine behavior','Contact, service and collision proposals require real room, actor, species and controller validation','No original ship reconstruction, room allocation or target-PC performance claim','Subsequent asset kits respond to documented district purposes and sections; every new batch waits for this durable backup gate']}
(ROOT/'batches/batch09/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());old=[r for r in cat['assets'] if r.get('batch')!='09'];assert len(old)==45
cat['assets']=old+rows;cat['unique_authored_asset_count']=51;cat['batch']='01–09';cat['current_batch']='09';cat['version']=9;cat['component_review_completed_utc']=a.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to07_and09_passed_for_components_only_with_batch08_readiness'
for key,value in [('batches','batches/batch09/manifest.json'),('reviews','qa/batch09/independent_final_review.json')]:
 if value not in cat[key]:cat[key].append(value)
for rel,scope in [('assets/guest_use/texture_manifest.json','Guest fixture and personal-use details'),('assets/library_use/texture_manifest.json','Original library display, labels and periodical art')]:
 if (ROOT/rel).is_file() and not any(x['path']==rel for x in cat['material_libraries']):cat['material_libraries'].append({'path':rel,'scope':scope})
p.write_text(json.dumps(cat,indent=2)+'\n')
print(json.dumps({'new_designs':len(rows),'total_unique':51,'new_exported_triangles':sum(r['evaluated_triangles'] for r in rows)},indent=2))
