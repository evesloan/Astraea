"""Contact sheet of frozen actual imported component views, raw pixels retained."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[2];font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=lambda n:ImageFont.truetype(font,n)
im=Image.new('RGB',(1280,892),(26,32,36));d=ImageDraw.Draw(im)
d.text((24,16),'ASTRAEA / AUDITORIUM COMPONENTS',font=f(25),fill=(242,238,226));d.text((24,52),'Four editable component designs; actual imported GLBs in inspection lighting',font=f(17),fill=(200,210,211))
frames=[('assets/auditorium_arrival/qa/001_public_standing.png','Programme return / original cultural graphic'),('assets/auditorium_arrival/qa/002_public_standing.png','Usher station / shaped public and staff sides'),('assets/auditorium_use/qa/seat_closed_seated_640.png','868-triangle repeating seat / retained folding pan'),('assets/auditorium_use/qa/stand_work_standing_640.png','Backstage cue and work light / inactive fixture')];inputs=[]
for i,(rel,label) in enumerate(frames):
 p=R/rel;src=Image.open(p).convert('RGB');assert src.size==(640,360);x=i%2*640;y=84+i//2*390;im.paste(src,(x,y));d.text((x+14,y+365),label,font=f(14),fill=(230,228,219));inputs.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d.text((24,871),'Component examples only. Original aisle/body/rake fit, acoustics, live controls and engine performance remain pending.',font=f(14),fill=(197,205,207))
p=R/'qa/batch16/Astraea_Batch16_Component_Preview.png';im.save(p);(R/'qa/batch16/preview_manifest.json').write_text(json.dumps({'scope':'Labelled actual imported-component views with unchanged raw image pixels; individual framing is not a relative size comparison','inputs':inputs,'output':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n');print(p)
