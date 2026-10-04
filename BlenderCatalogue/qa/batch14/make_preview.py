"""Contact sheet of frozen actual imported component views, raw pixels retained."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[2];font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=lambda n:ImageFont.truetype(font,n)
im=Image.new('RGB',(1280,892),(26,32,36));d=ImageDraw.Draw(im)
d.text((24,16),'ASTRAEA / AQUATIC ARRIVAL AND USE',font=f(25),fill=(242,238,226));d.text((24,52),'Four editable component designs; actual imported GLBs in inspection lighting',font=f(17),fill=(200,210,211))
frames=[('assets/aquatic_towel_use/qa/dry_standing_raw.png','Protected dry supply / integrated stock'),('assets/aquatic_towel_use/qa/return_standing_raw.png','Guarded used return / closed container state'),('assets/aquatic_wet_use/qa/009_standing.png','Optional refreshment fixture / capped connections'),('assets/aquatic_wet_use/qa/010_standing.png','Supported rinse-control housing / inactive controls')];inputs=[]
for i,(rel,label) in enumerate(frames):
 p=R/rel;src=Image.open(p).convert('RGB');assert src.size==(640,360);x=i%2*640;y=84+i//2*390;im.paste(src,(x,y));d.text((x+14,y+365),label,font=f(14),fill=(230,228,219));inputs.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d.text((24,871),'Source includes removable parts. Original room fit, fluids, laundry, species suitability and game operation remain pending.',font=f(14),fill=(197,205,207))
p=R/'qa/batch14/Astraea_Batch14_Component_Preview.png';im.save(p);(R/'qa/batch14/preview_manifest.json').write_text(json.dumps({'scope':'Labelled actual imported-component views with unchanged raw image pixels; individual framing is not a relative size comparison','inputs':inputs,'output':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n');print(p)
