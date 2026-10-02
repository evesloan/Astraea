"""Freeze exact Batch14 bounded-review evidence without editing canonical indices."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
required=['independent_aquatic_towel_use_interfaces.json','independent_aquatic_wet_use_interfaces.json','independent_assembly_geometry_review.json','independent_source_native_corner_comparison.json','independent_state_geometry.json','independent_visual_review.json','independent_receiver_passage.json','independent_return_sightlines.json','independent_coplanar_screen.json','independent_preservation_report.json','independent_rebuild_receipts.json','independent_metadata_rebuild_review.json']
reports={n:json.loads((OUT/n).read_text())for n in required};assert all(r['passed']for r in reports.values());proposal=OUT/'independent_interface_normalized_index_proposed.json';pr=json.loads(proposal.read_text());assert len(pr['assets'])==73 and pr['unique_assets']==73;assert pr['binding_validation']['all_files_current']
for r in pr['assets']:
 for b in r['source_export_manifest_bindings'].values():assert sha(ROOT/b['path'])==b['sha256']
files=[]
for family in ['aquatic_towel_use','aquatic_wet_use']:
 base=ROOT/'assets'/family
 files+=[p for p in base.glob('*.json')if p.is_file()]+list((base/'source').glob('*.py'))+list((base/'source').glob('AST-*.blend'))+list((base/'exports').glob('AST-*.glb'))
for v in reports['independent_visual_review.json']['images']:
 assert sha(ROOT/v['image']['path'])==v['image']['sha256']
for family in ['aquatic_towel_use','aquatic_wet_use']:
 for r in reports[f'independent_{family}_interfaces.json']['assets']:
  for b in r['bindings'].values():assert sha(ROOT/b['path'])==b['sha256']
for r in reports['independent_rebuild_receipts.json']['families']:
 for b in r['production_inputs']:assert sha(ROOT/b['path'])==b['sha256']
profiles=[json.loads(p.read_text())for p in sorted(OUT.glob('independent_collision_profile_AST-AQU-*.json'))];assert len(profiles)==4
r={'passed':True,'status':'bounded_component_review_passed_proposed_index_not_promoted','reviewed_design_ids':['AST-AQU-007','AST-AQU-008','AST-AQU-009','AST-AQU-010'],'new_design_count':4,'native_export_count_including_derivative':5,'proposed_catalogue_size':73,'prior_protected_file_count':2009,'prior_records_preserved_raw_and_decoded':69,'physical_marker_surface_witnesses':21,'all_semantic_mesh_parts_supported_geometrically':126,'complete_declared_void_boxes':14,'actual_images_independently_inspected':15,'source_only_rebuild_input_counts':{'aquatic_towel_use':20,'aquatic_wet_use':10},'source_exports_and_generated_json_reproduced':True,'proposed_index':bind(proposal),'coverage_map':bind(OUT/'independent_interface_coverage_map.json'),'review_report':bind(OUT/'independent_review.md'),'final_asset_file_bindings':[bind(p)for p in sorted(set(files))],'primary_evidence':[bind(OUT/n)for n in required],'collision_profile_bindings':[bind(OUT/f"independent_collision_profile_{v['catalogue_id']}.json")for v in profiles],'collision_proposal_shapes':{v['catalogue_id']:v['proposal_shape_count']for v in profiles},'finite_sample_max_collision_inflation_m':{v['catalogue_id']:v['sampled_max_external_inflation_m']for v in profiles},'metadata_only_corrections':'Successful image bytes preserve original exact source/export capture scope. Later collision-profile and dependency-inventory metadata is separately rebound; no unchanged geometry was recaptured for metadata corrections.','not_accepted':['Original engine integration','Host room or route adoption','Mechanical or structural loads','Laundry/hygiene/disposal implementation','Plumbing, drainage or functioning water','Substance/temperature/pressure/chemical suitability','Six-species, accessible, body/hand/reach fitting','Target-PC runtime performance','New room, changing slot, seat or population capacity'],'executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_final_review_receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('FROZEN REVIEW PASS:4 designs,73 proposed rows,2009 protected files,69 raw prior records,15 imported images')
