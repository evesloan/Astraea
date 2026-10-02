"""Publish four independently reviewed R3-guided landing components."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
review=json.loads((ROOT/'qa/batch11/independent_final_review.json').read_text());assert review['passed'] is True
ids={f'AST-LND-{i:03d}' for i in range(1,5)};rows=[]
for family in ('landing_guest','landing_service'):
 base=ROOT/'assets'/family
 for path in sorted(base.glob('AST-*.manifest.json')):
  m=json.loads(path.read_text());assert m['catalogue_id'] in ids
  source,export=base/m['source'],base/m['export'];assert source.is_file() and export.is_file() and (base/m['generator']).is_file()
  if family=='landing_service':
   assert 'title' in m and 'dimensions_m' in m['bounds_blender_z_up'];name=m['title'];dimensions=m['bounds_blender_z_up']['dimensions_m']
  else:
   name=m['name'];dimensions=m['dimensions_blender_xyz_m']
  rows.append({'catalogue_id':m['catalogue_id'],'name':name,'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(path.relative_to(ROOT)),'dimensions_blender_xyz_m':dimensions,'evaluated_triangles':m['evaluated_triangles'],'batch':'11','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export),'interface_record_id':m['catalogue_id']})
assert len(rows)==4 and {r['catalogue_id'] for r in rows}==ids;rows.sort(key=lambda r:r['catalogue_id'])
manifest={'batch':'11','started_utc':'2026-10-02T19:24:06Z','kind':'district_guided_guest_service_landing_interfaces','unique_authored_asset_count':4,'assets':rows,'actual_game_adoptions':0,'scope':'Guest directory/cove return and fitted waiting/luggage edge; protected staff arrival/control return and fixed service inspection/retrieval edge. Proposed separate landing interfaces guided by R3. Existing guest/staff lighting is disclosed QA reuse, adding zero designs.','review_completed_utc':a.review_completed_utc,'review':'qa/batch11/independent_final_review.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch11/reference_manifest.json','interface_contract':'batches/batch11/interface_contract.json','arrangement_plan':'qa/batch11/assembly/plan.json','category_coverage':'CATEGORY_COVERAGE.json','quality_baseline_user_message':'Sentinel_1f1516ffa9a08191a5f37800301a001c','limits':['R3 plan boxes are proposals, not recovered host or safe solid envelopes','No actual aperture, leaf/cassette travel, headroom, shaft, support, pit or lift operation is established','Preserve empty guest central/front zones and the west staff approach; the upper staff route still joins the public cross-street','Components have explicit designed heights only; no available ceiling height is inferred from deck intervals','Nominal guest edge margins and staff component separation include only 0.1m reserve; later trim and motion need renewed fit checks','Controls, directory art, waiting posture, storage use and fixture mounts are component interfaces, not implemented game behavior or universal species fit','Collision and source tests remain bounded offline evidence; no actor/cart route, guard/safety or target-PC certification']}
(ROOT/'batches/batch11/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());old=[r for r in cat['assets'] if r.get('batch')!='11'];assert len(old)==57
cat['assets']=old+rows;cat['unique_authored_asset_count']=61;cat['batch']='01–11';cat['current_batch']='11';cat['version']=11;cat['component_review_completed_utc']=a.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to07_09_to11_passed_for_components_only_with_batch08_readiness'
for key,value in [('batches','batches/batch11/manifest.json'),('reviews','qa/batch11/independent_final_review.json')]:
 if value not in cat[key]:cat[key].append(value)
p.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'new_designs':4,'total_unique':61,'new_exported_triangles':sum(r['evaluated_triangles'] for r in rows)},indent=2))
