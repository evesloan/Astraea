"""One-time immutable acceptance binding all current evidence; no canonical promotion."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch18';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
PROMOTABLE={'catalogue_manifest.json','standards/catalogue_interfaces.json','CATEGORY_COVERAGE.json'}
finalpath=OUT/'independent_final_review.json';assert not finalpath.exists(),'Preserve immutable receipt; use a new explicit revision for any later change'
required=['independent_programme_review.json','independent_reference_pixels_review.json','independent_retail_material_rebuild.json','independent_display_geometry_review.json','work_review_summary.json','independent_finish_resolution.json','independent_source_native_corner_comparison.json','independent_arrangement_review.json','independent_visual_review.json','independent_preservation_report.json','rebuild_review/FINAL_REBUILD_RECEIPT.json','rebuild_review/STAGE2_ROLE_REVIEW.json']
accepted={};pending=[]
def add(p):
 p=Path(p).resolve();assert p.is_relative_to(ROOT)and p.is_file(),p
 if str(p.relative_to(ROOT))in PROMOTABLE:return
 if str(p)not in accepted:accepted[str(p)]=bind(p);pending.append(p)
for name in required:
 p=OUT/name;data=json.loads(p.read_text());assert data['passed'],name;add(p)
visual=json.loads((OUT/'independent_visual_review.json').read_text());assert visual['image_count']>=16,'Final actual arrangement plan/section still required'
for name in ['independent_interface_normalized_index_proposed.json','independent_interface_coverage_map.json','independent_baseline_catalogue_interfaces.json','independent_baseline_catalogue_manifest.json','independent_baseline_CATEGORY_COVERAGE.json','prior_protected_source_hashes.json','independent_review.md','arrangement_freeze_receipt.json']:
 add(OUT/name)
for pattern in ['independent_*.py','work_review_*.py']:
 for p in OUT.glob(pattern):add(p)
for pattern in ['independent_source_AST-*.json','independent_export_AST-*.json','independent_corner_comparison_AST-*.json','independent_source_corners_AST-*.json','independent_support_finish_AST-*.json','independent_display_geometry_AST-*.json','work_review_AST-*.json']:
 for p in OUT.glob(pattern):
  if p.stem in {'independent_export_AST-RTL-003_drawer_open','independent_export_AST-RTL-004_open'}:continue
  add(p)
for family,revision in [('retail_display','r02'),('retail_work','r05')]:
 add(OUT/f'rebuild_review/rebuild_{family}_{revision}.json')
 for p in (ROOT/'assets'/family).glob('*.json'):add(p)
spatial=OUT/'spatial_audit/final_frozen_actual_export_review.json';spatial_data=json.loads(spatial.read_text());assert spatial_data['status'].startswith('PASS')and spatial_data['final_freeze_confirmed']and spatial_data['inputs_unchanged_during_review'];add(spatial);add(OUT/'spatial_audit/manifest.json')
for p in (ROOT/'references/retail').glob('*'):
 if p.is_file():add(p)
for p in [ROOT/'batches/batch18/CONTRACT.md',ROOT/'batches/batch18/reference_manifest.json',ROOT/'batches/batch18/production_checkpoint.json',ROOT/'standards/COORDINATE_CONTRACT.md',ROOT/'standards/COMPONENT_QA_ENVIRONMENT.md',ROOT/'standards/ARCHITECTURAL_PROFILE_QA.md',OUT/'rebuild_review/finalize_rebuild_review.py',OUT/'rebuild_review/review_stage2_roles.py']:add(p)
def discover(node,base=ROOT):
 if isinstance(node,list):
  for x in node:discover(x,base)
 elif isinstance(node,dict):
  if isinstance(node.get('path'),str)and isinstance(node.get('sha256'),str):
   p=base/node['path']
   if not p.is_file():p=ROOT/node['path']
   # Absolute or unavailable historical programme provenance is not an on-disk package dependency.
   if node['path']not in PROMOTABLE and p.is_file()and p.resolve().is_relative_to(ROOT):assert sha(p)==node['sha256'],node['path'];add(p)
  for value in node.values():discover(value,base)
while pending:
 p=pending.pop()
 if p.name.startswith('independent_baseline_'):continue
 if p.name=='independent_interface_normalized_index_proposed.json':
  index=json.loads(p.read_text())
  for row in index['assets']:discover(row['source_export_manifest_bindings'])
  for row in index['assets'][-4:]:discover(row)
  continue
 if p.suffix=='.json' and (str(p.relative_to(ROOT)).startswith(('qa/batch18/','assets/retail_display/','assets/retail_work/','references/retail/','batches/batch18/'))):
  try:node=json.loads(p.read_text())
  except Exception:continue
  base=next((ROOT/'assets'/family for family in ['retail_display','retail_work']if p.is_relative_to(ROOT/'assets'/family)),ROOT)
  try:discover(node,base)
  except Exception:
   print('FAILED_BINDING_ORIGIN',p)
   raise
  # Source geometry/corner arrays are explicitly named by these receipts.
  for key in ['geometry_cache','corner_cache']:
   if isinstance(node,dict)and key in node:add(ROOT/node[key])
for x in visual['images']:assert sha(ROOT/x['path'])==x['sha256']and x['pixels_independently_inspected']and x['visual_pass'];add(ROOT/x['path'])
# Every old row is preserved as raw JSON text by the proposal builder.
proposal=json.loads((OUT/'independent_interface_normalized_index_proposed.json').read_text());assert len(proposal['assets'])==89 and proposal['binding_validation']['all_files_current']
assert all(sha(ROOT/x['path'])==x['sha256']for x in accepted.values())
receipt={'passed':True,'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':'batch18-independent-final-01','baseline_commit':'95dc75eeb5ea36af8e74ddf372e191e9dd39432e','accepted_designs':['AST-RTL-001','AST-RTL-002','AST-RTL-003','AST-RTL-004'],'new_design_count':4,'proposed_total_designs':89,'protected_prior_record_count':85,'protected_file_count':3381,'actual_original_game_adoptions':0,'independent_report_bindings':[bind(OUT/name)for name in required],'proposed_interface_index':bind(OUT/'independent_interface_normalized_index_proposed.json'),'review_summary':bind(OUT/'independent_review.md'),'inspected_image_count':visual['image_count'],'accepted_file_count':len(accepted),'accepted_file_bindings':sorted(accepted.values(),key=lambda x:x['path']),'scope':'Independent source/export/profile/support/contact/useful-space/material/UV/normal/manual-motion/collision/reconstruction and actual-pixel acceptance of four authored components plus a bounded R070 source study. Canonical promotion remains the lead action.','limits':['No recovered actual R070 interior/door/pocket/head/local support/services/slots or host installation; historical outer allocation is the boundary of the spatial conclusion','No species/body/reach/cart, load/stability/material safety, lighting/physics, inventory, payments, ownership, capacity or target-PC/engine acceptance','Container lifted carrier is explicitly externally held; the parked lid has actual support. No retained mechanism is inferred','Source-only original-input closure and stage2 generated selection are separated. Python/native-image tracing is not OS-syscall-complete','Displayed author capture scripts are exact frozen launch snapshots. Lead arrangement receipt binds actual script/plan startup and post-capture hashes plus final input freeze; no later reconstructed script is called launch-verified','Previous failed/stale/preflight/UV-comparison diagnostics remain preserved and are outside current acceptance unless explicitly bound as provenance'],'executed_script_sha256':sha(Path(__file__))};finalpath.write_text(json.dumps(receipt,indent=2)+'\n');print('IMMUTABLE_FINAL',receipt['passed'],'files',len(accepted),'images',visual['image_count'],'sha256',sha(finalpath))
