"""Publish four independently reviewed aquatic arrival/use designs."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
assert json.loads((ROOT/'qa/batch14/independent_final_review_receipt.json').read_text())['passed'] is True
rows=[]
for i in range(7,11):
 aid=f'AST-AQU-{i:03d}';family='aquatic_towel_use' if i<9 else 'aquatic_wet_use';base=ROOT/'assets'/family;mp=base/(aid+'.manifest.json');m=json.loads(mp.read_text());source=base/m['source'];export=base/m['export'];assert source.is_file() and export.is_file()
 row={'catalogue_id':aid,'name':m['name'],'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(mp.relative_to(ROOT)),'dimensions_blender_xyz_m':m.get('dimensions_blender_xyz_m',m.get('dimensions_m')),'evaluated_triangles':m.get('evaluated_triangles',m.get('triangles')),'batch':'14','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export),'interface_record_id':aid}
 if i==8:
  derivative=base/'exports/AST-AQU-008_withdrawn.glb';assert derivative.is_file();row['state_derivatives']=[{'state':'withdrawn','export':str(derivative.relative_to(ROOT)),'sha256':sha(derivative),'counts_as_new_design':False}]
 rows.append(row)
assert len(rows)==4 and sum(x['evaluated_triangles'] for x in rows)==16860
manifest={'batch':'14','started_utc':'2026-10-02T22:40:54Z','kind':'D08_programme_guided_aquatic_arrival_use_components','unique_authored_asset_count':4,'assets':rows,'actual_game_adoptions':0,'scope':'Protected clean towel niche, guarded used return with removable wheeled container, optional compatible-user refreshment fixture and supported rinse-control housing. Relative component examples, no recovered aquatic room.','review_completed_utc':a.review_completed_utc,'review':'qa/batch14/independent_final_review_receipt.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch14/reference_manifest.json','programme_handoff':'references/aquatic_program/D08_programme_handoff.json','contract':'batches/batch14/CONTRACT.md','arrangement':'qa/batch14/assembly/plan.json','category_coverage':'CATEGORY_COVERAGE.json','quality_baseline_user_message':'Sentinel_1f1516ffa9a08191a5f37800301a001c','limits':['Historical D08 dry changing and aft towel-care service allocations remain separate; no adjoining-room or private-connector claim','Historical sixteen changing cubicles do not add occupancy or establish six-species/accessible fitting','Source/native control, mount and state interfaces do not implement gameplay, release hardware, loads or water/laundry behavior','The checked throat is a geometric air passage, not proof of towel deformation or handling capacity','Substances, hydration/rinse suitability, plumbing, drainage integration, hygiene and species compatibility remain unassigned','Collision profiles and clear spaces remain component proposals with finite measured limits; target-PC/engine performance is unmeasured','The withdrawn container state and integrated towel stock add no new design count; game adoptions remain zero']}
(ROOT/'batches/batch14/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());old=[x for x in cat['assets'] if x.get('batch')!='14'];assert len(old)==69;cat.update({'assets':old+rows,'unique_authored_asset_count':73,'batch':'01–14','current_batch':'14','version':14,'component_review_completed_utc':a.review_completed_utc});cat['status']['independent_component_visual_review']='batches01_to07_09_to14_passed_for_components_only_with_batch08_readiness'
for key,value in [('batches','batches/batch14/manifest.json'),('reviews','qa/batch14/independent_final_review_receipt.json')]:
 if value not in cat[key]:cat[key].append(value)
p.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'published_designs':4,'catalogue_total':73,'triangles':16860,'adoptions':0},indent=2))
