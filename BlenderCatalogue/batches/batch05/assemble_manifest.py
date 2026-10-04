"""Assemble source-backed records for the reviewed aquatic component checkpoint."""
from pathlib import Path
import json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--review-completed-utc',required=True);a=ap.parse_args();rows=[]
for family in ('aquatic_lounge','aquatic_edges','aquatic_float'):
 base=ROOT/'assets'/family
 for mp in sorted(base.glob('AST-AQU-*.manifest.json')):
  m=json.loads(mp.read_text());sp=base/m['source'];ep=base/m.get('exchange',m.get('export'));assert sp.is_file() and ep.is_file()
  row={'catalogue_id':m['catalogue_id'],'name':m.get('name',m.get('title',m.get('design'))),'family':family,'source':str(sp.relative_to(ROOT)),'export':str(ep.relative_to(ROOT)),'manifest':str(mp.relative_to(ROOT)),'dimensions_blender_xyz_m':m.get('dimensions_m',m.get('bounds_blender_z_up',{}).get('dimensions_m')),'evaluated_triangles':m.get('triangles',m.get('evaluated_triangles')),'batch':'05','adopted_game_instances':0,'source_sha256':sha(sp),'export_sha256':sha(ep)}
  assert row['dimensions_blender_xyz_m'] and row['evaluated_triangles'];rows.append(row)
rows.sort(key=lambda r:r['catalogue_id']);assert len(rows)==6 and len({r['catalogue_id'] for r in rows})==6
m={'batch':'05','started_utc':'2026-10-02T12:06:20Z','unique_authored_asset_count':6,'derived_exports_not_unique':['AST-AQU-003_START','AST-AQU-003_END'],'assets':rows,'actual_game_adoptions':0,'scope':'Wet-area lounge pair, coping/drain edges, compact entry and seating float. Component catalogue, not a recovered pool district or complete aquatic programme.','review_completed_utc':a.review_completed_utc,'review':'qa/batch05/independent_review.md','coordinate_contract':'standards/COORDINATE_CONTRACT.md','coordinate_evidence':'qa/batch05/independent_coordinate_report.json','reference_manifest':'batches/batch05/reference_manifest.json','material_library':'materials/aquatic/manifest.json','limitations':['Actual water physics, boarding, species fit, safe/accessible installed routes, structural load and engine collisions remain pending','Target-PC performance, resource sharing and LOD require game adoption','Neutral inspection platforms are QA fixtures and are not game assets']}
(ROOT/'batches/batch05/manifest.json').write_text(json.dumps(m,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());cat['assets']=[r for r in cat['assets'] if r.get('batch')!='05']+rows;cat['unique_authored_asset_count']=len(cat['assets']);cat['batch']='01–05';cat['version']=5;cat['current_batch']='05';cat['component_review_completed_utc']=a.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to05_passed_for_components_only'
for value in ['batches/batch05/manifest.json']:
 if value not in cat['batches']:cat['batches'].append(value)
for value in ['qa/batch05/independent_review.md','qa/batch05/independent_coordinate_report.json']:
 if value not in cat['reviews']:cat['reviews'].append(value)
if not any(r['path']=='materials/aquatic/manifest.json' for r in cat['material_libraries']):cat['material_libraries'].append({'path':'materials/aquatic/manifest.json','scope':'ordinary opaque aquatic furniture, float and edge finishes','revision':'astraea-aquatic-materials-01'})
cat['coordinate_contract']='standards/COORDINATE_CONTRACT.md';cat['coordinate_compatibility']='standards/coordinate_compatibility.json'
source_report=json.loads((ROOT/'qa/batch05/cabinet_metadata_revision/source_preservation_report.json').read_text())
glb_report=json.loads((ROOT/'qa/batch05/cabinet_metadata_revision/glb_preservation_report.json').read_text())
assert all(x['unchanged'] for x in source_report['components'].values())
assert glb_report['non_json_chunks_byte_identical'] and glb_report['all_json_outside_hinge_extras_identical'] and glb_report['unqualified_axis_absent']
for row in cat['assets']:
 if row['catalogue_id']=='AST-STF-007':
  row['source_sha256']=sha(ROOT/row['source']);row['export_sha256']=sha(ROOT/row['export']);row['metadata_revision']='hinge-frame-metadata-02';row['last_metadata_revision_batch']='05';row['geometry_revision']='Original Batch03 geometry preserved';row['metadata_evidence']='qa/batch05/cabinet_metadata_revision/'
  assert row['source_sha256']==source_report['source_after_sha256'] and row['export_sha256']==glb_report['current_glb_sha256']
  m['existing_asset_metadata_revisions']=[{'catalogue_id':'AST-STF-007','revision':'hinge-frame-metadata-02','source_before_sha256':source_report['source_before_sha256'],'source_after_sha256':row['source_sha256'],'export_before_sha256':glb_report['old_glb_sha256'],'export_after_sha256':row['export_sha256'],'new_artistic_asset':False,'geometry_and_materials_preserved':True}]
(ROOT/'batches/batch05/manifest.json').write_text(json.dumps(m,indent=2)+'\n')
p.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'new_designs':len(rows),'total_unique':cat['unique_authored_asset_count'],'unique_design_triangles':sum(r['evaluated_triangles'] for r in rows)},indent=2))
