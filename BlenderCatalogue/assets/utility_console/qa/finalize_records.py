"""Tie delivery media and dependency hashes to the final source/GLB bytes."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];C=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'AST-ENG-003.manifest.json').read_text());v=json.loads((R/'qa/render_evidence.json').read_text());source=R/m['source'];glb=R/m['exchange']
assert sha(source)==m['source_sha256']==v['source_sha256']
assert sha(glb)==m['glb_sha256']==v['glb_sha256']
assert not v['preflight_only']
media=[]
for row in v['views']:
 p=R/'qa'/(row['key']+'.png');size=list(Image.open(p).size);assert size==row['resolution']
 media.append({'file':str(p.relative_to(R)),'resolution':size,'sha256':sha(p),'bytes':p.stat().st_size,'purpose':row['purpose'],'source_glb_sha256':sha(glb),'source_blend_sha256':sha(source)})
(R/'qa/review_media_manifest.json').write_text(json.dumps({'asset_id':'AST-ENG-003','evidence_scope':v['evidence_scope'],'renderer':v['renderer'],'denoiser':v['denoiser'],'views':media},indent=2))
staff=json.loads((C/'materials/staff/manifest.json').read_text());paths=[C/'standards/staff_materials.py',C/'materials/staff/manifest.json']+[C/'materials/staff'/staff['materials'][role]['file'] for role in m['material_roles'] if role in staff['materials']]+[R/'textures/console_graphics.png',R/'textures/draw_console_graphics.py',R/'textures/console_graphics.json',R/'source/build_utility_console.py',R/'source/write_collision_proposals.py']
(R/'dependency_manifest.json').write_text(json.dumps({'asset_id':'AST-ENG-003','scope':'Source-generation dependencies and exact used image bytes. Shared staff definitions/textures unchanged.','files':[{'path':str(p.relative_to(C)),'sha256':sha(p),'bytes':p.stat().st_size} for p in paths]},indent=2))
print('CONSOLE_DELIVERY_HASHES_MATCH',len(media),'views',sha(glb))
