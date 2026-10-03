"""Contact sheet of frozen actual imported component views, raw pixels retained."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[2];font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=lambda n:ImageFont.truetype(font,n)
im=Image.new('RGB',(1280,892),(26,32,36));d=ImageDraw.Draw(im)
d.text((24,16),'ASTRAEA / RETAIL DISPLAY AND WORK',font=f(25),fill=(242,238,226));d.text((24,52),'Four editable component designs; actual imported GLBs in inspection lighting',font=f(17),fill=(200,210,211))
frames=[('qa/batch18/assembly/r01/entry_facing_bay.png','Joined display profile / entry-facing recess'),('qa/batch18/assembly/r01/island_browse.png','Stepped display / supported reusable case'),('qa/batch18/assembly/r01/public_wrapping_edge.png','Guest parcel rest beside the clear wrapping wing'),('qa/batch18/assembly/r01/staff_wrapping_edge.png','Staff stock and wrapping access')];inputs=[]
for i,(rel,label) in enumerate(frames):
 p=R/rel;src=Image.open(p).convert('RGB');assert src.size==(640,360);x=i%2*640;y=84+i//2*390;im.paste(src,(x,y));d.text((x+14,y+365),label,font=f(14),fill=(230,228,219));inputs.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d.text((24,871),'Partial R070 source study. Host doors, activity slots, operator fit, transactions and engine use remain pending.',font=f(14),fill=(197,205,207))
p=R/'qa/batch18/Astraea_Batch18_Component_Preview.png';im.save(p);(R/'qa/batch18/preview_manifest.json').write_text(json.dumps({'scope':'Labelled actual imported-component views with unchanged raw image pixels; individual framing is not a relative size comparison','inputs':inputs,'output':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n');print(p)
