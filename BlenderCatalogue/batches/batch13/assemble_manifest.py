"""Publish four reviewed botanical designs. Reused seat/closure add no count."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
review=json.loads((ROOT/'qa/batch13/independent_final_review.json').read_text());assert review['passed'] is True
rows=[]
for i in range(7,11):
 aid=f'AST-BOT-{i:03d}';family='botanical_cluster' if i<10 else 'botanical_transition';base=ROOT/'assets'/family;mp=base/(aid+'.manifest.json');m=json.loads(mp.read_text())
 source=base/(m['source'] if i<10 else m['source_blend']);export=base/(m['export'] if i<10 else m['runtime_glb']);assert source.is_file() and export.is_file()
 rows.append({'catalogue_id':aid,'name':m['title'] if i<10 else m['name'],'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(mp.relative_to(ROOT)),'dimensions_blender_xyz_m':m['bounds_blender_z_up']['dimensions_m'] if i<10 else m['dimensions_m'],'evaluated_triangles':m['evaluated_triangles'] if i<10 else m['triangles'],'batch':'13','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export),'interface_record_id':aid})
assert len(rows)==4
manifest={'batch':'13','started_utc':'2026-10-02T21:51:58Z','kind':'commons_guided_botanical_edge_expansion','unique_authored_asset_count':4,'assets':rows,'actual_game_adoptions':0,'scope':'Denser pleated fan crown, rearward unequal trailing cluster, upright flowering bank and raised planted-seat end transition. A partial joined commons edge, no recovered courtyard.','review_completed_utc':a.review_completed_utc,'review':'qa/batch13/independent_final_review.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch13/reference_manifest.json','contract':'batches/batch13/CONTRACT.md','arrangement':'qa/batch13/assembly/plan.json','category_coverage':'CATEGORY_COVERAGE.json','quality_baseline_user_message':'Sentinel_1f1516ffa9a08191a5f37800301a001c','limits':['Reference garden density informs clustered placement, not a universal foliage wall or finished receiving court','The seated outlook, front approach and maintenance regions are source/component geometry proposals; no actor/species/cart acceptance','Source support and soil reservations do not certify horticulture, irrigation, substrate loads or growing roots','Opaque and two-sided foliage costs are recorded; wind, LOD and runtime/target-PC performance remain unmeasured','Reused AST-BOT-004 and006_START, inspection environment, generators and materials add no new design count','Game adoption remains zero while original project recovery is pending']}
(ROOT/'batches/batch13/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());old=[r for r in cat['assets'] if r.get('batch')!='13'];assert len(old)==65
cat['assets']=old+rows;cat['unique_authored_asset_count']=69;cat['batch']='01–13';cat['current_batch']='13';cat['version']=13;cat['component_review_completed_utc']=a.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to07_09_to13_passed_for_components_only_with_batch08_readiness'
for key,value in [('batches','batches/batch13/manifest.json'),('reviews','qa/batch13/independent_final_review.json')]:
 if value not in cat[key]:cat[key].append(value)
p.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'published_designs':len(rows),'catalogue_total':len(cat['assets']),'triangles':sum(x['evaluated_triangles'] for x in rows),'adoptions':0},indent=2))
