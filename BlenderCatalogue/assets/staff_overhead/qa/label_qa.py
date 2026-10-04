"""Add scope labels outside the untouched Blender image; no crop/color alteration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
views={
 'service_bay':('JOINED STAFF SERVICE BAY  |  CAMERA 1.65 m','QA mounting datum 3.30 m; marked aisle 1.8 m wide; closed cabinet outside it','Imported components only. 295 mm cabinet-to-aisle gap; no real ship-route acceptance.'),
 'silhouette':('JOINED SERVICE COMPONENTS  |  AST-STF-004 / 005 / 006','1.2 m straight pitch + R0.60 m quarter turn; formed housing, visible supports','Full silhouette. Imported GLBs; ceiling mounting datum Z0 in each source.'),
 'standing':('STANDING VIEW  |  CAMERA 1.65 m','Mount 3.30 m; lowest guard 2.6925 m','Component placement only; no ship route clearance claim.'),
 'joint':('JOIN CONSTRUCTION  |  STRAIGHT TO TURN','2 mm body seam; rail splice collars, hollow conduit sleeves and cable ties','Imported GLB close crop. Final material roles and metric UVs.'),
 'fixture':('UTILITY FIXTURE  |  AST-STF-006','Formed housing, opal lens, reflector, guard and two supported mounts','No electrical function or runtime light. Minimum mount for 2.65 m: 3.2575 m.')}
for name,(title,line1,line2) in views.items():
 im=Image.open(BASE/(name+'_raw.png')).convert('RGB');w,h=im.size;sm=w<=640;top=45 if sm else 66;bottom=54 if sm else 82;out=Image.new('RGB',(w,h+top+bottom),(24,32,37));out.paste(im,(0,top));d=ImageDraw.Draw(out);f=ImageFont.truetype(font,12 if sm else 20);g=ImageFont.truetype(font,11 if sm else 17)
 d.text((16,8),title,font=f,fill=(230,236,233));d.text((16,27 if sm else 36),'BLENDER COMPONENT EVIDENCE  |  NOT A GAME OR SHIP INSTALLATION',font=g,fill=(164,187,190))
 d.text((16,h+top+8),line1,font=g,fill=(230,236,233));d.text((16,h+top+(29 if sm else 39)),line2,font=g,fill=(181,199,201));out.save(BASE/(name+'_labelled.png'))
print('LABELS_COMPLETE')
