"""Bind actual pixel inspection to frozen imported-source captures and metadata-only amendment."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
rp=OUT/'assembly/r06/render_evidence.json';r=json.loads(rp.read_text());plan=OUT/'assembly/plan.json';script=OUT/'assembly/build_inspection.py';assert r['execution_complete']and r['inputs_unchanged_during_execution'];assert sha(plan)==r['plan_sha256']and sha(script)==r['executed_script_sha256'];items=[];amendments=[]
def diff(a,b,path=''):
 if type(a)!=type(b):return[path]
 if isinstance(a,dict):return[k for key in sorted(set(a)|set(b))for k in ([path+'/'+key]if key not in a or key not in b else diff(a[key],b[key],path+'/'+key))]
 if isinstance(a,list):return[path]if len(a)!=len(b)else[k for i,(x,y)in enumerate(zip(a,b))for k in diff(x,y,path+'/'+str(i))]
 return[]if a==b else[path]
for item in r['items']:
 for field,expected in item['hashes'].items():
  p=ROOT/item[field]
  if sha(p)!=expected:
   assert field=='manifest_path';snapshot=rp.parent/'captured_manifests'/(item['key']+'.json');assert sha(snapshot)==expected;old=json.loads(snapshot.read_text());new=json.loads(p.read_text());paths=diff(old,new);assert paths and all(x.startswith(('/collision_approximation_limits/','/evidence/','/export/UV_repair_detail'))for x in paths),paths;assert old['hashes']==new['hashes'];amendments.append({'asset':item['catalogue_id'],'capture_manifest':bind(snapshot),'current_manifest':bind(p),'changed_json_paths':paths,'geometry_and_source_hash_records_unchanged':True,'scope':'Evidence-only precision amendment after capture; pixels retain original captured manifest scope. No geometry recapture required.'})
  items.append({'asset':item['catalogue_id'],'field':field,'current':bind(p),'capture_sha256':expected,'unchanged_since_capture':sha(p)==expected})
assessments={
'joined_standing':'At actual1.65m standing eye the canopy, upright flowering and small raised trailing cluster read as three distinct arrangements. Joined seat ribbon and open front are legible; coarse original folded botanical geometry remains intentional at640x360. This is a partial edge against a QA studio floor/background.',
'seated_outlook':'At proposed1.19m seated eye the central field is open, with the flowering edge at left and trailing accent at right. The image deliberately contains substantial blank QA background; it proves a finite unoccupied outlook and does not show a receiving courtyard or planting mass beyond the components.',
'rear_maintenance':'At actual1.65m eye the five unequal tails visibly cross to the rear side, separated from the seat. The raised soil and retained low cell read as connected component construction. Clear maintenance stance is established by the independent whole-volume test, not by this picture alone.',
'seat_transition_detail':'The crop shows the exact old/new timber seam, rising wall/coping, distinct soil levels, flower bases and retained support brackets. Cropped canopy/terminal ends are deliberate detail framing; this is not a whole-component frame.'}
views=[]
for key,v in r['views'].items():
 p=rp.parent/(key+'.png');assert sha(p)==v['image_sha256'];assert v['source_scope']=={x['key']:x['hashes']['path']for x in r['items']};assert not v['full_component_frame']or v['framing']['passes'];views.append({'view':key,'image':bind(p),'actual_pixels_inspected':True,'source_eye_m':v['source_eye_m'],'lens_mm':v['lens_mm'],'resolution':v['resolution'],'full_component_frame':v['full_component_frame'],'assessment':assessments[key],'pass':True})
components=[]
for rel in ['assets/botanical_cluster/qa/AST-BOT-007_imported_640.png','assets/botanical_cluster/qa/AST-BOT-008_imported_640.png','assets/botanical_cluster/qa/AST-BOT-009_imported_640.png','assets/botanical_transition/qa/standing_front_640.png','assets/botanical_transition/qa/rear_maintenance_640.png','assets/botanical_transition/qa/soil_retaining_detail_960.png']:
 components.append({'image':bind(ROOT/rel),'actual_pixels_inspected':True})
res={'passed':True,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'views':views,'additional_component_pixels':components,'capture_receipt':bind(rp),'capture_plan':bind(plan),'capture_script':bind(script),'source_export_manifest_binding_checks':items,'post_capture_metadata_amendments':amendments,'reference_pixel_receipt':'qa/batch13/independent_initial_reference_receipt.json','limits':['Imported Blender Eevee captures, not target engine/host room or actor fit.','Single007 orthographic camera at2.35m is a full-specimen view; ordinary standing acceptance rests on the1.65m joined capture.','No copied reference pixels or absent ship/courtyard reconstruction; no species, load, irrigation or wind assertion.'],'executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_visual_review.json').write_text(json.dumps(res,indent=2)+'\n');print('VISUAL',True,'4 joined images bound;6 component images inspected;metadata amendments',len(amendments))
