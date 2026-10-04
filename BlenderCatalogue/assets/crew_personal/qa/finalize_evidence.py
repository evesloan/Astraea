"""Bind inspected imported pictures and verify frozen asset inputs remain current."""
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
render=json.loads((BASE/'qa/render_evidence.json').read_text());checks=[]
for v in render['views']:
 inputs=[{'path':d['file'],'captured_sha256':d['sha256'],'current_sha256':sha(CAT/d['file']),'unchanged':sha(CAT/d['file'])==d['sha256']}for d in v['inputs']]
 checks.append({'image':v['image'],'captured_image_sha256':v['image_sha256'],'current_image_sha256':sha(BASE/'qa'/v['image']),'image_matches':v['image_sha256']==sha(BASE/'qa'/v['image']),'inputs':inputs,'whole_target_visible':v['camera_preflight']['whole_target_visible']})
sources=[]
for r in json.loads((BASE/'manifest.json').read_text())['assets']:
 for field,hfield in[('source','source_sha256'),('export','glb_sha256')]:sources.append({'file':r[field],'manifest_recorded_sha256':r[hfield],'current_sha256':sha(BASE/r[field]),'unchanged_since_pre_capture_manifest':sha(BASE/r[field])==r[hfield]})
row={'method':'Compare final capture hashes and pre-capture source/export manifest records to current physical files, without rerendering or writing assets','checks':checks,'source_export_checks':sources,'all_passed':all(c['image_matches']and c['whole_target_visible']and all(q['unchanged']for q in c['inputs'])for c in checks)and all(c['unchanged_since_pre_capture_manifest']for c in sources)};(BASE/'qa/final_evidence_guard.json').write_text(json.dumps(row,indent=2)+'\n')
visual={'reviewer':'Author pixel inspection using image viewer, 2026-10-03','images':[{'image':v['image'],'sha256':v['image_sha256']}for v in render['views']],'observations':['Storage closed and open at standing eye show complete unit, supported four feet, accessible open shelves, actual hollow drawer and separated moving body','Reading module seated and detailed images show real backplate on headboard, returned light shield, small control face, side suspension brackets and clear liner surface','All new modeled parts remain modest staff finishes; no assigned personal belongings, signage identities, story or room allocation','The opal underside is deliberately shielded from upper viewing angles; geometry/physical surface records establish it, images do not claim emitter photometry','QA light/grain/shadows remain inspection art, not Godot renderer/performance evidence'],'passes':True};(BASE/'qa/author_visual_review.json').write_text(json.dumps(visual,indent=2)+'\n');print('FINAL_EVIDENCE_GUARD',row['all_passed'])
