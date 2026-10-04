"""Annotate rendered inspection frames; no geometry/image content retouching."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
BASE=Path(__file__).resolve().parents[1]
evidence=json.loads((BASE/'qa/render_evidence.json').read_text());rows=[]
for name,view in evidence['views'].items():
    raw=BASE/'qa'/f'{name}_raw.png';im=Image.open(raw).convert('RGB');draw=ImageDraw.Draw(im)
    factor=im.width/640;size=max(10,round(11*factor));font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    h=round(24*factor);draw.rectangle((0,0,im.width,h),fill=(20,29,32));draw.text((round(8*factor),round(5*factor)), 'BLENDER COMPONENT QA | IMPORTED FINAL GLB',font=font,fill=(229,233,230))
    draw.rectangle((0,im.height-h,im.width,im.height),fill=(20,29,32));draw.text((round(8*factor),im.height-h+round(5*factor)),view['camera']['caption'],font=font,fill=(229,233,230))
    out=BASE/'qa'/f'{name}_labelled.png';im.save(out)
    rows.append({'file':str(out.relative_to(BASE)),'raw_file':str(raw.relative_to(BASE)),'size_px':list(im.size),'label':'Blender component QA, imported final GLB','caption':view['camera']['caption'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(BASE/'qa/review_media_manifest.json').write_text(json.dumps({'media':rows,'export_hashes':evidence['export_hashes']},indent=2)+'\n')
print('LABELLED_EVIDENCE',len(rows))
