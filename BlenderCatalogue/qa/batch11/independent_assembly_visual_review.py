"""Final actual r03 pixel review and frozen render/spatial evidence bindings."""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch11';Q=OUT/'assembly/r03'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
ep=Q/'render_evidence.json';e=json.loads(ep.read_text());fp=Q/'source_freeze.json';f=json.loads(fp.read_text());assert e['execution_complete']and e['inputs_unchanged_during_execution'];assert sha(OUT/'assembly/build_inspection.py')==e['executed_script_sha256'];assert sha(OUT/'assembly/plan.json')==e['plan_sha256']
for x in f['files']:assert sha(ROOT/x['path'])==x['sha256']
for a in e['items']:
 for key,h in a['hashes'].items():assert sha(ROOT/a[key])==h
for x in e['context']:assert sha(ROOT/x['path'])==x['sha256']and x['new_design']is False
assess={
 'guest_arrival_standing':'Pass. The1.65m standing composition clearly separates the warm directory/cove return from the lower waiting/luggage edge, leaving a broad visibly empty central core-facing approach. No inferred lift door, central map, threshold or invented wall closes the gap. Original artwork remains solid at640px.',
 'guest_waiting_directory':'Pass within disclosed oblique cropped scope. The author-proposed1.19m waiting eye sees the inward-canted directory landmark, supported fixture and rolled local cove from the seat side. Broad emblem remains identifiable; fine text is not a readable seated-route system at this angle. Crop is not a full wall or room frame. No actor/species-fit claim.',
 'staff_side_arrival':'Pass. A1.65m west-side approach sees the practical control/service return and fixed work/retrieval edge as a coherent pair with a visible separation. SERVICE and broad symbols remain identifiable at640px. The empty approach foreground and open retrieval bay are visible; this does not establish exclusive back-of-house routing.',
 'staff_inspection_use':'Pass as explicitly cropped ordinary-height work-surface view. Broad fixed top, formed rear stop and supported nose are readable without clutter or an invented moving cart. Full lower bay is outside this crop and is established by the separate component views, not inferred here.'}
views=[]
for key,v in e['views'].items():
 p=Q/(key+'.png');assert sha(p)==v['image_sha256'];assert list(Image.open(p).size)==v['resolution'];assert v['executed_script_sha256']==e['executed_script_sha256'];assert v['resolution']==[640,360]
 for ident,h in v['source_scope'].items():a=next(a for a in e['items']if a['catalogue_id']==ident);assert sha(ROOT/a['path'])==h
 views.append({'image':bind(p),'camera_and_scope':v,'actual_pixels_inspected':True,'assessment':assess[key],'pass':True})
sp=OUT/'spatial_review/batch11_frozen_export_screen.json';s=json.loads(sp.read_text());assert s['status'].startswith('PASS')and s['freeze_sha256']==sha(fp)
for p,h in s['input_sha256'].items():assert sha(ROOT/p)==h
assert all(a['inside_candidate_envelope']and not a['empty_plan_reservation_intersections']for a in s['items'])
r={'passed':True,'scope':'Actual imported r03 normal-height arrangement image review; independently sourced reservation screen is read and hash-checked rather than duplicated','executed_script_sha256':sha(Path(__file__)),'render_receipt':bind(ep),'executed_render_script':bind(OUT/'assembly/build_inspection.py'),'render_helper':bind(ROOT/'standards/qa_frame.py'),'plan':bind(OUT/'assembly/plan.json'),'source_freeze':bind(fp),'all_frozen_inputs_current':True,'views':views,'spatial_receipt':bind(sp),'spatial_reproducer_current':bind(OUT/'spatial_review/screen_exported_landing.py'),'new_designs':4,'reused_fixture_designs_counted':0,'new_export_triangles':sum(a['triangles']for a in e['items']),'all_context_triangles':e['source_geometry_triangles'],'limits':['R3 boxes are plan reservations, not safe room envelopes. Original host is absent.','Door/shaft/leaf/pocket/head/ceiling/floor/support dimensions are unknown.','Guest oblique waiting crop establishes broad landmark visibility, not readable fine text, actor eyes or a route system.','No photometry, working lift, installed room, door mechanism, structural support, actor/cart or target-engine acceptance.']};(OUT/'independent_assembly_visual_review.json').write_text(json.dumps(r,indent=2)+'\n');print('All4 r03 images, frozen sources/scripts/placement and independent spatial receipt verified')
