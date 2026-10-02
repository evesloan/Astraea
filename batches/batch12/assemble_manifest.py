"""Publish four reviewed clinical designs; the privacy state is a derivative."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--review-completed-utc',required=True);a=p.parse_args()
review=json.loads((ROOT/'qa/batch12/independent_final_review.json').read_text());assert review['passed'] is True
ids={f'AST-MED-{i:03d}' for i in range(1,5)};rows=[]
for family in ('clinical_architecture','clinical_support'):
 base=ROOT/'assets'/family
 for path in sorted(base.glob('AST-*.manifest.json')):
  m=json.loads(path.read_text());assert m['catalogue_id'] in ids
  source,export=base/m['source'],base/m['export'];assert source.is_file() and export.is_file() and (base/m['generator']).is_file()
  row={'catalogue_id':m['catalogue_id'],'name':m['name'],'family':family,'source':str(source.relative_to(ROOT)),'export':str(export.relative_to(ROOT)),'manifest':str(path.relative_to(ROOT)),'dimensions_blender_xyz_m':m['dimensions_blender_xyz_m'],'evaluated_triangles':m['evaluated_triangles'],'batch':'12','adopted_game_instances':0,'source_sha256':sha(source),'export_sha256':sha(export),'interface_record_id':m['catalogue_id']}
  if m['catalogue_id']=='AST-MED-001':
   derived=base/m['states']['open']['export'];assert derived.is_file() and sha(derived)==m['states']['open']['sha256'];row['state_derivatives']=[{'state':'open','export':str(derived.relative_to(ROOT)),'sha256':sha(derived),'counts_as_new_design':False}]
  rows.append(row)
assert len(rows)==4 and {r['catalogue_id'] for r in rows}==ids;rows.sort(key=lambda r:r['catalogue_id']);assert sum(r['evaluated_triangles'] for r in rows)==12034
manifest={'batch':'12','started_utc':'2026-10-02T20:23:51Z','kind':'district_guided_clinical_support_components','unique_authored_asset_count':4,'assets':rows,'actual_game_adoptions':0,'scope':'Controllable opaque privacy/arrival field, shaped wash/supply bay, neutral modular support platform and separate medical supply trolley. Forward D05 triage/medical purpose, no recovered room or new clinical capacity.','review_completed_utc':a.review_completed_utc,'review':'qa/batch12/independent_final_review.json','coordinate_contract':'standards/COORDINATE_CONTRACT.md','reference_manifest':'batches/batch12/reference_manifest.json','interface_contract':'batches/batch12/interface_contract.json','arrangement':'qa/batch12/assembly/r02/render_evidence.json','independent_rebuild_receipts':'qa/batch12/independent_rebuild_receipts.json','category_coverage':'CATEGORY_COVERAGE.json','quality_baseline_user_message':'Sentinel_1f1516ffa9a08191a5f37800301a001c','limits':['The D05 programme is distributed; Family waiting remains at the aft stop, not relocated beside the forward pair','Historical staff-only flags remain implementation evidence for later reconciliation, not a rule that guests cannot receive staff-assisted care','Blueprint medical quantities and old accommodation arithmetic do not allocate new beds or change current ship capacity','Original room polygons, doors, support, ceiling, service access and body/species suitability remain unresolved','Privacy checks prove only declared component sightlines and visual motion; open edges/top and absent host prevent whole-room confidentiality claims','Collision profiles retain finite observed simplifications, including62.9mm around basin wall corners; no continuous or runtime acceptance follows','Fluids, chemicals, treatment, medical operation and game interaction are unimplemented','Four authored designs remain four; the open screen derivative, integrated pads/cases, inspection arrangements and material tiles add zero']}
(ROOT/'batches/batch12/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';cat=json.loads(p.read_text());old=[r for r in cat['assets'] if r.get('batch')!='12'];assert len(old)==61
cat['assets']=old+rows;cat['unique_authored_asset_count']=65;cat['batch']='01–12';cat['current_batch']='12';cat['version']=12;cat['component_review_completed_utc']=a.review_completed_utc;cat['status']['independent_component_visual_review']='batches01_to07_09_to12_passed_for_components_only_with_batch08_readiness'
for key,value in [('batches','batches/batch12/manifest.json'),('reviews','qa/batch12/independent_final_review.json')]:
 if value not in cat[key]:cat[key].append(value)
for path,scope in [('materials/care/manifest.json','Three original shared care-oriented visual roles'),('assets/clinical_architecture/material_manifest.json','Original opaque privacy and clinical ink roles; unused exploratory roles remain disclosed')]:
 assert (ROOT/path).is_file()
 if not any(x['path']==path for x in cat['material_libraries']):cat['material_libraries'].append({'path':path,'scope':scope})
p.write_text(json.dumps(cat,indent=2)+'\n');print(json.dumps({'new_designs':4,'total_unique':65,'unique_design_export_triangles':12034,'state_derivatives_counted_as_new':False},indent=2))
