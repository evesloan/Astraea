"""Assemble the reviewed hospitality family from explicit shared manifest fields."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);args=p.parse_args()
rows=[]
for family in ('hospitality_counters','hospitality_stations','hospitality_serviceware'):
 base=ROOT/'assets'/family
 for path in sorted(base.glob('AST-HSP-*.manifest.json')):
  m=json.loads(path.read_text())
  for key in ('catalogue_id','name','source','export','generator','dimensions_blender_xyz_m','evaluated_triangles','material_roles'):assert key in m,(path,key)
  source,export=base/m['source'],base/m['export'];assert source.is_file() and export.is_file() and (base/m['generator']).is_file()
  rows.append({'catalogue_id':m['catalogue_id'],'name':m['name'],'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(path.relative_to(ROOT)),'dimensions_blender_xyz_m':m['dimensions_blender_xyz_m'],'evaluated_triangles':m['evaluated_triangles'],'batch':'07','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export)})
rows.sort(key=lambda r:r['catalogue_id']);assert [r['catalogue_id'] for r in rows]==[f'AST-HSP-{i:03d}' for i in range(1,7)]
manifest={'batch':'07','started_utc':'2026-10-02T14:17:23Z','unique_authored_asset_count':6,'assets':rows,'actual_game_adoptions':0,'scope':'Pantry counter and return, beverage station, dirty-dish return, plate/tray storage and distinct dining service trolley. New script-assisted editable components, not a recovered restaurant or player cart.','review_completed_utc':args.review_completed_utc,'review':'qa/batch07/independent_final_review.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch07/reference_manifest.json','shared_materials':['materials/material_manifest.json','materials/staff/manifest.json'],'connected_component_evidence':'qa/batch07/arrangement/evidence.json','limitations':['Component mating/support/service proposals require actual room, actor, species, route and engine validation','No appliance, food, fluid, caster/controller or cargo behavior implemented','Finite component motion checks are not mechanical, food-safety or load certification','Trolley is a new service furnishing, not a replacement for the original player cart','Neutral inspection supports and lighting are QA, not final dining architecture or atmosphere','Runtime material sharing, LOD, shadows, memory and target-PC performance remain pending']}
(ROOT/'batches/batch07/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());cat['assets']=[r for r in cat['assets'] if r.get('batch')!='07']+rows;assert len(cat['assets'])==45
cat['unique_authored_asset_count']=45;cat['batch']='01–07';cat['current_batch']='07';cat['version']=7;cat['component_review_completed_utc']=args.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to07_passed_for_components_only'
for key,value in [('batches','batches/batch07/manifest.json'),('reviews','qa/batch07/independent_final_review.json')]:
 if value not in cat[key]:cat[key].append(value)
p.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'new_designs':len(rows),'total_unique':45,'new_triangles':sum(r['evaluated_triangles'] for r in rows)},indent=2))
