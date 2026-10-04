from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parent
labels={
'joined_full_silhouette_640':'BLENDER / imported GLB • joined wall family • full silhouette',
'joined_eye_height_640':'BLENDER / imported GLB • eye Z1.65 m • lower-foot crop',
'corner_bumper_cove_detail_1280':'BLENDER / imported GLB • continuous inner guard, wash-panel joints and upper cove',
'closed_terminal_detail_1280':'BLENDER / imported GLB • closed end cap, folded edge and foot'}
for name,label in labels.items():
 im=Image.open(ROOT/(name+'.png')).convert('RGB');draw=ImageDraw.Draw(im);h=25 if im.width<1000 else 32
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11 if im.width<700 else 16)
 draw.rectangle((0,im.height-h,im.width,im.height),fill=(20,29,35));draw.text((9,im.height-h+6),label,font=font,fill=(226,232,234))
 im.save(ROOT/(name+'_labelled.png'),optimize=True)
print('Four evidence labels written; image resolutions preserved')
