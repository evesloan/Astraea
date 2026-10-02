"""Publish the reviewed salon kit without treating QA stock as new designs."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
review=json.loads((ROOT/'qa/batch10/independent_final_review.json').read_text());assert review['passed'] is True
ids={f'AST-SAL-{i:03d}' for i in range(1,7)};rows=[]
for family in ('salon_threshold','salon_edges'):
 base=ROOT/'assets'/family
 for path in sorted(base.glob('AST-*.manifest.json')):
  m=json.loads(path.read_text());assert m['catalogue_id'] in ids
  source,export=base/m['source'],base/m['export'];assert source.is_file() and export.is_file() and (base/m['generator']).is_file()
  rows.append({'catalogue_id':m['catalogue_id'],'name':m['name'],'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(path.relative_to(ROOT)),'dimensions_blender_xyz_m':m['dimensions_blender_xyz_m'],'evaluated_triangles':m['evaluated_triangles'],'batch':'10','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export),'interface_record_id':m['catalogue_id']})
assert len(rows)==6 and {r['catalogue_id'] for r in rows}==ids
rows.sort(key=lambda r:r['catalogue_id']);assert sum(r['evaluated_triangles'] for r in rows)==16728
manifest={'batch':'10','kind':'district_guided_adjustable_component_kit','unique_authored_asset_count':6,'assets':rows,'actual_game_adoptions':0,'scope':'Deep portal return, rising cove insert, quiet acoustic book/seat return, planted seat junction, balcony/portal terminal and two-faced service storage. Spatially arranged component kit and partial joined bay, using archived D09 salon intent and new adjustable QA dimensions.','review_completed_utc':a.review_completed_utc,'review':'qa/batch10/independent_final_review.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch10/reference_manifest.json','interface_contract':'batches/batch10/interface_contract.json','source_only_rebuilds':['assets/salon_threshold/qa/source_only_rebuild.json','assets/salon_edges/qa/source_only_rebuild.json'],'independent_rebuild_review':'qa/batch10/independent_rebuild_receipts.json','arrangement':'qa/batch10/assembly/render_evidence_v2.json','independent_spatial_screen':'qa/batch10/spatial_review/exported_arrangement_screen.json','category_coverage':'CATEGORY_COVERAGE.json','quality_baseline_user_message':'Sentinel_1f1516ffa9a08191a5f37800301a001c','limits':['Original host geometry, final guest polygon, floor support and moving-door interfaces are unavailable; no actual room adoption','Quiet/cove QA bounds have zero reserve at route edge and only0.06m below the proposed3.8m maximum; preserve adjustable sizing and placement','The4.4x3.1m minimum rectangular opening is a new QA exemplar; real aperture, leaf stroke, cassette and head reservations remain unknown','Balcony terminal has no infill and is an incomplete guard; no barrier compliance or load rating','Side storage cheek screens the lateral seated look toward arrival; forward and opposing planted-bay views are the accepted component relationships','Collision compounds are finite sampled proposals: four-facet exterior allowance18mm, crown clearance reduction11.774mm, cove underside intrusion4.023mm and intentional shallow finish-channel filling47.023mm; not continuous or runtime clearance certification','Two unscaled five-book QA subsets and two existing plants add zero artistic designs and establish no extra capacity','Neutral inspection lighting is not final venue lighting; actor/species/cart use, engine controls, native performance and full room composition remain pending']}
for rel in manifest['source_only_rebuilds']:assert (ROOT/rel).is_file(),rel
(ROOT/'batches/batch10/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());old=[r for r in cat['assets'] if r.get('batch')!='10'];assert len(old)==51
cat['assets']=old+rows;cat['unique_authored_asset_count']=57;cat['batch']='01–10';cat['current_batch']='10';cat['version']=10;cat['component_review_completed_utc']=a.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to07_09_10_passed_for_components_only_with_batch08_readiness'
for key,value in [('batches','batches/batch10/manifest.json'),('reviews','qa/batch10/independent_final_review.json')]:
 if value not in cat[key]:cat[key].append(value)
p.write_text(json.dumps(cat,indent=2)+'\n')
print(json.dumps({'new_designs':6,'total_unique':57,'new_exported_triangles':16728},indent=2))
