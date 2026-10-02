"""Freeze exact independently reviewed inputs after all final surface/visual gates pass."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10';BASE='ea303a53c42de3d8b9fb3f05ae513c5d83cbab59'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def read(name):return json.loads((OUT/name).read_text())
required=['independent_salon_threshold_interfaces.json','independent_salon_edges_interfaces.json','independent_section_seams.json','independent_arrangement_interfaces.json','independent_profile_collision.json','independent_coplanar_screen.json','independent_context_fit.json','independent_book_context_geometry.json','independent_threshold_visual_review.json','independent_edges_visual_review.json','independent_assembly_visual_review.json','independent_rebuild_receipts.json','independent_preservation_report.json']
for name in required:assert read(name)['passed'],name
families=['salon_threshold','salon_edges'];assets=[];source_inputs={};evidence=set(required)
def keep(path):
 path=Path(path).resolve();source_inputs[str(path.relative_to(ROOT))]=bind(path)
for f in families:
 base=ROOT/'assets'/f;ir=read('independent_'+f+'_interfaces.json');aud={a['id']:a for a in ir['assets']};keep(base/'dependency_manifest.json');keep(base/'collision_proposals.json')
 if (base/'marker_api.json').exists():keep(base/'marker_api.json')
 if (base/'README.md').exists():keep(base/'README.md')
 for mp in sorted(base.glob('AST-SAL-*.manifest.json')):
  m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=base/m['source'];gp=base/m['export'];s=read('independent_source_'+ident+'.json');e=read('independent_export_'+ident+'.json');a=aud[ident]
  assert sha(sp)==s['sha256']==m['source_sha256'] and sha(gp)==e['sha256']==m['glb_sha256'] and not e['issues']
  assert sha(base/m['generator'])==m['generator_sha256']
  for b in a['bindings'].values():assert sha(ROOT/b['path'])==b['sha256'],b['path']
  for p in [sp,gp,mp,base/m['generator']]:keep(p)
  evidence|={'independent_source_'+ident+'.json','independent_export_'+ident+'.json','independent_source_geometry_'+ident+'.npz'}
  assets.append({'catalogue_id':ident,'source':bind(sp),'export':bind(gp),'manifest':bind(mp),'triangles':e['triangles'],'editable_semantic_parts':m['editable_semantic_parts'],'material_roles':m['material_roles'],'marker_checks':len(a['markers']),'physical_join_witnesses':len(a['joins']),'finite_clear_and_blocked_paths':len(a['void_and_blocked_tests']),'collision_shapes':a['collision_shape_count'],'wrong_axis_negative_controls':a['wrong_axis_negative_control_count'],'pass':True})
for r in read('independent_rebuild_receipts.json')['families']:
 for b in r['production_inputs']:assert sha(ROOT/b['path'])==b['sha256'];keep(ROOT/b['path'])
for p in ['batches/batch10/CONTRACT.md','batches/batch10/interface_contract.json','references/salon/D09_CONNECTED_SALON.md','references/salon/D09_COMPOSITION_CONTRACT.md','standards/COORDINATE_CONTRACT.md','standards/ASSET_CONTRACT.md','standards/COMPONENT_QA_ENVIRONMENT.md','standards/qa_frame.py','qa/inspect_glb_independent.py','qa/batch07/independent_geometry.py','qa/batch08/independent_collision_geometry.py','qa/batch10/assembly/plan.json','qa/batch10/assembly/build_inspection.py']:keep(ROOT/p)
for p in OUT.glob('independent_*.py'):keep(p)
context=json.loads((OUT/'assembly/render_evidence_v2.json').read_text())
for row in context['context']:keep(ROOT/row['path'])
for name in ['assembly/camera_margin_revision/build_inspection.py','assembly/first_camera_evidence/build_inspection.py','assembly/first_camera_evidence/interpretation.json','assembly/build_book_context.py','assembly/book_context_receipt.json','assembly/quiet_books_left.blend','assembly/quiet_books_right.blend']:keep(OUT/name)
for p in (ROOT/'references/salon').iterdir():
 if p.suffix in ['.png','.jpg']:keep(p)
# Visual reports assert their exact captured source/export/camera/image bindings internally.
for fn in ['independent_threshold_visual_review.json','independent_edges_visual_review.json','independent_assembly_visual_review.json']:
 v=read(fn)
 for im in v['views']:
  assert sha(ROOT/im['image']['path'])==im['image']['sha256']
  if 'source'in im:assert sha(ROOT/im['source']['path'])==im['source']['sha256']
  if 'export'in im:assert sha(ROOT/im['export']['path'])==im['export']['sha256']
  for b in im.get('source_export_bindings',[]):assert sha(ROOT/b['path'])==b['sha256']
  assert hashlib.sha256(json.dumps(im['camera'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==im['camera_canonical_sha256']
assert len(assets)==6
receipt={'passed':True,'scope':'Exact final independently reviewed production, dependency and design-input bytes. Camera/image receipts are separate bound evidence.','files':[source_inputs[k]for k in sorted(source_inputs)],'source_export_asset_count':6}
(OUT/'independent_final_source_hash_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
for x in ['independent_interface_normalized_index_proposed.json','independent_interface_coverage_map.json','independent_interface_proposed_corrections.json','independent_coplanar_screen.json']:evidence.add(x)
result={'passed':True,'scope':'Six-design component geometry/material/UV/contact/collision-proposal/source-only restoration and normal-height proposed-arrangement visual review','baseline_commit':BASE,'new_unique_artistic_designs':6,'resulting_catalogue_unique_designs':57,'actual_new_export_triangles':sum(a['triangles']for a in assets),'assets':assets,'source_receipt':bind(OUT/'independent_final_source_hash_receipt.json'),'interface_proposal':bind(OUT/'independent_interface_normalized_index_proposed.json'),'evidence':[bind(OUT/p)for p in sorted(evidence)],'art_readout':'Joined rising quiet return, shaped seat/book edges, low open planted seat, supported portal terminal and distinct service/storage faces are legible in ordinary640×360 component and proposed-arrangement views. Material roles remain ivory primary, recessed teal, tactile timber and restrained metal joints.','spatial_limits':['New proposed adjustable component arrangement only; original ship and final guest polygon remain missing.','Historical rectangular allocation, X48 architectural portal, X52/X98 moving-door locations and8.25m budget are archived claims. Later quiet authoring maximum7.2×5.4×3.8m governs this component; it does not recover a room.','Actual public/service clear width/height, leaf stroke, cassette and head reservation remain unknown. Editable4.4×3.1m opening contains no leaves.','The quiet side/book cheek screens the proposed lateral seated look toward arrival. Forward and opposing bay-mouth views establish the useful relationship; no seated-atrium-view claim.','Service return is a separate rear candidate with intervening host geometry/route unmodeled. No complete room, actor/cart route, universal species fit, guard compliance or structural load rating.','Collision screens use finite clear/blocked controls and conservative compounds. Profile sampling records up to11.77mm crown clearance reduction,4.03mm cove intrusion and47.03mm intentional finish-channel filling. Shape counts and approximation limits are explicit; no exact sweep or runtime budget acceptance.','Source-only runs executed by authors under lead coordination and independently scope/hash checked here; no duplicate build. Six regenerated GLBs match byte-for-byte.','Complete archive/restore, remote push and durable user delivery remain separate lead gates.']}
(OUT/'independent_final_review.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'independent_review.md').write_text('# Independent Batch10 component review\n\nPassed the bounded six-design source/export, geometry, material, interface, finite collision, source-only restoration and final normal-height proposed-arrangement visual gates. This is new catalogue work, not recovered host geometry or a completed room.\n\n'+result['art_readout']+'\n\nThe exact reviewed source receipt and six-row proposed canonical extension are beside this report. The earlier51 canonical row bytes and protected source/common assets are unchanged. Small physical-bearing/void and exposed coplanar-material defects were corrected before final acceptance; the correction map and initial evidence remain available.\n\nFinal export total: '+str(result['actual_new_export_triangles'])+' triangles across six unique designs. All contacts, receiver/opening/pose datums and fixed/no-motion limits are kept distinct. The catalogue collision compounds remain proposals with explicit counts, not a runtime budget.\n\n'+'\n\n'.join(result['spatial_limits'])+'\n')
print(json.dumps({'passed':True,'assets':6,'triangles':result['actual_new_export_triangles'],'reviewed_source_input_files':len(source_inputs)},indent=2))
