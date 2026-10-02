"""Add small evidence captions in existing image margins; no asset pixels changed."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
BASE=Path(__file__).resolve().parents[1];ev=json.loads((BASE/'qa/render_evidence.json').read_text())
for name,row in ev['views'].items():
 p=BASE/'qa'/f'{name}.png';im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);w,h=im.size;large=w>640;top=34 if large else 22;bottom=24 if large else 17
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17 if large else 10);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12 if large else 8)
 d.rectangle((0,0,w,top),fill=(29,36,39));d.rectangle((0,h-bottom,w,h),fill=(29,36,39))
 title=row['camera']['id']+' | '+name.split('_',1)[1].replace('_',' ')+' | ACTUAL GLB'
 d.text((10,7 if large else 5),title,font=font,fill=(240,236,223));d.text((10,h-bottom+5 if large else h-bottom+4),'Blender component QA only | no engine lighting, physics or species-fit claim',font=small,fill=(220,225,224));im.save(p)
print('LABELLED',len(ev['views']))
