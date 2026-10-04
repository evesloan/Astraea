from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent/'arrangement'
for p in ROOT.glob('*.png'):
 if p.stem.endswith('_labelled'):continue
 im=Image.open(p).convert('RGB');w,h=im.size
 band=28 if w==640 else 44
 out=Image.new('RGB',(w,h+2*band),(22,30,31));out.paste(im,(0,band));d=ImageDraw.Draw(out)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12 if w==640 else 19)
 d.text((9,7 if w==640 else 11),'BLENDER COMPONENT QA | Imported final GLBs',font=font,fill=(227,234,230))
 label='Six original designs + same-design start closure | No game integration'
 if p.stem=='seated_bench_glance_640':label='Proposed bench-eye glance | Contact / actor fit pending in game'
 d.text((9,h+band+7 if w==640 else h+band+11),label,font=font,fill=(227,234,230))
 out.save(ROOT/(p.stem+'_labelled.png'))
