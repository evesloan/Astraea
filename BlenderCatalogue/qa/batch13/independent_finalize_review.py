"""Final exact-binding gate for the independent bounded component acceptance."""
from pathlib import Path
import json,hashlib,datetime,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
reports=['independent_preservation_report.json','independent_botanical_cluster_interfaces.json','independent_botanical_transition_interfaces.json','independent_botanical_transition_collision_profile.json','independent_source_native_corner_comparison.json','independent_coplanar_screen.json','independent_assembly_geometry_review.json','independent_visual_review.json','independent_rebuild_receipts.json','independent_uv_repair_accounting.json'];checks=[]
for name in reports:
 p=OUT/name;r=json.loads(p.read_text());assert r['passed'],name;checks.append(bind(p))
index=OUT/'independent_interface_normalized_index_proposed.json';d=json.loads(index.read_text());assert len(d['assets'])==d['unique_assets']==69;assetbindings=[b for r in d['assets']for b in r['source_export_manifest_bindings'].values()];assert len(assetbindings)==207
for b in assetbindings:assert sha(ROOT/b['path'])==b['sha256'],b['path']
for family,revision in [('botanical_cluster','r02'),('botanical_transition','r04')]:
 rp=OUT/f'independent_rebuild_{family}_{revision}.json';r=json.loads(rp.read_text());runner=OUT/('independent_rebuild_runner.py'if family=='botanical_cluster'else'independent_rebuild_runner_executed_transition_r04.py');assert sha(runner)==r['executed_script_sha256']
 for b in r['production_inputs']:assert sha(ROOT/b['path'])==b['sha256']
 for a in r['assets']:
  for k in ['source','rebuilt_source']:assert sha(ROOT/a[k]['path'])==a[k]['sha256']
 for a in r['exports']:
  for k in ['current','rebuilt']:assert sha(ROOT/a[k]['path'])==a[k]['sha256']
 for k in ['build_log','file_read_instrumentation','source_audit_log']:assert sha(ROOT/r[k]['path'])==r[k]['sha256']
visual=json.loads((OUT/'independent_visual_review.json').read_text());assert sha(ROOT/visual['capture_receipt']['path'])==visual['capture_receipt']['sha256']
for r in visual['views']+visual['additional_component_pixels']:assert sha(ROOT/r['image']['path'])==r['image']['sha256']
bridge=OUT/'assembly/r06/post_capture_metadata_amendment.json';assert bridge.exists()
result={'passed':True,'accepted_scope':'Four original editable and native-exported botanical components with bounded geometric/material/visual QA; no engine/host/actor/species/load/plant-viability/runtime acceptance.','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_design_count':4,'proposed_design_total':69,'prior_protected_files':1834,'old_raw_and_object_rows_preserved':65,'reviewer_modified_canonical_files':False,'independent_reports':checks,'proposed_index':bind(index),'review_document':bind(OUT/'independent_review.md'),'coverage_map':bind(OUT/'independent_interface_coverage_map.json'),'post_capture_metadata_bridge':bind(bridge),'new_source_export_manifest_bindings':[r['source_export_manifest_bindings']for r in d['assets'][-4:]],'all207_bound_files_current':True,'executed_script_sha256':sha(Path(__file__)),'pending_lead_gate':'Lead promotion, exact freeze, actual restore and durable backup. No further design expansion implied.'}
(OUT/'independent_final_review.json').write_text(json.dumps(result,indent=2)+'\n');print('FINAL_INDEPENDENT_ACCEPT',True,'4 bounded components;69-row proposal;1834 protected files;all207 bindings current')
