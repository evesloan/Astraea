"""Contact sheet of frozen actual imported component views, raw pixels retained."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[2];font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=lambda n:ImageFont.truetype(font,n)
im=Image.new('RGB',(1280,892),(26,32,36));d=ImageDraw.Draw(im)
d.text((24,16),'ASTRAEA / SHARED CREW REST AND PRIVACY',font=f(25),fill=(242,238,226));d.text((24,52),'Four editable component designs; actual imported GLBs in inspection lighting',font=f(17),fill=(200,210,211))
frames=[('assets/crew_rest/qa/001_standing.png','Single-place rest frame / shaped fitted bedding'),('assets/crew_rest/qa/002_closed_standing.png','Supported side curtain / one geometric privacy state'),('assets/crew_personal/qa/storage_open_standing_640.png','Personal storage / actual hollow drawer withdrawn'),('qa/batch15/assembly/r02/headboard_local_use.png','Individual light and shelf / mounted to actual frame')];inputs=[]
for i,(rel,label) in enumerate(frames):
 p=R/rel;src=Image.open(p).convert('RGB');assert src.size==(640,360);x=i%2*640;y=84+i//2*390;im.paste(src,(x,y));d.text((x+14,y+365),label,font=f(14),fill=(230,228,219));inputs.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d.text((24,871),'Four designs, reused in paired QA. Original cabin/body fit, full privacy, live controls and game adoption remain pending.',font=f(14),fill=(197,205,207))
p=R/'qa/batch15/Astraea_Batch15_Component_Preview.png';im.save(p);(R/'qa/batch15/preview_manifest.json').write_text(json.dumps({'scope':'Labelled actual imported-component views with unchanged raw image pixels; individual framing is not a relative size comparison','inputs':inputs,'output':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n');print(p)
