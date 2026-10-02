"""Labelled actual imported-component frames, preserving raw pixel arrays."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=lambda n:ImageFont.truetype(font,n)
canvas=Image.new('RGB',(1280,892),(26,32,36));d=ImageDraw.Draw(canvas)
d.text((24,16),'ASTRAEA / BOTANICAL COMMONS COMPONENTS',font=f(25),fill=(242,238,226))
d.text((24,52),'Four editable source designs; partial joined planted-seat edge in component inspection lighting',font=f(17),fill=(200,210,211))
frames=[('qa/batch13/assembly/r06/joined_standing.png','Joined planted edge / standing inspection'),('qa/batch13/assembly/r06/rear_maintenance.png','Rear trailing form / separate maintenance side'),('qa/batch13/assembly/r06/seat_transition_detail.png','Retained seat and supported raised planting cell'),('assets/botanical_cluster/qa/AST-BOT-007_imported_640.png','Pleated fan crown / actual consolidated GLB')];inputs=[]
for i,(rel,label) in enumerate(frames):
 p=ROOT/rel;im=Image.open(p).convert('RGB');assert im.size==(640,360);x=i%2*640;y=84+i//2*390;canvas.paste(im,(x,y));d.text((x+14,y+365),label,font=f(14),fill=(230,228,219));inputs.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d.text((24,871),'Existing seat/closure reused. Whole-court, body/species, growing roots, wind and game performance remain unverified.',font=f(14),fill=(197,205,207))
out=ROOT/'qa/batch13/Astraea_Batch13_Component_Preview.png';canvas.save(out)
(ROOT/'qa/batch13/preview_manifest.json').write_text(json.dumps({'scope':'Labelled actual imported-component views; source pixels unchanged','inputs':inputs,'output':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n');print(out)
