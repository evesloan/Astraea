from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[1];e=json.loads((BASE/'qa/render_evidence.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for name,v in e['views'].items():
    src=BASE/'qa'/f'{name}_raw.png';im=Image.open(src).convert('RGB');w,h=im.size;large=w>800;bar=104 if large else 72;out=Image.new('RGB',(w,h+bar),(25,37,40));out.paste(im,(0,0));d=ImageDraw.Draw(out);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22 if large else 12);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17 if large else 10)
    label={'silhouette':'AST-AQU-006 Cove leisure seating float | imported GLB at 640 x 360','standing':'AST-AQU-006 | body-scale view, camera Z 1.65 m | imported GLB','handle':'Grip component detail | 46 mm grip diameter; about 121 mm clear below arch','seat':'Seat component detail | shaped membrane + open drain; contact points at X +/-0.12 m'}[name]
    d.text((14,h+10),label,font=font,fill=(232,229,216));d.text((14,h+(40 if large else 32)),'COMPONENT QA ONLY | Datum Z0 = proposed waterline; no buoyancy or species-fit result',font=small,fill=(180,207,204));d.text((14,h+(70 if large else 49)),'Opaque orange / pearl flexible skin, teal sling, dark grips | studio floor and lights are QA aids',font=small,fill=(180,207,204))
    dest=BASE/'qa'/f'{name}_labelled.png';out.save(dest);rows.append({'view':name,'raw_file':str(src.relative_to(BASE)),'raw_sha256':sha(src),'raw_size_px':list(im.size),'labelled_file':str(dest.relative_to(BASE)),'labelled_sha256':sha(dest),'labelled_size_px':list(out.size),'label_edit':'Added caption strip outside unaltered raw render pixels','source_glb_sha256':e['glb_sha256'],'source_blend_sha256':e['source_sha256']})
(BASE/'qa/review_media_manifest.json').write_text(json.dumps({'scope':e['scope'],'artifacts':rows},indent=2)+'\n');print('Labelled',len(rows),'views')
