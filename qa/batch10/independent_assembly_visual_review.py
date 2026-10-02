"""Bind manually inspected ordinary-height final arrangement views; no rendering."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10';BASE=OUT/'assembly'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
meta=json.loads((BASE/'render_evidence_v2.json').read_text());initial=json.loads((OUT/'independent_initial_assembly_visual_review.json').read_text());assert meta['inputs_unchanged_during_execution'] and meta['execution_complete'] and meta['all_final_views_present'];assert sha(BASE/'plan.json')==meta['plan_sha256'];assert sha(BASE/'build_inspection.py')==meta['script_sha256']
inputs=[]
for a in meta['items']:
 for key,h in [('source_path','source_sha256'),('path','glb_sha256'),('manifest_path','manifest_sha256')]:assert sha(ROOT/a[key])==a[h];inputs.append(bind(ROOT/a[key]))
for c in meta['context']:assert sha(ROOT/c['path'])==c['sha256'];inputs.append(bind(ROOT/c['path']))
assert all(x['shifted_100mm_row_rejected']for x in meta['context_fit'])
executed_scripts={sha(p):bind(p)for p in [BASE/'build_inspection.py',BASE/'first_camera_evidence/build_inspection.py',BASE/'camera_margin_revision/build_inspection.py']}
views=[];new_standing=0;new_seated=0
for name,row in meta['views'].items():
 p=BASE/(name+'.png');assert sha(p)==row['raw_image_sha256'];assert row['resolution']==[640,360];assert row['executed_script_sha256']in executed_scripts
 camera={k:row[k]for k in ['position','target','lens','resolution','camera_matrix_world']};source_scope=row['source_scope']
 for a in meta['items']:assert a['glb_sha256']==source_scope[a['catalogue_id']]
 old=initial['render_evidence']['views'].get(name);retained=bool(old and old['raw_image_sha256']==row['raw_image_sha256']);old_occluded=name=='quiet_seated_return'and row['target']==[-3,-.6,1.35]
 if not retained and row['position'][2]>=1.5:new_standing+=1
 if not retained and row['position'][2]<1.5:new_seated+=1
 views.append({'name':name,'image':bind(p),'camera':camera,'camera_canonical_sha256':hashlib.sha256(json.dumps(camera,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'source_export_bindings':inputs,'captured_renderer_script_sha256':row['executed_script_sha256'],'exact_executed_renderer_script':executed_scripts[row['executed_script_sha256']],'retained_unchanged_capture':retained,'manually_pixels_inspected':True,'acceptance_role':'honest occlusion observation only'if old_occluded else'ordinary-height proposed component arrangement','meaning':row['meaning']})
assert new_standing>=1 and new_seated>=1,'Additional standing and seated use views must be inspected and present'
res={'passed':True,'scope':'Independent final640×360 normal-height proposed component arrangement visual review. New source placements, not recovered host geometry or runtime performance.','render_evidence':bind(BASE/'render_evidence_v2.json'),'final_renderer_script':bind(BASE/'build_inspection.py'),'original_retained_frame_renderer_script':bind(BASE/'first_camera_evidence/build_inspection.py'),'superseded_view_interpretation':bind(BASE/'first_camera_evidence/interpretation.json'),'plan':bind(BASE/'plan.json'),'views':views,'readout':[
 'The actual portal/terminal join makes the low supported edge a purposeful terminal. It remains outside the proposed strip and is not a completed guard.',
 'The additional standing and opposing seated views make the rising quiet return, sheltered seating/storage and low open planted edge legible as related uses, with breathing room through the proposed strip. The initial broad axial view mainly shows the section in profile.',
 'The mouth-facing seated view shows the actual quiet edge relationship to the planted court. The archived earlier side-looking arrival view is an occlusion observation: the tall quiet book cheek blocks that sightline at this proposed eye position.',
 'The separate service-end view shows actual fixed shelves, turned work surface and rear approach. The distant unmodeled host segment is not accepted as a completed connecting room.',
 'Unscaled existing-book subsets and existing plants are disclosed QA context. Their support/clearance is independently checked; they add zero designs.'
 ],'limits':['Ordinary height is a camera position, not a solved actor rig, species fit or live player traversal.','Inspection ground and lights are QA aids; actual terrace substrate, real public/service moving doors, cassettes/head space and final guest polygon remain unavailable.','Neutral imported-GLB Blender images establish this bounded visual gate, not game renderer acceptance, structural loading or target-PC performance.','No whole-room or whole-ship completion follows from the six components and proposed arrangement.']}
(OUT/'independent_assembly_visual_review.json').write_text(json.dumps(res,indent=2)+'\n');print('Bound',len(views),'final normal-height arrangement/occlusion views')
