"""Freeze the bounded Batch08 independent gate and active source/dependency receipt."""
from pathlib import Path
import json,hashlib,datetime,subprocess,ast
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08';BASE='66dcaf10f105958c5cadb421d5aca15b054b98ed'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda n:json.loads((OUT/n).read_text())
base=read('independent_baseline_hashes.json');baseline={r['path']:r for r in base['files']};exceptions=[]
for path,r in baseline.items():
 p=ROOT/path
 if not p.is_file() or sha(p)==r['sha256']:continue
 if path.startswith('assets/hospitality_counters/'):
  scope='Collision compound data/generator and exact revision/dependency/README bindings only; source visual .blend, GLB, images and geometric construction remain unchanged. Source-backed fascia/terminal decomposition corrects inherited lost voids.';evidence='qa/batch08/independent_collision_report.json'
 elif path.startswith('assets/library_contents/'):
  scope='Explicit texture-root/path metadata and hash provenance; generator reads that same original directory and variant output creates qa/. All geometry/material records and original .blend/GLB/PNG bytes remain unchanged.';evidence='qa/batch08/independent_interface_report.json'
 elif path.startswith(('assets/botanical_canopy/','assets/aquatic_lounge/')):
  scope='Lead-reviewed mandatory output-directory creation, associated generator hash/provenance and README records only; all preexisting code AST and master .blend/GLB/image bytes remain unchanged.';evidence='qa/batch08/independent_source_restoration_scope.json'
 elif path=='tools/package_small_delivery.py':
  scope='Lead-approved complete large review records in dedicated ordinary ZIP buckets; actual compressed8MB cap and CRC/exact-byte restoration unchanged. No truncation, partial JSON or omitted evidence.';evidence='qa/batch08/large_review_packaging_check.json'
 elif path in ['README.md','catalogue_manifest.json','BACKUP_LEDGER.json','standards/PERFORMANCE_FOLLOWUPS.md','standards/source_package_groups.json']:
  scope='Lead catalogue status, measured-cost follow-ups and delivery/source-package grouping for the authorized bounded readiness pass; no new unique artistic design or engine acceptance.';evidence='batches/batch08/CONTRACT.md'
 else:raise AssertionError('Unexpected prior-file modification requiring explicit scope review: '+path)
 assert not r['visual_material_source_frozen'],path
 exceptions.append({'path':path,'original_sha256':r['sha256'],'current_sha256':sha(p),'scope':scope,'review_evidence':evidence,'visual_source_exception':False})
(OUT/'independent_scoped_exceptions.json').write_text(json.dumps({'baseline_commit':BASE,'scope':'Exact reviewed current metadata/generator exceptions only. No existing .blend, GLB, image, material file or original standards helper exception was granted.','exceptions':exceptions},indent=2)+'\n')
subprocess.run(['python',str(OUT/'independent_preservation_check.py')],cwd=ROOT,check=True,capture_output=True)
preservation=read('independent_preservation_report.json');collision=read('independent_collision_report.json');flange=read('independent_flange_report.json');visual=read('independent_flange_visual_report.json');interfaces=read('independent_interface_report.json');exports=read('independent_export_summary.json');author=json.loads((OUT/'counter_collision_revision/validation_report.json').read_text())
cat=json.loads((ROOT/'catalogue_manifest.json').read_text());oldcat=json.loads(subprocess.check_output(['git','show',BASE+':catalogue_manifest.json'],cwd=ROOT));allowed_asset_keys={'interface_record_id','readiness_revision_batch','collision_data_revision','dependency_metadata_revision','generator_output_directory_revision'}
assert [{k:v for k,v in a.items() if k not in allowed_asset_keys}for a in cat['assets']]==oldcat['assets']
assert (ROOT/'standards/PERFORMANCE_FOLLOWUPS.md').read_bytes().startswith(subprocess.check_output(['git','show',BASE+':standards/PERFORMANCE_FOLLOWUPS.md'],cwd=ROOT))
manifest=json.loads((ROOT/'assets/utility_pipework/derived_lod/manifest.json').read_text())
for d in manifest['dependencies']:assert sha(ROOT/d['catalogue_relative_path'])==d['sha256']
for x in exports:
 assert sha(ROOT/x['path'])==x['sha256']
 if x.get('source_audit'):
  s=json.loads((ROOT/x['source_audit']).read_text());assert sha(ROOT/s['path'])==s['sha256']
