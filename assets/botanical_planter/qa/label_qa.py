from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa'
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';rows=[]
for p in sorted(QA.glob('*.png')):
 if p.stem.endswith('_labelled'):continue
 im=Image.open(p).convert('RGB');draw=ImageDraw.Draw(im);size=12 if im.width==640 else 17;font=ImageFont.truetype(font_path,size)
 title='BLENDER COMPONENT QA  |  '+p.stem.replace('_',' ').upper()
 draw.rectangle((0,0,im.width,26 if im.width==640 else 35),fill=(25,29,31));draw.text((10,6),title,font=font,fill=(232,234,229))
 note='Actual imported GLBs · independent catalogue · no room / game / actor certification'
 draw.rectangle((0,im.height-23 if im.width==640 else im.height-31,im.width,im.height),fill=(25,29,31));draw.text((10,im.height-18 if im.width==640 else im.height-25),note,font=ImageFont.truetype(font_path,10 if im.width==640 else 15),fill=(214,216,210))
 out=p.with_stem(p.stem+'_labelled');im.save(out)
 rows.append({'raw':p.name,'labelled':out.name,'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'labelled_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'resolution':list(im.size)})
(QA/'labelled_evidence.json').write_text(json.dumps(rows,indent=2)+'\n')
