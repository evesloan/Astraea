"""Label component renders without altering the actual rendered view."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
for file in sorted(ROOT.glob('structure_*.png')):
    if file.stem.endswith('_labelled'):continue
    image=Image.open(file).convert('RGB');width,height=image.size
    size=9 if width==640 else 17
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    footer=13 if width==640 else 25
    out=image.copy();draw=ImageDraw.Draw(out);draw.rectangle((0,0,width,footer),fill=(24,31,38))
    title='BLENDER COMPONENT QA | IMPORTED GLBs | NO ORIGINAL-ROOM OR GAME ACCEPTANCE'
    draw.text((7,1),title,font=font,fill=(228,233,232))
    out.save(file.with_name(file.stem+'_labelled.png'))
    print(file.with_name(file.stem+'_labelled.png'))
