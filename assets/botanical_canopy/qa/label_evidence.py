from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];rows=[]
for p in sorted((ROOT/'qa').glob('*_raw.png')):
 im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);s=im.width/640
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',max(10,int(11*s)))
 d.rectangle((0,0,im.width,int(24*s)),fill=(23,30,34));d.text((int(10*s),int(5*s)),'AST-BOT-001  |  BLENDER COMPONENT QA  |  ACTUAL GLB',font=font,fill=(227,237,234))
 d.rectangle((0,im.height-int(24*s),im.width,im.height),fill=(23,30,34))
 desc='OPAQUE FOLDED LEAVES  /  EDITABLE SOURCE  /  NO GAME ADOPTION'
 d.text((int(10*s),im.height-int(19*s)),desc,font=font,fill=(198,217,207))
 out=p.with_name(p.name.replace('_raw',''));im.save(out)
 rows.append({'file':out.name,'dimensions_px':list(im.size),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source':'Actual imported AST-BOT-001.glb rendered by Blender EEVEE_NEXT; label overlay only'})
(ROOT/'qa/labelled_evidence.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