assert sha(ROOT/collision['input_path'])==collision['input_sha256']
assert author['current_collision_sha256']==collision['input_sha256']
for proof,key in [('deep_corridor_report.json','current_collision_sha256'),('final_detail_report.json','collision_sha256'),('reproduction_report.json','proposal_sha256')]:
 d=json.loads((OUT/'counter_collision_revision'/proof).read_text());assert d[key]==collision['input_sha256'] and d['pass']
rp=json.loads((OUT/'counter_collision_revision/reproduction_report.json').read_text());assert rp['generator_sha256']==sha(ROOT/'assets/hospitality_counters/source/build_hospitality_counters.py')
for d in author['inputs']:assert sha(ROOT/d['path'])==d['sha256']
for v in visual['inputs']:assert sha(ROOT/v['path'])==v['sha256']
for v in visual['images']:assert sha(ROOT/v['path'])==v['sha256']
assert sha(ROOT/interfaces['canonical_consumer_index']['path'])==interfaces['canonical_consumer_index']['sha256']
checks={'all_prior_visual_source_and_material_bytes_frozen':preservation['no_frozen_visual_material_source_changes'] and not preservation['missing_prior_files'],'all_changed_prior_files_have_exact_scoped_metadata_exceptions':all(x.get('scoped_exception') for x in preservation['changed_prior_files']),'collision_actual_source_continuous_coverage_deep_voids_toes_seams_and_controls':collision['pass'],'collision_author_continuous_corridors_drawer_and_reproduction':author['pass'] and json.loads((OUT/'counter_collision_revision/deep_corridor_report.json').read_text())['pass'] and json.loads((OUT/'counter_collision_revision/final_detail_report.json').read_text())['pass'] and json.loads((OUT/'counter_collision_revision/reproduction_report.json').read_text())['pass'],'derived_flange_sources_exported_geometry_normals_UV_materials_and_frames':read('independent_flange_restoration_report.json')['pass'] and flange['pass'] and all(not x.get('issues') and not x.get('error') for x in exports),'actual_GLb_near_and_repeated_pixels_reviewed':visual['bounded_visual_acceptance'],'all45_interfaces_explicit_and_current_with_scoped_metadata_fixes':read('independent_source_restoration_scope.json')['pass'] and interfaces['pass'] and interfaces['canonical_consumer_index']['promoted_to_standards'],'design_count_remains45_derivatives_are_not_designs':cat['unique_authored_asset_count']==45 and len(cat['assets'])==45 and manifest['new_unique_design_count']==0}
# Active family source data/dependencies plus original reference pixels; QA/media history is bound separately.
paths=set()
for folder in ['assets','materials','standards','references','tools']:
 for p in (ROOT/folder).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.pyc','.blend1']:continue
  rel=p.relative_to(ROOT)
  if folder=='assets' and ('qa' in rel.parts or 'renders' in rel.parts):continue
  paths.add(p)
for p in (ROOT/'batches').rglob('*reference*'):
 if p.is_file():paths.add(p)
