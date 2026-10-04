"""Publish four independently reviewed auditorium component designs."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
assert json.loads((ROOT/'qa/batch16/independent_final_review.json').read_text())['passed'] is True
rows=[]
for i in range(1,5):
 aid=f'AST-CUL-{i:03d}';family='auditorium_arrival' if i<3 else 'auditorium_use';base=ROOT/'assets'/family;mp=base/(aid+'.manifest.json');m=json.loads(mp.read_text());source=base/m['source'];export=base/m['export'];assert source.is_file() and export.is_file()
 row={'catalogue_id':aid,'name':m['title'],'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(mp.relative_to(ROOT)),'dimensions_blender_xyz_m':m['bounds_blender_z_up']['dimensions_m'],'evaluated_triangles':m['evaluated_triangles'],'batch':'16','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export),'interface_record_id':aid}
 for st in m.get('state_derivatives',[]):
  derivative=base/st['export'];assert derivative.is_file();row.setdefault('state_derivatives',[]).append({'state':st.get('state',st.get('name')),'export':str(derivative.relative_to(ROOT)),'sha256':sha(derivative),'counts_as_new_design':False})
 rows.append(row)
assert len(rows)==4
manifest={'batch':'16','started_utc':'2026-10-03T01:27:33Z','kind':'D11_programme_guided_auditorium_arrival_audience_backstage_components','unique_authored_asset_count':4,'assets':rows,'actual_game_adoptions':0,'scope':'Acoustic/programme return, usher station, economical audience-seat/end module and separate backstage cue/work-light stand. Relative component examples do not create a foyer, row allocation or stage-wing connection.','review_completed_utc':a.review_completed_utc,'review':'qa/batch16/independent_final_review.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch16/reference_manifest.json','programme_handoff':'references/auditorium/D11_programme_reference_handoff.json','contract':'batches/batch16/CONTRACT.md','arrangement':'qa/batch16/assembly/plan.json','category_coverage':'CATEGORY_COVERAGE.json','quality_baseline_user_message':'Sentinel_1f1516ffa9a08191a5f37800301a001c','limits':['The historical 2,200 + 6×200 places remain unchanged; D12/D13 access aliases add no admissions','The workshop is a separate allocation, without an established direct stage-wing connection','Proposed seat dimensions and adjacent QA examples do not establish host row pitch, rakes, aisles, six-species or actor/cart fit','Fold/removal/aim states and source/native control markers do not implement gameplay, ticketing, persistence, loads or electrical behaviour','Acoustic and light roles are visual/design intent; performance, wiring, live cues and photometry remain unmeasured','Repeated geometry counts are component data, not a crowd-rendering benchmark; original engine adoption is zero']}
(ROOT/'batches/batch16/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());old=[x for x in cat['assets'] if x.get('batch')!='16'];assert len(old)==77;cat.update({'assets':old+rows,'unique_authored_asset_count':81,'batch':'01–16','current_batch':'16','version':16,'component_review_completed_utc':a.review_completed_utc});cat['status']['independent_component_visual_review']='batches01_to07_09_to16_passed_for_components_only_with_batch08_readiness'
for key,value in [('batches','batches/batch16/manifest.json'),('reviews','qa/batch16/independent_final_review.json')]:
 if value not in cat[key]:cat[key].append(value)
p.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'published_designs':4,'catalogue_total':81,'triangles':sum(x['evaluated_triangles'] for x in rows),'adoptions':0},indent=2))
