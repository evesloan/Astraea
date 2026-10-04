"""Label finished imported-GLB captures without modifying product textures."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
ev=json.loads((BASE/'qa/render_evidence.json').read_text());out=[]
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
for name,row in ev['views'].items():
 raw=BASE/'qa'/f'{name}_raw.png';im=Image.open(raw).convert('RGB');d=ImageDraw.Draw(im);w,h=im.size;size=13 if w==640 else 22;small=11 if w==640 else 17
 f=ImageFont.truetype(font_path,size);fs=ImageFont.truetype(font_path,small)
 height=23 if w==640 else 38;d.rectangle((0,0,w,height),fill=(24,34,39));d.text((10,4 if w==640 else 7),row['camera']['caption'],font=f,fill=(235,241,243))
 foot='ACTUAL IMPORTED GLB | component QA only | EEVEE, no denoiser';bottom=20 if w==640 else 30;d.rectangle((0,h-bottom,w,h),fill=(24,34,39));d.text((10,h-bottom+3),foot,font=fs,fill=(207,219,222))
 dest=BASE/'qa'/f'{name}.png';im.save(dest)
 out.append({'name':name,'labelled_path':str(dest.relative_to(BASE)),'raw_path':str(raw.relative_to(BASE)),'resolution_px':[w,h],'glb_sha256':row['glb_sha256'],'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'labelled_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'full_silhouette':row['full_component_required'],'intentional_crop':row['intentional_crop'],'scope':'Actual imported GLB in neutral component QA stage, not original-engine evidence'})
(BASE/'qa/review_media_manifest.json').write_text(json.dumps({'renderer':'EEVEE_NEXT, no denoiser','views':out},indent=2)+'\n');print('LABELLED_MACHINE_EVIDENCE',len(out))
