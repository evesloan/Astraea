"""Label accepted actual GLB frames without altering their rendered content."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=lambda n:ImageFont.truetype(fontfile,n)
canvas=Image.new('RGB',(1280,892),(26,32,36));draw=ImageDraw.Draw(canvas)
draw.text((24,16),'ASTRAEA / GUEST + STAFF LANDING INTERFACES',font=f(25),fill=(242,238,226))
draw.text((24,52),'Four editable components guided by R3; imported-component QA, not a working lift or recovered room',font=f(16),fill=(200,210,211))
frames=[('assets/landing_guest/qa/001_standing_640.png','Guest directory / local cove / reused sconce'),('assets/landing_service/qa/003_supported_return_standing_640.png','Staff service controls / protected return / reused fixture'),('assets/landing_guest/qa/002_standing_640.png','Guest waiting seat / luggage surface / open retrieval'),('assets/landing_service/qa/004_fixed_edge_standing_640.png','Staff inspection surface / protected open retrieval edge')]
inputs=[]
for i,(rel,label) in enumerate(frames):
 p=ROOT/rel;im=Image.open(p).convert('RGB');assert im.size==(640,360);x=i%2*640;y=84+i//2*390;canvas.paste(im,(x,y));draw.text((x+14,y+365),label,font=f(14),fill=(230,228,219));inputs.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
draw.text((24,871),'Existing lights add no new designs. Host doors, headroom, support, actor fit and engine adoption remain pending.',font=f(14),fill=(197,205,207))
out=ROOT/'qa/batch11/Astraea_Batch11_Component_Preview.png';canvas.save(out)
(ROOT/'qa/batch11/preview_manifest.json').write_text(json.dumps({'scope':'Labelled contact sheet of actual accepted component frames, original pixels unchanged','inputs':inputs,'output':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n');print(out)
