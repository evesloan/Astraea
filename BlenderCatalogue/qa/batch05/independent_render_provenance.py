from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
glbs={p.name:p for f in ['aquatic_lounge','aquatic_edges','aquatic_float'] for p in (ROOT/'assets'/f).rglob('*.glb') if 'qa' not in p.parts}
sources={p.stem:p for f in ['aquatic_lounge','aquatic_edges','aquatic_float'] for p in (ROOT/'assets'/f).rglob('*.blend') if 'qa' not in p.parts}
for f in ['aquatic_lounge','aquatic_edges','aquatic_float']:
 p=ROOT/'assets'/f/'qa/render_evidence.json';j=json.loads(p.read_text());checks=[]
 if f=='aquatic_lounge':
  for n,h in j['export_hashes'].items():checks.append({'asset':n,'glb_matches':sha(glbs[n])==h})
 elif f=='aquatic_edges':
  for r in j['artifacts']:checks.append({'asset':r['asset'],'glb_matches':sha(glbs[r['asset']+'.glb'])==r['glb_sha256'],'source_matches':sha(sources[r['asset']])==r['source_sha256']})
 else:checks.append({'asset':'AST-AQU-006','glb_matches':sha(glbs['AST-AQU-006.glb'])==j['glb_sha256'],'source_matches':sha(sources['AST-AQU-006'])==j['source_sha256']})
 rows.append({'family':f,'evidence_path':str(p.relative_to(ROOT)),'evidence_sha256':sha(p),'checks':checks})
p=OUT/'arrangement/evidence.json';j=json.loads(p.read_text());rows.append({'family':'arrangement','evidence_path':str(p.relative_to(ROOT)),'evidence_sha256':sha(p),'checks':[{'asset':r['name'],'glb_matches':sha(ROOT/r['file'])==r['sha256']} for r in j['imports']]})
v=json.loads((OUT/'independent_visual_review.json').read_text());images=[]
for r in v['reviews']:
 for x in r['images']:
  p=ROOT/x['path'];w,h=Image.open(p).size;images.append({'path':x['path'],'sha256':sha(p),'reviewed_image_hash_matches':sha(p)==x['sha256'],'width_px':w,'height_px':h,'review_stage':r['family']})
out={'scope':'Final metadata binds actual GLB/source hashes and independently inspected image bytes. Image-generation provenance is corroborated by the inspected render scripts and saved import evidence; not an engine trace.','evidence':rows,'images':images,'all_current_glb_hashes_match':all(all(c.get('glb_matches',True) and c.get('source_matches',True) for c in r['checks']) for r in rows),'all_reviewed_image_hashes_match':all(i['reviewed_image_hash_matches'] for i in images)}
(OUT/'independent_render_provenance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['evidence','images']},indent=2))
