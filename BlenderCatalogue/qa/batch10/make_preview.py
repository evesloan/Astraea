"""Label existing accepted raw frames; no scene or image content is synthesized."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];base=ROOT/'qa/batch10/assembly'
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda n:ImageFont.truetype(fontfile,n)
canvas=Image.new('RGB',(1280,892),(26,32,36));d=ImageDraw.Draw(canvas)
d.text((24,16),'ASTRAEA / D09 SALON TRANSITION KIT',font=f(25),fill=(242,238,226))
d.text((24,52),'Imported-component QA: spatially arranged kit and partial joined bay',font=f(17),fill=(200,210,211))
frames=[('quiet_from_planted_seat.png','Joined quiet edge / view from proposed planted seat'),('portal_join_standing.png','Deep portal and edge terminal / standing'),('quiet_forward_court.png','Forward view from quiet seat / proposed planted edge'),('service_end_standing.png','Separate rear service return / standing')]
rows=[]
for i,(name,label) in enumerate(frames):
 p=base/name;im=Image.open(p).convert('RGB');assert im.size==(640,360)
 x=(i%2)*640;y=84+(i//2)*390;canvas.paste(im,(x,y));d.text((x+14,y+365),label,font=f(14),fill=(230,228,219));rows.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d.text((24,871),'Six new designs. Host geometry, door mechanisms, guard infill and game adoption remain pending.',font=f(14),fill=(197,205,207))
out=ROOT/'qa/batch10/Astraea_Batch10_Component_Preview.png';canvas.save(out)
(ROOT/'qa/batch10/preview_manifest.json').write_text(json.dumps({'scope':'Labelled contact sheet of unmodified accepted imported-GLB frames','inputs':rows,'output':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n')
print(out)
