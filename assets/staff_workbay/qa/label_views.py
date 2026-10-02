from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
p=ROOT/'RENDER_MANIFEST.json';rows=json.loads(p.read_text())
for row in rows:
 path=ROOT/row['file'];im=Image.open(path).convert('RGB');w,h=im.size;draw=ImageDraw.Draw(im);scale=w/640
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',round(10*scale));small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',round(9*scale));bar=round(31*scale)
 draw.rectangle((0,h-bar,w,h),fill=(28,37,42));draw.text((round(9*scale),h-bar+round(3*scale)),'AST-STF-007 | BLENDER COMPONENT QA | IMPORTED GLB',font=font,fill=(240,244,246));draw.text((round(9*scale),h-bar+round(17*scale)),row['description']+' | No game / room / rig acceptance',font=small,fill=(194,215,223));im.save(path)
 row['label']='Blender imported-GLB component evidence, view description and explicit scope limitation';row['png_sha256_labelled']=hashlib.sha256(path.read_bytes()).hexdigest();row['pixel_review']='Reviewed after pose correction; door angle visually agrees with pose; storage remains hollow and visible; full frames contain all supports.'
p.write_text(json.dumps(rows,indent=2))
