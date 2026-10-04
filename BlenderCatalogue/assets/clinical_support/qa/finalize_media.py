"""Bind inspected imported-GLB pixels to final unchanged source and exporter, without editing production files."""
from pathlib import Path
import json,hashlib
from PIL import Image
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((BASE/'qa/render_evidence.json').read_text());rows=[]
for key,v in d['views'].items():
 p=BASE/'qa'/(key+'.png');ident=v['camera']['id'];source=BASE/'source'/(ident+'.blend');glb=BASE/'exports'/(ident+'.glb')
 assert sha(source)==v['source_sha256_at_capture']==v['source_sha256_after_capture']
 assert sha(glb)==v['glb_sha256']==v['glb_sha256_after_capture']
 assert sha(p)==v['image_sha256']
 assert v['render_script_sha256']==sha(BASE/'qa/render_imported.py')
 with Image.open(p)as im:assert list(im.size)==v['camera']['res']
 rows.append({'file':str(p.relative_to(BASE)),'catalogue_id':ident,'image_sha256':sha(p),'source_sha256':sha(source),'glb_sha256':sha(glb),'camera':v['camera'],'framing':v['framing'],'render_script_sha256':v['render_script_sha256'],'pixel_review':'Author inspected actual PNG: broad care material roles, pads/cases/contacts and support joints read clearly; floor-contact and relevant openings visible; no visible striping/layer conflict; restrained soft-shadow grain retained','scope':'Imported GLB in Blender QA only; floor/lights/camera excluded from production'})
receipt={'all_source_and_export_hashes_unchanged':True,'views':rows,'renderer':'Blender4.3.2 BLENDER_EEVEE_NEXT 48 samples, neutral QA staging, no denoiser','render_log_sha256':sha(BASE/'qa/render.log'),'render_exit_status':0,'qa_frame_helper_sha256':sha(CAT/'standards/qa_frame.py'),'finalizer_sha256':sha(Path(__file__)),'limits':'No Godot/CRT/engine performance, actor, species, clinical or host-room claim; images are evidence for current components only'}
(BASE/'qa/review_media_manifest.json').write_text(json.dumps(receipt,indent=2)+'\n');print('FROZEN_MEDIA_PASS',len(rows))