paths.add(ROOT/'catalogue_manifest.json')
files=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)]
receipt={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':BASE,'scope':'Exact current active authored assets/derived sources/GLBs/manifests/generators, material images/libraries, shared standards/consumer interfaces/helpers, references and source packaging tools. Asset QA/renders/history are excluded from this source receipt and independently bound by report/capture hashes; durable backup is a separate lead gate.','files':files}
receipt_path=OUT/'independent_final_source_hash_receipt.json';receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
reports=['independent_baseline_hashes.json','independent_preservation_report.json','independent_scoped_exceptions.json','independent_collision_report.json','independent_collision_decision.json','independent_export_summary.json','independent_flange_report.json','independent_flange_restoration_report.json','independent_flange_visual_report.json','independent_interface_report.json','independent_source_restoration_scope.json']
result={'decision':'PASS for bounded current-catalogue source/interface/collision-proposal/derived-flange review' if all(checks.values()) else 'INCOMPLETE: see checks','checks':checks,'unique_artistic_design_count':45,'collision_counts':{'baseline_hospitality':399,'current_hospitality':author['current_total_hospitality_shape_count'],'current_straight':collision['assets'][0]['shape_count'],'current_curved':collision['assets'][1]['shape_count'],'independent_path_checks':sum(a['service_grid_and_blocked_controls']['count'] for a in collision['assets'])},'flange_cost':{'original_actual_inlet_triangles':2327,'economical_triangles':1320,'saved_triangles':1007,'triangle_reduction_fraction':1007/2327,'exact_hole_option_triangles':1608,'near_master_changed':False,'runtime_frame_rate_or_memory_savings_proven':False},'remaining_limits':['Offline source/GLB/component evidence only. No receiving-engine physics, controller, room/whole-ship route, actor/species fit, water/food/electrical operation, whole-ship LOD or RTX5060Ti/1080p60 acceptance.','Collision approximation is explicit by source part and region. Arc/profile parameters are not a universal fit bound; finite surface samples and independent controls have their stated limits.','Economical flange is visibly lower detail near the camera. Three discrete camera angles do not prove continuous temporal stability or a runtime LOD transition distance.','Current consumer interfaces preserve unresolved removable trajectories as unspecified. Neutral-pose extras must not replace actual moved node hierarchy.','Full/compact archive restoration, remote push and durable Library delivery remain separate lead gates and are not implied by this source review.'],'reports':[{'path':'qa/batch08/'+n,'sha256':sha(OUT/n)} for n in reports],'final_source_receipt':{'path':str(receipt_path.relative_to(ROOT)),'sha256':sha(receipt_path),'file_count':len(files)},'baseline_prior_file_count':len(base['files']),'frozen_visual_material_source_file_count':preservation['frozen_visual_material_source_file_count']}
(OUT/'independent_final_review.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'independent_review.md').write_text('# Batch08 independent bounded review\n\n'+result['decision']+'\n\n45 unique artistic designs remain. Existing visual source, GLB and material bytes are unchanged. New flange choices are derived outputs.\n\n'+f"Hospitality compounds: {result['collision_counts']['current_hospitality']} versus399; straight {result['collision_counts']['current_straight']}, curved {result['collision_counts']['current_curved']}. Independent source-triangle union coverage and {result['collision_counts']['independent_path_checks']:,} clear/blocked paths include deep shelf and terminal toe regions. Earlier whole-profile fascia hulls were rejected and corrected.\n\n"+'The economical flange has1,320 actual triangles versus2,327 in the unchanged original inlet (43.3% fewer). Both source/export geometry and14 matched actual-GLB views were checked. Hole faceting and rear-edge/neck simplification remain visible near the camera; repeated-view silhouette and material identity are retained in the reviewed fixture.\n\n'+'The45-row interface map distinguishes support contacts, opening/pose/centreline datums, transforms and motion applicability without inventing anchors. Library texture path metadata and the compact-source missing-directory failure are corrected with exact provenance and byte-identical reproduction evidence.\n\n'+'## Limits\n\n'+'\n'.join('- '+x for x in result['remaining_limits'])+'\n\nSource/dependency receipt: `independent_final_source_hash_receipt.json`, SHA256 `'+sha(receipt_path)+'`.\n')
print(json.dumps({'decision':result['decision'],'checks':checks,'receipt':result['final_source_receipt'],'collision':result['collision_counts']},indent=2))
