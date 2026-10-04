"""Bind current actual-GLB capture files to source/export and validation receipts."""
from pathlib import Path
import hashlib,json
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ev=json.loads((BASE/'qa/render_evidence.json').read_text());records=[]
for name,r in ev['views'].items():
 p=BASE/'qa'/f'{name}.png';im=Image.open(p);assert list(im.size)==r['camera']['res'];im.verify()
 for a in r['assets']:
  assert sha(BASE/a['relative_path'])==a['sha256'];assert sha(BASE/'source'/f"{a['id']}.blend")==a['source_sha256']
 records.append({'path':'qa/'+p.name,'sha256':sha(p),'resolution':r['camera']['res'],'purpose':r['camera']['purpose'],'evidence':'Actual GLB import, component/section QA only','camera_eye_source_z_m':r['camera']['location'][2],'asset_bindings':r['assets']})
checks={}
for fn in('glb_independent_validation.json','source_reload_checks.json','collision_validation.json','source_only_rebuild.json'):
 p=BASE/'qa'/fn;d=json.loads(p.read_text());ok=all(x['status']=='PASS' for x in d) if isinstance(d,list) else d['status']=='PASS';assert ok;checks[fn]={'sha256':sha(p),'status':'PASS'}
family=json.loads((BASE/'manifest.json').read_text())
out={'status':'PASS','scope':'Three new adjustable catalogue designs; actual GLB component views. No installation, recovered host, game render or universal fit claim.','new_unique_designs':3,'total_triangles':sum(a['evaluated_triangles'] for a in family['assets']),'media':records,'verification_receipts':checks,'prior_evidence':'qa/before_coplanar_surface_fix/','known_scope_limits':['Collision curved chords are proposed approximations, local exterior error up to18mm','The arrival/quiet/court/service spatial relationship is owned by the lead combined inspection','No moving-door interface dimensions or final host polygon are available']}
(BASE/'qa/review_media_manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','views':len(records),'triangles':out['total_triangles']},indent=2))
