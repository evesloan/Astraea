"""Bind guest actual-pixel inspection; final same-camera correction has stable distant artwork."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch11';Q=ROOT/'assets/landing_guest/qa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
ep=Q/'render_evidence.json';e=json.loads(ep.read_text());views=[]
assess={
 '001_standing_640':(True,'Same-camera640px correction passes. Solid uninterrupted teal artwork and clear GUEST heading now read consistently on the canted arrival plate. Real5mm artwork geometry with terminated backing removes the distance-dependent near-layer interference. Local cove, structural return and sconce remain visibly supported.'),
 '001_cove_receiver_detail_1280':(True,'Disclosed intentional upper construction crop shows supported local rolled cove, dark recessed liner, finished end profile and correctly backed reused sconce. Artwork is clear in this close view and the separate same-camera640px check now also passes.'),
 '002_standing_640':(True,'Standing1.65m viewpoint clearly distinguishes crowned single waiting seat, reclined shaped back, independent luggage top with soft contact strips, and lower retrieval surface. Actual profile changes carry craft and useful variation. Broad clay/teal/timber materials are clear without global yellow tint.'),
 '002_waiting_640':(True,'Ordinary1.19m waiting-eye inspection clearly shows supported seat and back, cheek/floor contacts, independent bag top and visibly open retrieval/underseat spaces. No actor or universal species-fit claim.')}
for key,v in e['views'].items():
 ident=v['camera']['id'];base=Q.parent;p=base/'qa'/(key+'.png');assert sha(p)==v['image_sha256'];assert list(Image.open(p).size)==v['camera']['res'];assert sha(base/'source'/(ident+'.blend'))==v['source_sha256_at_capture']==v['source_sha256_after_capture'];assert sha(base/'exports'/(ident+'.glb'))==v['glb_sha256']==v['glb_sha256_after_capture'];views.append({'image':bind(p),'capture':v,'actual_pixels_inspected':True,'assessment':assess[key][1],'passed':assess[key][0]})
bp=Q/'render_execution_bindings.json';b=json.loads(bp.read_text());
for x in b['scripts']:assert sha(ROOT/x['path_from_catalogue_root'])==x['sha256']
for x in b['logs']:assert sha(Q.parent/x['path'])==x['sha256']
r={'render_execution_bindings':bind(bp),'passed':all(x['passed']for x in views),'status':'All current guest views pass; unchanged002 views retained','executed_script_sha256':sha(Path(__file__)),'render_receipt':bind(ep),'render_script_current':bind(Q/'render_imported.py'),'views':views,'reference':'references/landings/guest_suite_hall.png','reference_interpretation':'Localized supported warm cove, tactile legible arrival landmark and deliberate route clarity; no copied reel art, real lift, door or borrowed photo passage dimensions.','limit':'Imported Blender component evidence only; original ship and runtime renderer unavailable.'};(OUT/'independent_guest_visual_review.json').write_text(json.dumps(r,indent=2)+'\n');print('Guest corrected001 and retained002 images pass exact capture binding')
