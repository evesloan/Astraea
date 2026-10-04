from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
plans={'guest':('AST-HSP-001 + 002 | GUEST THREE-QUARTER','Actual imported GLB | Pantry counter and compatible curved return'),'staff':('AST-HSP-001 + 002 | STAFF SERVICE VIEW','Actual imported GLB | Proposed drawer travel +Y 0.32m; open service shelving'),'standing':('AST-HSP-001 + 002 | STANDING VIEW','Actual imported GLB | Camera Z1.65m | Raw render 640 x 360'),'joint':('AST-HSP-001 + 002 | JOINT DETAIL','Actual imported GLB | 2mm seam; matching shaped profiles and closed end bulkheads')}
manifest={'scope':'Labels are appended outside original render pixels; no asset pixels retouched','views':[]}
for name,(title,sub) in plans.items():
 p=BASE/'qa'/f'{name}_raw.png';im=Image.open(p).convert('RGB');w,h=im.size;small=w<1000;footer=72 if small else 92;out=Image.new('RGB',(w,h+footer),(22,29,34));out.paste(im,(0,0));d=ImageDraw.Draw(out)
 def font(size):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
 x=15 if small else 24;y=h+12;d.text((x,y),title,font=font(14 if small else 22),fill=(230,234,236));d.text((x,y+(21 if small else 31)),sub,font=font(11 if small else 16),fill=(193,203,209));d.text((x,y+(39 if small else 54)),'COMPONENT QA ONLY | No game, room, physics or target-PC claim',font=font(10 if small else 14),fill=(154,170,179));dest=BASE/'qa'/f'{name}_labelled.png';out.save(dest)
 manifest['views'].append({'name':name,'raw_file':str(p.relative_to(BASE)),'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'raw_dimensions_px':[w,h],'labelled_file':str(dest.relative_to(BASE)),'labelled_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'labelled_dimensions_px':list(out.size),'caption':[title,sub]})
(BASE/'qa/review_media_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
