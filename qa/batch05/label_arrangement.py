from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent/'arrangement'
for p in OUT.glob('*.png'):
 if p.stem.endswith('_labelled'):continue
 im=Image.open(p).convert('RGB');w,h=im.size;band=28 if w==640 else 44
 out=Image.new('RGB',(w,h+2*band),(22,30,31));out.paste(im,(0,band));d=ImageDraw.Draw(out);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12 if w==640 else 19)
 d.text((9,7 if w==640 else 11),'AQUATIC COMPONENT QA | Actual imported GLBs',font=font,fill=(228,235,230))
 d.text((9,h+band+7 if w==640 else h+band+11),'Neutral inspection supports | No water simulation or game adoption',font=font,fill=(228,235,230))
 out.save(OUT/(p.stem+'_labelled.png'))
