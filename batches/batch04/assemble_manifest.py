"""Assemble source-backed catalogue records for the reviewed botanical checkpoint."""
from pathlib import Path
import json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
rows=[]
for family in ['botanical_canopy','botanical_understory','botanical_planter']:
 base=ROOT/'assets'/family
 for mp in sorted(base.glob('AST-BOT-*.manifest.json')):
  m=json.loads(mp.read_text());source=m.get('source',m.get('source_blend'));export=m.get('exchange',m.get('runtime_glb',m.get('export')))
  assert isinstance(source,str) and isinstance(export,str)
  sp=base/source;ep=base/export;assert sp.is_file() and ep.is_file()
  row={'catalogue_id':m['catalogue_id'],'name':m.get('name',m.get('title',m.get('design'))),'family':family,'source':str(sp.relative_to(ROOT)),'export':str(ep.relative_to(ROOT)),'manifest':str(mp.relative_to(ROOT)),'dimensions_blender_xyz_m':m.get('dimensions_m',m.get('bounds_blender_z_up',{}).get('dimensions_m')),'evaluated_triangles':m.get('triangles',m.get('evaluated_triangles')),'batch':'04','adopted_game_instances':0,'source_sha256':sha(sp),'export_sha256':sha(ep)}
  assert row['dimensions_blender_xyz_m'] and row['evaluated_triangles']
  rows.append(row)
assert len(rows)==6 and len({r['catalogue_id'] for r in rows})==6
rows.sort(key=lambda r:r['catalogue_id'])
manifest={'batch':'04','started_utc':'2026-10-02T11:20:28Z','unique_authored_asset_count':6,'derived_exports_not_unique':['AST-BOT-006_START'],'assets':rows,'actual_game_adoptions':0,'component_scope':'Small open-crown specimen, two low planting forms and joined planted seating. Not a complete botanical library or lush garden/courtyard installation.','review_completed_utc':a.review_completed_utc,'review':'qa/batch04/independent_review.md','reference_manifest':'batches/batch04/reference_manifest.json','material_library':'materials/botanical/manifest.json','limitations':['Game integration, species contact, collider behavior, wind, LOD, runtime material sharing and target-PC performance pending','Dense mature/large canopy variants and aquatic planting are separate future designs','Seated outlook and approach checks apply only to the measured component arrangement']}
(ROOT/'batches/batch04/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
pth=ROOT/'catalogue_manifest.json';cat=json.loads(pth.read_text());cat['assets']=[r for r in cat['assets'] if r.get('batch')!='04']+rows;cat['unique_authored_asset_count']=len(cat['assets']);cat['batch']='01–04';cat['version']=4;cat['current_batch']='04';cat['component_review_completed_utc']=a.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to04_passed_for_components_only'
for value in ['batches/batch04/manifest.json']:
 if value not in cat['batches']:cat['batches'].append(value)
for value in ['qa/batch04/independent_review.md','qa/batch04/independent_reviewed_files.json']:
 if value not in cat['reviews']:cat['reviews'].append(value)
if not any(r['path']=='materials/botanical/manifest.json' for r in cat['material_libraries']):cat['material_libraries'].append({'path':'materials/botanical/manifest.json','scope':'opaque botanical foliage, bark and soil','revision':'astraea-botanical-materials-01'})
pth.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'assets':len(rows),'total_unique':cat['unique_authored_asset_count'],'triangles':sum(r['evaluated_triangles'] for r in rows)},indent=2))
